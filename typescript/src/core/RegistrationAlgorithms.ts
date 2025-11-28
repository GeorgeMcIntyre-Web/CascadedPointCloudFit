/**
 * Core registration algorithms: PCA, RANSAC, and ICP.
 *
 * Ported from Python implementation in cascaded_fit/core/registration.py
 */

import { Matrix } from 'ml-matrix';
import { PointCloud, Transform4x4, ICPResult } from './types';
import { PointCloudHelper } from './PointCloudHelper';
import { computeSVD3x3 } from './SVDHelper';
import { createKDTree } from './KDTreeHelper';
import { RANSACHelper, RANSACOptions } from './RANSACHelper';

export class RegistrationAlgorithms {
  /**
   * PCA-based initial alignment.
   * 
   * Ported from Python: RegistrationAlgorithms.pca_registration()
   * 
   * @param source Source point cloud
   * @param target Target point cloud
   * @returns 4x4 transformation matrix
   */
  static pcaRegistration(source: PointCloud, target: PointCloud): Transform4x4 {
    // Validate inputs
    if (source.count < 3) {
      throw new Error('Source point cloud must have at least 3 points');
    }
    if (target.count < 3) {
      throw new Error('Target point cloud must have at least 3 points');
    }

    // For very large clouds, downsample during PCA computation to avoid stack overflow in matrix operations
    let workingSource = source;
    let workingTarget = target;

    // Only downsample for very large clouds where matrix operations would fail
    if (source.count > 80000) {
      const downsampleFactor = Math.ceil(source.count / 10000); // Downsample to ~10k for PCA
      workingSource = this.downsample(source, downsampleFactor);
      workingTarget = this.downsample(target, downsampleFactor);
    } else if (source.count > 50000) {
      const downsampleFactor = Math.ceil(source.count / 15000); // Lighter downsampling for medium clouds
      workingSource = this.downsample(source, downsampleFactor);
      workingTarget = this.downsample(target, downsampleFactor);
    }

    // Compute centroids from original clouds (not downsampled)
    const sourceCentroid = PointCloudHelper.computeCentroid(source);
    const targetCentroid = PointCloudHelper.computeCentroid(target);

    // Center point clouds (use downsampled versions)
    const sourceCentered = this.centerPointCloud(workingSource, sourceCentroid);
    const targetCentered = this.centerPointCloud(workingTarget, targetCentroid);

    // Compute covariance matrix: source_centered^T * target_centered
    const sourceMatrix = this.pointCloudToMatrix(sourceCentered);
    const targetMatrix = this.pointCloudToMatrix(targetCentered);
    const cov = sourceMatrix.transpose().mmul(targetMatrix);

    // SVD: cov = U * S * V^T
    const svdResult = computeSVD3x3(cov);
    const U = svdResult.U;
    const V = svdResult.V;
    
    // Rotation: R = V * U^T
    const R = V.mmul(U.transpose());

    // Ensure right-handed coordinate system (det(R) = 1)
    const det = this.determinant3x3(R.to2DArray());
    if (det < 0) {
      // Flip last column of V
      const V_flipped = V.clone();
      const col2 = V_flipped.getColumn(2);
      V_flipped.setColumn(2, col2.map((v: number) => -v));
      const R_corrected = V_flipped.mmul(U.transpose());
      return this.buildTransformMatrix(R_corrected, sourceCentroid, targetCentroid);
    }

    return this.buildTransformMatrix(R, sourceCentroid, targetCentroid);
  }

  /**
   * ICP refinement with optional RANSAC preprocessing.
   *
   * Ported from Python: RegistrationAlgorithms.icp_refinement()
   *
   * @param source Source point cloud
   * @param target Target point cloud
   * @param initialTransform Initial 4x4 transformation matrix
   * @param maxIterations Maximum iterations
   * @param tolerance Convergence tolerance
   * @param useRANSAC Enable RANSAC outlier rejection (default: false)
   * @param ransacOptions RANSAC parameters (optional)
   * @returns ICP result with final transform, iterations, and error
   */
  static icpRefinement(
    source: PointCloud,
    target: PointCloud,
    initialTransform: Transform4x4,
    maxIterations: number = 50,
    tolerance: number = 1e-7,
    useRANSAC: boolean = false,
    ransacOptions?: RANSACOptions
  ): ICPResult {
    // Validate inputs
    if (source.count < 3) {
      throw new Error('Source point cloud must have at least 3 points');
    }
    if (target.count < 3) {
      throw new Error('Target point cloud must have at least 3 points');
    }

    // Optional RANSAC preprocessing for outlier rejection
    let currentTransform = this.cloneTransform(initialTransform);
    let workingSource = source;

    if (useRANSAC) {
      const ransacResult = RANSACHelper.ransacRegistration(source, target, initialTransform, ransacOptions);

      // Use RANSAC-refined transform as starting point
      currentTransform = ransacResult.transform;

      // If RANSAC found good inliers, use only those points for ICP (faster and more robust)
      if (ransacResult.inlierRatio > 0.5 && ransacResult.inlierCount >= 100) {
        const inlierPoints = new Float32Array(ransacResult.inlierCount * 3);
        let writeIdx = 0;
        for (const idx of ransacResult.inlierIndices) {
          inlierPoints[writeIdx++] = source.points[idx * 3];
          inlierPoints[writeIdx++] = source.points[idx * 3 + 1];
          inlierPoints[writeIdx++] = source.points[idx * 3 + 2];
        }
        workingSource = { points: inlierPoints, count: ransacResult.inlierCount };
      }
    }

    // Build KD-Tree from target for efficient nearest neighbor search
    const targetTree = createKDTree(target);
    let prevError = Infinity;

    // Pre-allocate buffers to reduce GC pressure (reuse across iterations)
    const transformedPoints = new Float32Array(workingSource.count * 3);
    const correspondingPoints = new Float32Array(workingSource.count * 3);

    for (let iteration = 0; iteration < maxIterations; iteration++) {
      // Adaptive downsampling: start coarse, progressively refine
      // This reduces total queries while maintaining accuracy
      // Strategy: Keep most iterations downsampled, only use full resolution near convergence
      let effectiveSource = workingSource;

      if (workingSource.count > 100000) {
        // Very large clouds: Keep ALL iterations downsampled for speed
        // Iteration 0-1: 20k points (coarse - fast convergence)
        // Iteration 2+: 40k points (refined - good balance of speed/accuracy)
        // Never use full 155k points - converges well at 40k with much less time
        if (iteration < 2) {
          const factor = Math.ceil(workingSource.count / 20000);
          effectiveSource = this.downsample(workingSource, factor);
        } else {
          const factor = Math.ceil(workingSource.count / 40000);
          effectiveSource = this.downsample(workingSource, factor);
        }
      } else if (workingSource.count > 30000) {
        // Large clouds: 2-stage progressive refinement
        // Iteration 0: 15k points (coarse)
        // Iteration 1+: 25k points (refined but still downsampled)
        if (iteration < 1) {
          const factor = Math.ceil(workingSource.count / 15000);
          effectiveSource = this.downsample(workingSource, factor);
        } else {
          const factor = Math.ceil(workingSource.count / 25000);
          effectiveSource = this.downsample(workingSource, factor);
        }
      }
      // Small clouds (<30k): always use full resolution

      // Transform source points in-place to avoid allocation
      const count = effectiveSource.count;
      this.applyTransformationInPlace(effectiveSource, currentTransform, transformedPoints, count);

      // Find nearest neighbors using KD-Tree
      let totalDistanceSq = 0;
      
      for (let i = 0; i < count; i++) {
        const idx = i * 3;
        const x = transformedPoints[idx];
        const y = transformedPoints[idx + 1];
        const z = transformedPoints[idx + 2];

        const nearest = targetTree.nearestRaw(x, y, z);
        const np = nearest.point;
        correspondingPoints[idx] = np.x;
        correspondingPoints[idx + 1] = np.y;
        correspondingPoints[idx + 2] = np.z;

        totalDistanceSq += nearest.distance * nearest.distance;
      }

      // Compute mean error (RMSE)
      const error = Math.sqrt(totalDistanceSq / count);

      // Early termination if error is already very low (avoid unnecessary iterations)
      if (error < tolerance * 10) {
        return {
          transform: currentTransform,
          iterations: iteration + 1,
          error
        };
      }

      // Check convergence
      if (Math.abs(error - prevError) < tolerance) {
        return {
          transform: currentTransform,
          iterations: iteration + 1,
          error
        };
      }

      prevError = error;

      // Compute incremental transformation via SVD
      const transformedSourceCloud: PointCloud = { points: transformedPoints, count };
      const targetCloud: PointCloud = { points: correspondingPoints, count };

      const sourceMean = PointCloudHelper.computeCentroid(transformedSourceCloud);
      const targetMean = PointCloudHelper.computeCentroid(targetCloud);

      // Compute cross-covariance directly from Float32Arrays (avoid Point3D conversions)
      const cov = this.computeCrossCovarianceFast(
        transformedSourceCloud,
        sourceMean,
        targetCloud,
        targetMean
      );

      const svdResult = computeSVD3x3(cov);
      const U = svdResult.U;
      let V = svdResult.V;

      let R = V.mmul(U.transpose());

      // Ensure right-handed coordinate system
      if (this.determinant3x3(R.to2DArray()) < 0) {
        const V_flipped = V.clone();
        const col2 = V_flipped.getColumn(2);
        V_flipped.setColumn(2, col2.map((v: number) => -v));
        R = V_flipped.mmul(U.transpose());
      }

      // Compute translation
      const R_array = R.to2DArray();
      const t = {
        x: targetMean.x - (R_array[0][0] * sourceMean.x + R_array[0][1] * sourceMean.y + R_array[0][2] * sourceMean.z),
        y: targetMean.y - (R_array[1][0] * sourceMean.x + R_array[1][1] * sourceMean.y + R_array[1][2] * sourceMean.z),
        z: targetMean.z - (R_array[2][0] * sourceMean.x + R_array[2][1] * sourceMean.y + R_array[2][2] * sourceMean.z)
      };

      // Update cumulative transformation
      const R_3x3 = R.to2DArray();
      const currentR = currentTransform.matrix.slice(0, 3).map(row => row.slice(0, 3));
      const newR = this.multiply3x3Matrices(currentR, R_3x3);
      
      const currentT = [
        currentTransform.matrix[0][3],
        currentTransform.matrix[1][3],
        currentTransform.matrix[2][3]
      ];
      
      const newT = [
        newR[0][0] * currentT[0] + newR[0][1] * currentT[1] + newR[0][2] * currentT[2] + t.x,
        newR[1][0] * currentT[0] + newR[1][1] * currentT[1] + newR[1][2] * currentT[2] + t.y,
        newR[2][0] * currentT[0] + newR[2][1] * currentT[1] + newR[2][2] * currentT[2] + t.z
      ];

      currentTransform = {
        matrix: [
          [newR[0][0], newR[0][1], newR[0][2], newT[0]],
          [newR[1][0], newR[1][1], newR[1][2], newT[1]],
          [newR[2][0], newR[2][1], newR[2][2], newT[2]],
          [0, 0, 0, 1]
        ]
      };
    }

    // Didn't converge
    throw new Error(`ICP did not converge after ${maxIterations} iterations (error=${prevError})`);
  }

  // Private helper methods

  /**
   * Downsample point cloud by taking every nth point.
   */
  private static downsample(cloud: PointCloud, factor: number): PointCloud {
    if (factor <= 1) {
      return cloud;
    }
    
    const newCount = Math.floor(cloud.count / factor);
    const downsampled = new Float32Array(newCount * 3);
    
    for (let i = 0; i < newCount; i++) {
      const srcIdx = i * factor * 3;
      downsampled[i * 3] = cloud.points[srcIdx];
      downsampled[i * 3 + 1] = cloud.points[srcIdx + 1];
      downsampled[i * 3 + 2] = cloud.points[srcIdx + 2];
    }
    
    return { points: downsampled, count: newCount };
  }

  private static centerPointCloud(cloud: PointCloud, centroid: { x: number; y: number; z: number }): PointCloud {
    const centered = new Float32Array(cloud.count * 3);
    for (let i = 0; i < cloud.count; i++) {
      centered[i * 3] = cloud.points[i * 3] - centroid.x;
      centered[i * 3 + 1] = cloud.points[i * 3 + 1] - centroid.y;
      centered[i * 3 + 2] = cloud.points[i * 3 + 2] - centroid.z;
    }
    return { points: centered, count: cloud.count };
  }

  private static pointCloudToMatrix(cloud: PointCloud): Matrix {
    // For very large clouds, avoid creating intermediate arrays
    // Pre-allocate the matrix data
    const data: number[][] = new Array(cloud.count);
    for (let i = 0; i < cloud.count; i++) {
      data[i] = [
        cloud.points[i * 3],
        cloud.points[i * 3 + 1],
        cloud.points[i * 3 + 2]
      ];
    }
    return new Matrix(data);
  }

  private static buildTransformMatrix(
    R: Matrix,
    sourceCentroid: { x: number; y: number; z: number },
    targetCentroid: { x: number; y: number; z: number }
  ): Transform4x4 {
    const R_array = R.to2DArray();
    
    // Translation: t = target_mean - R * source_mean
    const t = {
      x: targetCentroid.x - (R_array[0][0] * sourceCentroid.x + R_array[0][1] * sourceCentroid.y + R_array[0][2] * sourceCentroid.z),
      y: targetCentroid.y - (R_array[1][0] * sourceCentroid.x + R_array[1][1] * sourceCentroid.y + R_array[1][2] * sourceCentroid.z),
      z: targetCentroid.z - (R_array[2][0] * sourceCentroid.x + R_array[2][1] * sourceCentroid.y + R_array[2][2] * sourceCentroid.z)
    };

    return {
      matrix: [
        [R_array[0][0], R_array[0][1], R_array[0][2], t.x],
        [R_array[1][0], R_array[1][1], R_array[1][2], t.y],
        [R_array[2][0], R_array[2][1], R_array[2][2], t.z],
        [0, 0, 0, 1]
      ]
    };
  }

  private static cloneTransform(transform: Transform4x4): Transform4x4 {
    return {
      matrix: transform.matrix.map(row => [...row])
    };
  }

  /**
   * Apply transformation to point cloud in-place (write to output buffer).
   * Avoids allocating new Float32Array on each iteration.
   */
  private static applyTransformationInPlace(
    cloud: PointCloud,
    transform: Transform4x4,
    output: Float32Array,
    count: number
  ): void {
    const m = transform.matrix;
    const points = cloud.points;

    // Extract matrix elements for faster access
    const m00 = m[0][0], m01 = m[0][1], m02 = m[0][2], m03 = m[0][3];
    const m10 = m[1][0], m11 = m[1][1], m12 = m[1][2], m13 = m[1][3];
    const m20 = m[2][0], m21 = m[2][1], m22 = m[2][2], m23 = m[2][3];

    for (let i = 0; i < count; i++) {
      const idx = i * 3;
      const x = points[idx];
      const y = points[idx + 1];
      const z = points[idx + 2];

      output[idx] = m00 * x + m01 * y + m02 * z + m03;
      output[idx + 1] = m10 * x + m11 * y + m12 * z + m13;
      output[idx + 2] = m20 * x + m21 * y + m22 * z + m23;
    }
  }

  private static multiply3x3Matrices(A: number[][], B: number[][]): number[][] {
    const result: number[][] = [[0, 0, 0], [0, 0, 0], [0, 0, 0]];
    for (let i = 0; i < 3; i++) {
      for (let j = 0; j < 3; j++) {
        for (let k = 0; k < 3; k++) {
          result[i][j] += A[i][k] * B[k][j];
        }
      }
    }
    return result;
  }

  /**
   * Compute determinant of 3x3 matrix.
   */
  private static determinant3x3(matrix: number[][]): number {
    const [[a, b, c], [d, e, f], [g, h, i]] = matrix;
    return a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g);
  }

  /**
   * Fast cross-covariance computation using Float32Array directly.
   */
  private static computeCrossCovarianceFast(
    cloudA: PointCloud,
    meanA: { x: number; y: number; z: number },
    cloudB: PointCloud,
    meanB: { x: number; y: number; z: number }
  ): Matrix {
    const cov = [
      [0, 0, 0],
      [0, 0, 0],
      [0, 0, 0],
    ];

    const length = Math.min(cloudA.count, cloudB.count);
    for (let i = 0; i < length; i++) {
      const ax = cloudA.points[i * 3] - meanA.x;
      const ay = cloudA.points[i * 3 + 1] - meanA.y;
      const az = cloudA.points[i * 3 + 2] - meanA.z;
      
      const bx = cloudB.points[i * 3] - meanB.x;
      const by = cloudB.points[i * 3 + 1] - meanB.y;
      const bz = cloudB.points[i * 3 + 2] - meanB.z;

      cov[0][0] += ax * bx;
      cov[0][1] += ax * by;
      cov[0][2] += ax * bz;
      cov[1][0] += ay * bx;
      cov[1][1] += ay * by;
      cov[1][2] += ay * bz;
      cov[2][0] += az * bx;
      cov[2][1] += az * by;
      cov[2][2] += az * bz;
    }

    return new Matrix(cov);
  }

}

