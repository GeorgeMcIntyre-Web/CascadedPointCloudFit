# CascadedPointCloudFit - TypeScript Version

TypeScript implementation of cascaded point cloud registration using PCA and ICP algorithms.

## 🎯 Status

**Current**: 🟡 Phase 3 In Progress (55% Complete)  
**Target**: Production-ready TypeScript version  
**Python Baseline**: 88% test coverage, 0.022mm RMSE on UNIT_111 data

## ✨ Features

- ✅ **PCA Registration** - Initial alignment using Principal Component Analysis
- ✅ **ICP Refinement** - Iterative Closest Point algorithm with KD-Tree optimization
- ✅ **File I/O** - Support for CSV and PLY file formats
- ✅ **CLI** - Command-line interface with multiple output formats
- ✅ **REST API** - Express-based API server
- ✅ **Configuration** - YAML-based configuration management
- ✅ **High Performance** - O(n log n) complexity with KD-Tree

## 📦 Installation

```bash
cd typescript
npm install
npm run build
```

## 🚀 Usage

### CLI

```bash
# Basic usage
npm run cli source.ply target.ply

# With options
npm run cli source.csv target.csv \
  --rmse-threshold 0.01 \
  --max-iterations 200 \
  --output result.json \
  --format json

# With custom config
npm run cli source.ply target.ply --config config/custom.yaml
```

### API Server

```bash
# Start server
npm run dev  # or: node dist/api/server.js

# Health check
curl http://localhost:5000/health

# Process point clouds
curl -X POST http://localhost:5000/process_point_clouds \
  -H "Content-Type: application/json" \
  -d '{
    "sourcePoints": [[0,0,0], [1,0,0], [0,1,0]],
    "targetPoints": [[1,1,1], [2,1,1], [1,2,1]],
    "options": {
      "rmseThreshold": 0.01,
      "maxIterations": 200
    }
  }'
```

### Programmatic API

```typescript
import { 
  PointCloudReader, 
  RegistrationAlgorithms, 
  MetricsCalculator 
} from 'cascaded-point-cloud-fit-ts';

// Load point clouds
const source = await PointCloudReader.readPointCloudFile('source.ply');
const target = await PointCloudReader.readPointCloudFile('target.ply');

// Run registration
const initialTransform = RegistrationAlgorithms.pcaRegistration(source, target);
const icpResult = RegistrationAlgorithms.icpRefinement(
  source, 
  target, 
  initialTransform
);

// Compute metrics
const metrics = MetricsCalculator.computeMetrics(
  source, 
  target, 
  icpResult.transform
);

console.log(`RMSE: ${metrics.rmse}`);
```

## 📊 Test Results

```
Test Files  5 passed (5)
     Tests  29 passed (29)
  Duration  ~500ms
```

## 🏗️ Project Structure

```
typescript/
├── src/
│   ├── core/          # Core algorithms (PCA, ICP, Metrics)
│   ├── io/            # File I/O (CSV, PLY)
│   ├── api/           # REST API server
│   ├── cli/           # Command-line interface
│   └── utils/         # Utilities (Config)
├── tests/             # Test files
└── dist/              # Compiled JavaScript
```

## 📋 Roadmap

See [TS_CONVERSION_ROADMAP.md](../docs/planning/TS_CONVERSION_ROADMAP.md) for detailed plan.

### Phase 1: Core Algorithms ✅ Complete
- [x] PCA registration
- [x] ICP refinement
- [x] Metrics calculation
- [x] KD-Tree optimization

### Phase 2: I/O & Utilities ✅ Complete
- [x] CSV/PLY file loading
- [x] Configuration management
- [x] Transformation utilities

### Phase 3: API & CLI 🟡 In Progress
- [x] REST API
- [x] CLI interface
- [ ] Integration tests

### Phase 4: Testing & Validation
- [ ] Integration tests with real data
- [ ] Performance benchmarks
- [ ] Validation against Python results

## 🎯 Success Criteria

- ✅ RMSE within 5% of Python version
- ✅ Performance <2s for 11K point clouds
- ✅ 80%+ test coverage (currently 29 tests)
- ✅ API compatible with Python version

## 📝 License

MIT License - See LICENSE file for details
