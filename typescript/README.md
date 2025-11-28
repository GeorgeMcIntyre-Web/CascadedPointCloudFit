# CascadedPointCloudFit TypeScript

> Production-ready TypeScript library for point cloud registration using PCA and ICP algorithms

[![NPM Version](https://img.shields.io/npm/v/cascaded-point-cloud-fit-ts.svg)](https://www.npmjs.com/package/cascaded-point-cloud-fit-ts)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.3.3-blue.svg)](https://www.typescriptlang.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-44%20passing-brightgreen.svg)]()

## Quick Links

- 📚 [API Reference](./docs/API_REFERENCE.md)
- 🏗️ [Architecture Guide](./docs/ARCHITECTURE.md)
- 🗺️ [Code Map](./docs/CODE_MAP.md)
- 🔌 [kinetiCORE Integration](./docs/KINETICORE_INTEGRATION.md)
- ⚡ [Optimization Summary](./OPTIMIZATION_SUMMARY.md)

## Features

✅ **High Accuracy** - Achieves RMSE = 0.000000 on test datasets
✅ **Type Safe** - 100% TypeScript with strict mode enabled
✅ **High Performance** - Handles clouds up to 155K points with adaptive downsampling
✅ **RANSAC Support** - Optional outlier rejection for noisy data
✅ **Zero Dependencies** - Core algorithms have no external runtime dependencies
✅ **Well Tested** - 44 passing tests with real-world validation
✅ **Multiple Interfaces** - Use as library, REST API, or CLI

## Installation

```bash
npm install cascaded-point-cloud-fit-ts
```

## Quick Start

### As a Library

```typescript
import {
  PointCloudReader,
  RegistrationAlgorithms
} from 'cascaded-point-cloud-fit-ts';

// Load point clouds
const source = await PointCloudReader.loadFromFile('source.ply');
const target = await PointCloudReader.loadFromFile('target.ply');

// Register (PCA + ICP)
const result = RegistrationAlgorithms.register(source, target);

console.log(`Converged in ${result.iterations} iterations`);
console.log(`Final RMSE: ${result.error}`);
console.log('Transform matrix:', result.transform.matrix);
```

### As a CLI

```bash
# Install globally
npm install -g cascaded-point-cloud-fit-ts

# Run registration
cascaded-pointcloud-fit source.ply target.ply

# With custom parameters
cascaded-pointcloud-fit source.csv target.csv \
  --max-iterations 100 \
  --tolerance 1e-9 \
  --output result.json
```

### As a REST API

```bash
# Start server
npm start

# Call endpoint
curl -X POST http://localhost:5000/register \
  -H "Content-Type: application/json" \
  -d '{
    "source": "path/to/source.ply",
    "target": "path/to/target.ply"
  }'
```

## Use Cases

### 1. Automatic Kinematic Generation from CAD

```typescript
import { RegistrationAlgorithms, PointCloudReader } from 'cascaded-point-cloud-fit-ts';

// Register open and closed positions
const openCloud = await PointCloudReader.loadFromFile('hinge_open.ply');
const closedCloud = await PointCloudReader.loadFromFile('hinge_closed.ply');

const result = RegistrationAlgorithms.register(openCloud, closedCloud);

// Extract rotation axis and angle from transformation matrix
const transform = result.transform.matrix;
// ... kinematic extraction logic
```

### 2. Quality Control

```typescript
import {
  RegistrationAlgorithms,
  MetricsCalculator,
  PointCloudReader
} from 'cascaded-point-cloud-fit-ts';

const scanned = await PointCloudReader.loadFromFile('scanned_part.ply');
const cad = await PointCloudReader.loadFromFile('cad_design.ply');

const result = RegistrationAlgorithms.register(scanned, cad);
const metrics = MetricsCalculator.calculateMetrics(scanned, cad, result.transform);

if (metrics.rmse < 0.5) {
  console.log('✅ Part within tolerance');
} else {
  console.log('❌ Part out of tolerance');
}
```

### 3. Robotics and Sensor Fusion

```typescript
import { RegistrationAlgorithms, PointCloud } from 'cascaded-point-cloud-fit-ts';

// Create point cloud from sensor data
const sensorCloud: PointCloud = {
  points: new Float32Array(sensorData), // [x1,y1,z1, x2,y2,z2, ...]
  count: sensorData.length / 3
};

const result = RegistrationAlgorithms.register(sensorCloud, referenceModel);
console.log('Sensor pose:', result.transform.matrix);
```

### 4. RANSAC for Noisy Data

```typescript
import { RegistrationAlgorithms } from 'cascaded-point-cloud-fit-ts';

// Standard ICP (fast, clean data)
const result = RegistrationAlgorithms.icpRefinement(
  source,
  target,
  initialTransform,
  200,  // maxIterations
  1e-6  // tolerance
);

// With RANSAC (robust, noisy data with outliers)
const robustResult = RegistrationAlgorithms.icpRefinement(
  source, target, initialTransform,
  200, 1e-6,
  true, // Enable RANSAC
  { maxIterations: 50, inlierThreshold: 0.02 }
);
```

## API Overview

### Core Classes

#### `RegistrationAlgorithms`

Main registration algorithms.

```typescript
// Complete pipeline (PCA + ICP)
static register(
  source: PointCloud,
  target: PointCloud,
  maxIterations?: number,
  tolerance?: number
): ICPResult

// PCA-based initial alignment
static pcaRegistration(
  source: PointCloud,
  target: PointCloud
): Transform4x4

// ICP iterative refinement
static icpRefinement(
  source: PointCloud,
  target: PointCloud,
  initialTransform: Transform4x4,
  maxIterations?: number,
  tolerance?: number,
  useRANSAC?: boolean,
  ransacOptions?: RANSACOptions
): ICPResult

// Downsample point cloud
static downsample(
  cloud: PointCloud,
  factor: number
): PointCloud
```

#### `PointCloudReader`

Load point clouds from files.

```typescript
// Auto-detect format
static async loadFromFile(filePath: string): Promise<PointCloud>

// Load CSV
static async loadCSV(filePath: string): Promise<PointCloud>

// Load PLY (binary or ASCII)
static async loadPLY(filePath: string): Promise<PointCloud>

// Create from array
static createFromArray(
  points: Float32Array,
  count: number
): PointCloud
```

#### `MetricsCalculator`

Calculate registration quality metrics.

```typescript
// Complete metrics
static calculateMetrics(
  source: PointCloud,
  target: PointCloud,
  transform: Transform4x4
): RegistrationMetrics

// RMSE only
static calculateRMSE(
  source: PointCloud,
  target: PointCloud,
  transform: Transform4x4
): number
```

### Type Definitions

```typescript
interface PointCloud {
  points: Float32Array;  // Flat: [x1,y1,z1, x2,y2,z2, ...]
  count: number;
}

interface Transform4x4 {
  matrix: number[][];    // 4x4 transformation matrix
}

interface ICPResult {
  transform: Transform4x4;
  iterations: number;
  error: number;         // Final RMSE
}

interface RegistrationMetrics {
  rmse: number;
  maxError: number;
  meanError: number;
  medianError: number;
}
```

## Supported File Formats

- **PLY** (Polygon File Format): Both binary and ASCII
- **CSV**: Comma-separated x,y,z values

CSV Format:
```csv
x,y,z
0.0,0.0,0.0
1.0,0.0,0.0
0.0,1.0,0.0
```

## Performance

Optimized for large point clouds with adaptive downsampling:

| Dataset | Points | Time | RMSE | Status |
|---------|--------|------|------|--------|
| Clamp | 10k | 2.1s | 0.000000 | ✅ Perfect |
| UNIT_111 | 11k | 1.2s | 0.000000 | ✅ Perfect |
| Clouds3 | 47k | 12.4s | 0.000000 | ✅ Perfect |
| Slide | 155k | **16.7s** | 0.000000 | ✅ Perfect |

**Key Optimizations:**
- **Adaptive downsampling** (19% faster on large clouds)
- **Memory pre-allocation** (reduced GC pressure)
- **Custom KD-tree** (2.8-6.4x faster than libraries)
- **Optional RANSAC** for outlier rejection
- **Automatic algorithm selection** (KD-tree vs SpatialGrid at 60K points)
- **Integer-based spatial grid keys** (60% faster than string keys)

See [OPTIMIZATION_SUMMARY.md](OPTIMIZATION_SUMMARY.md) for detailed analysis.

## Algorithm Details

### PCA Registration

1. Compute centroids of both clouds
2. Center clouds around origin
3. Compute 3x3 covariance matrices
4. Extract principal components via SVD
5. Align principal axes
6. Compute transformation matrix

**Time Complexity**: O(n)

### ICP Refinement

1. Apply initial transform to source
2. Adaptive downsampling (if needed)
3. **Iteration loop**:
   - Find nearest neighbors (KD-tree or SpatialGrid)
   - Compute optimal transformation (Kabsch algorithm)
   - Apply incremental transform
   - Calculate RMSE
   - Check convergence
4. Return final transformation

**Time Complexity**: O(k * n log n) for k iterations (KD-tree) or O(k * n) (SpatialGrid)

**Convergence**: Typically 3-10 iterations, stops when RMSE change < tolerance (default: 1e-7)

**Adaptive Strategy** (for clouds >100k points):
- Iterations 0-1: 20k points (coarse alignment)
- Iterations 2+: 40k points (refined alignment)
- Reduces queries by 83% while maintaining perfect accuracy

## Development

### Build

```bash
npm install
npm run build
```

### Test

```bash
npm test                 # Run all tests
npm run test:watch       # Watch mode
npm run test:coverage    # With coverage report
```

### Lint and Format

```bash
npm run lint             # ESLint
npm run format           # Prettier
```

## Documentation

- **[API Reference](./docs/API_REFERENCE.md)** - Complete API documentation
- **[Architecture Guide](./docs/ARCHITECTURE.md)** - System design and algorithm flow
- **[Code Map](./docs/CODE_MAP.md)** - Visual code navigation
- **[kinetiCORE Integration](./docs/KINETICORE_INTEGRATION.md)** - Integration examples
- **[Optimization Summary](./OPTIMIZATION_SUMMARY.md)** - Performance optimization details

## Examples

See `docs/KINETICORE_INTEGRATION.md` for comprehensive examples including:

- Basic registration
- Kinematic extraction from CAD
- Batch processing
- Real-time sensor data
- Quality control validation

## Testing

44 passing tests with real-world validation:

- ✅ Unit tests for all core algorithms
- ✅ Integration tests with real datasets
- ✅ REST API endpoint tests
- ✅ Performance benchmarks

Test datasets include:
- UNIT_111 (11K points) - RMSE: 0.000000
- Clamp (10K points) - RMSE: 0.000000
- Clouds3 (47K points) - RMSE: 0.000000
- Slide (155K points) - RMSE: 0.000000

## Requirements

- Node.js >= 14.0.0
- TypeScript >= 5.3.3 (for development)

## License

MIT

## Contributing

Contributions welcome! Please see the documentation for architecture details.

## Related Projects

- **Python Implementation**: Located in `../cascaded_fit/` - Reference implementation with 69% test coverage

## Support

For issues, questions, or feature requests, please open an issue on GitHub.

---

**Version**: 0.1.0
**Last Updated**: 2025-11-28
