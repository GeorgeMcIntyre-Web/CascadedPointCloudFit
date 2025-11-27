/**
 * Command-line interface for CascadedPointCloudFit.
 * 
 * Ported from Python: cascaded_fit/cli/main.py
 */

import { Command } from 'commander';
import * as path from 'path';
import { PointCloudReader } from '../io/PointCloudReader';
import { RegistrationAlgorithms } from '../core/RegistrationAlgorithms';
import { MetricsCalculator } from '../core/MetricsCalculator';
import { TransformationUtils } from '../core/TransformationUtils';
import { Config } from '../utils/Config';
import { PointCloudHelper } from '../core/PointCloudHelper';

const program = new Command();

program
  .name('cascaded-pointcloud-fit')
  .description('Cascaded point cloud registration using PCA and ICP')
  .version('0.1.0');

program
  .argument('<source>', 'Source point cloud file (.csv or .ply)')
  .argument('<target>', 'Target point cloud file (.csv or .ply)')
  .option('--config <path>', 'Path to configuration file')
  .option('--rmse-threshold <number>', 'RMSE threshold for success', parseFloat)
  .option('--max-iterations <number>', 'Maximum ICP iterations', parseInt)
  .option('--tolerance <number>', 'Convergence tolerance', parseFloat)
  .option('--output <path>', 'Output file path (JSON, CSV, or text)')
  .option('--format <type>', 'Output format: json, csv, or text', 'text')
  .option('--verbose', 'Enable verbose logging', false)
  .action(async (source: string, target: string, options) => {
    try {
      // Load configuration if provided
      if (options.config) {
        const config = Config.getInstance();
        await config.load(options.config);
      }

      // Load point clouds
      console.log(`Loading source point cloud: ${source}`);
      const sourceCloud = await PointCloudReader.readPointCloudFile(source);
      console.log(`Loaded ${sourceCloud.count} points from source`);

      console.log(`Loading target point cloud: ${target}`);
      const targetCloud = await PointCloudReader.readPointCloudFile(target);
      console.log(`Loaded ${targetCloud.count} points from target`);

      // Align cloud sizes
      const [alignedSource, alignedTarget] = PointCloudReader.alignCloudSizes(
        sourceCloud,
        targetCloud
      );
      console.log(`Aligned to ${alignedSource.count} points each`);

      // Get configuration
      const rmseThreshold = options.rmseThreshold || 0.01;
      const maxIterations = options.maxIterations || 200;
      const tolerance = options.tolerance || 1e-7;

      // Run PCA registration
      console.log('Running PCA registration...');
      const initialTransform = RegistrationAlgorithms.pcaRegistration(
        alignedSource,
        alignedTarget
      );

      // Run ICP refinement
      console.log(`Running ICP refinement (max_iterations=${maxIterations}, tolerance=${tolerance})...`);
      const icpResult = RegistrationAlgorithms.icpRefinement(
        alignedSource,
        alignedTarget,
        initialTransform,
        maxIterations,
        tolerance
      );

      console.log(`ICP converged after ${icpResult.iterations} iterations (error=${icpResult.error.toFixed(6)})`);

      // Compute metrics
      console.log('Computing metrics...');
      const metrics = MetricsCalculator.computeMetrics(
        alignedSource,
        alignedTarget,
        icpResult.transform
      );

      // Output results
      const output = formatOutput(icpResult.transform, metrics, options.format);

      if (options.output) {
        const fs = await import('fs/promises');
        await fs.writeFile(options.output, output);
        console.log(`Results written to ${options.output}`);
      } else {
        console.log('\n' + output);
      }

      // Exit code based on success
      const isSuccess = metrics.rmse < rmseThreshold;
      if (!isSuccess) {
        console.error(`\nRegistration failed: RMSE ${metrics.rmse.toFixed(6)} exceeds threshold ${rmseThreshold}`);
        process.exit(1);
      }

      console.log(`\nRegistration successful! RMSE: ${metrics.rmse.toFixed(6)}`);
      process.exit(0);
    } catch (error) {
      console.error(`Error: ${error}`);
      process.exit(2);
    }
  });

function formatOutput(
  transform: any,
  metrics: any,
  format: string
): string {
  switch (format.toLowerCase()) {
    case 'json':
      return JSON.stringify({
        transformation: transform.matrix,
        metrics: {
          rmse: metrics.rmse,
          maxError: metrics.maxError,
          meanError: metrics.meanError,
          medianError: metrics.medianError
        }
      }, null, 2);

    case 'csv':
      return TransformationUtils.arrayToCSVString(transform);

    case 'text':
    default:
      const transformStr = TransformationUtils.arrayToCSVString(transform);
      return `Transformation Matrix:
${transformStr}

Metrics:
  RMSE: ${metrics.rmse.toFixed(6)}
  Max Error: ${metrics.maxError.toFixed(6)}
  Mean Error: ${metrics.meanError.toFixed(6)}
  Median Error: ${metrics.medianError.toFixed(6)}`;
  }
}

program.parse();

