/**
 * RANSAC (Random Sample Consensus) for robust point cloud registration.
 *
 * Removes outliers and provides a robust initial alignment estimate.
 */

import { PointCloud, Transform4x4, Point3D } from './types';
import { PointCloudHelper } from './PointCloudHelper';
import { createKDTree } from './KDTreeHelper';
import { computeSVD3x3 } from './SVDHelper';
import { Matrix } from 'ml-matrix';

export interface RANSACOptions {
  /** Maximum iterations */
  maxIterations?: number;
  /** Distance threshold for inliers (in same units as point cloud) */
  inlierThreshold?: number;
  /** Minimum number of inliers required */
  minInliers?: number;
  /** Sample size for each iteration */
  sampleSize?: number;
}

export interface RANSACResult {
  /** Best transformation found */
  transform: Transform4x4;
  /** Indices of inlier points in source cloud */
  inlierIndices: number[];
  /** Number of inliers */
  inlierCount: number;
  /** Inlier ratio (0-1) */
  inlierRatio: number;
}

export class RANSACHelper {
  /**
   * Run RANSAC to find robust initial alignment and identify inliers.
   *
   * @param source Source point cloud
   * @param target Target point cloud
   * @param initialTransform Initial transformation estimate (from PCA)
   * @param options RANSAC parameters
   * @returns RANSAC result with refined transform and inlier set
   */
  static ransacRegistration(
    source: PointCloud,
    target: PointCloud,
    initialTransform: Transform4x4,
    options?: RANSACOptions
  ): RANSACResult {
    // Default parameters
    const maxIterations = options?.maxIterations ?? 100;
    const inlierThreshold = options?.inlierThreshold ?? 0.01; // 1cm default
    const sampleSize = options?.sampleSize ?? Math.min(100, Math.max(10, Math.floor(source.count * 0.001))); // 0.1% sample, 10-100 points

    // Apply initial transform to source
    const transformedSource = PointCloudHelper.applyTransformation(source, initialTransform);

    // Build KD-tree for target
    const targetTree = createKDTree(target);

    let bestTransform = this.identityTransform();
    let bestInliers: number[] = [];
    let bestInlierCount = 0;

    // RANSAC iterations
    for (let iter = 0; iter < maxIterations; iter++) {
      // 1. Randomly sample points from source
      const sampleIndices = this.randomSample(source.count, sampleSize);

      // 2. Find correspondences for sample points
      const sourcePoints: Point3D[] = [];
      const targetPoints: Point3D[] = [];

      for (const idx of sampleIndices) {
        const x = transformedSource.points[idx * 3];
        const y = transformedSource.points[idx * 3 + 1];
        const z = transformedSource.points[idx * 3 + 2];

        const nearest = targetTree.nearestRaw(x, y, z);

        // Only use correspondence if distance is reasonable
        if (nearest.distance < inlierThreshold * 5) {
          sourcePoints.push({ x, y, z });
          targetPoints.push(nearest.point);
        }
      }

      // Need at least 3 correspondences to compute transformation
      if (sourcePoints.length < 3) {
        continue;
      }

      // 3. Compute transformation from sample correspondences
      const sampleTransform = this.computeTransformFromCorrespondences(sourcePoints, targetPoints);
      if (!sampleTransform) {
        continue;
      }

      // 4. Apply transformation and count inliers
      const currentInliers: number[] = [];

      for (let i = 0; i < transformedSource.count; i++) {
        const x = transformedSource.points[i * 3];
        const y = transformedSource.points[i * 3 + 1];
        const z = transformedSource.points[i * 3 + 2];

        // Apply sample transform
        const m = sampleTransform.matrix;
        const tx = m[0][0] * x + m[0][1] * y + m[0][2] * z + m[0][3];
        const ty = m[1][0] * x + m[1][1] * y + m[1][2] * z + m[1][3];
        const tz = m[2][0] * x + m[2][1] * y + m[2][2] * z + m[2][3];

        // Find nearest neighbor in target
        const nearest = targetTree.nearestRaw(tx, ty, tz);

        // Check if inlier
        if (nearest.distance < inlierThreshold) {
          currentInliers.push(i);
        }
      }

      // 5. Update best model if this is better
      if (currentInliers.length > bestInlierCount) {
        bestInlierCount = currentInliers.length;
        bestInliers = currentInliers;
        bestTransform = sampleTransform;

        // Early termination if we have enough inliers
        if (bestInlierCount >= source.count * 0.8) {
          break;
        }
      }
    }

    // Recompute transformation using all inliers for better accuracy
    if (bestInliers.length >= 3) {
      const inlierSourcePoints: Point3D[] = [];
      const inlierTargetPoints: Point3D[] = [];

      for (const idx of bestInliers) {
        const x = transformedSource.points[idx * 3];
        const y = transformedSource.points[idx * 3 + 1];
        const z = transformedSource.points[idx * 3 + 2];

        const nearest = targetTree.nearestRaw(x, y, z);

        inlierSourcePoints.push({ x, y, z });
        inlierTargetPoints.push(nearest.point);
      }

      const refinedTransform = this.computeTransformFromCorrespondences(
        inlierSourcePoints,
        inlierTargetPoints
      );

      if (refinedTransform) {
        bestTransform = refinedTransform;
      }
    }

    // Combine initial transform with RANSAC refinement
    const finalTransform = this.composeTransforms(initialTransform, bestTransform);

    return {
      transform: finalTransform,
      inlierIndices: bestInliers,
      inlierCount: bestInlierCount,
      inlierRatio: bestInlierCount / source.count,
    };
  }

  /**
   * Randomly sample indices without replacement.
   */
  private static randomSample(max: number, count: number): number[] {
    const indices: number[] = [];
    const used = new Set<number>();

    while (indices.length < count) {
      const idx = Math.floor(Math.random() * max);
      if (!used.has(idx)) {
        used.add(idx);
        indices.push(idx);
      }
    }

    return indices;
  }

  /**
   * Compute transformation from point correspondences using SVD.
   */
  private static computeTransformFromCorrespondences(
    source: Point3D[],
    target: Point3D[]
  ): Transform4x4 | null {
    if (source.length !== target.length || source.length < 3) {
      return null;
    }

    // Compute centroids
    let srcCentroid = { x: 0, y: 0, z: 0 };
    let tgtCentroid = { x: 0, y: 0, z: 0 };

    for (let i = 0; i < source.length; i++) {
      srcCentroid.x += source[i].x;
      srcCentroid.y += source[i].y;
      srcCentroid.z += source[i].z;
      tgtCentroid.x += target[i].x;
      tgtCentroid.y += target[i].y;
      tgtCentroid.z += target[i].z;
    }

    const n = source.length;
    srcCentroid.x /= n;
    srcCentroid.y /= n;
    srcCentroid.z /= n;
    tgtCentroid.x /= n;
    tgtCentroid.y /= n;
    tgtCentroid.z /= n;

    // Center point clouds
    const srcCentered: number[][] = [];
    const tgtCentered: number[][] = [];

    for (let i = 0; i < n; i++) {
      srcCentered.push([
        source[i].x - srcCentroid.x,
        source[i].y - srcCentroid.y,
        source[i].z - srcCentroid.z,
      ]);
      tgtCentered.push([
        target[i].x - tgtCentroid.x,
        target[i].y - tgtCentroid.y,
        target[i].z - tgtCentroid.z,
      ]);
    }

    // Compute covariance matrix
    const srcMatrix = new Matrix(srcCentered);
    const tgtMatrix = new Matrix(tgtCentered);
    const cov = srcMatrix.transpose().mmul(tgtMatrix);

    // SVD
    const svdResult = computeSVD3x3(cov);
    const U = svdResult.U;
    const V = svdResult.V;

    // Rotation: R = V * U^T
    let R = V.mmul(U.transpose());

    // Ensure right-handed coordinate system
    const det = this.determinant3x3(R.to2DArray());
    if (det < 0) {
      const V_flipped = V.clone();
      const col2 = V_flipped.getColumn(2);
      V_flipped.setColumn(2, col2.map((v: number) => -v));
      R = V_flipped.mmul(U.transpose());
    }

    const R_array = R.to2DArray();

    // Translation: t = target_centroid - R * source_centroid
    const t = {
      x: tgtCentroid.x - (R_array[0][0] * srcCentroid.x + R_array[0][1] * srcCentroid.y + R_array[0][2] * srcCentroid.z),
      y: tgtCentroid.y - (R_array[1][0] * srcCentroid.x + R_array[1][1] * srcCentroid.y + R_array[1][2] * srcCentroid.z),
      z: tgtCentroid.z - (R_array[2][0] * srcCentroid.x + R_array[2][1] * srcCentroid.y + R_array[2][2] * srcCentroid.z),
    };

    return {
      matrix: [
        [R_array[0][0], R_array[0][1], R_array[0][2], t.x],
        [R_array[1][0], R_array[1][1], R_array[1][2], t.y],
        [R_array[2][0], R_array[2][1], R_array[2][2], t.z],
        [0, 0, 0, 1],
      ],
    };
  }

  private static identityTransform(): Transform4x4 {
    return {
      matrix: [
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1],
      ],
    };
  }

  private static composeTransforms(t1: Transform4x4, t2: Transform4x4): Transform4x4 {
    const m1 = t1.matrix;
    const m2 = t2.matrix;
    const result: number[][] = [
      [0, 0, 0, 0],
      [0, 0, 0, 0],
      [0, 0, 0, 0],
      [0, 0, 0, 1],
    ];

    for (let i = 0; i < 3; i++) {
      for (let j = 0; j < 4; j++) {
        for (let k = 0; k < 3; k++) {
          result[i][j] += m2[i][k] * m1[k][j];
        }
        if (j === 3) {
          result[i][j] += m2[i][3];
        }
      }
    }

    return { matrix: result };
  }

  private static determinant3x3(matrix: number[][]): number {
    const [[a, b, c], [d, e, f], [g, h, i]] = matrix;
    return a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g);
  }
}
