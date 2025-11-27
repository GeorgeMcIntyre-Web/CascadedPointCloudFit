/**
 * Point cloud file reader.
 * 
 * Supports CSV and PLY file formats.
 * Ported from Python: cascaded_fit/io/readers.py
 */

import * as fs from 'fs/promises';
import * as path from 'path';
import Papa from 'papaparse';
import { PointCloud } from '../core/types';
import { PointCloudHelper } from '../core/PointCloudHelper';

export class PointCloudReader {
  /**
   * Read point cloud from file (CSV or PLY).
   * 
   * @param filePath Path to point cloud file
   * @returns PointCloud object
   */
  static async readPointCloudFile(filePath: string): Promise<PointCloud> {
    const ext = path.extname(filePath).toLowerCase();
    
    switch (ext) {
      case '.csv':
        return await this.readCSVFile(filePath);
      case '.ply':
        return await this.readPLYFile(filePath);
      default:
        throw new Error(`Unsupported file format: ${ext}. Supported formats: .csv, .ply`);
    }
  }

  /**
   * Read point cloud from CSV file.
   * 
   * CSV format: x,y,z (one point per line)
   * 
   * @param filePath Path to CSV file
   * @returns PointCloud object
   */
  static async readCSVFile(filePath: string): Promise<PointCloud> {
    try {
      const content = await fs.readFile(filePath, 'utf-8');
      
      return new Promise((resolve, reject) => {
        Papa.parse(content, {
          header: false,
          skipEmptyLines: true,
          complete: (results) => {
            try {
              const points: Array<{ x: number; y: number; z: number }> = [];
              
              for (const row of results.data as string[][]) {
                if (row.length >= 3) {
                  const x = parseFloat(row[0]);
                  const y = parseFloat(row[1]);
                  const z = parseFloat(row[2]);
                  
                  if (!isNaN(x) && !isNaN(y) && !isNaN(z)) {
                    points.push({ x, y, z });
                  }
                }
              }
              
              if (points.length === 0) {
                reject(new Error(`No valid points found in CSV file: ${filePath}`));
                return;
              }
              
              const cloud = PointCloudHelper.fromPoints(points);
              resolve(cloud);
            } catch (error) {
              reject(new Error(`Failed to parse CSV file: ${error}`));
            }
          },
          error: (error) => {
            reject(new Error(`CSV parsing error: ${error.message}`));
          }
        });
      });
    } catch (error) {
      throw new Error(`Failed to read CSV file ${filePath}: ${error}`);
    }
  }

  /**
   * Read point cloud from PLY file.
   * 
   * Supports ASCII PLY format with vertex data.
   * 
   * @param filePath Path to PLY file
   * @returns PointCloud object
   */
  static async readPLYFile(filePath: string): Promise<PointCloud> {
    try {
      const content = await fs.readFile(filePath, 'utf-8');
      const lines = content.split('\n').map(line => line.trim());
      
      // Find header
      let headerEnd = -1;
      let vertexCount = 0;
      let hasX = false, hasY = false, hasZ = false;
      let xIdx = -1, yIdx = -1, zIdx = -1;
      
      for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        
        if (line.startsWith('element vertex')) {
          const match = line.match(/element vertex (\d+)/);
          if (match) {
            vertexCount = parseInt(match[1], 10);
          }
        }
        
        if (line.startsWith('property')) {
          const parts = line.split(/\s+/);
          if (parts.length >= 3) {
            const propName = parts[parts.length - 1].toLowerCase();
            const propIdx = i;
            
            if (propName === 'x') {
              hasX = true;
              xIdx = propIdx;
            } else if (propName === 'y') {
              hasY = true;
              yIdx = propIdx;
            } else if (propName === 'z') {
              hasZ = true;
              zIdx = propIdx;
            }
          }
        }
        
        if (line === 'end_header') {
          headerEnd = i;
          break;
        }
      }
      
      if (headerEnd === -1) {
        throw new Error('PLY file missing end_header');
      }
      
      if (!hasX || !hasY || !hasZ) {
        throw new Error('PLY file missing x, y, or z properties');
      }
      
      // Find property indices in actual data
      // Re-parse to find property order
      let propOrder: { x: number; y: number; z: number } = { x: -1, y: -1, z: -1 };
      let propCount = 0;
      
      for (let i = 0; i <= headerEnd; i++) {
        const line = lines[i];
        if (line.startsWith('property')) {
          const parts = line.split(/\s+/);
          if (parts.length >= 3) {
            const propName = parts[parts.length - 1].toLowerCase();
            if (propName === 'x') propOrder.x = propCount;
            if (propName === 'y') propOrder.y = propCount;
            if (propName === 'z') propOrder.z = propCount;
            propCount++;
          }
        }
      }
      
      // Parse vertex data
      const points: Array<{ x: number; y: number; z: number }> = [];
      const dataStart = headerEnd + 1;
      
      for (let i = dataStart; i < lines.length && points.length < vertexCount; i++) {
        const line = lines[i];
        if (!line || line.startsWith('comment')) continue;
        
        const values = line.split(/\s+/).filter(v => v.length > 0);
        if (values.length >= Math.max(propOrder.x, propOrder.y, propOrder.z) + 1) {
          const x = parseFloat(values[propOrder.x]);
          const y = parseFloat(values[propOrder.y]);
          const z = parseFloat(values[propOrder.z]);
          
          if (!isNaN(x) && !isNaN(y) && !isNaN(z)) {
            points.push({ x, y, z });
          }
        }
      }
      
      if (points.length === 0) {
        throw new Error(`No valid points found in PLY file: ${filePath}`);
      }
      
      return PointCloudHelper.fromPoints(points);
    } catch (error) {
      throw new Error(`Failed to read PLY file ${filePath}: ${error}`);
    }
  }

  /**
   * Align cloud sizes by truncating to minimum size.
   * 
   * @param source Source point cloud
   * @param target Target point cloud
   * @returns Tuple of [aligned_source, aligned_target]
   */
  static alignCloudSizes(
    source: PointCloud,
    target: PointCloud
  ): [PointCloud, PointCloud] {
    return PointCloudHelper.alignCloudSizes(source, target);
  }
}

