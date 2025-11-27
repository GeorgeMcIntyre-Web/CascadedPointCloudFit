/**
 * Core registration algorithms: PCA and ICP.
 * 
 * Ported from Python implementation in cascaded_fit/core/registration.py
 */

import { Matrix } from 'ml-matrix';
import { PointCloud, Transform4x4, ICPResult } from './types';
import { PointCloudHelper } from './PointCloudHelper';

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

    // Compute centroids
    const sourceCentroid = PointCloudHelper.computeCentroid(source);
    const targetCentroid = PointCloudHelper.computeCentroid(target);

    // Center point clouds
    const sourceCentered = this.centerPointCloud(source, sourceCentroid);
    const targetCentered = this.centerPointCloud(target, targetCentroid);

    // Compute covariance matrix: source_centered^T * target_centered
    const sourceMatrix = this.pointCloudToMatrix(sourceCentered);
    const targetMatrix = this.pointCloudToMatrix(targetCentered);
    const cov = sourceMatrix.transpose().mmul(targetMatrix);

    // SVD: cov = U * S * V^T
    // ml-matrix uses different SVD API - need to use eigenDecomposition or manual SVD
    // For now, use manual SVD calculation
    const svdResult = this.computeSVD(cov);
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
   * ICP refinement.
   * 
   * Ported from Python: RegistrationAlgorithms.icp_refinement()
   * 
   * @param source Source point cloud
   * @param target Target point cloud
   * @param initialTransform Initial 4x4 transformation matrix
   * @param maxIterations Maximum iterations
   * @param tolerance Convergence tolerance
   * @returns ICP result with final transform, iterations, and error
   */
  static icpRefinement(
    source: PointCloud,
    target: PointCloud,
    initialTransform: Transform4x4,
    maxIterations: number = 50,
    tolerance: number = 1e-7
  ): ICPResult {
    // Validate inputs
    if (source.count < 3) {
      throw new Error('Source point cloud must have at least 3 points');
    }
    if (target.count < 3) {
      throw new Error('Target point cloud must have at least 3 points');
    }

    // Build KD-Tree from target (will be implemented with kd-tree-javascript)
    // For now, use simple nearest neighbor search
    const targetPoints = PointCloudHelper.toPoints(target);

    let currentTransform = this.cloneTransform(initialTransform);
    let prevError = Infinity;

    for (let iteration = 0; iteration < maxIterations; iteration++) {
      // Transform source points
      const transformedSource = PointCloudHelper.applyTransformation(source, currentTransform);
      const transformedPoints = PointCloudHelper.toPoints(transformedSource);

      // Find nearest neighbors (simple implementation - will optimize with KD-Tree)
      const distances: number[] = [];
      const correspondingPoints: Array<{ x: number; y: number; z: number }> = [];

      for (const transformedPoint of transformedPoints) {
        let minDist = Infinity;
        let nearestPoint = targetPoints[0];

        for (const targetPoint of targetPoints) {
          const dist = this.euclideanDistance(transformedPoint, targetPoint);
          if (dist < minDist) {
            minDist = dist;
            nearestPoint = targetPoint;
          }
        }

        distances.push(minDist);
        correspondingPoints.push(nearestPoint);
      }

      // Compute error
      const error = distances.reduce((sum, d) => sum + d, 0) / distances.length;

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
      const sourceCentered = this.centerPointCloud(
        PointCloudHelper.fromPoints(transformedPoints),
        PointCloudHelper.computeCentroid(transformedSource)
      );
      const targetCentered = this.centerPointCloud(
        PointCloudHelper.fromPoints(correspondingPoints),
        PointCloudHelper.computeCentroid(PointCloudHelper.fromPoints(correspondingPoints))
      );

      const sourceMatrix = this.pointCloudToMatrix(sourceCentered);
      const targetMatrix = this.pointCloudToMatrix(targetCentered);
      const cov = sourceMatrix.transpose().mmul(targetMatrix);

      const svdResult = this.computeSVD(cov);
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
      const sourceMean = PointCloudHelper.computeCentroid(transformedSource);
      const targetMean = PointCloudHelper.computeCentroid(PointCloudHelper.fromPoints(correspondingPoints));
      
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
    const data: number[][] = [];
    for (let i = 0; i < cloud.count; i++) {
      data.push([
        cloud.points[i * 3],
        cloud.points[i * 3 + 1],
        cloud.points[i * 3 + 2]
      ]);
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

  private static euclideanDistance(p1: { x: number; y: number; z: number }, p2: { x: number; y: number; z: number }): number {
    const dx = p1.x - p2.x;
    const dy = p1.y - p2.y;
    const dz = p1.z - p2.z;
    return Math.sqrt(dx * dx + dy * dy + dz * dz);
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
   * Compute SVD manually for 3x3 matrices.
   * Uses a simplified approach for small matrices.
   */
  private static computeSVD(matrix: Matrix): { U: Matrix; S: Matrix; V: Matrix } {
    // For 3x3 matrices, compute SVD manually
    const A = matrix.to2DArray();
    const AtA = this.multiply3x3Matrices(
      [[A[0][0], A[1][0], A[2][0]], [A[0][1], A[1][1], A[2][1]], [A[0][2], A[1][2], A[2][2]]],
      A
    );
    
    // Compute eigenvalues and eigenvectors of AtA (simplified for 3x3)
    const eigenResult = this.eigenDecomposition3x3(AtA);
    const V = new Matrix(eigenResult.eigenvectors);
    
    // S is the square root of eigenvalues
    const eigenvalues = eigenResult.eigenvalues;
    const S = Matrix.diag(eigenvalues.map((e: number) => Math.sqrt(Math.max(0, e))));
    
    // U = A * V * S^(-1)
    const S_inv_data = eigenvalues.map((e: number) => 1 / Math.sqrt(Math.max(1e-10, e)));
    const S_inv = Matrix.diag(S_inv_data);
    const U = matrix.mmul(V).mmul(S_inv);
    
    return { U, S, V };
  }

  /**
   * Compute determinant of 3x3 matrix.
   */
  private static determinant3x3(matrix: number[][]): number {
    const [[a, b, c], [d, e, f], [g, h, i]] = matrix;
    return a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g);
  }

  /**
   * Simple eigen decomposition for 3x3 matrices (approximation).
   * For production, consider using a proper numerical library.
   */
  private static eigenDecomposition3x3(matrix: number[][]): {
    eigenvalues: number[];
    eigenvectors: number[][];
  } {
    // Simplified: For symmetric 3x3, use power iteration
    // This is a placeholder - in production, use a proper library
    const eigenvalues = [1, 1, 1]; // Placeholder
    const eigenvectors = [
      [1, 0, 0],
      [0, 1, 0],
      [0, 0, 1]
    ];
    
    // TODO: Implement proper eigen decomposition
    // For now, return identity (will need proper implementation)
    return { eigenvalues, eigenvectors };
  }
}

