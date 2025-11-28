/**
 * End-to-End tests for complete registration workflows.
 *
 * These tests validate the entire pipeline from loading files
 * through registration to metrics calculation.
 */

import { describe, it, expect, beforeAll } from 'vitest';
import * as path from 'path';
import * as fs from 'fs';
import { PointCloudReader } from '../../src/io/PointCloudReader';
import { RegistrationAlgorithms } from '../../src/core/RegistrationAlgorithms';
import { MetricsCalculator } from '../../src/core/MetricsCalculator';
import type { PointCloud, ICPResult, RegistrationMetrics } from '../../src/core/types';

// Test data paths
const TEST_DATA_DIR = path.resolve(__dirname, '../../../test_data');
const UNIT_111_DIR = path.join(TEST_DATA_DIR, 'unit_111');

// Dataset configurations
const TEST_DATASETS = [
  {
    name: 'UNIT_111',
    dir: UNIT_111_DIR,
    source: 'UNIT_111_Closed_J1.ply',
    target: 'UNIT_111_Open_J1.ply',
    expectedPoints: { min: 10000, max: 12000 },
    timeout: 30000,
    maxRMSE: 0.001, // Very tight tolerance for clean data
  },
];

// Helper to check if dataset exists
function datasetExists(dataset: typeof TEST_DATASETS[0]): boolean {
  const sourcePath = path.join(dataset.dir, dataset.source);
  const targetPath = path.join(dataset.dir, dataset.target);
  return fs.existsSync(sourcePath) && fs.existsSync(targetPath);
}

describe('E2E: Complete Registration Workflow', () => {
  TEST_DATASETS.forEach((dataset) => {
    const hasData = datasetExists(dataset);

    describe(`Dataset: ${dataset.name}`, () => {
      let source: PointCloud;
      let target: PointCloud;

      beforeAll(async () => {
        if (!hasData) return;

        const sourcePath = path.join(dataset.dir, dataset.source);
        const targetPath = path.join(dataset.dir, dataset.target);

        source = await PointCloudReader.readPointCloudFile(sourcePath);
        target = await PointCloudReader.readPointCloudFile(targetPath);
      });

      it.skipIf(!hasData)('should load point clouds successfully', () => {
        expect(source).toBeDefined();
        expect(target).toBeDefined();
        expect(source.count).toBeGreaterThanOrEqual(dataset.expectedPoints.min);
        expect(source.count).toBeLessThanOrEqual(dataset.expectedPoints.max);
        expect(target.count).toBeGreaterThanOrEqual(dataset.expectedPoints.min);
        expect(target.count).toBeLessThanOrEqual(dataset.expectedPoints.max);
      });

      it.skipIf(!hasData)(
        'should complete full PCA + ICP pipeline',
        async () => {
          // Align cloud sizes
          const [alignedSource, alignedTarget] = PointCloudReader.alignCloudSizes(
            source,
            target
          );

          expect(alignedSource.count).toBe(alignedTarget.count);

          // Run complete registration
          const result = RegistrationAlgorithms.register(
            alignedSource,
            alignedTarget,
            200, // maxIterations
            1e-7 // tolerance
          );

          // Validate ICP result
          expect(result).toBeDefined();
          expect(result.transform).toBeDefined();
          expect(result.transform.matrix).toBeDefined();
          expect(result.transform.matrix.length).toBe(4);
          expect(result.transform.matrix[0].length).toBe(4);
          expect(result.iterations).toBeGreaterThan(0);
          expect(result.iterations).toBeLessThanOrEqual(200);
          expect(result.error).toBeGreaterThanOrEqual(0);
          expect(result.error).toBeLessThan(dataset.maxRMSE);

          console.log(`\n${dataset.name} - Full Pipeline:`);
          console.log(`  Iterations: ${result.iterations}`);
          console.log(`  Final RMSE: ${result.error.toFixed(9)}`);
        },
        dataset.timeout
      );

      it.skipIf(!hasData)(
        'should produce valid transformation matrix',
        async () => {
          const [alignedSource, alignedTarget] = PointCloudReader.alignCloudSizes(
            source,
            target
          );

          const result = RegistrationAlgorithms.register(
            alignedSource,
            alignedTarget
          );

          const matrix = result.transform.matrix;

          // Check matrix structure (4x4)
          expect(matrix.length).toBe(4);
          matrix.forEach((row) => {
            expect(row.length).toBe(4);
          });

          // Bottom row should be [0, 0, 0, 1]
          expect(matrix[3][0]).toBe(0);
          expect(matrix[3][1]).toBe(0);
          expect(matrix[3][2]).toBe(0);
          expect(matrix[3][3]).toBe(1);

          // All values should be finite
          matrix.forEach((row) => {
            row.forEach((val) => {
              expect(Number.isFinite(val)).toBe(true);
            });
          });
        },
        dataset.timeout
      );

      it.skipIf(!hasData)(
        'should calculate comprehensive metrics',
        async () => {
          const [alignedSource, alignedTarget] = PointCloudReader.alignCloudSizes(
            source,
            target
          );

          const result = RegistrationAlgorithms.register(
            alignedSource,
            alignedTarget
          );

          const metrics = MetricsCalculator.computeMetrics(
            alignedSource,
            alignedTarget,
            result.transform
          );

          // All metrics should be non-negative
          expect(metrics.rmse).toBeGreaterThanOrEqual(0);
          expect(metrics.maxError).toBeGreaterThanOrEqual(0);
          expect(metrics.meanError).toBeGreaterThanOrEqual(0);
          expect(metrics.medianError).toBeGreaterThanOrEqual(0);

          // RMSE should match ICP result error
          expect(Math.abs(metrics.rmse - result.error)).toBeLessThan(1e-9);

          // Logical consistency: max >= mean >= median >= 0
          expect(metrics.maxError).toBeGreaterThanOrEqual(metrics.meanError);
          expect(metrics.meanError).toBeGreaterThanOrEqual(0);

          // For clean data, all metrics should be very small
          expect(metrics.rmse).toBeLessThan(dataset.maxRMSE);

          console.log(`\n${dataset.name} - Metrics:`);
          console.log(`  RMSE: ${metrics.rmse.toFixed(9)}`);
          console.log(`  Max Error: ${metrics.maxError.toFixed(9)}`);
          console.log(`  Mean Error: ${metrics.meanError.toFixed(9)}`);
          console.log(`  Median Error: ${metrics.medianError.toFixed(9)}`);
        },
        dataset.timeout
      );

      it.skipIf(!hasData)(
        'should handle downsampling for large clouds',
        async () => {
          const [alignedSource, alignedTarget] = PointCloudReader.alignCloudSizes(
            source,
            target
          );

          // Test explicit downsampling
          const downsampleFactor = 2;
          const downsampledSource = RegistrationAlgorithms.downsample(
            alignedSource,
            downsampleFactor
          );

          // Downsampled cloud should be roughly half the size
          const expectedCount = Math.floor(alignedSource.count / downsampleFactor);
          const tolerance = Math.ceil(alignedSource.count * 0.1); // 10% tolerance

          expect(downsampledSource.count).toBeGreaterThanOrEqual(
            expectedCount - tolerance
          );
          expect(downsampledSource.count).toBeLessThanOrEqual(
            expectedCount + tolerance
          );

          // Points should still be valid
          expect(downsampledSource.points).toBeDefined();
          expect(downsampledSource.points.length).toBe(downsampledSource.count * 3);

          // Can still register downsampled clouds
          const result = RegistrationAlgorithms.register(
            downsampledSource,
            alignedTarget
          );

          expect(result.error).toBeLessThan(dataset.maxRMSE * 2); // Allow 2x tolerance for downsampled
        },
        dataset.timeout
      );
    });
  });
});

describe('E2E: Error Handling', () => {
  it('should handle empty point clouds gracefully', () => {
    const emptyCloud: PointCloud = {
      points: new Float32Array(0),
      count: 0,
    };

    const validCloud: PointCloud = {
      points: new Float32Array([0, 0, 0, 1, 0, 0, 0, 1, 0]),
      count: 3,
    };

    // Should throw or return gracefully
    expect(() => {
      RegistrationAlgorithms.register(emptyCloud, validCloud);
    }).toThrow();
  });

  it('should handle mismatched cloud sizes', async () => {
    const small: PointCloud = {
      points: new Float32Array([0, 0, 0, 1, 0, 0, 0, 1, 0]),
      count: 3,
    };

    const large: PointCloud = {
      points: new Float32Array(Array(3000).fill(0)),
      count: 1000,
    };

    // Should align clouds automatically in register()
    const result = RegistrationAlgorithms.register(small, large);
    expect(result).toBeDefined();
  });

  it('should handle degenerate point clouds', () => {
    // All points at origin
    const degenerate: PointCloud = {
      points: new Float32Array([0, 0, 0, 0, 0, 0, 0, 0, 0]),
      count: 3,
    };

    const valid: PointCloud = {
      points: new Float32Array([0, 0, 0, 1, 0, 0, 0, 1, 0]),
      count: 3,
    };

    // May fail or return identity transform - just shouldn't crash
    expect(() => {
      const result = RegistrationAlgorithms.register(degenerate, valid);
      expect(result).toBeDefined();
    }).not.toThrow();
  });
});

describe('E2E: Performance Benchmarks', () => {
  const PERFORMANCE_TIMEOUT = 60000; // 60 seconds

  it.skipIf(!datasetExists(TEST_DATASETS[0]))(
    'should meet performance targets for UNIT_111',
    async () => {
      const dataset = TEST_DATASETS[0];
      const sourcePath = path.join(dataset.dir, dataset.source);
      const targetPath = path.join(dataset.dir, dataset.target);

      const source = await PointCloudReader.readPointCloudFile(sourcePath);
      const target = await PointCloudReader.readPointCloudFile(targetPath);

      const [alignedSource, alignedTarget] = PointCloudReader.alignCloudSizes(
        source,
        target
      );

      const startTime = performance.now();

      const result = RegistrationAlgorithms.register(
        alignedSource,
        alignedTarget,
        200,
        1e-7
      );

      const endTime = performance.now();
      const duration = endTime - startTime;

      // Should complete in < 5 seconds for 11K points
      expect(duration).toBeLessThan(5000);

      console.log(`\nPerformance Benchmark:`);
      console.log(`  Dataset: ${dataset.name}`);
      console.log(`  Points: ${alignedSource.count}`);
      console.log(`  Duration: ${Math.round(duration)}ms`);
      console.log(`  Iterations: ${result.iterations}`);
      console.log(`  RMSE: ${result.error.toFixed(9)}`);
    },
    PERFORMANCE_TIMEOUT
  );
});
