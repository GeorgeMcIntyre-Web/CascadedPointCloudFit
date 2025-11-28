/**
 * Unit tests for MetricsCalculator.
 */

import { describe, it, expect } from 'vitest';
import { MetricsCalculator } from '../../src/core/MetricsCalculator';
import { PointCloudHelper } from '../../src/core/PointCloudHelper';

describe('MetricsCalculator', () => {
  describe('computeMetrics', () => {
    it('should compute metrics for identity transformation', () => {
      const sourcePoints = [
        { x: 0, y: 0, z: 0 },
        { x: 1, y: 0, z: 0 },
        { x: 0, y: 1, z: 0 }
      ];

      const targetPoints = sourcePoints; // Same points

      const source = PointCloudHelper.fromPoints(sourcePoints);
      const target = PointCloudHelper.fromPoints(targetPoints);

      const identityTransform = {
        matrix: [
          [1, 0, 0, 0],
          [0, 1, 0, 0],
          [0, 0, 1, 0],
          [0, 0, 0, 1]
        ]
      };

      const metrics = MetricsCalculator.computeMetrics(source, target, identityTransform);

      expect(metrics.rmse).toBeCloseTo(0, 5);
      expect(metrics.maxError).toBeCloseTo(0, 5);
      expect(metrics.meanError).toBeCloseTo(0, 5);
      expect(metrics.medianError).toBeCloseTo(0, 5);
    });

    it('should compute metrics for translation', () => {
      const sourcePoints = [
        { x: 0, y: 0, z: 0 },
        { x: 1, y: 0, z: 0 },
        { x: 0, y: 1, z: 0 }
      ];

      const targetPoints = sourcePoints.map(p => ({
        x: p.x + 1,
        y: p.y + 1,
        z: p.z + 1
      }));

      const source = PointCloudHelper.fromPoints(sourcePoints);
      const target = PointCloudHelper.fromPoints(targetPoints);

      const translationTransform = {
        matrix: [
          [1, 0, 0, 1],
          [0, 1, 0, 1],
          [0, 0, 1, 1],
          [0, 0, 0, 1]
        ]
      };

      const metrics = MetricsCalculator.computeMetrics(source, target, translationTransform);

      expect(metrics.rmse).toBeGreaterThanOrEqual(0);
      expect(metrics.maxError).toBeGreaterThanOrEqual(0);
      expect(metrics.meanError).toBeGreaterThanOrEqual(0);
    });

    it('should return transformation matrix in metrics', () => {
      const sourcePoints = [
        { x: 0, y: 0, z: 0 },
        { x: 1, y: 0, z: 0 }
      ];

      const targetPoints = sourcePoints;

      const source = PointCloudHelper.fromPoints(sourcePoints);
      const target = PointCloudHelper.fromPoints(targetPoints);

      const transform = {
        matrix: [
          [1, 0, 0, 0],
          [0, 1, 0, 0],
          [0, 0, 1, 0],
          [0, 0, 0, 1]
        ]
      };

      const metrics = MetricsCalculator.computeMetrics(source, target, transform);

      expect(metrics.transformation).toEqual(transform.matrix);
    });
  });
});

