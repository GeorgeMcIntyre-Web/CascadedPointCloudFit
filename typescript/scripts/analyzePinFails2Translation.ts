/**
 * Analyze PinFails2 to validate translation hypothesis
 *
 * User hypothesis:
 * - 8951 vs 7181 points (~20% missing geometry)
 * - Pure translational offset (~50mm)
 * - Along specific axis
 */

import * as path from 'path';
import { PointCloudReader } from '../src/io/PointCloudReader';
import { PointCloudHelper } from '../src/core/PointCloudHelper';

interface BoundingBox {
  minX: number; maxX: number;
  minY: number; maxY: number;
  minZ: number; maxZ: number;
}

function computeBounds(cloud: { points: Float32Array; count: number }): BoundingBox {
  let minX = Infinity, maxX = -Infinity;
  let minY = Infinity, maxY = -Infinity;
  let minZ = Infinity, maxZ = -Infinity;

  for (let i = 0; i < cloud.count; i++) {
    const idx = i * 3;
    const x = cloud.points[idx];
    const y = cloud.points[idx + 1];
    const z = cloud.points[idx + 2];

    if (x < minX) minX = x;
    if (x > maxX) maxX = x;
    if (y < minY) minY = y;
    if (y > maxY) maxY = y;
    if (z < minZ) minZ = z;
    if (z > maxZ) maxZ = z;
  }

  return { minX, maxX, minY, maxY, minZ, maxZ };
}

async function analyzePinFails2() {
  console.log('═══════════════════════════════════════');
  console.log('  PinFails2 Translation Analysis');
  console.log('═══════════════════════════════════════\n');

  // Load point clouds
  const sourcePath = path.resolve(__dirname, '../../test_data/external/PinFails2/file1.ply');
  const targetPath = path.resolve(__dirname, '../../test_data/external/PinFails2/file2.ply');

  const source = await PointCloudReader.readPointCloudFile(sourcePath);
  const target = await PointCloudReader.readPointCloudFile(targetPath);

  console.log('📊 Point Cloud Info:');
  console.log(`   Source: ${source.count.toLocaleString()} points`);
  console.log(`   Target: ${target.count.toLocaleString()} points`);
  console.log(`   Missing: ${Math.abs(source.count - target.count).toLocaleString()} points (${(Math.abs(source.count - target.count) / Math.max(source.count, target.count) * 100).toFixed(1)}%)\n`);

  // Compute centroids
  const sourceCentroid = PointCloudHelper.computeCentroid(source);
  const targetCentroid = PointCloudHelper.computeCentroid(target);

  console.log('🎯 Centroids:');
  console.log(`   Source: (${sourceCentroid.x.toFixed(2)}, ${sourceCentroid.y.toFixed(2)}, ${sourceCentroid.z.toFixed(2)})`);
  console.log(`   Target: (${targetCentroid.x.toFixed(2)}, ${targetCentroid.y.toFixed(2)}, ${targetCentroid.z.toFixed(2)})\n`);

  // Compute centroid difference (translation vector)
  const tx = targetCentroid.x - sourceCentroid.x;
  const ty = targetCentroid.y - sourceCentroid.y;
  const tz = targetCentroid.z - sourceCentroid.z;
  const magnitude = Math.sqrt(tx * tx + ty * ty + tz * tz);

  console.log('📏 Translation Vector (Target - Source):');
  console.log(`   ΔX = ${tx.toFixed(3)}mm`);
  console.log(`   ΔY = ${ty.toFixed(3)}mm`);
  console.log(`   ΔZ = ${tz.toFixed(3)}mm`);
  console.log(`   Magnitude = ${magnitude.toFixed(3)}mm\n`);

  // Identify primary axis
  const absX = Math.abs(tx);
  const absY = Math.abs(ty);
  const absZ = Math.abs(tz);
  const maxAxis = Math.max(absX, absY, absZ);
  let primaryAxis = 'X';
  if (absY === maxAxis) primaryAxis = 'Y';
  if (absZ === maxAxis) primaryAxis = 'Z';

  console.log('🧭 Primary Axis:');
  console.log(`   ${primaryAxis}-axis (${maxAxis.toFixed(3)}mm)`);
  console.log(`   Is pure ${primaryAxis}-translation: ${maxAxis / magnitude > 0.95 ? 'YES ✓' : 'NO ✗'}\n`);

  // Compute bounding boxes
  const sourceBounds = computeBounds(source);
  const targetBounds = computeBounds(target);

  console.log('📦 Bounding Boxes:');
  console.log('   Source:');
  console.log(`     X: [${sourceBounds.minX.toFixed(2)}, ${sourceBounds.maxX.toFixed(2)}] (range: ${(sourceBounds.maxX - sourceBounds.minX).toFixed(2)})`);
  console.log(`     Y: [${sourceBounds.minY.toFixed(2)}, ${sourceBounds.maxY.toFixed(2)}] (range: ${(sourceBounds.maxY - sourceBounds.minY).toFixed(2)})`);
  console.log(`     Z: [${sourceBounds.minZ.toFixed(2)}, ${sourceBounds.maxZ.toFixed(2)}] (range: ${(sourceBounds.maxZ - sourceBounds.minZ).toFixed(2)})`);
  console.log('   Target:');
  console.log(`     X: [${targetBounds.minX.toFixed(2)}, ${targetBounds.maxX.toFixed(2)}] (range: ${(targetBounds.maxX - targetBounds.minX).toFixed(2)})`);
  console.log(`     Y: [${targetBounds.minY.toFixed(2)}, ${targetBounds.maxY.toFixed(2)}] (range: ${(targetBounds.maxY - targetBounds.minY).toFixed(2)})`);
  console.log(`     Z: [${targetBounds.minZ.toFixed(2)}, ${targetBounds.maxZ.toFixed(2)}] (range: ${(targetBounds.maxZ - targetBounds.minZ).toFixed(2)})\n`);

  // Compute overlap
  const overlapX = Math.max(0, Math.min(sourceBounds.maxX, targetBounds.maxX) - Math.max(sourceBounds.minX, targetBounds.minX));
  const overlapY = Math.max(0, Math.min(sourceBounds.maxY, targetBounds.maxY) - Math.max(sourceBounds.minY, targetBounds.minY));
  const overlapZ = Math.max(0, Math.min(sourceBounds.maxZ, targetBounds.maxZ) - Math.max(sourceBounds.minZ, targetBounds.minZ));

  const sourceVolume = (sourceBounds.maxX - sourceBounds.minX) * (sourceBounds.maxY - sourceBounds.minY) * (sourceBounds.maxZ - sourceBounds.minZ);
  const overlapVolume = overlapX * overlapY * overlapZ;
  const overlapPercent = (overlapVolume / sourceVolume) * 100;

  console.log('🔍 Overlap Analysis:');
  console.log(`   X overlap: ${overlapX.toFixed(2)}mm`);
  console.log(`   Y overlap: ${overlapY.toFixed(2)}mm`);
  console.log(`   Z overlap: ${overlapZ.toFixed(2)}mm`);
  console.log(`   Volume overlap: ${overlapPercent.toFixed(1)}%\n`);

  // Hypothesis validation
  console.log('✅ Hypothesis Validation:');
  console.log(`   User claim: "~50mm translation"`);
  console.log(`   Actual magnitude: ${magnitude.toFixed(2)}mm`);
  console.log(`   Match: ${Math.abs(magnitude - 50) < 10 ? 'YES ✓' : 'NO ✗ (off by ' + Math.abs(magnitude - 50).toFixed(1) + 'mm)'}\n`);

  console.log(`   User claim: "Pure translational (no rotation)"`);
  console.log(`   Pure ${primaryAxis}-axis: ${maxAxis / magnitude > 0.95 ? 'YES ✓' : 'NO ✗'}`);
  console.log(`   If YES: Rotation matrix should be IDENTITY\n`);

  console.log(`   User claim: "~20% missing geometry"`);
  console.log(`   Actual missing: ${(Math.abs(source.count - target.count) / Math.max(source.count, target.count) * 100).toFixed(1)}%`);
  console.log(`   Match: ${Math.abs(Math.abs(source.count - target.count) / Math.max(source.count, target.count) * 100 - 20) < 5 ? 'YES ✓' : 'NO ✗'}\n`);

  // Recommendation
  console.log('💡 Recommendation:');
  if (maxAxis / magnitude > 0.95) {
    console.log(`   ✓ Use TRANSLATION-ONLY registration`);
    console.log(`   ✓ Set initial transform: R = Identity, t = [${tx.toFixed(1)}, ${ty.toFixed(1)}, ${tz.toFixed(1)}]`);
    console.log(`   ✓ ICP should refine to RMSE < 1mm in <10 iterations`);
  } else {
    console.log(`   ! Complex transformation detected`);
    console.log(`   ! Use full 6-DOF registration (rotation + translation)`);
  }

  if (overlapPercent < 60) {
    console.log(`   ⚠ Low overlap (${overlapPercent.toFixed(1)}%) - RANSAC recommended`);
  }

  console.log('\n═══════════════════════════════════════\n');
}

analyzePinFails2().catch(console.error);
