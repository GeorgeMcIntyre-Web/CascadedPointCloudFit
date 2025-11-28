# Quick Start Guide

## Python Version (Current - Working)

### Setup
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements-minimal.txt
```

### Run Tests
```bash
# Run comprehensive test suite
python test_registration.py

# Expected output:
# Open3D CascadedProcessor:    RMSE = N/A (did not converge)
# Custom ICP (shared):          RMSE = 0.022029
# Best direction (forward):     RMSE = 0.022029
```

### Run CLI
```bash
# Process two point clouds
python CascadedPointCloudFit.py "UNIT_111_Closed_J1.csv" "UNIT_111_Open_J1.csv" --rmse_threshold 1.0

# Expected output:
# RMS: 0.024742603883900
# Total Execution Time: ~0.08 seconds
```

### Run API Server
```bash
# Start Flask server
python app.py

# Server runs on http://localhost:5000
# POST to /process_point_clouds with JSON body
```

---

## TypeScript Version (Planned - Not Yet Implemented)

### Prerequisites
```bash
# Install Node.js 18+ and npm
# Verify: node -v && npm -v
```

### Setup (Future)
```bash
# Initialize project
npm init -y

# Install dependencies
npm install typescript @types/node ts-node
npm install ml-matrix ml-pca kd-tree-javascript papaparse three express commander

# Install dev dependencies
npm install --save-dev @types/express @types/papaparse @types/three vitest
```

### Project Structure (Future)
```
cascaded-point-cloud-fit-ts/
├── src/
│   ├── core/
│   │   ├── RegistrationAlgorithms.ts
│   │   ├── PointCloudHelper.ts
│   │   ├── ComputeMetrics.ts
│   │   └── types.ts
│   ├── api/
│   │   └── server.ts
│   └── cli/
│       └── index.ts
├── tests/
│   └── registration.test.ts
├── package.json
├── tsconfig.json
└── README.md
```

### Run (Future)
```bash
# Run tests
npm test

# Run CLI
npm run cli -- input1.csv input2.csv

# Run API server
npm start
```

---

## Key Files Reference

### Python Implementation
| File | Purpose | Status |
|------|---------|--------|
| [registration_algorithms.py](registration_algorithms.py) | Shared PCA/ICP algorithms | ✅ Working |
| [PointCloudHelper.py](PointCloudHelper.py) | File I/O, utilities | ✅ Enhanced |
| [IcpFitter.py](IcpFitter.py) | Open3D ICP wrapper | ✅ Bug fixed |
| [FgrFitter.py](FgrFitter.py) | Open3D FGR wrapper | ✅ Working |
| [CascadedFitter.py](CascadedFitter.py) | Pipeline orchestration | ✅ Working |
| [app.py](app.py) | Flask API server | ⚠️ Has duplication |
| [test_registration.py](test_registration.py) | Test suite | ✅ Working |

### Planning Documents
| File | Purpose |
|------|---------|
| [PROJECT_STATUS_SUMMARY.md](PROJECT_STATUS_SUMMARY.md) | Complete status overview |
| [TYPESCRIPT_CONVERSION_PLAN.md](TYPESCRIPT_CONVERSION_PLAN.md) | Detailed TS conversion plan |
| [REFACTORING_PLAN.md](REFACTORING_PLAN.md) | Python refactoring strategy |
| [QUICK_START.md](QUICK_START.md) | This file - quick reference |

---

## Decision Tree

```
Do you need web browser support?
├── YES → Go TypeScript
│   └── Timeline: 26-33 days
│   └── Performance: 2-3x slower (still <1sec)
│   └── Libraries: ml-matrix + kd-tree-javascript + three.js
│
└── NO → Consider your team
    ├── TypeScript team → Go TypeScript anyway
    │   └── Benefits: Unified stack, type safety
    │
    └── Python team → Stay Python
        └── Benefits: Faster, Open3D features, existing code
```

---

## Performance Targets

### Python (Current)
- ✅ Load 11K points: ~5ms
- ✅ Full ICP pipeline: ~100ms
- ✅ RMSE achieved: 0.022mm

### TypeScript (Target)
- 🎯 Load 11K points: <20ms
- 🎯 Full ICP pipeline: <300ms
- 🎯 RMSE achieved: <0.025mm (within 10% of Python)

---

## Common Commands

### Python Development
```bash
# Activate environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Run tests
python test_registration.py

# Run with sample data
python CascadedPointCloudFit.py UNIT_111_Closed_J1.csv UNIT_111_Open_J1.csv

# Start API server
python app.py
```

### TypeScript Development (Future)
```bash
# Install dependencies
npm install

# Run in development
npm run dev

# Build for production
npm run build

# Run tests
npm test

# Run CLI
npm run cli -- input.csv output.csv
```

---

## Testing Checklist

### Python (Current)
- [x] Load CSV files (UNIT_111 data)
- [x] PCA registration
- [x] ICP refinement
- [x] Metrics calculation
- [x] Forward/reverse alignment
- [x] API endpoint testing
- [x] Performance benchmarking

### TypeScript (Future)
- [ ] Load CSV files (PapaParse)
- [ ] Load PLY files (THREE.PLYLoader)
- [ ] PCA registration (ml-pca)
- [ ] ICP refinement (custom + kd-tree)
- [ ] Metrics calculation (custom)
- [ ] Forward/reverse alignment
- [ ] API endpoint testing (Express)
- [ ] Performance benchmarking
- [ ] Accuracy validation vs Python

---

## Troubleshooting

### Python Issues

**Problem**: `ModuleNotFoundError: No module named 'open3d'`
```bash
# Solution: Install dependencies
pip install -r requirements-minimal.txt
```

**Problem**: `TypeError: FitResult.__init__() missing 1 required positional argument`
```bash
# Solution: Already fixed in IcpFitter.py
# If you see this, pull latest code
```

**Problem**: Test fails with "RMSE too high"
```bash
# Expected: Custom ICP achieves ~0.022mm RMSE
# If higher, check:
# 1. Point cloud data is correct (11K+ points)
# 2. KD-Tree parameters are reasonable
# 3. ICP convergence criteria
```

### TypeScript Issues (Future)

**Problem**: TypeScript compilation errors
```bash
# Check tsconfig.json settings
# Ensure @types packages are installed
npm install --save-dev @types/node @types/express
```

**Problem**: Performance too slow
```bash
# Consider:
# 1. Use WebAssembly for heavy computations
# 2. Reduce KD-Tree search radius
# 3. Decrease ICP iterations
# 4. Optimize point cloud data structure
```

---

## Next Actions

### For Python Developers
1. ✅ Review [test_registration.py](test_registration.py) results
2. ✅ Run CLI with your own point cloud data
3. ⏳ Optionally refactor app.py to use shared modules
4. ⏳ Add more test cases if needed

### For TypeScript Conversion
1. 📋 Review [TYPESCRIPT_CONVERSION_PLAN.md](TYPESCRIPT_CONVERSION_PLAN.md)
2. 📋 Make go/no-go decision
3. 🚀 If yes: Start Phase 1 (Project Setup)
4. 🚀 If no: Continue with Python improvements

---

## Support & Documentation

- **Python Documentation**: See README.md
- **TypeScript Plan**: [TYPESCRIPT_CONVERSION_PLAN.md](TYPESCRIPT_CONVERSION_PLAN.md)
- **Refactoring Details**: [REFACTORING_PLAN.md](REFACTORING_PLAN.md)
- **Complete Status**: [PROJECT_STATUS_SUMMARY.md](PROJECT_STATUS_SUMMARY.md)

---

## Summary

- ✅ **Python code**: Working, tested, refactored
- ✅ **Test data**: UNIT_111 samples validated
- ✅ **Performance**: 0.022mm RMSE in ~100ms
- 📋 **TypeScript**: Planned, feasible, 26-33 days effort
- 🎯 **Decision**: Review plans and choose path forward
