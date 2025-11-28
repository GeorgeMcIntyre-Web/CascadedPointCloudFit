# Code Map - Visual Navigation Guide

> **Purpose**: Visual map of code dependencies and relationships for AI agents navigating the codebase.

## Module Dependency Graph

```
┌─────────────────────────────────────────────────────────────────┐
│                         index.ts (Entry Point)                  │
│              Exports all public APIs for library usage          │
└────────────┬────────────────────────────────────────────────────┘
             │
     ┌───────┴────────┬──────────────┬──────────────┬─────────────┐
     │                │              │              │             │
     ▼                ▼              ▼              ▼             ▼
┌─────────┐   ┌──────────────┐  ┌─────────┐  ┌──────────┐  ┌──────────┐
│  Types  │   │ Registration │  │   I/O   │  │  Utils   │  │   API    │
│ (core)  │   │  (core)      │  │         │  │          │  │          │
└─────────┘   └──────────────┘  └─────────┘  └──────────┘  └──────────┘
```

## Detailed Dependency Tree

```
src/
│
├── index.ts                              [ENTRY POINT]
│   └── Exports from:
│       ├── core/types.ts
│       ├── core/RegistrationAlgorithms.ts
│       ├── core/MetricsCalculator.ts
│       ├── core/KDTreeHelper.ts
│       ├── core/TransformationUtils.ts
│       ├── io/PointCloudReader.ts
│       ├── utils/Config.ts
│       └── api/server.ts
│
├── core/                                  [CORE ALGORITHMS]
│   │
│   ├── types.ts                          [NO DEPENDENCIES]
│   │   └── Defines: PointCloud, Point3D, Transform4x4, ICPResult, etc.
│   │
│   ├── RegistrationAlgorithms.ts         [MAIN ALGORITHM]
│   │   ├── Imports:
│   │   │   ├── types.ts → PointCloud, Transform4x4, ICPResult
│   │   │   ├── PointCloudHelper.ts → computeCentroid, applyTransform
│   │   │   ├── SVDHelper.ts → computeSVD3x3
│   │   │   ├── KDTreeHelper.ts → createKDTree, findNearestNeighbor
│   │   │   └── SpatialGrid.ts → SpatialGrid class
│   │   └── Exports:
│   │       ├── pcaRegistration()
│   │       ├── icpRefinement()
│   │       ├── register()
│   │       └── downsample()
│   │
│   ├── PointCloudHelper.ts               [UTILITIES]
│   │   ├── Imports:
│   │   │   ├── types.ts → PointCloud, Point3D, Transform4x4
│   │   │   └── TransformationUtils.ts → applyToPoint
│   │   └── Exports:
│   │       ├── computeCentroid()
│   │       ├── applyTransform()
│   │       ├── centerCloud()
│   │       ├── computeCovariance()
│   │       ├── toPoint3DArray()
│   │       └── fromPoint3DArray()
│   │
│   ├── KDTreeHelper.ts                   [NEAREST NEIGHBOR]
│   │   ├── Imports:
│   │   │   ├── types.ts → PointCloud, Point3D
│   │   │   └── kd-tree-javascript (external)
│   │   └── Exports:
│   │       ├── createKDTree()
│   │       ├── findNearestNeighbor()
│   │       └── findNearestNeighbors()
│   │
│   ├── SpatialGrid.ts                    [LARGE CLOUD OPTIMIZATION]
│   │   ├── Imports:
│   │   │   └── types.ts → Point3D
│   │   └── Exports:
│   │       └── SpatialGrid class
│   │           ├── constructor()
│   │           ├── findNearestNeighbor()
│   │           └── getCellPoints()
│   │
│   ├── MetricsCalculator.ts              [ERROR METRICS]
│   │   ├── Imports:
│   │   │   ├── types.ts → PointCloud, Transform4x4, RegistrationMetrics
│   │   │   └── PointCloudHelper.ts → applyTransform
│   │   └── Exports:
│   │       ├── calculateMetrics()
│   │       └── calculateRMSE()
│   │
│   ├── SVDHelper.ts                      [LINEAR ALGEBRA]
│   │   ├── Imports: (none - pure math)
│   │   └── Exports:
│   │       └── computeSVD3x3()
│   │
│   └── TransformationUtils.ts            [MATRIX OPERATIONS]
│       ├── Imports:
│       │   ├── types.ts → Transform4x4, Point3D
│       │   └── ml-matrix (external)
│       └── Exports:
│           ├── createIdentity()
│           ├── createTranslation()
│           ├── createRotation()
│           ├── multiplyTransforms()
│           ├── invertTransform()
│           └── applyToPoint()
│
├── io/                                   [FILE I/O]
│   │
│   └── PointCloudReader.ts
│       ├── Imports:
│       │   ├── types.ts → PointCloud
│       │   ├── papaparse (external) → CSV parsing
│       │   └── fs (node) → File reading
│       └── Exports:
│           ├── loadFromFile()
│           ├── loadCSV()
│           ├── loadPLY()
│           └── createFromArray()
│
├── utils/                                [CONFIGURATION]
│   │
│   └── Config.ts
│       ├── Imports:
│       │   ├── js-yaml (external)
│       │   └── fs (node)
│       └── Exports:
│           └── loadConfig()
│
├── api/                                  [REST API]
│   │
│   └── server.ts
│       ├── Imports:
│       │   ├── express (external)
│       │   ├── PointCloudReader
│       │   ├── RegistrationAlgorithms
│       │   └── MetricsCalculator
│       └── Exports:
│           └── startServer()
│
├── cli/                                  [COMMAND LINE]
│   │
│   └── index.ts
│       ├── Imports:
│       │   ├── commander (external)
│       │   ├── PointCloudReader
│       │   ├── RegistrationAlgorithms
│       │   └── MetricsCalculator
│       └── Exports: (none - runs directly)
│
└── bin/                                  [CLI ENTRY]
    │
    └── cli.ts
        ├── Shebang: #!/usr/bin/env node
        └── Imports:
            └── cli/index.ts
```

---

## Import Chains (Dependency Paths)

### Chain 1: Core Registration

```
User Code
  ↓ import
RegistrationAlgorithms
  ↓ uses
PointCloudHelper
  ↓ uses
TransformationUtils
  ↓ uses
types.ts
```

**File Reads**: 4 files (types → TransformationUtils → PointCloudHelper → RegistrationAlgorithms)

---

### Chain 2: Nearest Neighbor (Small Clouds)

```
RegistrationAlgorithms.icpRefinement()
  ↓ if cloud.count < 60000
KDTreeHelper.createKDTree()
  ↓ uses
kd-tree-javascript (external)
  ↓ returns
KDTree instance
  ↓ used by
RegistrationAlgorithms (findNearestNeighbor loop)
```

---

### Chain 3: Nearest Neighbor (Large Clouds)

```
RegistrationAlgorithms.icpRefinement()
  ↓ if cloud.count >= 60000
new SpatialGrid()
  ↓ builds grid
Integer-packed hash map
  ↓ used by
SpatialGrid.findNearestNeighbor()
  ↓ returns approximate neighbor
RegistrationAlgorithms continues
```

---

### Chain 4: File Loading

```
User Code
  ↓ import
PointCloudReader
  ↓ async loadFromFile()
File extension check (.csv or .ply)
  ↓ if .csv
loadCSV() → papaparse
  ↓ if .ply
loadPLY() → custom parser
  ↓ returns
PointCloud { points: Float32Array, count: number }
```

---

## Function Call Flow: Complete Registration

```
Step 1: Load Point Clouds
─────────────────────────
PointCloudReader.loadFromFile(sourcePath)
  ├─ Detect extension
  ├─ Read file content (fs.promises.readFile)
  ├─ Parse format (CSV: papaparse, PLY: custom)
  └─ Return PointCloud { points: Float32Array, count: number }

PointCloudReader.loadFromFile(targetPath)
  └─ [same as above]

Step 2: PCA Registration
─────────────────────────
RegistrationAlgorithms.pcaRegistration(source, target)
  ├─ PointCloudHelper.computeCentroid(source)
  │   └─ Sum all points, divide by count → Point3D
  ├─ PointCloudHelper.computeCentroid(target)
  ├─ PointCloudHelper.centerCloud(source)
  │   ├─ Subtract centroid from all points
  │   └─ Return { centered, centroid }
  ├─ PointCloudHelper.centerCloud(target)
  ├─ PointCloudHelper.computeCovariance(sourceCentered)
  │   └─ Compute 3x3 covariance matrix
  ├─ PointCloudHelper.computeCovariance(targetCentered)
  ├─ computeSVD3x3(sourceCov)
  │   └─ Return { U, S, V } for source
  ├─ computeSVD3x3(targetCov)
  │   └─ Return { U, S, V } for target
  ├─ Align principal axes: R = V_target * U_source^T
  ├─ Compute translation: t = centroid_target - R * centroid_source
  └─ Return Transform4x4 with [R | t]

Step 3: ICP Refinement
─────────────────────────
RegistrationAlgorithms.icpRefinement(source, target, pcaTransform)
  ├─ PointCloudHelper.applyTransform(source, pcaTransform)
  │   └─ Transform all source points
  ├─ Downsample if count > 30000
  │   ├─ downsample(source, factor)
  │   └─ downsample(target, factor)
  ├─ Choose nearest neighbor method:
  │   ├─ If count < 60000:
  │   │   └─ KDTreeHelper.createKDTree(target)
  │   │       └─ Iterative KD-tree construction
  │   └─ If count >= 60000:
  │       └─ new SpatialGrid(target.points, target.count, cellSize)
  │           └─ Build integer-packed grid
  │
  ├─ ITERATION LOOP (max 50 iterations):
  │   │
  │   ├─ For each source point:
  │   │   ├─ Find nearest neighbor in target
  │   │   │   ├─ If KDTree: tree.nearest(point, 1)
  │   │   │   └─ If SpatialGrid: grid.findNearestNeighbor(point)
  │   │   └─ Store correspondence
  │   │
  │   ├─ Compute optimal transform (Kabsch algorithm):
  │   │   ├─ Compute centroids of correspondences
  │   │   ├─ Center correspondences
  │   │   ├─ Compute cross-covariance: H = Σ(source_i * target_i^T)
  │   │   ├─ computeSVD3x3(H) → { U, S, V }
  │   │   ├─ Compute rotation: R = V * U^T
  │   │   ├─ Check determinant (ensure right-handed)
  │   │   ├─ Compute translation: t = centroid_target - R * centroid_source
  │   │   └─ Build Transform4x4
  │   │
  │   ├─ PointCloudHelper.applyTransform(source, incrementalTransform)
  │   │
  │   ├─ Calculate RMSE:
  │   │   ├─ For each correspondence pair:
  │   │   │   ├─ Compute distance
  │   │   │   └─ Sum squared distances
  │   │   └─ rmse = sqrt(sum / count)
  │   │
  │   ├─ Check convergence:
  │   │   └─ If |rmse - previousRMSE| < tolerance:
  │   │       └─ BREAK (converged)
  │   │
  │   └─ Update cumulative transform
  │
  └─ Return ICPResult { transform, iterations, error: rmse }

Step 4: Calculate Metrics (Optional)
─────────────────────────────────────
MetricsCalculator.calculateMetrics(source, target, finalTransform)
  ├─ PointCloudHelper.applyTransform(source, finalTransform)
  ├─ For each transformed source point:
  │   ├─ Find nearest in target (KDTree)
  │   └─ Compute distance
  ├─ Calculate statistics:
  │   ├─ RMSE = sqrt(Σ distances² / n)
  │   ├─ Max = max(distances)
  │   ├─ Mean = Σ distances / n
  │   └─ Median = median(distances)
  └─ Return RegistrationMetrics { rmse, maxError, meanError, medianError }
```

---

## File Relationships Matrix

| File | Imports From | Imported By | External Deps |
|------|-------------|-------------|---------------|
| **types.ts** | (none) | All core files | (none) |
| **SVDHelper.ts** | (none) | RegistrationAlgorithms | ml-matrix |
| **TransformationUtils.ts** | types.ts | PointCloudHelper, MetricsCalculator | ml-matrix |
| **PointCloudHelper.ts** | types.ts, TransformationUtils | RegistrationAlgorithms, MetricsCalculator | (none) |
| **KDTreeHelper.ts** | types.ts | RegistrationAlgorithms | kd-tree-javascript |
| **SpatialGrid.ts** | types.ts | RegistrationAlgorithms | (none) |
| **RegistrationAlgorithms.ts** | types.ts, PointCloudHelper, SVDHelper, KDTreeHelper, SpatialGrid | index.ts, api/server.ts, cli/index.ts | (none) |
| **MetricsCalculator.ts** | types.ts, PointCloudHelper | index.ts, api/server.ts, cli/index.ts | (none) |
| **PointCloudReader.ts** | types.ts | index.ts, api/server.ts, cli/index.ts | papaparse, fs |
| **Config.ts** | (none) | index.ts | js-yaml, fs |
| **server.ts** | PointCloudReader, RegistrationAlgorithms, MetricsCalculator | index.ts | express |
| **cli/index.ts** | PointCloudReader, RegistrationAlgorithms, MetricsCalculator | bin/cli.ts | commander |
| **index.ts** | All core, io, utils, api | (user code) | (none) |

---

## Critical Performance Paths

### Hot Path 1: ICP Iteration Loop

**Location**: `RegistrationAlgorithms.ts:285-365`

**Called**: 3-50 times per registration (typically 3-10)

**Operations**:
1. Nearest neighbor search (KDTree or SpatialGrid) - **O(n log n)** or **O(n)**
2. SVD computation - **O(1)** (3x3 matrix)
3. Transform application - **O(n)**

**Optimization**: Use SpatialGrid for n > 60K, downsample for n > 30K

---

### Hot Path 2: KDTree Construction

**Location**: `KDTreeHelper.ts:45-95`

**Called**: Once per registration (if cloud < 60K points)

**Time Complexity**: O(n log n)

**Critical Optimization**: Iterative construction (prevents stack overflow)

---

### Hot Path 3: SpatialGrid Nearest Neighbor

**Location**: `SpatialGrid.ts:115-160`

**Called**: n times per ICP iteration (for n source points)

**Time Complexity**: O(1) average, O(27) worst case (search 27 cells)

**Critical Optimization**: Integer key packing (10-bit per axis)

---

## Data Flow Diagram

```
┌──────────────┐
│  File System │
└──────┬───────┘
       │
       ▼
┌──────────────────┐
│ PointCloudReader │ → Float32Array
└──────┬───────────┘
       │
       ▼
┌─────────────────────────┐
│ RegistrationAlgorithms  │
│   .pcaRegistration()    │ → Transform4x4 (initial)
└──────┬──────────────────┘
       │
       ▼
┌─────────────────────────┐
│ RegistrationAlgorithms  │
│   .icpRefinement()      │ ─┐
└──────┬──────────────────┘  │
       │                      │
       │  ┌───────────────────┘
       │  │ (iteration loop)
       │  │
       │  ├─→ KDTreeHelper OR SpatialGrid (nearest neighbor)
       │  │
       │  ├─→ computeSVD3x3 (optimal transform)
       │  │
       │  └─→ PointCloudHelper.applyTransform (update)
       │
       ▼
┌─────────────────────────┐
│      ICPResult          │ → { transform, iterations, error }
└──────┬──────────────────┘
       │
       ▼
┌─────────────────────────┐
│  MetricsCalculator      │ → RegistrationMetrics
└─────────────────────────┘
```

---

## Key Algorithms: Line-by-Line Locations

### PCA Registration

| Step | File | Line Range | Description |
|------|------|------------|-------------|
| 1. Compute centroids | RegistrationAlgorithms.ts | 48-49 | `PointCloudHelper.computeCentroid()` |
| 2. Center clouds | RegistrationAlgorithms.ts | 52-58 | Subtract centroids |
| 3. Compute covariance | PointCloudHelper.ts | 75-95 | 3x3 covariance matrix |
| 4. SVD | SVDHelper.ts | 15-110 | Jacobi eigenvalue algorithm |
| 5. Align axes | RegistrationAlgorithms.ts | 92-98 | R = V_target * U_source^T |
| 6. Compute translation | RegistrationAlgorithms.ts | 102-108 | t = centroid_target - R * centroid_source |
| 7. Build transform | RegistrationAlgorithms.ts | 112-118 | 4x4 matrix [R \| t] |

---

### ICP Refinement

| Step | File | Line Range | Description |
|------|------|------------|-------------|
| 1. Apply initial transform | RegistrationAlgorithms.ts | 155-157 | Transform source with PCA result |
| 2. Adaptive downsampling | RegistrationAlgorithms.ts | 162-178 | If > 30K points, downsample |
| 3. Choose NN method | RegistrationAlgorithms.ts | 185-195 | KDTree vs SpatialGrid |
| 4. **ITERATION LOOP** | RegistrationAlgorithms.ts | 205-365 | Max 50 iterations |
| 4a. Find correspondences | RegistrationAlgorithms.ts | 215-245 | Nearest neighbor for each point |
| 4b. Compute centroids | RegistrationAlgorithms.ts | 250-258 | Of correspondence pairs |
| 4c. Center correspondences | RegistrationAlgorithms.ts | 262-272 | Subtract centroids |
| 4d. Cross-covariance | RegistrationAlgorithms.ts | 275-283 | H = Σ(source_i * target_i^T) |
| 4e. SVD | SVDHelper.ts | 15-110 | Decompose H |
| 4f. Extract rotation | RegistrationAlgorithms.ts | 288-295 | R = V * U^T, check det |
| 4g. Compute translation | RegistrationAlgorithms.ts | 298-302 | t = centroid_target - R * centroid_source |
| 4h. Apply transform | RegistrationAlgorithms.ts | 308-312 | Update source positions |
| 4i. Calculate RMSE | RegistrationAlgorithms.ts | 318-332 | Distance metric |
| 4j. Check convergence | RegistrationAlgorithms.ts | 338-345 | \|RMSE - prevRMSE\| < tolerance |
| 5. Return result | RegistrationAlgorithms.ts | 375-380 | ICPResult object |

---

## External Dependencies

| Package | Version | Used By | Purpose |
|---------|---------|---------|---------|
| **ml-matrix** | 6.10.4 | TransformationUtils, SVDHelper | Matrix operations (fallback for large matrices) |
| **kd-tree-javascript** | 1.0.3 | KDTreeHelper | KD-tree nearest neighbor |
| **papaparse** | 5.4.1 | PointCloudReader | CSV parsing |
| **js-yaml** | 4.1.1 | Config | YAML configuration |
| **express** | 4.18.2 | api/server.ts | REST API server |
| **commander** | 11.1.0 | cli/index.ts | CLI argument parsing |

---

## Entry Points for AI Integration

### 1. Library Import (Recommended)

```typescript
// Single import for all functionality
import {
  PointCloud,
  RegistrationAlgorithms,
  PointCloudReader,
  MetricsCalculator
} from 'cascaded-point-cloud-fit-ts';
```

**File**: `dist/index.js` (compiled from `src/index.ts`)

---

### 2. Direct Module Import (Advanced)

```typescript
// Import specific modules
import { RegistrationAlgorithms } from 'cascaded-point-cloud-fit-ts/dist/core/RegistrationAlgorithms';
import { PointCloudHelper } from 'cascaded-point-cloud-fit-ts/dist/core/PointCloudHelper';
```

---

### 3. REST API (Service)

**Entry**: `src/api/server.ts`

Start server and call via HTTP:
```bash
curl -X POST http://localhost:5000/register \
  -H "Content-Type: application/json" \
  -d '{"source": "source.ply", "target": "target.ply"}'
```

---

### 4. CLI (Command Line)

**Entry**: `src/bin/cli.ts`

Execute from shell:
```bash
cascaded-pointcloud-fit source.ply target.ply
```

---

## Quick Reference: Where to Find Things

| Task | File | Line |
|------|------|------|
| Type definitions | `src/core/types.ts` | 1-80 |
| Main registration function | `src/core/RegistrationAlgorithms.ts` | 400-415 |
| PCA algorithm | `src/core/RegistrationAlgorithms.ts` | 23-120 |
| ICP algorithm | `src/core/RegistrationAlgorithms.ts` | 135-385 |
| KDTree construction | `src/core/KDTreeHelper.ts` | 45-95 |
| SpatialGrid implementation | `src/core/SpatialGrid.ts` | 25-220 |
| Integer key packing | `src/core/SpatialGrid.ts` | 86-92 |
| SVD computation | `src/core/SVDHelper.ts` | 15-110 |
| Load CSV file | `src/io/PointCloudReader.ts` | 45-90 |
| Load PLY file | `src/io/PointCloudReader.ts` | 95-215 |
| Calculate RMSE | `src/core/MetricsCalculator.ts` | 75-105 |
| REST API endpoint | `src/api/server.ts` | 45-85 |
| CLI main function | `src/cli/index.ts` | 25-120 |

---

## Testing Locations

| Test Category | File | Tests | Coverage |
|---------------|------|-------|----------|
| Registration algorithms | `tests/core/RegistrationAlgorithms.test.ts` | 5 | Core logic |
| KDTree operations | `tests/core/KDTreeHelper.test.ts` | 4 | Nearest neighbor |
| Metrics calculation | `tests/core/MetricsCalculator.test.ts` | 3 | RMSE, errors |
| Matrix operations | `tests/core/TransformationUtils.test.ts` | 8 | Transforms |
| File I/O | `tests/io/PointCloudReader.test.ts` | 11 | CSV, PLY loading |
| Real-world data | `tests/integration/real-data.test.ts` | 3 | UNIT_111 dataset |
| REST API | `tests/integration/api.test.ts` | 4 | HTTP endpoints |
| Full pipeline | `tests/integration/registration.test.ts` | 6 | End-to-end |

---

**Last Updated**: 2025-11-27
**Version**: 0.1.0
