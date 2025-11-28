# API Reference - Complete TypeScript Interface

> **Purpose**: Complete API documentation for AI agents integrating CascadedPointCloudFit into other projects.

## Table of Contents

1. [Core Types](#core-types)
2. [RegistrationAlgorithms](#registrationalgorithms)
3. [PointCloudHelper](#pointcloudhelper)
4. [KDTreeHelper](#kdtreehelper)
5. [SpatialGrid](#spatialgrid)
6. [MetricsCalculator](#metricscalculator)
7. [TransformationUtils](#transformationutils)
8. [SVDHelper](#svdhelper)
9. [PointCloudReader](#pointcloudreader)
10. [Config](#config)
11. [REST API](#rest-api)
12. [CLI](#cli)

---

## Core Types

**Source**: `src/core/types.ts`

### `PointCloud`

Represents a point cloud using a flat Float32Array for performance.

```typescript
interface PointCloud {
  points: Float32Array;  // Flat array: [x1,y1,z1, x2,y2,z2, ...]
  count: number;         // Number of points (length / 3)
}
```

**Example**:
```typescript
const cloud: PointCloud = {
  points: new Float32Array([
    0, 0, 0,    // Point 1
    1, 0, 0,    // Point 2
    0, 1, 0,    // Point 3
  ]),
  count: 3
};

// Access point i: x=points[i*3], y=points[i*3+1], z=points[i*3+2]
```

---

### `Point3D`

Represents a single 3D point (used sparingly for API clarity).

```typescript
interface Point3D {
  x: number;
  y: number;
  z: number;
}
```

**Usage**: Only used when object form is more readable (KDTree results, individual points).

---

### `Transform4x4`

4x4 homogeneous transformation matrix.

```typescript
interface Transform4x4 {
  matrix: number[][];  // 4x4 array
}
```

**Example**:
```typescript
const identity: Transform4x4 = {
  matrix: [
    [1, 0, 0, 0],
    [0, 1, 0, 0],
    [0, 0, 1, 0],
    [0, 0, 0, 1]
  ]
};
```

**Matrix Layout**:
```
| R11  R12  R13  Tx |   R = 3x3 rotation matrix
| R21  R22  R23  Ty |   T = translation vector [Tx, Ty, Tz]
| R31  R32  R33  Tz |
|  0    0    0    1 |
```

---

### `ICPResult`

Result from ICP refinement.

```typescript
interface ICPResult {
  transform: Transform4x4;  // Final transformation
  iterations: number;       // Number of iterations to convergence
  error: number;            // Final RMSE
}
```

---

### `RegistrationMetrics`

Detailed error metrics for registration quality.

```typescript
interface RegistrationMetrics {
  rmse: number;        // Root mean square error
  maxError: number;    // Maximum point-to-point error
  meanError: number;   // Average error
  medianError: number; // Median error
}
```

---

## RegistrationAlgorithms

**Source**: `src/core/RegistrationAlgorithms.ts`

Main class for point cloud registration algorithms.

### Methods

#### `pcaRegistration`

Perform PCA-based initial alignment.

```typescript
static pcaRegistration(
  source: PointCloud,
  target: PointCloud
): Transform4x4
```

**Parameters**:
- `source`: Source point cloud (will be aligned to target)
- `target`: Target point cloud (reference)

**Returns**: 4x4 transformation matrix

**Throws**:
- `Error` if either cloud has fewer than 3 points

**Algorithm**:
1. Compute centroids
2. Center both clouds
3. Compute covariance matrices
4. Extract principal components via SVD
5. Align principal axes
6. Return transformation matrix

**Example**:
```typescript
import { RegistrationAlgorithms, PointCloudReader } from 'cascaded-point-cloud-fit-ts';

const source = await PointCloudReader.loadFromFile('source.ply');
const target = await PointCloudReader.loadFromFile('target.ply');

const initialTransform = RegistrationAlgorithms.pcaRegistration(source, target);
console.log('Initial alignment:', initialTransform);
```

**Performance**: O(n) for n points

**File Location**: `src/core/RegistrationAlgorithms.ts:23-120`

---

#### `icpRefinement`

Perform ICP (Iterative Closest Point) refinement.

```typescript
static icpRefinement(
  source: PointCloud,
  target: PointCloud,
  initialTransform: Transform4x4,
  maxIterations: number = 50,
  tolerance: number = 1e-7
): ICPResult
```

**Parameters**:
- `source`: Source point cloud
- `target`: Target point cloud
- `initialTransform`: Initial transformation (usually from PCA)
- `maxIterations`: Maximum iterations (default: 50)
- `tolerance`: Convergence threshold for RMSE change (default: 1e-7)

**Returns**: `ICPResult` with final transform, iteration count, and RMSE

**Algorithm**:
1. Apply initial transform to source
2. Adaptive downsampling (if >30K points)
3. **For each iteration**:
   - Find nearest neighbors (KDTree or SpatialGrid)
   - Compute optimal transformation via SVD
   - Apply incremental transform
   - Calculate RMSE
   - Check convergence
4. Return result

**Convergence**: Stops when RMSE change < tolerance or max iterations reached

**Example**:
```typescript
const initialTransform = RegistrationAlgorithms.pcaRegistration(source, target);
const result = RegistrationAlgorithms.icpRefinement(
  source,
  target,
  initialTransform,
  100,   // max iterations
  1e-9   // tight tolerance
);

console.log(`Converged in ${result.iterations} iterations`);
console.log(`Final RMSE: ${result.error}`);
```

**Performance**:
- Best case: O(k * n log n) for k iterations, n points (using KDTree)
- Large clouds: O(k * n) (using SpatialGrid)
- Typical: 3-10 iterations for convergence

**File Location**: `src/core/RegistrationAlgorithms.ts:135-385`

---

#### `register`

Complete registration pipeline (PCA + ICP).

```typescript
static register(
  source: PointCloud,
  target: PointCloud,
  maxIterations: number = 50,
  tolerance: number = 1e-7
): ICPResult
```

**Parameters**:
- `source`: Source point cloud
- `target`: Target point cloud
- `maxIterations`: Maximum ICP iterations (default: 50)
- `tolerance`: Convergence threshold (default: 1e-7)

**Returns**: `ICPResult` with final transform, iteration count, and RMSE

**Algorithm**:
1. PCA registration (initial alignment)
2. ICP refinement (iterative optimization)
3. Return result

**Example**:
```typescript
// Simplest usage - one line!
const result = RegistrationAlgorithms.register(source, target);
```

**This is the recommended method** for most use cases.

**Performance**: Same as `icpRefinement` (PCA is fast, ~O(n))

**File Location**: `src/core/RegistrationAlgorithms.ts:400-415`

---

#### `downsample`

Downsample a point cloud by a given factor.

```typescript
static downsample(
  cloud: PointCloud,
  factor: number
): PointCloud
```

**Parameters**:
- `cloud`: Input point cloud
- `factor`: Downsampling factor (e.g., 2 = keep every 2nd point)

**Returns**: New downsampled point cloud

**Example**:
```typescript
const downsampled = RegistrationAlgorithms.downsample(cloud, 4);
// If cloud had 40K points, downsampled has ~10K points
```

**Performance**: O(n / factor)

**File Location**: `src/core/RegistrationAlgorithms.ts:420-435`

---

## PointCloudHelper

**Source**: `src/core/PointCloudHelper.ts`

Utility functions for point cloud operations.

### Methods

#### `computeCentroid`

Calculate the centroid (center of mass) of a point cloud.

```typescript
static computeCentroid(cloud: PointCloud): Point3D
```

**Returns**: Point3D representing the centroid

**Example**:
```typescript
const centroid = PointCloudHelper.computeCentroid(cloud);
console.log(`Centroid: (${centroid.x}, ${centroid.y}, ${centroid.z})`);
```

**Performance**: O(n)

---

#### `applyTransform`

Apply a 4x4 transformation to a point cloud.

```typescript
static applyTransform(
  cloud: PointCloud,
  transform: Transform4x4
): PointCloud
```

**Returns**: New transformed point cloud (original unchanged)

**Example**:
```typescript
const transformed = PointCloudHelper.applyTransform(cloud, transform);
```

**Performance**: O(n)

---

#### `centerCloud`

Center a point cloud around the origin.

```typescript
static centerCloud(cloud: PointCloud): {
  centered: PointCloud;
  centroid: Point3D;
}
```

**Returns**: Object with centered cloud and original centroid

**Example**:
```typescript
const { centered, centroid } = PointCloudHelper.centerCloud(cloud);
```

**Performance**: O(n)

---

#### `computeCovariance`

Compute 3x3 covariance matrix of a centered point cloud.

```typescript
static computeCovariance(cloud: PointCloud): number[][]
```

**Returns**: 3x3 covariance matrix

**Note**: Cloud must be centered (mean = 0)

**Performance**: O(n)

---

#### `toPoint3DArray`

Convert PointCloud to Point3D array (use sparingly).

```typescript
static toPoint3DArray(cloud: PointCloud): Point3D[]
```

**Returns**: Array of Point3D objects

**Warning**: Creates many objects. Only use when necessary (e.g., visualization).

**Performance**: O(n) with object allocation overhead

---

#### `fromPoint3DArray`

Convert Point3D array to PointCloud.

```typescript
static fromPoint3DArray(points: Point3D[]): PointCloud
```

**Returns**: PointCloud with flat Float32Array

**Performance**: O(n)

---

## KDTreeHelper

**Source**: `src/core/KDTreeHelper.ts`

Optimized KD-tree construction and nearest neighbor search.

### Methods

#### `createKDTree`

Create a KD-tree from a point cloud (iterative construction).

```typescript
static createKDTree(cloud: PointCloud): KDTree
```

**Returns**: KDTree instance (from kd-tree-javascript library)

**Algorithm**: Iterative construction to prevent stack overflow

**Performance**: O(n log n) construction

**Example**:
```typescript
const tree = KDTreeHelper.createKDTree(cloud);
```

**File Location**: `src/core/KDTreeHelper.ts:25-95`

---

#### `findNearestNeighbor`

Find the nearest neighbor for a single point.

```typescript
static findNearestNeighbor(
  tree: KDTree,
  point: Point3D
): Point3D | null
```

**Returns**: Nearest neighbor or null if tree is empty

**Performance**: O(log n) average case

**Example**:
```typescript
const nearest = KDTreeHelper.findNearestNeighbor(tree, { x: 1, y: 2, z: 3 });
if (nearest) {
  console.log(`Nearest: (${nearest.x}, ${nearest.y}, ${nearest.z})`);
}
```

---

#### `findNearestNeighbors`

Find k nearest neighbors for multiple query points.

```typescript
static findNearestNeighbors(
  tree: KDTree,
  queryPoints: PointCloud,
  k: number = 1
): number[][]
```

**Returns**: Array of neighbor indices for each query point

**Performance**: O(m * k * log n) for m queries, k neighbors, n tree points

---

## SpatialGrid

**Source**: `src/core/SpatialGrid.ts`

Approximate nearest neighbor search for very large point clouds.

### Constructor

```typescript
constructor(
  points: Float32Array,
  count: number,
  cellSize: number = 0.1
)
```

**Parameters**:
- `points`: Flat Float32Array of points
- `count`: Number of points
- `cellSize`: Grid cell size (default: 0.1)

---

### Methods

#### `findNearestNeighbor`

Find approximate nearest neighbor.

```typescript
findNearestNeighbor(queryPoint: Point3D): Point3D | null
```

**Returns**: Nearest neighbor or null

**Algorithm**:
1. Hash query point to grid cell
2. Search current cell + 26 neighbors
3. Return closest point found

**Performance**: O(1) average case, O(n) worst case

**Trade-off**: Fast but approximate (good enough for ICP)

**Example**:
```typescript
const grid = new SpatialGrid(cloud.points, cloud.count, 0.1);
const nearest = grid.findNearestNeighbor({ x: 5, y: 10, z: 15 });
```

**File Location**: `src/core/SpatialGrid.ts:45-160`

---

#### `getCellPoints`

Get all points in a specific grid cell.

```typescript
getCellPoints(x: number, y: number, z: number): Point3D[]
```

**Returns**: Array of points in the cell

**Example**:
```typescript
const cellPoints = grid.getCellPoints(5, 10, 15);
console.log(`Cell has ${cellPoints.length} points`);
```

---

## MetricsCalculator

**Source**: `src/core/MetricsCalculator.ts`

Calculate registration quality metrics.

### Methods

#### `calculateMetrics`

Calculate complete registration metrics.

```typescript
static calculateMetrics(
  source: PointCloud,
  target: PointCloud,
  transform: Transform4x4
): RegistrationMetrics
```

**Returns**: Object with RMSE, max, mean, and median errors

**Example**:
```typescript
const metrics = MetricsCalculator.calculateMetrics(source, target, transform);
console.log(`RMSE: ${metrics.rmse}`);
console.log(`Max Error: ${metrics.maxError}`);
console.log(`Mean Error: ${metrics.meanError}`);
console.log(`Median Error: ${metrics.medianError}`);
```

**Performance**: O(n)

---

#### `calculateRMSE`

Calculate only RMSE (faster).

```typescript
static calculateRMSE(
  source: PointCloud,
  target: PointCloud,
  transform: Transform4x4
): number
```

**Returns**: RMSE value

**Performance**: O(n)

---

## TransformationUtils

**Source**: `src/core/TransformationUtils.ts`

Matrix transformation utilities.

### Methods

#### `createIdentity`

Create 4x4 identity matrix.

```typescript
static createIdentity(): Transform4x4
```

**Returns**: Identity transformation

---

#### `createTranslation`

Create translation matrix.

```typescript
static createTranslation(x: number, y: number, z: number): Transform4x4
```

**Example**:
```typescript
const T = TransformationUtils.createTranslation(10, 20, 30);
```

---

#### `createRotation`

Create rotation matrix from 3x3 rotation.

```typescript
static createRotation(R: number[][]): Transform4x4
```

**Parameters**: 3x3 rotation matrix

---

#### `multiplyTransforms`

Multiply two 4x4 transformation matrices.

```typescript
static multiplyTransforms(
  T1: Transform4x4,
  T2: Transform4x4
): Transform4x4
```

**Returns**: T1 * T2 (applied right-to-left: T2 first, then T1)

**Example**:
```typescript
const combined = TransformationUtils.multiplyTransforms(rotation, translation);
```

---

#### `invertTransform`

Compute inverse of a transformation matrix.

```typescript
static invertTransform(transform: Transform4x4): Transform4x4
```

**Returns**: Inverse transformation

**Note**: Uses closed-form inversion for rigid transforms (rotation + translation)

---

#### `applyToPoint`

Apply transformation to a single Point3D.

```typescript
static applyToPoint(point: Point3D, transform: Transform4x4): Point3D
```

**Returns**: Transformed point

**Example**:
```typescript
const transformed = TransformationUtils.applyToPoint(
  { x: 1, y: 2, z: 3 },
  transform
);
```

---

## SVDHelper

**Source**: `src/core/SVDHelper.ts`

Custom 3x3 Singular Value Decomposition.

### Functions

#### `computeSVD3x3`

Compute SVD of a 3x3 matrix.

```typescript
export function computeSVD3x3(A: number[][]): {
  U: number[][];  // Left singular vectors (3x3)
  S: number[];    // Singular values (length 3)
  V: number[][];  // Right singular vectors (3x3)
}
```

**Returns**: SVD decomposition where A = U * diag(S) * V^T

**Example**:
```typescript
import { computeSVD3x3 } from 'cascaded-point-cloud-fit-ts';

const A = [
  [1, 2, 3],
  [4, 5, 6],
  [7, 8, 9]
];

const { U, S, V } = computeSVD3x3(A);
console.log('Singular values:', S);
```

**Performance**: O(1) for 3x3 matrices (optimized Jacobi algorithm)

---

## PointCloudReader

**Source**: `src/io/PointCloudReader.ts`

Load point clouds from files.

### Methods

#### `loadFromFile`

Auto-detect format and load point cloud.

```typescript
static async loadFromFile(filePath: string): Promise<PointCloud>
```

**Supported Formats**: CSV, PLY (auto-detected by extension)

**Example**:
```typescript
const cloud = await PointCloudReader.loadFromFile('data/cloud.ply');
```

**Throws**: Error if file format is unsupported or file doesn't exist

---

#### `loadCSV`

Load CSV file (comma-separated x,y,z).

```typescript
static async loadCSV(filePath: string): Promise<PointCloud>
```

**CSV Format**:
```
x,y,z
0.0,0.0,0.0
1.0,0.0,0.0
0.0,1.0,0.0
```

**Example**:
```typescript
const cloud = await PointCloudReader.loadCSV('points.csv');
```

---

#### `loadPLY`

Load PLY file (binary or ASCII).

```typescript
static async loadPLY(filePath: string): Promise<PointCloud>
```

**Supports**: Both binary and ASCII PLY formats

**Example**:
```typescript
const cloud = await PointCloudReader.loadPLY('model.ply');
```

---

#### `createFromArray`

Create PointCloud from Float32Array.

```typescript
static createFromArray(
  points: Float32Array,
  count: number
): PointCloud
```

**Example**:
```typescript
const points = new Float32Array([0,0,0, 1,0,0, 0,1,0]);
const cloud = PointCloudReader.createFromArray(points, 3);
```

---

## Config

**Source**: `src/utils/Config.ts`

YAML configuration management.

### Methods

#### `loadConfig`

Load configuration from YAML file.

```typescript
static async loadConfig(configPath: string): Promise<ConfigData>
```

**Returns**: Configuration object

**Example**:
```typescript
const config = await Config.loadConfig('config/default.yaml');
console.log(`Max ICP iterations: ${config.icp.maxIterations}`);
```

**Default Config Location**: `C:\Users\George\source\repos\cursor\CascadedPointCloudFit\config\default.yaml`

---

## REST API

**Source**: `src/api/server.ts`

Express-based REST API for point cloud registration.

### Starting the Server

```bash
npm start
# Server listening on http://localhost:5000
```

Or programmatically:
```typescript
import { startServer } from 'cascaded-point-cloud-fit-ts';

const app = startServer(5000);
console.log('Server running on port 5000');
```

---

### Endpoints

#### `POST /register`

Register two point clouds.

**Request Body**:
```json
{
  "source": "path/to/source.ply",
  "target": "path/to/target.ply",
  "maxIterations": 50,
  "tolerance": 1e-7
}
```

**Response** (200 OK):
```json
{
  "transform": [
    [1, 0, 0, 0],
    [0, 1, 0, 0],
    [0, 0, 1, 0],
    [0, 0, 0, 1]
  ],
  "iterations": 3,
  "rmse": 0.000123,
  "maxError": 0.000456,
  "meanError": 0.000098,
  "medianError": 0.000087
}
```

**Error Response** (400 or 500):
```json
{
  "error": "Error message"
}
```

**cURL Example**:
```bash
curl -X POST http://localhost:5000/register \
  -H "Content-Type: application/json" \
  -d '{
    "source": "test_data/unit_111/source.ply",
    "target": "test_data/unit_111/target.ply"
  }'
```

---

#### `GET /health`

Health check endpoint.

**Response** (200 OK):
```json
{
  "status": "ok"
}
```

---

## CLI

**Source**: `src/cli/index.ts`, `src/bin/cli.ts`

Command-line interface for point cloud registration.

### Installation

```bash
npm install -g cascaded-point-cloud-fit-ts
```

### Usage

```bash
cascaded-pointcloud-fit <source> <target> [options]
```

**Arguments**:
- `source`: Path to source point cloud (CSV or PLY)
- `target`: Path to target point cloud (CSV or PLY)

**Options**:
- `--max-iterations <n>`: Maximum ICP iterations (default: 50)
- `--tolerance <n>`: Convergence tolerance (default: 1e-7)
- `--output <file>`: Save result to JSON file
- `--format <type>`: Output format: json|csv|text (default: text)

**Examples**:

```bash
# Basic usage
cascaded-pointcloud-fit source.ply target.ply

# Custom parameters
cascaded-pointcloud-fit source.csv target.csv \
  --max-iterations 100 \
  --tolerance 1e-9

# Save to file
cascaded-pointcloud-fit source.ply target.ply \
  --output result.json \
  --format json

# CSV output
cascaded-pointcloud-fit source.ply target.ply \
  --format csv > transform.csv
```

**Output Format (text)**:
```
Registration Complete
====================
Iterations: 3
RMSE: 0.000123
Max Error: 0.000456
Mean Error: 0.000098
Median Error: 0.000087

Transformation Matrix:
1.0000  0.0000  0.0000  0.0000
0.0000  1.0000  0.0000  0.0000
0.0000  0.0000  1.0000  0.0000
0.0000  0.0000  0.0000  1.0000
```

---

## Quick Integration Patterns

### Pattern 1: Simple Registration

```typescript
import { PointCloudReader, RegistrationAlgorithms } from 'cascaded-point-cloud-fit-ts';

async function registerClouds(sourcePath: string, targetPath: string) {
  const source = await PointCloudReader.loadFromFile(sourcePath);
  const target = await PointCloudReader.loadFromFile(targetPath);
  return RegistrationAlgorithms.register(source, target);
}

const result = await registerClouds('source.ply', 'target.ply');
console.log(`RMSE: ${result.error}`);
```

---

### Pattern 2: Custom Pipeline

```typescript
import {
  PointCloudReader,
  RegistrationAlgorithms,
  MetricsCalculator,
  PointCloudHelper
} from 'cascaded-point-cloud-fit-ts';

async function customPipeline(sourcePath: string, targetPath: string) {
  // Load
  const source = await PointCloudReader.loadFromFile(sourcePath);
  const target = await PointCloudReader.loadFromFile(targetPath);

  // PCA alignment
  const pcaTransform = RegistrationAlgorithms.pcaRegistration(source, target);

  // ICP with custom parameters
  const icpResult = RegistrationAlgorithms.icpRefinement(
    source,
    target,
    pcaTransform,
    100,   // max iterations
    1e-9   // tight tolerance
  );

  // Calculate detailed metrics
  const metrics = MetricsCalculator.calculateMetrics(
    source,
    target,
    icpResult.transform
  );

  // Apply transform to source
  const aligned = PointCloudHelper.applyTransform(source, icpResult.transform);

  return { result: icpResult, metrics, aligned };
}
```

---

### Pattern 3: Batch Processing

```typescript
import { PointCloudReader, RegistrationAlgorithms } from 'cascaded-point-cloud-fit-ts';
import { promises as fs } from 'fs';

async function batchRegister(pairs: Array<[string, string]>) {
  const results = [];

  for (const [sourcePath, targetPath] of pairs) {
    const source = await PointCloudReader.loadFromFile(sourcePath);
    const target = await PointCloudReader.loadFromFile(targetPath);
    const result = RegistrationAlgorithms.register(source, target);

    results.push({
      source: sourcePath,
      target: targetPath,
      ...result
    });
  }

  return results;
}

const pairs = [
  ['pair1_source.ply', 'pair1_target.ply'],
  ['pair2_source.ply', 'pair2_target.ply'],
];

const results = await batchRegister(pairs);
console.log(JSON.stringify(results, null, 2));
```

---

### Pattern 4: Real-Time Monitoring

```typescript
import {
  PointCloudReader,
  RegistrationAlgorithms,
  PointCloudHelper
} from 'cascaded-point-cloud-fit-ts';

async function registerWithProgress(sourcePath: string, targetPath: string) {
  console.log('Loading point clouds...');
  const source = await PointCloudReader.loadFromFile(sourcePath);
  const target = await PointCloudReader.loadFromFile(targetPath);
  console.log(`Loaded ${source.count} source points, ${target.count} target points`);

  console.log('Computing PCA alignment...');
  const pcaTransform = RegistrationAlgorithms.pcaRegistration(source, target);

  console.log('Running ICP refinement...');
  const startTime = Date.now();
  const result = RegistrationAlgorithms.icpRefinement(
    source,
    target,
    pcaTransform,
    50,
    1e-7
  );
  const elapsed = Date.now() - startTime;

  console.log(`Converged in ${result.iterations} iterations (${elapsed}ms)`);
  console.log(`Final RMSE: ${result.error}`);

  return result;
}
```

---

## Performance Guidelines

### Point Cloud Size Recommendations

| Points | Method | Expected Time | Notes |
|--------|--------|---------------|-------|
| < 10K | Standard ICP | <1s | Optimal performance |
| 10K-30K | Standard ICP | 1-3s | Good performance |
| 30K-60K | ICP + downsample | 3-6s | Adaptive downsampling |
| 60K-100K | SpatialGrid | 6-12s | Approximate but fast |
| 100K+ | SpatialGrid + downsample | 12-20s | Heavy downsampling |

### Optimization Tips

1. **Use downsampling for large clouds**:
   ```typescript
   if (source.count > 50000) {
     source = RegistrationAlgorithms.downsample(source, 2);
     target = RegistrationAlgorithms.downsample(target, 2);
   }
   ```

2. **Adjust tolerance for speed**:
   ```typescript
   // Faster (may stop early)
   const result = RegistrationAlgorithms.register(source, target, 50, 1e-5);

   // More precise (more iterations)
   const result = RegistrationAlgorithms.register(source, target, 100, 1e-9);
   ```

3. **Use PCA-only for rough alignment**:
   ```typescript
   const roughTransform = RegistrationAlgorithms.pcaRegistration(source, target);
   // Skip ICP if rough alignment is sufficient
   ```

---

**Last Updated**: 2025-11-27
**Version**: 0.1.0
