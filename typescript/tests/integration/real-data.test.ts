/**
 * Integration tests with real UNIT_111 test data.
 * 
 * These tests validate the TypeScript implementation against
 * real-world point cloud data.
 */

import { describe, it, expect } from 'vitest';
import * as path from 'path';
import * as fs from 'fs';
import { PointCloudReader } from '../../src/io/PointCloudReader';
import { RegistrationAlgorithms } from '../../src/core/RegistrationAlgorithms';
import { MetricsCalculator } from '../../src/core/MetricsCalculator';

// Path to test data (relative to project root)
const TEST_DATA_DIR = path.resolve(__dirname, '../../../test_data/unit_111');
const SOURCE_FILE = path.join(TEST_DATA_DIR, 'UNIT_111_Closed_J1.ply');
const TARGET_FILE = path.join(TEST_DATA_DIR, 'UNIT_111_Open_J1.ply');

// Check if test data is available
const hasTestData = fs.existsSync(SOURCE_FILE) && fs.existsSync(TARGET_FILE);

describe('Integration: Real Data (UNIT_111)', () => {
  describe('File Loading', () => {
    it.skipIf(!hasTestData)('should load UNIT_111 PLY files', async () => {
      const source = await PointCloudReader.readPointCloudFile(SOURCE_FILE);
      const target = await PointCloudReader.readPointCloudFile(TARGET_FILE);

      // UNIT_111 files should have ~11,200 points each
      expect(source.count).toBeGreaterThan(10000);
      expect(source.count).toBeLessThan(12000);
      expect(target.count).toBeGreaterThan(10000);
      expect(target.count).toBeLessThan(12000);
    });
  });

  describe('Registration with Real Data', () => {
    it.skipIf(!hasTestData)('should register UNIT_111 point clouds', async () => {
      const source = await PointCloudReader.readPointCloudFile(SOURCE_FILE);
      const target = await PointCloudReader.readPointCloudFile(TARGET_FILE);

      // Align cloud sizes
      const [alignedSource, alignedTarget] = PointCloudReader.alignCloudSizes(source, target);

      expect(alignedSource.count).toBe(alignedTarget.count);

      // Run PCA registration
      const initialTransform = RegistrationAlgorithms.pcaRegistration(
        alignedSource,
        alignedTarget
      );

      // Run ICP refinement
      const icpResult = RegistrationAlgorithms.icpRefinement(
        alignedSource,
        alignedTarget,
        initialTransform,
        200, // Max iterations
        1e-7 // Tolerance
      );

      // Compute metrics
      const metrics = MetricsCalculator.computeMetrics(
        alignedSource,
        alignedTarget,
        icpResult.transform
      );

      // Validate results
      expect(icpResult.iterations).toBeGreaterThan(0);
      expect(icpResult.iterations).toBeLessThanOrEqual(200);
      expect(metrics.rmse).toBeGreaterThan(0);
      expect(metrics.rmse).toBeLessThan(10); // Should be reasonable for real data
      expect(metrics.maxError).toBeGreaterThan(0);
      expect(metrics.meanError).toBeGreaterThan(0);
      expect(metrics.medianError).toBeGreaterThan(0);

      // Log results for manual inspection
      console.log(`\nUNIT_111 Registration Results:`);
      console.log(`  Iterations: ${icpResult.iterations}`);
      console.log(`  RMSE: ${metrics.rmse.toFixed(6)}`);
      console.log(`  Max Error: ${metrics.maxError.toFixed(6)}`);
      console.log(`  Mean Error: ${metrics.meanError.toFixed(6)}`);
      console.log(`  Median Error: ${metrics.medianError.toFixed(6)}`);
    }, 30000); // 30 second timeout for real data

    it.skipIf(!hasTestData)('should complete registration in reasonable time', async () => {
      const source = await PointCloudReader.readPointCloudFile(SOURCE_FILE);
      const target = await PointCloudReader.readPointCloudFile(TARGET_FILE);

      const [alignedSource, alignedTarget] = PointCloudReader.alignCloudSizes(source, target);

      const startTime = Date.now();

      const initialTransform = RegistrationAlgorithms.pcaRegistration(
        alignedSource,
        alignedTarget
      );

      const icpResult = RegistrationAlgorithms.icpRefinement(
        alignedSource,
        alignedTarget,
        initialTransform,
        100, // Reduced iterations for speed test
        1e-6
      );

      const endTime = Date.now();
      const duration = endTime - startTime;

      // Should complete in reasonable time (< 10 seconds for 11K points)
      expect(duration).toBeLessThan(10000);

      console.log(`\nPerformance: ${duration}ms for ${alignedSource.count} points`);
    }, 15000);
  });
});

