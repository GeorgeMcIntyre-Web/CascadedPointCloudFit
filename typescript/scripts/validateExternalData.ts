/**
 * Validate registration performance on external test datasets.
 */

import * as path from 'path';
import * as fs from 'fs/promises';
import { existsSync } from 'fs';
import { PointCloudReader } from '../src/io/PointCloudReader';
import { RegistrationAlgorithms } from '../src/core/RegistrationAlgorithms';
import { MetricsCalculator } from '../src/core/MetricsCalculator';

interface DatasetCase {
  name: string;
  source: string;
  target: string;
}

interface ValidationResult {
  name: string;
  sourcePoints?: number;
  targetPoints?: number;
  alignedPoints?: number;
  iterations?: number;
  rmse?: number;
  maxError?: number;
  meanError?: number;
  medianError?: number;
  durationMs?: number;
  loadTimeMs?: number;
  alignTimeMs?: number;
  pcaTimeMs?: number;
  icpTimeMs?: number;
  error?: string;
  updatedAt?: string;
}

const DATA_ROOT = path.resolve(__dirname, '../../test_data/external');

const DATASETS: DatasetCase[] = [
  { name: 'Clamp', source: 'Clamp1.ply', target: 'Clamp2.ply' },
  { name: 'Slide', source: 'Slide1.ply', target: 'Slide2.ply' },
  {
    name: 'Clouds3',
    source: 'Clouds3/016ZF-20137361-670B-109R_CI00_M2.ply',
    target: 'Clouds3/016ZF-20137361-670B-109R_CI00_O2.ply',
  },
  {
    name: 'Fails4',
    source: 'Fails4/016ZF-20137361-670B-108_CI00_M1.ply',
    target: 'Fails4/016ZF-20137361-670B-108_CI00_O1.ply',
  },
  {
    name: 'IcpFails-A',
    source: 'IcpFails/016ZF-20137361-670B-103R_CI00_M3.ply',
    target: 'IcpFails/016ZF-20137361-670B-103R_CI00_O3.ply',
  },
  {
    name: 'IcpFails-B',
    source: 'IcpFails/M.ply',
    target: 'IcpFails/O.ply',
  },
  {
    name: 'PinFails1',
    source: 'PinFails1/016ZF-20137366-370-103-R_CI00_M.ply',
    target: 'PinFails1/016ZF-20137366-370-103-R_CI00_O.ply',
  },
  {
    name: 'PinFails2',
    source: 'PinFails2/file1.ply',
    target: 'PinFails2/file2.ply',
  },
];

async function runDataset(dataset: DatasetCase): Promise<ValidationResult> {
  const sourcePath = path.join(DATA_ROOT, dataset.source);
  const targetPath = path.join(DATA_ROOT, dataset.target);

  if (!existsSync(sourcePath) || !existsSync(targetPath)) {
    return {
      name: dataset.name,
      error: `Missing files (source: ${existsSync(sourcePath)}, target: ${existsSync(targetPath)})`,
    };
  }

  try {
    const start = Date.now();

    const loadStart = Date.now();
    const source = await PointCloudReader.readPointCloudFile(sourcePath);
    const target = await PointCloudReader.readPointCloudFile(targetPath);
    const loadTime = Date.now() - loadStart;

    const alignStart = Date.now();
    const [alignedSource, alignedTarget] = PointCloudReader.alignCloudSizes(source, target);
    const alignTime = Date.now() - alignStart;

    const pcaStart = Date.now();
    const initialTransform = RegistrationAlgorithms.pcaRegistration(alignedSource, alignedTarget);
    const pcaTime = Date.now() - pcaStart;

    const icpStart = Date.now();
    const icpResult = RegistrationAlgorithms.icpRefinement(
      alignedSource,
      alignedTarget,
      initialTransform,
      200,
      1e-6
    );
    const icpTime = Date.now() - icpStart;

    const metrics = MetricsCalculator.computeMetrics(alignedSource, alignedTarget, icpResult.transform);

    const duration = Date.now() - start;

    return {
      name: dataset.name,
      sourcePoints: source.count,
      targetPoints: target.count,
      alignedPoints: alignedSource.count,
      iterations: icpResult.iterations,
      rmse: metrics.rmse,
      maxError: metrics.maxError,
      meanError: metrics.meanError,
      medianError: metrics.medianError,
      durationMs: duration,
      loadTimeMs: loadTime,
      alignTimeMs: alignTime,
      pcaTimeMs: pcaTime,
      icpTimeMs: icpTime,
    };
  } catch (error: any) {
    return {
      name: dataset.name,
      error: error?.message ?? String(error),
    };
  }
}

async function main() {
  const args = process.argv.slice(2);
  const selectedNames = args.map((arg) => arg.toLowerCase());
  const selectedDatasets =
    selectedNames.length === 0
      ? DATASETS
      : DATASETS.filter((dataset) => selectedNames.includes(dataset.name.toLowerCase()));

  const missingNames = selectedNames.filter(
    (name) => !DATASETS.some((dataset) => dataset.name.toLowerCase() === name)
  );

  if (missingNames.length > 0) {
    console.error('Unknown dataset name(s):', missingNames.join(', '));
    console.error('Available datasets:', DATASETS.map((d) => d.name).join(', '));
    process.exit(1);
  }

  console.log('Validating external datasets located in', DATA_ROOT);
  if (selectedNames.length > 0) {
    console.log('Datasets selected:', selectedDatasets.map((d) => d.name).join(', '));
  }

  const results: ValidationResult[] = [];

  for (const dataset of selectedDatasets) {
    console.log(`\n▶ Running ${dataset.name}...`);
    const result = await runDataset(dataset);
    if (result.error) {
      console.error(`  ✘ Failed: ${result.error}`);
    } else {
      console.log(
        `  ✓ RMSE=${result.rmse?.toFixed(6)} | Points=${result.alignedPoints} | Iterations=${result.iterations} | Duration=${result.durationMs}ms`
      );
    }
    results.push(result);
  }

  const summaryPath = path.resolve(__dirname, '../reports');
  await fs.mkdir(summaryPath, { recursive: true });
  const outputFile = path.join(summaryPath, 'external_validation.json');

  let existingResults: ValidationResult[] = [];
  if (existsSync(outputFile)) {
    try {
      const existingContent = await fs.readFile(outputFile, 'utf-8');
      existingResults = JSON.parse(existingContent) as ValidationResult[];
    } catch (error) {
      console.warn('Could not parse existing validation report, overwriting...');
    }
  }

  const mergedMap = new Map<string, ValidationResult>();
  for (const existing of existingResults) {
    mergedMap.set(existing.name, existing);
  }
  for (const result of results) {
    mergedMap.set(result.name, { ...result, updatedAt: new Date().toISOString() });
  }

  const mergedResults = Array.from(mergedMap.values()).sort((a, b) => a.name.localeCompare(b.name));

  await fs.writeFile(outputFile, JSON.stringify(mergedResults, null, 2), 'utf-8');
  console.log('\nResults written to', outputFile);
}

main().catch((error) => {
  console.error('Validation script failed', error);
  process.exitCode = 1;
});

