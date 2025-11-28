# Quick Start Guide

Get up and running with CascadedPointCloudFit in 5 minutes.

---

## Python (5 minutes)

### 1. Install
```bash
# Clone and navigate
git clone https://github.com/GeorgeMcIntyre-Web/CascadedPointCloudFit.git
cd CascadedPointCloudFit

# Setup virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/macOS

# Install
pip install -e .
```

### 2. Test
```bash
pytest tests/ -v
# Expected: 116 PASSED ✅
```

### 3. Use
```bash
# CLI
python -m cascaded_fit.cli test_data/unit_111/UNIT_111_Closed_J1.ply \
                             test_data/unit_111/UNIT_111_Open_J1.ply

# Python API
python
>>> from cascaded_fit.fitters.cascaded_fitter import CascadedFitter
>>> fitter = CascadedFitter()
>>> result = fitter.run('test_data/unit_111/UNIT_111_Closed_J1.ply',
...                      'test_data/unit_111/UNIT_111_Open_J1.ply')
>>> print(f"RMSE: {result['inlier_rmse']:.6f}")
```

---

## TypeScript (5 minutes)

### 1. Install
```bash
# Navigate to TypeScript
cd typescript

# Install dependencies
npm install
```

### 2. Build & Test
```bash
# Build
npm run build

# Test
npm test
# Expected: 82 PASSED ✅
```

### 3. Use
```typescript
// TypeScript/JavaScript
import {
  PointCloudReader,
  RegistrationAlgorithms
} from 'cascaded-point-cloud-fit-ts';

const source = await PointCloudReader.loadFromFile('source.ply');
const target = await PointCloudReader.loadFromFile('target.ply');
const result = RegistrationAlgorithms.register(source, target);

console.log(`RMSE: ${result.error}`);
```

```bash
# CLI
npm run cli -- ../test_data/unit_111/UNIT_111_Closed_J1.ply \
               ../test_data/unit_111/UNIT_111_Open_J1.ply
```

---

## Verification

### Check Everything Works

**Python**:
```bash
# All tests pass
pytest tests/ -v
# Result: 116 PASSED ✅

# CLI works
python -m cascaded_fit.cli --help
# Shows usage ✅
```

**TypeScript**:
```bash
cd typescript

# All tests pass
npm test
# Result: 82 PASSED ✅

# Build successful
npm run build
# No errors ✅
```

---

## Common First Commands

### Python
```bash
# See all CLI options
python -m cascaded_fit.cli --help

# Run with visualization
python -m cascaded_fit.cli source.ply target.ply --visualize

# Save to JSON
python -m cascaded_fit.cli source.ply target.ply -o result.json --format json

# Start API server
python -m cascaded_fit.api.app
```

### TypeScript
```bash
# Run tests with coverage
npm run test:coverage

# Lint code
npm run lint

# Format code
npm run format

# Start API server
npm start
```

---

## Next Steps

1. **Read Documentation**
   - [Main README](README.md)
   - [Python Package](cascaded_fit/)
   - [TypeScript Docs](typescript/README.md)

2. **Explore Examples**
   - [kinetiCORE Integration](typescript/docs/KINETICORE_INTEGRATION.md)
   - [Test Data](test_data/README.md)

3. **Check Performance**
   - [Optimization Summary](typescript/docs/OPTIMIZATION_SUMMARY.md)
   - [Performance Benchmarks](typescript/tests/performance/)

4. **Build Something**
   - See [CONTRIBUTING.md](CONTRIBUTING.md)
   - Check [BUILD_AND_TEST.md](BUILD_AND_TEST.md)

---

## Troubleshooting

**Python not found?**
```bash
python --version
# If not found, install from python.org
```

**Node/npm not found?**
```bash
node --version
# If not found, install from nodejs.org
```

**Virtual environment issues?**
```bash
# Deactivate and recreate
deactivate
rm -rf venv
python -m venv venv
venv\Scripts\activate
pip install -e .
```

**TypeScript build fails?**
```bash
# Clean and reinstall
rm -rf node_modules dist
npm install
npm run build
```

---

## Success Criteria ✅

You're all set if:
- ✅ Python tests pass (116/116)
- ✅ TypeScript tests pass (82/82)
- ✅ CLI commands work
- ✅ Can import libraries

**Time to completion**: ~5 minutes per implementation

---

**Need Help?** See [BUILD_AND_TEST.md](BUILD_AND_TEST.md) for detailed instructions.
