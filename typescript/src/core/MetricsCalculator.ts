/**
 * Metrics calculation for point cloud registration.
 * 
 * Ported from Python: cascaded_fit/core/metrics.py
 */

import { PointCloud, Transform4x4, Metrics } from './types';
import { PointCloudHelper } from './PointCloudHelper';
import { createKDTree } from './KDTreeHelper';

export class MetricsCalculator {
  /**
   * Compute registration metrics.
   * 
   * @param source Source point cloud
   * @param target Target point cloud
   * @param transform 4x4 transformation matrix
   * @returns Metrics object
   */
  static computeMetrics(
    source: PointCloud,
    target: PointCloud,
    transform: Transform4x4
  ): Metrics {
    // Transform source points
    const transformedSource = PointCloudHelper.applyTransformation(source, transform);
    const transformedPoints = PointCloudHelper.toPoints(transformedSource);

    // Build KD-Tree from target for efficient nearest neighbor search
    const targetTree = createKDTree(target);

    // Find nearest neighbors and compute distances
    const distances: number[] = [];
    
    for (const transformedPoint of transformedPoints) {
      const nearest = targetTree.nearest(transformedPoint);
      distances.push(nearest.distance);
    }

    // Calculate metrics
    const rmse = Math.sqrt(
      distances.reduce((sum, d) => sum + d * d, 0) / distances.length
    );
    const maxError = Math.max(...distances);
    const meanError = distances.reduce((sum, d) => sum + d, 0) / distances.length;
    const medianError = this.median(distances);

    return {
      transformation: transform.matrix,
      rmse,
      maxError,
      meanError,
      medianError
    };
  }

  private static euclideanDistance(
    p1: { x: number; y: number; z: number },
    p2: { x: number; y: number; z: number }
  ): number {
    const dx = p1.x - p2.x;
    const dy = p1.y - p2.y;
    const dz = p1.z - p2.z;
    return Math.sqrt(dx * dx + dy * dy + dz * dz);
  }

  private static median(values: number[]): number {
    const sorted = [...values].sort((a, b) => a - b);
    const mid = Math.floor(sorted.length / 2);
    return sorted.length % 2 === 0
      ? (sorted[mid - 1] + sorted[mid]) / 2
      : sorted[mid];
  }
}

