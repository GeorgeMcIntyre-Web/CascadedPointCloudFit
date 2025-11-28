/**
 * Debug script for PinFails2 dataset failure
 */

import * as path from 'path';
import { PointCloudReader } from '../src/io/PointCloudReader';
import { RegistrationAlgorithms } from '../src/core/RegistrationAlgorithms';

async function debugPinFails2() {
  const sourcePath = path.resolve(__dirname, '../../test_data/external/PinFails2/file1.ply');
  const targetPath = path.resolve(__dirname, '../../test_data/external/PinFails2/file2.ply');

  console.log('═══════════════════════════════════════');
  console.log('  PinFails2 Debug Analysis');
  console.log('═══════════════════════════════════════\n');

  // Load point clouds
  console.log('📂 Loading point clouds...');
  const source = await PointCloudReader.readPointCloudFile(sourcePath);
  const target = await PointCloudReader.readPointCloudFile(targetPath);

  console.log(`Source: ${source.count.toLocaleString()} points`);
  console.log(`Target: ${target.count.toLocaleString()} points`);

  // Check for NaN or Infinity values
  console.log('\n🔍 Checking for invalid values...');
  let sourceNaN = 0;
  let sourceInf = 0;
  for (let i = 0; i < source.count; i++) {
    const idx = i * 3;
    if (isNaN(source.points[idx]) || isNaN(source.points[idx + 1]) || isNaN(source.points[idx + 2])) {
      sourceNaN++;
    }
    if (!isFinite(source.points[idx]) || !isFinite(source.points[idx + 1]) || !isFinite(source.points[idx + 2])) {
      sourceInf++;
    }
  }

  let targetNaN = 0;
  let targetInf = 0;
  for (let i = 0; i < target.count; i++) {
    const idx = i * 3;
    if (isNaN(target.points[idx]) || isNaN(target.points[idx + 1]) || isNaN(target.points[idx + 2])) {
      targetNaN++;
    }
    if (!isFinite(target.points[idx]) || !isFinite(target.points[idx + 1]) || !isFinite(target.points[idx + 2])) {
      targetInf++;
    }
  }

  console.log(`Source: ${sourceNaN} NaN points, ${sourceInf} Inf points`);
  console.log(`Target: ${targetNaN} NaN points, ${targetInf} Inf points`);

  // Compute bounds
  console.log('\n📏 Computing bounds...');
  let sourceMinX = Infinity, sourceMaxX = -Infinity;
  let sourceMinY = Infinity, sourceMaxY = -Infinity;
  let sourceMinZ = Infinity, sourceMaxZ = -Infinity;

  for (let i = 0; i < source.count; i++) {
    const idx = i * 3;
    const x = source.points[idx];
    const y = source.points[idx + 1];
    const z = source.points[idx + 2];

    if (isFinite(x)) {
      sourceMinX = Math.min(sourceMinX, x);
      sourceMaxX = Math.max(sourceMaxX, x);
    }
    if (isFinite(y)) {
      sourceMinY = Math.min(sourceMinY, y);
      sourceMaxY = Math.max(sourceMaxY, y);
    }
    if (isFinite(z)) {
      sourceMinZ = Math.min(sourceMinZ, z);
      sourceMaxZ = Math.max(sourceMaxZ, z);
    }
  }

  let targetMinX = Infinity, targetMaxX = -Infinity;
  let targetMinY = Infinity, targetMaxY = -Infinity;
  let targetMinZ = Infinity, targetMaxZ = -Infinity;

  for (let i = 0; i < target.count; i++) {
    const idx = i * 3;
    const x = target.points[idx];
    const y = target.points[idx + 1];
    const z = target.points[idx + 2];

    if (isFinite(x)) {
      targetMinX = Math.min(targetMinX, x);
      targetMaxX = Math.max(targetMaxX, x);
    }
    if (isFinite(y)) {
      targetMinY = Math.min(targetMinY, y);
      targetMaxY = Math.max(targetMaxY, y);
    }
    if (isFinite(z)) {
      targetMinZ = Math.min(targetMinZ, z);
      targetMaxZ = Math.max(targetMaxZ, z);
    }
  }

  console.log('Source bounds:');
  console.log(`  X: ${sourceMinX.toFixed(2)} to ${sourceMaxX.toFixed(2)}`);
  console.log(`  Y: ${sourceMinY.toFixed(2)} to ${sourceMaxY.toFixed(2)}`);
  console.log(`  Z: ${sourceMinZ.toFixed(2)} to ${sourceMaxZ.toFixed(2)}`);

  console.log('Target bounds:');
  console.log(`  X: ${targetMinX.toFixed(2)} to ${targetMaxX.toFixed(2)}`);
  console.log(`  Y: ${targetMinY.toFixed(2)} to ${targetMaxY.toFixed(2)}`);
  console.log(`  Z: ${targetMinZ.toFixed(2)} to ${targetMaxZ.toFixed(2)}`);

  // Check overlap
  const xOverlap = Math.max(0, Math.min(sourceMaxX, targetMaxX) - Math.max(sourceMinX, targetMinX));
  const yOverlap = Math.max(0, Math.min(sourceMaxY, targetMaxY) - Math.max(sourceMinY, targetMinY));
  const zOverlap = Math.max(0, Math.min(sourceMaxZ, targetMaxZ) - Math.max(sourceMinZ, targetMinZ));

  console.log('\n📊 Bounding box overlap:');
  console.log(`  X overlap: ${xOverlap.toFixed(2)}`);
  console.log(`  Y overlap: ${yOverlap.toFixed(2)}`);
  console.log(`  Z overlap: ${zOverlap.toFixed(2)}`);

  // Align cloud sizes
  console.log('\n⚙️  Aligning cloud sizes...');
  const [alignedSource, alignedTarget] = PointCloudReader.alignCloudSizes(source, target);
  console.log(`After alignment: ${alignedSource.count} vs ${alignedTarget.count}`);

  // Check first few points of aligned source
  console.log('First 3 aligned source points:');
  for (let i = 0; i < Math.min(3, alignedSource.count); i++) {
    const idx = i * 3;
    console.log(`  Point ${i}: (${alignedSource.points[idx].toFixed(2)}, ${alignedSource.points[idx+1].toFixed(2)}, ${alignedSource.points[idx+2].toFixed(2)})`);
  }

  // Try PCA registration
  console.log('\n🔄 Attempting PCA registration...');
  try {
    const pcaTransform = RegistrationAlgorithms.pcaRegistration(alignedSource, alignedTarget);
    console.log('✅ PCA succeeded');
    console.log('PCA Transform matrix:');
    console.log(pcaTransform.matrix.map(row =>
      row.map(v => v.toFixed(4)).join('  ')
    ).join('\n'));

    // Try ICP without RANSAC
    console.log('\n🔄 Attempting ICP refinement (without RANSAC)...');
    try {
      const result = RegistrationAlgorithms.icpRefinement(
        alignedSource,
        alignedTarget,
        pcaTransform,
        500, // Increased max iterations for translation-only refinement
        1e-9, // Tighter tolerance for better convergence
        false // No RANSAC
      );
      console.log('✅ ICP succeeded!');
      console.log(`Iterations: ${result.iterations}`);
      console.log(`Error: ${result.error.toFixed(6)}`);
    } catch (icpError) {
      console.log('❌ ICP failed:',icpError instanceof Error ? icpError.message : String(icpError));
      if (icpError instanceof Error && icpError.stack) {
        // Only show first few lines of stack
        const stackLines = icpError.stack.split('\n').slice(0, 5);
        console.log('Stack:', stackLines.join('\n'));
      }
    }

    // Try ICP with RANSAC
    console.log('\n🔄 Attempting ICP refinement (with RANSAC)...');
    try {
      const result = RegistrationAlgorithms.icpRefinement(
        alignedSource,
        alignedTarget,
        pcaTransform,
        500, // Increased max iterations for translation-only refinement
        1e-9, // Tighter tolerance for better convergence
        true, // Enable RANSAC
        {
          maxIterations: 200,
          inlierThreshold: 0.01,
          sampleSize: Math.min(100, Math.max(20, Math.floor(alignedSource.count * 0.002)))
        }
      );
      console.log('✅ ICP with RANSAC succeeded!');
      console.log(`Iterations: ${result.iterations}`);
      console.log(`Error: ${result.error.toFixed(6)}`);
    } catch (icpError) {
      console.log('❌ ICP with RANSAC failed:',icpError instanceof Error ? icpError.message : String(icpError));
      if (icpError instanceof Error && icpError.stack) {
        // Only show first few lines of stack
        const stackLines = icpError.stack.split('\n').slice(0, 5);
        console.log('Stack:', stackLines.join('\n'));
      }
    }

  } catch (pcaError) {
    console.log('❌ PCA failed:', pcaError instanceof Error ? pcaError.message : String(pcaError));
    console.log('Stack:', pcaError instanceof Error ? pcaError.stack : '');
  }

  console.log('\n═══════════════════════════════════════');
}

debugPinFails2().catch(error => {
  console.error('Fatal error:', error);
  process.exit(1);
});
