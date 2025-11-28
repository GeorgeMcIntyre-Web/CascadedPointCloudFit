/**
 * Integration tests for point cloud registration.
 * 
 * Tests the full registration pipeline with real-world scenarios.
 */

import { describe, it, expect } from 'vitest';
import { PointCloudReader } from '../../src/io/PointCloudReader';
import { RegistrationAlgorithms } from '../../src/core/RegistrationAlgorithms';
import { MetricsCalculator } from '../../src/core/MetricsCalculator';
import { PointCloudHelper } from '../../src/core/PointCloudHelper';

describe('Integration: Point Cloud Registration', () => {
  describe('Basic Registration Pipeline', () => {
    it('should register two simple point clouds', () => {
      // Create two simple point clouds (unit cube corners)
      const sourcePoints = [
        { x: 0, y: 0, z: 0 },
        { x: 1, y: 0, z: 0 },
        { x: 0, y: 1, z: 0 },
        { x: 0, y: 0, z: 1 },
        { x: 1, y: 1, z: 0 },
        { x: 1, y: 0, z: 1 },
        { x: 0, y: 1, z: 1 },
        { x: 1, y: 1, z: 1 }
      ];

      // Target: same cube translated by (1, 1, 1)
      const targetPoints = sourcePoints.map(p => ({
        x: p.x + 1,
        y: p.y + 1,
        z: p.z + 1
      }));

      const source = PointCloudHelper.fromPoints(sourcePoints);
      const target = PointCloudHelper.fromPoints(targetPoints);

      // Run PCA registration
      const initialTransform = RegistrationAlgorithms.pcaRegistration(source, target);

      // Run ICP refinement
      const icpResult = RegistrationAlgorithms.icpRefinement(
        source,
        target,
        initialTransform,
        50,
        1e-7
      );

      // Compute metrics
      const metrics = MetricsCalculator.computeMetrics(source, target, icpResult.transform);

      // Should achieve low RMSE
      expect(metrics.rmse).toBeLessThan(0.1);
      expect(icpResult.iterations).toBeGreaterThan(0);
      expect(icpResult.iterations).toBeLessThan(50);
    });

    it('should handle rotated point clouds', () => {
      // Create source points
      const sourcePoints = [
        { x: 0, y: 0, z: 0 },
        { x: 1, y: 0, z: 0 },
        { x: 0, y: 1, z: 0 },
        { x: 0, y: 0, z: 1 }
      ];

      // Target: rotated 90 degrees around Z-axis
      const targetPoints = [
        { x: 0, y: 0, z: 0 },
        { x: 0, y: 1, z: 0 },  // (1,0,0) -> (0,1,0)
        { x: -1, y: 0, z: 0 }, // (0,1,0) -> (-1,0,0)
        { x: 0, y: 0, z: 1 }
      ];

      const source = PointCloudHelper.fromPoints(sourcePoints);
      const target = PointCloudHelper.fromPoints(targetPoints);

      const initialTransform = RegistrationAlgorithms.pcaRegistration(source, target);
      const icpResult = RegistrationAlgorithms.icpRefinement(
        source,
        target,
        initialTransform,
        50,
        1e-7
      );

      const metrics = MetricsCalculator.computeMetrics(source, target, icpResult.transform);

      // Should achieve reasonable registration
      expect(metrics.rmse).toBeLessThan(1.0);
    });

    it('should handle different sized point clouds', () => {
      const sourcePoints = [
        { x: 0, y: 0, z: 0 },
        { x: 1, y: 0, z: 0 },
        { x: 0, y: 1, z: 0 },
        { x: 0, y: 0, z: 1 },
        { x: 1, y: 1, z: 1 }
      ];

      const targetPoints = [
        { x: 1, y: 1, z: 1 },
        { x: 2, y: 1, z: 1 },
        { x: 1, y: 2, z: 1 },
        { x: 1, y: 1, z: 2 }
      ];

      const source = PointCloudHelper.fromPoints(sourcePoints);
      const target = PointCloudHelper.fromPoints(targetPoints);

      // Align sizes
      const [alignedSource, alignedTarget] = PointCloudReader.alignCloudSizes(source, target);

      expect(alignedSource.count).toBe(alignedTarget.count);
      expect(alignedSource.count).toBe(4); // Minimum size

      const initialTransform = RegistrationAlgorithms.pcaRegistration(alignedSource, alignedTarget);
      const icpResult = RegistrationAlgorithms.icpRefinement(
        alignedSource,
        alignedTarget,
        initialTransform,
        50,
        1e-7
      );

      const metrics = MetricsCalculator.computeMetrics(alignedSource, alignedTarget, icpResult.transform);

      expect(metrics.rmse).toBeLessThan(1.0);
    });
  });

  describe('Error Handling', () => {
    it('should handle empty point clouds gracefully', () => {
      const empty = PointCloudHelper.fromPoints([]);
      const target = PointCloudHelper.fromPoints([{ x: 0, y: 0, z: 0 }]);

      expect(() => {
        RegistrationAlgorithms.pcaRegistration(empty, target);
      }).toThrow();
    });

    it('should handle point clouds with insufficient points', () => {
      const source = PointCloudHelper.fromPoints([{ x: 0, y: 0, z: 0 }]);
      const target = PointCloudHelper.fromPoints([{ x: 1, y: 1, z: 1 }]);

      expect(() => {
        RegistrationAlgorithms.pcaRegistration(source, target);
      }).toThrow();
    });
  });

  describe('Performance', () => {
    it('should complete registration for medium-sized clouds quickly', () => {
      // Generate 1000 points
      const sourcePoints: Array<{ x: number; y: number; z: number }> = [];
      const targetPoints: Array<{ x: number; y: number; z: number }> = [];

      for (let i = 0; i < 1000; i++) {
        sourcePoints.push({
          x: Math.random() * 10,
          y: Math.random() * 10,
          z: Math.random() * 10
        });
        targetPoints.push({
          x: sourcePoints[i].x + 1,
          y: sourcePoints[i].y + 1,
          z: sourcePoints[i].z + 1
        });
      }

      const source = PointCloudHelper.fromPoints(sourcePoints);
      const target = PointCloudHelper.fromPoints(targetPoints);

      const startTime = Date.now();

      const initialTransform = RegistrationAlgorithms.pcaRegistration(source, target);
      const icpResult = RegistrationAlgorithms.icpRefinement(
        source,
        target,
        initialTransform,
        30, // Reduced iterations for speed
        1e-6
      );

      const endTime = Date.now();
      const duration = endTime - startTime;

      // Should complete in reasonable time (< 5 seconds)
      expect(duration).toBeLessThan(5000);

      const metrics = MetricsCalculator.computeMetrics(source, target, icpResult.transform);
      expect(metrics.rmse).toBeLessThan(0.5);
    });
  });
});

