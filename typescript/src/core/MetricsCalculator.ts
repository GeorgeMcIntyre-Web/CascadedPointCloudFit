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

    // Build KD-Tree from target for efficient nearest neighbor search
    const targetTree = createKDTree(target);

    // Find nearest neighbors and compute distances
    // Work directly with Float32Array, avoid Point3D object creation
    const distances: number[] = new Array(transformedSource.count);
    let sumDistSq = 0;
    let sumDist = 0;
    let maxError = -Infinity;

    const points = transformedSource.points;
    for (let i = 0; i < transformedSource.count; i++) {
      const x = points[i * 3];
      const y = points[i * 3 + 1];
      const z = points[i * 3 + 2];

      const nearest = targetTree.nearestRaw(x, y, z);
      const dist = nearest.distance;

      distances[i] = dist;
      sumDistSq += dist * dist;
      sumDist += dist;
      if (dist > maxError) {
        maxError = dist;
      }
    }

    const count = transformedSource.count;

    // Calculate metrics
    const rmse = Math.sqrt(sumDistSq / count);
    const meanError = sumDist / count;
    const medianError = this.median(distances);

    return {
      transformation: transform.matrix,
      rmse,
      maxError,
      meanError,
      medianError
    };
  }

  private static median(values: number[]): number {
    const sorted = [...values].sort((a, b) => a - b);
    const mid = Math.floor(sorted.length / 2);
    return sorted.length % 2 === 0
      ? (sorted[mid - 1] + sorted[mid]) / 2
      : sorted[mid];
  }
}

