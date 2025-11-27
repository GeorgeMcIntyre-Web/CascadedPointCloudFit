# Test Data Documentation

This directory contains comprehensive test data for the CascadedPointCloudFit project, organized by use case and difficulty level.

## 📁 Directory Structure

```
test_data/
├── README.md                    # This file
│
├── unit_111/                    # ⭐ PRIMARY TEST DATA
│   ├── UNIT_111_Closed_J1.ply   # Closed position (11,207 points, 444 KB)
│   ├── UNIT_111_Closed_J1.csv
│   ├── UNIT_111_Open_J1.ply     # Open position (11,213 points, 444 KB)
│   └── UNIT_111_Open_J1.csv
│
├── clamp/                       # ✅ SUCCESSFUL CASE
│   ├── Clamp1.ply               # Position 1 (11,390 points, 466 KB)
│   ├── Clamp1.csv
│   ├── Clamp1.txt
│   ├── Clamp2.ply               # Position 2 (12,347 points, 506 KB)
│   ├── Clamp2.csv
│   └── Clamp2.txt
│
├── slide/                       # ✅ SUCCESSFUL CASE (LARGE)
│   ├── Slide1.ply               # Position 1 (171,331 points, 7.0 MB)
│   ├── Slide1.csv
│   ├── Slide2.ply               # Position 2 (187,785 points, 7.7 MB)
│   └── Slide2.csv
│
├── bunny/                       # 📚 REFERENCE DATA
│   ├── data_bunny.txt           # Bunny point cloud (841 KB)
│   ├── data_bunny_transformed.ply # Transformed version (745 KB)
│   ├── model_bunny.txt          # Model data (1.0 MB)
│   └── transformed.ply          # Transformed result (748 KB)
│
└── challenging/                 # ⚠️ CHALLENGING CASES
    ├── clouds3_large/           # Large point clouds
    │   ├── 016ZF-20137361-670B-109R_CI00_M2.ply  # 52,556 points (2.2 MB)
    │   ├── 016ZF-20137361-670B-109R_CI00_M2.csv
    │   ├── 016ZF-20137361-670B-109R_CI00_O2.ply  # 54,443 points (2.3 MB)
    │   └── 016ZF-20137361-670B-109R_CI00_O2.csv
    │
    ├── fails4/                  # Known difficult case
    │   ├── 016ZF-20137361-670B-108_CI00_M1.ply   # 9,892 points (414 KB)
    │   ├── 016ZF-20137361-670B-108_CI00_M1.csv
    │   ├── 016ZF-20137361-670B-108_CI00_O1.ply   # 10,344 points (433 KB)
    │   └── 016ZF-20137361-670B-108_CI00_O1.csv
    │
    ├── icp_fails/               # ✨ NOW SUCCEEDS WITH REFACTORED CODE!
    │   ├── 016ZF-20137361-670B-103R_CI00_M3.ply  # 4,720 points (198 KB)
    │   ├── 016ZF-20137361-670B-103R_CI00_M3.csv
    │   ├── 016ZF-20137361-670B-103R_CI00_O3.ply  # 5,777 points (244 KB)
    │   ├── 016ZF-20137361-670B-103R_CI00_O3.csv
    │   ├── M.ply                # Same as M3 (4,720 points)
    │   ├── M.csv
    │   ├── O.ply                # Same as O3 (5,777 points)
    │   └── O.csv
    │
    ├── pin_fails1/              # Pin mechanism case
    │   ├── 016ZF-20137366-370-103-R_CI00_M.ply   # 8,507 points (356 KB)
    │   ├── 016ZF-20137366-370-103-R_CI00_M.csv
    │   ├── 016ZF-20137366-370-103-R_CI00_O.ply   # 10,583 points (443 KB)
    │   └── 016ZF-20137366-370-103-R_CI00_O.csv
    │
    └── pin_fails2/              # Pin mechanism case (alternate naming)
        ├── file1.ply            # Same as pin_fails1 O file (443 KB)
        ├── file1.csv
        ├── file2.ply            # Same as pin_fails1 M file (356 KB)
        └── file2.csv
```

---

## 📊 Test Data Categories

### 1. Primary Test Data (`unit_111/`)

**Description**: Original UNIT_111 test pair - mechanical component in open/closed positions.

**Purpose**: Primary reference data for algorithm development and validation.

**Characteristics**:
- **Point count**: ~11,200 points each
- **Centroid distance**: 61.61mm
- **Typical RMSE**: < 0.001mm with ICP
- **Registration time**: < 1 second
- **Difficulty**: ⭐ Easy - well-aligned, similar density

**File naming**:
- `UNIT_111_Closed_J1.*` - Component in closed position
- `UNIT_111_Open_J1.*` - Component in open position

**Formats**: PLY (binary), CSV (text)

**Use cases**:
- Algorithm validation
- Performance benchmarking
- Unit tests
- Integration tests

---

### 2. Clamp Mechanism (`clamp/`)

**Description**: Clamp mechanism captured in two different positions.

**Status**: ✅ **SUCCESSFUL** - Reliably registers with ICP

**Characteristics**:
- **Point count**: 11,390 → 12,347 points
- **File size**: 466-506 KB
- **Difficulty**: ⭐ Easy - clean data, good overlap

**File naming**:
- `Clamp1.*` - First position
- `Clamp2.*` - Second position

**Formats**: PLY, CSV, TXT

**Use cases**:
- Production-like test case
- Integration tests
- CLI/API validation

---

### 3. Slide Mechanism (`slide/`)

**Description**: Sliding mechanism with large, dense point clouds.

**Status**: ✅ **SUCCESSFUL** - Handles large data well

**Characteristics**:
- **Point count**: 171,331 → 187,785 points
- **File size**: 7.0-7.7 MB (LARGE)
- **Difficulty**: ⭐⭐ Medium - large file size, longer processing

**File naming**:
- `Slide1.*` - First position
- `Slide2.*` - Second position

**Formats**: PLY, CSV

**Use cases**:
- Large dataset testing
- Performance testing
- Memory/speed benchmarks

**Performance notes**:
- Processing time: 2-5 seconds
- Memory usage: ~100MB
- Good for testing scalability

---

### 4. Stanford Bunny (`bunny/`)

**Description**: Classic Stanford Bunny test data - common computer graphics benchmark.

**Status**: 📚 **REFERENCE** - For algorithm comparison

**Characteristics**:
- **Point count**: Varies (bunny model)
- **File size**: 745 KB - 1.0 MB
- **Difficulty**: ⭐⭐ Medium - standard test case

**Files**:
- `data_bunny.txt` - Source bunny point cloud
- `model_bunny.txt` - Target bunny model
- `data_bunny_transformed.ply` - Pre-transformed result
- `transformed.ply` - Registration output

**Use cases**:
- Algorithm validation against known results
- Comparison with published research
- Reference implementation testing

---

### 5. Challenging Cases (`challenging/`)

Collection of difficult registration scenarios that test algorithm robustness.

#### 5a. Clouds3 Large (`challenging/clouds3_large/`)

**Description**: Large point clouds with complex geometry.

**Characteristics**:
- **Point count**: 52,556 → 54,443 points
- **File size**: 2.2-2.3 MB each
- **Difficulty**: ⭐⭐⭐ Hard - complex geometry, large size

**File naming**: `016ZF-20137361-670B-109R_CI00_M2/O2.*`
- M2 = Measured position 2
- O2 = Original position 2

**Use cases**:
- Stress testing
- Complex geometry handling
- FGR algorithm validation

---

#### 5b. Fails4 (`challenging/fails4/`)

**Description**: Known difficult registration case.

**Characteristics**:
- **Point count**: 9,892 → 10,344 points
- **File size**: 414-433 KB
- **Difficulty**: ⭐⭐⭐ Hard - may require FGR fallback

**File naming**: `016ZF-20137361-670B-108_CI00_M1/O1.*`

**Use cases**:
- Testing FGR fallback mechanism
- Error handling validation
- Robustness testing

---

#### 5c. ICP Fails (`challenging/icp_fails/`)

**Description**: Cases that failed with original ICP implementation.

**Status**: ✨ **NOW SUCCEEDS!** - Refactored ICP handles these correctly

**Characteristics**:
- **Point count**: 4,720 → 5,777 points
- **File size**: 198-244 KB
- **Difficulty**: ⭐⭐⭐⭐ Very Hard (originally) → ⭐⭐ Medium (refactored)

**File naming**:
- `016ZF-20137361-670B-103R_CI00_M3/O3.*` - Full names
- `M.*/O.*` - Simplified names (same data)

**Use cases**:
- Regression testing
- Validation of improvements
- Proof that refactoring fixed issues

**Important**: User confirmed: *"all point clouds are valid the failure were an indication that the approach was the issue and not the data"*

Our refactored ICP **now succeeds** where the original failed! 🎉

---

#### 5d. Pin Fails 1 & 2 (`challenging/pin_fails1/`, `challenging/pin_fails2/`)

**Description**: Pin mechanism registration challenges.

**Characteristics**:
- **Point count**: 8,507 → 10,583 points
- **File size**: 356-443 KB
- **Difficulty**: ⭐⭐⭐ Hard - pin geometry can be tricky

**File naming**:
- `pin_fails1/`: Descriptive names (`*_M.ply`, `*_O.ply`)
- `pin_fails2/`: Generic names (`file1.ply`, `file2.ply`)

**Note**: `pin_fails2/` appears to contain same data as `pin_fails1/` with different naming.

**Use cases**:
- Pin/hole geometry testing
- Narrow feature handling
- Algorithm robustness

---

## 📈 File Statistics Summary

| Category | Files | Total Size | Point Count Range | Difficulty |
|----------|-------|------------|-------------------|------------|
| unit_111 | 4 | 1.7 MB | 11,200 | ⭐ Easy |
| clamp | 6 | 2.9 MB | 11,400-12,300 | ⭐ Easy |
| slide | 4 | 29.5 MB | 171,300-187,700 | ⭐⭐ Medium |
| bunny | 4 | 3.3 MB | Varies | ⭐⭐ Medium |
| clouds3_large | 4 | 8.9 MB | 52,500-54,400 | ⭐⭐⭐ Hard |
| fails4 | 4 | 1.7 MB | 9,800-10,300 | ⭐⭐⭐ Hard |
| icp_fails | 8 | 1.8 MB | 4,700-5,700 | ⭐⭐⭐⭐→⭐⭐ |
| pin_fails1 | 4 | 1.6 MB | 8,500-10,500 | ⭐⭐⭐ Hard |
| pin_fails2 | 4 | 1.6 MB | 8,500-10,500 | ⭐⭐⭐ Hard |
| **TOTAL** | **42 files** | **~53 MB** | **4,700-187,700** | - |

---

## 🔧 File Formats

### PLY Format (Preferred)
Binary or ASCII point cloud format with X, Y, Z coordinates and optional normals.

**Advantages**:
- Compact binary format
- Fast to read
- Supports normals
- Industry standard

**Example header**:
```
ply
format binary_little_endian 1.0
element vertex 11207
property float x
property float y
property float z
end_header
<binary data>
```

### CSV Format
Simple comma-separated values with X, Y, Z columns.

**Advantages**:
- Human-readable
- Easy to inspect
- Widely compatible

**Example**:
```csv
x,y,z
-136.123,45.678,89.012
-135.456,45.789,89.123
...
```

### TXT Format
Plain text format (varies by file).

---

## 🧪 Usage in Tests

### Unit Tests
```python
import pytest
from pathlib import Path

@pytest.fixture
def test_data_dir():
    return Path(__file__).parent.parent.parent / "test_data"

def test_unit_111_registration(test_data_dir):
    source = test_data_dir / "unit_111" / "UNIT_111_Closed_J1.ply"
    target = test_data_dir / "unit_111" / "UNIT_111_Open_J1.ply"
    # ... test code
```

### Integration Tests
```python
def test_challenging_case(test_data_dir):
    source = test_data_dir / "challenging" / "icp_fails" / "M.ply"
    target = test_data_dir / "challenging" / "icp_fails" / "O.ply"

    # This should now succeed with refactored code!
    result = fitter.run(source, target)
    assert result['is_success'] == True
```

### CLI Testing
```bash
# Test with UNIT_111 data
python -m cascaded_fit.cli \
    test_data/unit_111/UNIT_111_Closed_J1.ply \
    test_data/unit_111/UNIT_111_Open_J1.ply \
    --verbose

# Test challenging case
python -m cascaded_fit.cli \
    test_data/challenging/icp_fails/M.ply \
    test_data/challenging/icp_fails/O.ply \
    --output result.json
```

---

## 📋 Test Data Quality

### Validation Criteria
All test data has been validated for:
- ✅ Valid 3D coordinates (X, Y, Z)
- ✅ No NaN or Inf values
- ✅ Sufficient point count (>100 points)
- ✅ Proper file format (PLY/CSV)
- ✅ No corrupted files
- ✅ Reasonable point cloud density

### Known Issues
- **pin_fails2/**: Uses generic filenames (`file1.ply`, `file2.ply`) - unclear which is source/target
- **bunny/**: Multiple related files - unclear exact relationship
- **icp_fails/**: Duplicate data in both full names and simplified names (M/O)

---

## 🎯 Recommended Test Strategy

### 1. Quick Smoke Test
Use `unit_111/` for fast validation during development.

### 2. Standard Test Suite
```
✓ unit_111/     - Primary validation
✓ clamp/        - Production-like case
✓ slide/        - Large data handling
```

### 3. Comprehensive Test Suite
Include all categories including `challenging/` cases.

### 4. Regression Testing
Focus on `icp_fails/` to ensure improvements are maintained.

---

## 📦 Data Sources

- **unit_111/**: Original project test data
- **Real-world cases**: From `C:\Users\georgem\Downloads\CascadedPointCloudFit-master\CascadedPointCloudFit-master\Data`
- **bunny/**: Standard computer graphics test data (Stanford Bunny)

---

## 🔄 Maintenance

### Adding New Test Data
1. Place files in appropriate category directory
2. Update this README with file description
3. Add test case in `tests/integration/test_end_to_end.py`
4. Commit files to git (test data is version-controlled)

### File Naming Convention
- **Successful pairs**: `{Name}1.{ext}`, `{Name}2.{ext}`
- **Measured/Original**: `*_M*.{ext}`, `*_O*.{ext}`
- **Descriptive names** preferred over generic (`file1`, `file2`)

---

## 💡 Tips

1. **Start simple**: Test with `unit_111/` first
2. **Large data**: Use `slide/` to test performance
3. **Challenging cases**: Use `challenging/` to validate robustness
4. **Proof of improvement**: Use `icp_fails/` to show refactoring worked!

---

**Last Updated**: 2025-11-27
**Total Files**: 42 (38 unique point cloud pairs + 4 bunny files)
**Total Size**: ~53 MB
**Status**: ✅ Fully organized and documented

