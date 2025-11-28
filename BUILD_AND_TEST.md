# Build and Test Guide

Quick reference for building and testing both Python and TypeScript implementations.

---

## Python Implementation

### Prerequisites
```bash
Python 3.10 or higher
pip (Python package manager)
```

### Setup & Build

```bash
# Navigate to repository root
cd CascadedPointCloudFit

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install package in development mode
pip install -e .

# Or install with development dependencies
pip install -r requirements-dev.txt
```

### Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ -v --cov=cascaded_fit --cov-report=html

# Run only unit tests
pytest tests/unit/ -v

# Run only integration tests
pytest tests/integration/ -v

# Run specific test file
pytest tests/unit/test_registration.py -v
```

### Expected Results
```
Tests:     116 PASSED, 1 KNOWN ISSUE, 8 SKIPPED
Coverage:  88% (874 statements, 108 missing)
Duration:  ~2 seconds
```

### Usage Examples

```bash
# CLI usage
python -m cascaded_fit.cli source.ply target.ply --visualize

# Start REST API
python -m cascaded_fit.api.app

# Python API
python
>>> from cascaded_fit.fitters.cascaded_fitter import CascadedFitter
>>> fitter = CascadedFitter()
>>> result = fitter.run('source.ply', 'target.ply')
```

---

## TypeScript Implementation

### Prerequisites
```bash
Node.js 14.0.0 or higher
npm (Node package manager)
```

### Setup & Build

```bash
# Navigate to TypeScript directory
cd typescript

# Install dependencies
npm install

# Build the project
npm run build
```

### Run Tests

```bash
# Run all tests (82 tests)
npm test

# Run tests in watch mode
npm run test:watch

# Run with coverage report
npm run test:coverage

# Run specific test category
npx vitest run tests/unit/
npx vitest run tests/integration/
npx vitest run tests/e2e/
npx vitest run tests/performance/

# Run specific test file
npx vitest run tests/core/RegistrationAlgorithms.test.ts
```

### Expected Results
```
Test Files:  11 passed (11)
Tests:       82 passed (82)
Duration:    ~90 seconds
Pass Rate:   100%

Test Breakdown:
- Unit tests:         35 passing
- Integration tests:  13 passing
- E2E tests:          9 passing
- Performance tests:  14 passing
```

### Lint and Format

```bash
# Run ESLint
npm run lint

# Run Prettier formatting
npm run format

# Build for production
npm run build
```

### Usage Examples

```bash
# CLI usage
npm run cli source.ply target.ply

# Start REST API server
npm start

# Validate external test data
npm run validate:external
```

### Library Usage (TypeScript)

```typescript
import {
  PointCloudReader,
  RegistrationAlgorithms
} from 'cascaded-point-cloud-fit-ts';

// Load and register
const source = await PointCloudReader.loadFromFile('source.ply');
const target = await PointCloudReader.loadFromFile('target.ply');
const result = RegistrationAlgorithms.register(source, target);
```

---

## Continuous Integration

### Automated Checks
Both implementations run tests automatically on:
- Pull requests
- Commits to main
- Pre-publish hooks (TypeScript)

### Pre-commit Hooks (TypeScript)
```bash
# TypeScript has husky pre-commit hooks
# Runs automatically on git commit:
- ESLint --fix
- Prettier --write
```

---

## Performance Benchmarks

### Python
```bash
# Generate test data
python scripts/generate_test_data.py

# Time a specific dataset
time python -m cascaded_fit.cli test_data/unit_111/UNIT_111_Closed_J1.ply \
                                  test_data/unit_111/UNIT_111_Open_J1.ply
# Expected: < 1 second for UNIT_111 (11K points)
```

### TypeScript
```bash
cd typescript

# Run performance benchmarks
npx vitest run tests/performance/

# Benchmark results:
# - PCA 1K points:     ~5ms
# - ICP 10K points:    ~117ms
# - Full pipeline 10K: ~48ms
# - UNIT_111 (11K):    ~1.3s
```

---

## Troubleshooting

### Python Issues

**Issue**: `ModuleNotFoundError: No module named 'cascaded_fit'`
```bash
# Solution: Install in development mode
pip install -e .
```

**Issue**: Tests fail with import errors
```bash
# Solution: Ensure virtual environment is activated
# Windows: venv\Scripts\activate
# Linux/macOS: source venv/bin/activate
```

**Issue**: `open3d` installation fails
```bash
# Solution: Install build tools
# Windows: Install Visual Studio Build Tools
# Linux: sudo apt-get install build-essential
# macOS: xcode-select --install
```

### TypeScript Issues

**Issue**: `Cannot find module 'vitest'`
```bash
# Solution: Install dependencies
npm install
```

**Issue**: Tests timeout
```bash
# Solution: Increase timeout in vitest.config.ts
# Or run with --no-coverage for faster execution
npm test -- --no-coverage
```

**Issue**: Build fails with type errors
```bash
# Solution: Clean and rebuild
npm run clean
npm install
npm run build
```

**Issue**: ESLint/Prettier conflicts
```bash
# Solution: Run formatter first, then linter
npm run format
npm run lint
```

---

## Quick Reference

### Python Commands
```bash
pip install -e .              # Install package
pytest tests/ -v              # Run tests
pytest --cov=cascaded_fit     # Coverage
python -m cascaded_fit.cli    # CLI
python -m cascaded_fit.api.app # API
```

### TypeScript Commands
```bash
npm install                   # Install deps
npm run build                 # Build
npm test                      # Test all
npm run lint                  # Lint
npm run format                # Format
npm start                     # Start API
```

---

## Environment Setup

### Development Environment

**Recommended Setup**:
1. Python 3.10+ installed
2. Node.js 14+ installed
3. Git installed
4. Virtual environment for Python
5. IDE with TypeScript/Python support (VS Code recommended)

### VS Code Extensions (Recommended)
- Python
- Pylance
- TypeScript
- ESLint
- Prettier
- Vitest

### Configuration Files
- **Python**: `setup.py`, `pyproject.toml`, `requirements*.txt`
- **TypeScript**: `package.json`, `tsconfig.json`, `vitest.config.ts`

---

## Build Outputs

### Python
```
cascaded_fit/
├── __pycache__/          # Compiled bytecode
└── *.pyc                 # Compiled modules
```

### TypeScript
```
typescript/
├── dist/                 # Compiled JavaScript
│   ├── index.js
│   ├── index.d.ts       # Type definitions
│   └── [modules]
└── coverage/            # Coverage reports (after npm run test:coverage)
```

---

## Next Steps After Build

### Python
1. Run tests to verify: `pytest tests/ -v`
2. Try CLI: `python -m cascaded_fit.cli --help`
3. Start API: `python -m cascaded_fit.api.app`
4. Check coverage: `pytest --cov=cascaded_fit --cov-report=html`

### TypeScript
1. Run tests: `npm test`
2. Build library: `npm run build`
3. Try CLI: `npm run cli -- --help`
4. Start API: `npm start`
5. Check coverage: `npm run test:coverage`

---

## CI/CD Integration

### GitHub Actions (TypeScript)
```yaml
# .github/workflows/typescript-ci.yml already configured
# Runs on: push, pull_request
# Tests: npm test
# Build: npm run build
```

### Future: Docker
```bash
# Planned for future release
docker build -t cascaded-fit .
docker run -p 5000:5000 cascaded-fit
```

---

**Last Updated**: 2025-11-28
**Python Version**: 2.0.0
**TypeScript Version**: 0.1.0
