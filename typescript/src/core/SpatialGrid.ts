/**
 * Spatial grid for approximate nearest neighbor search on very large point clouds.
 * Used as fallback when KD-tree construction would cause stack overflow.
 */

import { Point3D, PointCloud } from './types';

export class SpatialGrid {
  private grid: Map<string, number[]>; // Store indices into original point cloud
  private cellSize: number;
  private bounds: { minX: number; maxX: number; minY: number; maxY: number; minZ: number; maxZ: number };
  private cloud: PointCloud; // Store reference to original cloud

  constructor(cloud: PointCloud, cellSize?: number) {
    this.cloud = cloud;
    this.grid = new Map();
    
    // Calculate bounds directly from Float32Array
    let minX = Infinity, maxX = -Infinity;
    let minY = Infinity, maxY = -Infinity;
    let minZ = Infinity, maxZ = -Infinity;
    
    const points = cloud.points;
    for (let i = 0; i < cloud.count; i++) {
      const x = points[i * 3];
      const y = points[i * 3 + 1];
      const z = points[i * 3 + 2];
      minX = Math.min(minX, x);
      maxX = Math.max(maxX, x);
      minY = Math.min(minY, y);
      maxY = Math.max(maxY, y);
      minZ = Math.min(minZ, z);
      maxZ = Math.max(maxZ, z);
    }
    
    this.bounds = { minX, maxX, minY, maxY, minZ, maxZ };

    // Auto-calculate cell size if not provided
    // Optimize cell size for better locality - aim for ~50-100 points per cell on average
    const rangeX = maxX - minX;
    const rangeY = maxY - minY;
    const rangeZ = maxZ - minZ;
    const avgRange = (rangeX + rangeY + rangeZ) / 3;
    const targetPointsPerCell = 75; // Sweet spot for search performance
    const estimatedCells = Math.max(1, cloud.count / targetPointsPerCell);
    const cellsPerDim = Math.cbrt(estimatedCells);
    this.cellSize = cellSize || Math.max(avgRange / cellsPerDim, 0.01);
    
    // Populate grid using indices (no Point3D object creation)
    for (let i = 0; i < cloud.count; i++) {
      const x = points[i * 3];
      const y = points[i * 3 + 1];
      const z = points[i * 3 + 2];
      const key = this.getCellKey(x, y, z);
      if (!this.grid.has(key)) {
        this.grid.set(key, []);
      }
      this.grid.get(key)!.push(i); // Store index instead of point
    }
  }

  private getCellKey(x: number, y: number, z: number): string {
    const i = Math.floor((x - this.bounds.minX) / this.cellSize);
    const j = Math.floor((y - this.bounds.minY) / this.cellSize);
    const k = Math.floor((z - this.bounds.minZ) / this.cellSize);
    return `${i},${j},${k}`;
  }

  nearest(x: number, y: number, z: number): { point: Point3D; distance: number } {
    // Search in the cell and neighboring cells
    const centerKey = this.getCellKey(x, y, z);
    const [ci, cj, ck] = centerKey.split(',').map(Number);

    let bestIdx: number | null = null;
    let bestDistSq = Infinity;
    const points = this.cloud.points;

    // Start with immediate neighbors (radius 1) - most queries succeed here
    let radius = 1;
    const maxRadius = 5; // Reduced from 10 - if not found in 5, do linear search

    while (radius <= maxRadius) {
      let foundInThisRadius = false;

      // Only search shell (not entire cube) to reduce redundant checks
      for (let di = -radius; di <= radius; di++) {
        for (let dj = -radius; dj <= radius; dj++) {
          for (let dk = -radius; dk <= radius; dk++) {
            // Skip inner cells (already searched in previous radius)
            if (radius > 1 && Math.abs(di) < radius && Math.abs(dj) < radius && Math.abs(dk) < radius) {
              continue;
            }

            const key = `${ci + di},${cj + dj},${ck + dk}`;
            const cellIndices = this.grid.get(key);
            if (cellIndices) {
              foundInThisRadius = true;
              for (const idx of cellIndices) {
                const px = points[idx * 3];
                const py = points[idx * 3 + 1];
                const pz = points[idx * 3 + 2];
                const dx = x - px;
                const dy = y - py;
                const dz = z - pz;
                const distSq = dx * dx + dy * dy + dz * dz;
                if (distSq < bestDistSq) {
                  bestDistSq = distSq;
                  bestIdx = idx;
                }
              }
            }
          }
        }
      }

      // If we found points, we can potentially stop early
      if (bestIdx !== null) {
        // Check if expanding further could find a closer point
        const maxPossibleDistInNextShell = (radius + 1) * this.cellSize * Math.sqrt(3);
        if (bestDistSq < maxPossibleDistInNextShell * maxPossibleDistInNextShell) {
          break; // Current best is closer than any point in next shell
        }
      }

      radius++;
    }
    
    // Fallback: linear search if still no point found
    if (bestIdx === null) {
      for (let i = 0; i < this.cloud.count; i++) {
        const px = points[i * 3];
        const py = points[i * 3 + 1];
        const pz = points[i * 3 + 2];
        const dx = x - px;
        const dy = y - py;
        const dz = z - pz;
        const distSq = dx * dx + dy * dy + dz * dz;
        if (distSq < bestDistSq) {
          bestDistSq = distSq;
          bestIdx = i;
        }
      }
    }
    
    if (bestIdx === null) {
      throw new Error('No nearest neighbor found - grid is empty');
    }
    
    // Create Point3D only when returning (single object creation)
    const bestPoint: Point3D = {
      x: points[bestIdx * 3],
      y: points[bestIdx * 3 + 1],
      z: points[bestIdx * 3 + 2]
    };
    
    return { point: bestPoint, distance: Math.sqrt(bestDistSq) };
  }
}

