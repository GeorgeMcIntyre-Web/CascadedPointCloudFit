/**
 * Unit tests for PointCloudReader.
 */

import { describe, it, expect, beforeAll } from 'vitest';
import { PointCloudReader } from '../../src/io/PointCloudReader';
import * as fs from 'fs/promises';
import * as path from 'path';
import * as os from 'os';

describe('PointCloudReader', () => {
  let tempDir: string;

  beforeAll(async () => {
    tempDir = await fs.mkdtemp(path.join(os.tmpdir(), 'pointcloud-test-'));
  });

  describe('readCSVFile', () => {
    it('should read CSV file with x,y,z format', async () => {
      const csvContent = `0,0,0
1,0,0
0,1,0
0,0,1`;
      
      const csvPath = path.join(tempDir, 'test.csv');
      await fs.writeFile(csvPath, csvContent);

      const cloud = await PointCloudReader.readCSVFile(csvPath);

      expect(cloud.count).toBe(4);
      expect(cloud.points.length).toBe(12); // 4 points * 3 coordinates
    });

    it('should handle CSV with extra columns', async () => {
      const csvContent = `0,0,0,1,2
1,0,0,3,4
0,1,0,5,6`;
      
      const csvPath = path.join(tempDir, 'test_extra.csv');
      await fs.writeFile(csvPath, csvContent);

      const cloud = await PointCloudReader.readCSVFile(csvPath);

      expect(cloud.count).toBe(3);
    });

    it('should skip invalid lines', async () => {
      const csvContent = `0,0,0
invalid,line
1,0,0
,,
0,1,0`;
      
      const csvPath = path.join(tempDir, 'test_invalid.csv');
      await fs.writeFile(csvPath, csvContent);

      const cloud = await PointCloudReader.readCSVFile(csvPath);

      expect(cloud.count).toBe(3);
    });

    it('should throw error for non-existent file', async () => {
      await expect(
        PointCloudReader.readCSVFile(path.join(tempDir, 'nonexistent.csv'))
      ).rejects.toThrow();
    });
  });

  describe('readPLYFile', () => {
    it('should read ASCII PLY file', async () => {
      const plyContent = `ply
format ascii 1.0
element vertex 3
property float x
property float y
property float z
end_header
0 0 0
1 0 0
0 1 0`;
      
      const plyPath = path.join(tempDir, 'test.ply');
      await fs.writeFile(plyPath, plyContent);

      const cloud = await PointCloudReader.readPLYFile(plyPath);

      expect(cloud.count).toBe(3);
      expect(cloud.points.length).toBe(9); // 3 points * 3 coordinates
    });

    it('should handle PLY with additional properties', async () => {
      const plyContent = `ply
format ascii 1.0
element vertex 2
property float x
property float y
property float z
property float nx
property float ny
property float nz
end_header
0 0 0 1 0 0
1 0 0 0 1 0`;
      
      const plyPath = path.join(tempDir, 'test_normals.ply');
      await fs.writeFile(plyPath, plyContent);

      const cloud = await PointCloudReader.readPLYFile(plyPath);

      expect(cloud.count).toBe(2);
    });

    it('should throw error for missing x,y,z properties', async () => {
      const plyContent = `ply
format ascii 1.0
element vertex 1
property float nx
end_header
1`;
      
      const plyPath = path.join(tempDir, 'test_invalid.ply');
      await fs.writeFile(plyPath, plyContent);

      await expect(
        PointCloudReader.readPLYFile(plyPath)
      ).rejects.toThrow('missing x, y, or z properties');
    });
  });

  describe('readPointCloudFile', () => {
    it('should auto-detect CSV format', async () => {
      const csvContent = `0,0,0
1,0,0`;
      
      const csvPath = path.join(tempDir, 'auto.csv');
      await fs.writeFile(csvPath, csvContent);

      const cloud = await PointCloudReader.readPointCloudFile(csvPath);

      expect(cloud.count).toBe(2);
    });

    it('should auto-detect PLY format', async () => {
      const plyContent = `ply
format ascii 1.0
element vertex 2
property float x
property float y
property float z
end_header
0 0 0
1 0 0`;
      
      const plyPath = path.join(tempDir, 'auto.ply');
      await fs.writeFile(plyPath, plyContent);

      const cloud = await PointCloudReader.readPointCloudFile(plyPath);

      expect(cloud.count).toBe(2);
    });

    it('should throw error for unsupported format', async () => {
      const txtPath = path.join(tempDir, 'test.txt');
      await fs.writeFile(txtPath, 'some content');

      await expect(
        PointCloudReader.readPointCloudFile(txtPath)
      ).rejects.toThrow('Unsupported file format');
    });
  });

  describe('alignCloudSizes', () => {
    it('should truncate to minimum size', async () => {
      const csv1 = `0,0,0
1,0,0
0,1,0
0,0,1
1,1,1`;
      
      const csv2 = `0,0,0
1,0,0
0,1,0`;

      const path1 = path.join(tempDir, 'cloud1.csv');
      const path2 = path.join(tempDir, 'cloud2.csv');
      await fs.writeFile(path1, csv1);
      await fs.writeFile(path2, csv2);

      const cloud1 = await PointCloudReader.readCSVFile(path1);
      const cloud2 = await PointCloudReader.readCSVFile(path2);

      const [aligned1, aligned2] = PointCloudReader.alignCloudSizes(cloud1, cloud2);

      expect(aligned1.count).toBe(3);
      expect(aligned2.count).toBe(3);
      expect(aligned1.count).toBe(aligned2.count);
    });
  });
});

