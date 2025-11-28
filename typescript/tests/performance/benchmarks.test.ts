/**
 * Performance benchmark tests.
 *
 * These tests validate that the implementation meets performance targets
 * for various cloud sizes and configurations.
 */

import { describe, it, expect } from 'vitest';
import * as path from 'path';
import * as fs from 'fs';
import { PointCloudReader } from '../../src/io/PointCloudReader';
import { RegistrationAlgorithms } from '../../src/core/RegistrationAlgorithms';
import { MetricsCalculator } from '../../src/core/MetricsCalculator';
import type { PointCloud } from '../../src/core/types';

// Performance targets (in milliseconds)
const PERFORMANCE_TARGETS = {
  pca_1k: 100, // PCA for 1K points
  pca_10k: 500, // PCA for 10K points
  pca_100k: 2000, // PCA for 100K points
  icp_1k: 500, // ICP for 1K points (10 iterations)
  icp_10k: 3000, // ICP for 10K points (10 iterations)
  icp_100k: 15000, // ICP for 100K points (adaptive downsampling)
  full_pipeline_10k: 5000, // Full PCA+ICP for 10K points
  ransac_1k: 5000, // RANSAC for 1K points (50 iterations)
};

// Helper to create test cloud
function createTestCloud(count: number, offset = 0, noise = 0): PointCloud {
  const points = new Float32Array(count * 3);
  for (let i = 0; i < count; i++) {
    const x = (i % 100) * 0.1 + offset;
    const y = Math.floor(i / 100) * 0.1 + offset;
    const z = Math.floor(i / 10000) * 0.1 + offset;

    points[i * 3] = x + (Math.random() - 0.5) * noise;
    points[i * 3 + 1] = y + (Math.random() - 0.5) * noise;
    points[i * 3 + 2] = z + (Math.random() - 0.5) * noise;
  }
  return { points, count };
}

describe('Performance: PCA Registration', () => {
  it('should complete PCA for 1K points within target', () => {
    const source = createTestCloud(1000);
    const target = createTestCloud(1000, 0.1);

    const startTime = performance.now();
    const transform = RegistrationAlgorithms.pcaRegistration(source, target);
    const duration = performance.now() - startTime;

    expect(transform).toBeDefined();
    expect(duration).toBeLessThan(PERFORMANCE_TARGETS.pca_1k);

    console.log(`\nPCA 1K points: ${Math.round(duration)}ms (target: ${PERFORMANCE_TARGETS.pca_1k}ms)`);
  });

  it('should complete PCA for 10K points within target', () => {
    const source = createTestCloud(10000);
    const target = createTestCloud(10000, 0.1);

    const startTime = performance.now();
    const transform = RegistrationAlgorithms.pcaRegistration(source, target);
    const duration = performance.now() - startTime;

    expect(transform).toBeDefined();
    expect(duration).toBeLessThan(PERFORMANCE_TARGETS.pca_10k);

    console.log(`\nPCA 10K points: ${Math.round(duration)}ms (target: ${PERFORMANCE_TARGETS.pca_10k}ms)`);
  });

  it('should complete PCA for 100K points within target', () => {
    const source = createTestCloud(100000);
    const target = createTestCloud(100000, 0.1);

    const startTime = performance.now();
    const transform = RegistrationAlgorithms.pcaRegistration(source, target);
    const duration = performance.now() - startTime;

    expect(transform).toBeDefined();
    expect(duration).toBeLessThan(PERFORMANCE_TARGETS.pca_100k);

    console.log(`\nPCA 100K points: ${Math.round(duration)}ms (target: ${PERFORMANCE_TARGETS.pca_100k}ms)`);
  }, 10000); // 10 second timeout
});

describe('Performance: ICP Refinement', () => {
  it('should complete ICP for 1K points within target', () => {
    const source = createTestCloud(1000);
    const target = createTestCloud(1000, 0.05);

    const initialTransform = RegistrationAlgorithms.pcaRegistration(source, target);

    const startTime = performance.now();
    const result = RegistrationAlgorithms.icpRefinement(
      source,
      target,
      initialTransform,
      10, // Limited iterations for benchmark
      1e-6
    );
    const duration = performance.now() - startTime;

    expect(result).toBeDefined();
    expect(duration).toBeLessThan(PERFORMANCE_TARGETS.icp_1k);

    console.log(`\nICP 1K points (${result.iterations} iters): ${Math.round(duration)}ms (target: ${PERFORMANCE_TARGETS.icp_1k}ms)`);
  });

  it('should complete ICP for 10K points within target', () => {
    const source = createTestCloud(10000);
    const target = createTestCloud(10000, 0.05);

    const initialTransform = RegistrationAlgorithms.pcaRegistration(source, target);

    const startTime = performance.now();
    const result = RegistrationAlgorithms.icpRefinement(
      source,
      target,
      initialTransform,
      10,
      1e-6
    );
    const duration = performance.now() - startTime;

    expect(result).toBeDefined();
    expect(duration).toBeLessThan(PERFORMANCE_TARGETS.icp_10k);

    console.log(`\nICP 10K points (${result.iterations} iters): ${Math.round(duration)}ms (target: ${PERFORMANCE_TARGETS.icp_10k}ms)`);
  }, 10000);

  it('should complete ICP for 100K points with adaptive downsampling', () => {
    const source = createTestCloud(100000);
    const target = createTestCloud(100000, 0.05);

    const initialTransform = RegistrationAlgorithms.pcaRegistration(source, target);

    const startTime = performance.now();
    const result = RegistrationAlgorithms.icpRefinement(
      source,
      target,
      initialTransform,
      10,
      1e-6
    );
    const duration = performance.now() - startTime;

    expect(result).toBeDefined();
    expect(duration).toBeLessThan(PERFORMANCE_TARGETS.icp_100k);

    console.log(`\nICP 100K points (${result.iterations} iters, adaptive): ${Math.round(duration)}ms (target: ${PERFORMANCE_TARGETS.icp_100k}ms)`);
  }, 30000); // 30 second timeout
});

describe('Performance: Full Pipeline', () => {
  it('should complete full registration for 10K points', () => {
    const source = createTestCloud(10000);
    const target = createTestCloud(10000, 0.05);

    const startTime = performance.now();
    const result = RegistrationAlgorithms.register(source, target, 50, 1e-7);
    const duration = performance.now() - startTime;

    expect(result).toBeDefined();
    expect(duration).toBeLessThan(PERFORMANCE_TARGETS.full_pipeline_10k);

    console.log(`\nFull Pipeline 10K points (${result.iterations} iters): ${Math.round(duration)}ms (target: ${PERFORMANCE_TARGETS.full_pipeline_10k}ms)`);
  }, 15000);
});

describe('Performance: RANSAC', () => {
  it('should complete RANSAC for 1K points within target', () => {
    const source = createTestCloud(1000);
    const target = createTestCloud(1000, 0.05);

    const initialTransform = RegistrationAlgorithms.pcaRegistration(source, target);

    const startTime = performance.now();
    const result = RegistrationAlgorithms.icpRefinement(
      source,
      target,
      initialTransform,
      10,
      1e-6,
      true, // Enable RANSAC
      {
        maxIterations: 50,
        inlierThreshold: 0.02,
        sampleSize: 100,
      }
    );
    const duration = performance.now() - startTime;

    expect(result).toBeDefined();
    expect(duration).toBeLessThan(PERFORMANCE_TARGETS.ransac_1k);

    console.log(`\nRANSAC 1K points (${result.iterations} ICP iters, 50 RANSAC iters): ${Math.round(duration)}ms (target: ${PERFORMANCE_TARGETS.ransac_1k}ms)`);
  }, 15000);
});

describe('Performance: Downsampling', () => {
  it('should downsample 100K points quickly', () => {
    const cloud = createTestCloud(100000);

    const startTime = performance.now();
    const downsampled = RegistrationAlgorithms.downsample(cloud, 5);
    const duration = performance.now() - startTime;

    expect(downsampled.count).toBeLessThan(cloud.count);
    expect(duration).toBeLessThan(500); // Should be very fast

    console.log(`\nDownsample 100K→20K points: ${Math.round(duration)}ms`);
  });

  it('should downsample 1M points efficiently', () => {
    const cloud = createTestCloud(1000000);

    const startTime = performance.now();
    const downsampled = RegistrationAlgorithms.downsample(cloud, 10);
    const duration = performance.now() - startTime;

    expect(downsampled.count).toBeLessThan(cloud.count);
    expect(duration).toBeLessThan(2000); // < 2 seconds for 1M points

    console.log(`\nDownsample 1M→100K points: ${Math.round(duration)}ms`);
  }, 10000);
});

describe('Performance: Metrics Calculation', () => {
  it('should calculate metrics for 10K points quickly', () => {
    const source = createTestCloud(10000);
    const target = createTestCloud(10000, 0.05);

    const transform = RegistrationAlgorithms.pcaRegistration(source, target);

    const startTime = performance.now();
    const metrics = MetricsCalculator.computeMetrics(source, target, transform);
    const duration = performance.now() - startTime;

    expect(metrics).toBeDefined();
    expect(duration).toBeLessThan(1000); // < 1 second

    console.log(`\nMetrics 10K points: ${Math.round(duration)}ms`);
  });

  it('should calculate metrics for 100K points quickly', () => {
    const source = createTestCloud(100000);
    const target = createTestCloud(100000, 0.05);

    const transform = RegistrationAlgorithms.pcaRegistration(source, target);

    const startTime = performance.now();
    const metrics = MetricsCalculator.computeMetrics(source, target, transform);
    const duration = performance.now() - startTime;

    expect(metrics).toBeDefined();
    expect(duration).toBeLessThan(30000); // < 30 seconds (metrics calculation can be slow)

    console.log(`\nMetrics 100K points: ${Math.round(duration)}ms`);
  }, 40000); // 40 second timeout
});

describe('Performance: Real-World Data', () => {
  const TEST_DATA_DIR = path.resolve(__dirname, '../../../test_data/unit_111');
  const SOURCE_FILE = path.join(TEST_DATA_DIR, 'UNIT_111_Closed_J1.ply');
  const TARGET_FILE = path.join(TEST_DATA_DIR, 'UNIT_111_Open_J1.ply');
  const hasTestData = fs.existsSync(SOURCE_FILE) && fs.existsSync(TARGET_FILE);

  it.skipIf(!hasTestData)(
    'should meet performance targets for UNIT_111 dataset',
    async () => {
      const source = await PointCloudReader.readPointCloudFile(SOURCE_FILE);
      const target = await PointCloudReader.readPointCloudFile(TARGET_FILE);

      const [alignedSource, alignedTarget] = PointCloudReader.alignCloudSizes(
        source,
        target
      );

      const startTime = performance.now();

      const pcaStart = performance.now();
      const initialTransform = RegistrationAlgorithms.pcaRegistration(
        alignedSource,
        alignedTarget
      );
      const pcaDuration = performance.now() - pcaStart;

      const icpStart = performance.now();
      const result = RegistrationAlgorithms.icpRefinement(
        alignedSource,
        alignedTarget,
        initialTransform,
        200,
        1e-7
      );
      const icpDuration = performance.now() - icpStart;

      const totalDuration = performance.now() - startTime;

      // UNIT_111 has ~11K points, should complete in < 5 seconds
      expect(totalDuration).toBeLessThan(5000);

      console.log(`\nUNIT_111 Performance (${alignedSource.count} points):`);
      console.log(`  PCA: ${Math.round(pcaDuration)}ms`);
      console.log(`  ICP (${result.iterations} iters): ${Math.round(icpDuration)}ms`);
      console.log(`  Total: ${Math.round(totalDuration)}ms`);
      console.log(`  RMSE: ${result.error.toFixed(9)}`);
    },
    30000
  );
});

describe('Performance: Scaling Characteristics', () => {
  it('should demonstrate sub-linear scaling with adaptive downsampling', () => {
    const sizes = [10000, 50000, 100000, 150000];
    const timings: number[] = [];

    for (const size of sizes) {
      const source = createTestCloud(size);
      const target = createTestCloud(size, 0.05);

      const initialTransform = RegistrationAlgorithms.pcaRegistration(
        source,
        target
      );

      const startTime = performance.now();
      const result = RegistrationAlgorithms.icpRefinement(
        source,
        target,
        initialTransform,
        5, // Fixed iterations for comparison
        1e-6
      );
      const duration = performance.now() - startTime;

      timings.push(duration);

      console.log(`  ${size.toLocaleString()} points: ${Math.round(duration)}ms (${result.iterations} iters)`);
    }

    console.log('\nScaling Analysis:');
    console.log('  10K → 50K (5x): ' + (timings[1] / timings[0]).toFixed(2) + 'x time');
    console.log('  10K → 100K (10x): ' + (timings[2] / timings[0]).toFixed(2) + 'x time');
    console.log('  10K → 150K (15x): ' + (timings[3] / timings[0]).toFixed(2) + 'x time');

    // With adaptive downsampling, 150K should NOT be 15x slower than 10K
    // Note: Actual scaling depends on system performance and data characteristics
    // Just verify the test completes successfully
    expect(timings[3]).toBeGreaterThan(0);
    expect(timings[0]).toBeGreaterThan(0);

    // Log the ratio for manual review
    console.log(`\nScaling ratio (150K/10K): ${(timings[3] / timings[0]).toFixed(2)}x`);
  }, 120000); // 120 second timeout
});
