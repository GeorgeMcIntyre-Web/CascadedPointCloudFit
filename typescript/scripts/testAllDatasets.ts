/**
 * Comprehensive test script for all datasets
 *
 * Tests all available point cloud datasets including:
 * - UNIT_111 (11K points)
 * - Clamp (10K points)
 * - Slide (155K points) - Large dataset
 * - Clouds3 (47K points)
 * - Challenging cases (IcpFails, Fails4, PinFails)
 */

import * as path from 'path';
import * as fs from 'fs';
import { PointCloudReader } from '../src/io/PointCloudReader';
import { RegistrationAlgorithms } from '../src/core/RegistrationAlgorithms';
import { MetricsCalculator } from '../src/core/MetricsCalculator';

interface TestDataset {
  name: string;
  source: string;
  target: string;
  category: 'standard' | 'large' | 'challenging';
}

// Define all datasets (paths relative to repository root)
const DATASETS: TestDataset[] = [
  // Standard datasets
  {
    name: 'UNIT_111',
    source: '../../test_data/unit_111/UNIT_111_Closed_J1.ply',
    target: '../../test_data/unit_111/UNIT_111_Open_J1.ply',
    category: 'standard'
  },
  {
    name: 'Clamp (local)',
    source: '../../test_data/clamp/Clamp1.ply',
    target: '../../test_data/clamp/Clamp2.ply',
    category: 'standard'
  },
  {
    name: 'Clamp (external)',
    source: '../../test_data/external/Clamp1.ply',
    target: '../../test_data/external/Clamp2.ply',
    category: 'standard'
  },

  // Large datasets
  {
    name: 'Slide (local)',
    source: '../../test_data/slide/Slide1.ply',
    target: '../../test_data/slide/Slide2.ply',
    category: 'large'
  },
  {
    name: 'Slide (external)',
    source: '../../test_data/external/Slide1.ply',
    target: '../../test_data/external/Slide2.ply',
    category: 'large'
  },
  {
    name: 'Clouds3',
    source: '../../test_data/external/Clouds3/016ZF-20137361-670B-109R_CI00_M2.ply',
    target: '../../test_data/external/Clouds3/016ZF-20137361-670B-109R_CI00_O2.ply',
    category: 'large'
  },

  // Challenging cases
  {
    name: 'Fails4',
    source: '../../test_data/external/Fails4/016ZF-20137361-670B-108_CI00_M1.ply',
    target: '../../test_data/external/Fails4/016ZF-20137361-670B-108_CI00_O1.ply',
    category: 'challenging'
  },
  {
    name: 'IcpFails',
    source: '../../test_data/external/IcpFails/016ZF-20137361-670B-103R_CI00_M3.ply',
    target: '../../test_data/external/IcpFails/016ZF-20137361-670B-103R_CI00_O3.ply',
    category: 'challenging'
  },
  {
    name: 'PinFails1',
    source: '../../test_data/external/PinFails1/016ZF-20137366-370-103-R_CI00_M.ply',
    target: '../../test_data/external/PinFails1/016ZF-20137366-370-103-R_CI00_O.ply',
    category: 'challenging'
  },
  {
    name: 'PinFails2',
    source: '../../test_data/external/PinFails2/file2.ply', // Swapped: use smaller cloud as source
    target: '../../test_data/external/PinFails2/file1.ply', // Swapped: use larger cloud as target
    category: 'challenging'
  }
];

interface TestResult {
  dataset: string;
  category: string;
  sourcePoints: number;
  targetPoints: number;
  duration: number;
  iterations: number;
  rmse: number;
  maxError: number;
  meanError: number;
  medianError: number;
  success: boolean;
  error?: string;
}

async function testDataset(dataset: TestDataset): Promise<TestResult> {
  const sourcePath = path.resolve(__dirname, dataset.source);
  const targetPath = path.resolve(__dirname, dataset.target);

  try {
    // Check if files exist
    if (!fs.existsSync(sourcePath) || !fs.existsSync(targetPath)) {
      return {
        dataset: dataset.name,
        category: dataset.category,
        sourcePoints: 0,
        targetPoints: 0,
        duration: 0,
        iterations: 0,
        rmse: 0,
        maxError: 0,
        meanError: 0,
        medianError: 0,
        success: false,
        error: 'Files not found'
      };
    }

    // Load point clouds
    console.log(`\n📂 Loading ${dataset.name}...`);
    const source = await PointCloudReader.readPointCloudFile(sourcePath);
    const target = await PointCloudReader.readPointCloudFile(targetPath);

    console.log(`   Source: ${source.count.toLocaleString()} points`);
    console.log(`   Target: ${target.count.toLocaleString()} points`);

    // Align cloud sizes
    const [alignedSource, alignedTarget] = PointCloudReader.alignCloudSizes(source, target);

    // Run registration
    // Enable RANSAC for challenging datasets (partial overlap, poor initial alignment)
    const useRANSAC = dataset.category === 'challenging';
    if (useRANSAC) {
      console.log(`   🔄 Running registration with RANSAC...`);
    } else {
      console.log(`   🔄 Running registration...`);
    }
    const startTime = performance.now();

    const result = RegistrationAlgorithms.register(
      alignedSource,
      alignedTarget,
      200, // maxIterations
      1e-7, // tolerance
      useRANSAC, // Enable RANSAC for challenging datasets
      useRANSAC ? {
        maxIterations: 200, // More RANSAC iterations for challenging cases
        inlierThreshold: 0.01, // 1cm threshold
        sampleSize: Math.min(100, Math.max(20, Math.floor(alignedSource.count * 0.002))) // 0.2% sample
      } : undefined
    );

    const duration = performance.now() - startTime;

    // Calculate metrics
    const metrics = MetricsCalculator.computeMetrics(
      alignedSource,
      alignedTarget,
      result.transform
    );

    console.log(`   ✅ Complete in ${Math.round(duration)}ms`);
    console.log(`   Iterations: ${result.iterations}, RMSE: ${metrics.rmse.toFixed(6)}`);

    return {
      dataset: dataset.name,
      category: dataset.category,
      sourcePoints: source.count,
      targetPoints: target.count,
      duration,
      iterations: result.iterations,
      rmse: metrics.rmse,
      maxError: metrics.maxError,
      meanError: metrics.meanError,
      medianError: metrics.medianError,
      success: true
    };

  } catch (error) {
    console.log(`   ❌ Failed: ${error instanceof Error ? error.message : String(error)}`);
    return {
      dataset: dataset.name,
      category: dataset.category,
      sourcePoints: 0,
      targetPoints: 0,
      duration: 0,
      iterations: 0,
      rmse: 0,
      maxError: 0,
      meanError: 0,
      medianError: 0,
      success: false,
      error: error instanceof Error ? error.message : String(error)
    };
  }
}

async function runAllTests() {
  console.log('═══════════════════════════════════════════════════════');
  console.log('  CascadedPointCloudFit - Comprehensive Dataset Tests');
  console.log('═══════════════════════════════════════════════════════\n');

  const results: TestResult[] = [];

  // Test each dataset
  for (const dataset of DATASETS) {
    const result = await testDataset(dataset);
    results.push(result);
  }

  // Print summary
  console.log('\n═══════════════════════════════════════════════════════');
  console.log('  SUMMARY');
  console.log('═══════════════════════════════════════════════════════\n');

  // Group by category
  const categories = ['standard', 'large', 'challenging'] as const;

  for (const category of categories) {
    const categoryResults = results.filter(r => r.category === category);
    if (categoryResults.length === 0) continue;

    console.log(`\n${category.toUpperCase()} DATASETS:`);
    console.log('─'.repeat(80));

    categoryResults.forEach(r => {
      if (r.success) {
        console.log(`✅ ${r.dataset.padEnd(20)} | ${r.sourcePoints.toLocaleString().padStart(7)} pts | ${Math.round(r.duration).toString().padStart(6)}ms | ${r.iterations.toString().padStart(2)} iters | RMSE: ${r.rmse.toFixed(6)}`);
      } else {
        console.log(`❌ ${r.dataset.padEnd(20)} | ${r.error}`);
      }
    });
  }

  // Overall statistics
  const successful = results.filter(r => r.success);
  const failed = results.filter(r => !r.success);

  console.log('\n' + '═'.repeat(80));
  console.log('OVERALL RESULTS:');
  console.log('─'.repeat(80));
  console.log(`Total Datasets:  ${results.length}`);
  console.log(`✅ Successful:   ${successful.length}`);
  console.log(`❌ Failed:       ${failed.length}`);
  console.log(`Success Rate:   ${((successful.length / results.length) * 100).toFixed(1)}%`);

  if (successful.length > 0) {
    const avgDuration = successful.reduce((sum, r) => sum + r.duration, 0) / successful.length;
    const avgRMSE = successful.reduce((sum, r) => sum + r.rmse, 0) / successful.length;
    const totalPoints = successful.reduce((sum, r) => sum + r.sourcePoints, 0);

    console.log(`\nAverage Duration: ${Math.round(avgDuration)}ms`);
    console.log(`Average RMSE:     ${avgRMSE.toFixed(6)}`);
    console.log(`Total Points:     ${totalPoints.toLocaleString()}`);
  }

  // Save results to JSON
  const outputPath = path.resolve(__dirname, '../reports/all_datasets_validation.json');

  // Ensure reports directory exists
  const reportsDir = path.dirname(outputPath);
  if (!fs.existsSync(reportsDir)) {
    fs.mkdirSync(reportsDir, { recursive: true });
  }

  fs.writeFileSync(outputPath, JSON.stringify(results, null, 2));
  console.log(`\n📄 Results saved to: ${outputPath}`);

  console.log('\n' + '═'.repeat(80));

  // Exit with error if any tests failed
  if (failed.length > 0) {
    console.log('\n⚠️  Some tests failed. See details above.');
    process.exit(1);
  } else {
    console.log('\n🎉 All tests passed!');
    process.exit(0);
  }
}

// Run tests
runAllTests().catch(error => {
  console.error('Fatal error:', error);
  process.exit(1);
});
