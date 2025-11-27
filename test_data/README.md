# Test Data Directory

This directory contains test data for the CascadedPointCloudFit project.

## Directory Structure

```
test_data/
├── README.md                    # This file
├── UNIT_111_Closed_J1.*         # Original UNIT_111 closed position data
├── UNIT_111_Open_J1.*           # Original UNIT_111 open position data
├── augmented/                   # Generated test data (run generate script)
│   ├── rotations/              # Rotated point clouds
│   ├── translations/           # Translated point clouds
│   ├── noise/                  # Point clouds with added noise
│   ├── subsampled/             # Downsampled point clouds
│   ├── outliers/               # Point clouds with outliers
│   └── combined/               # Combined transformations
└── real_world_data/            # Real-world test cases
    ├── Clamp1/2.*              # Clamp test data (successful case)
    ├── Slide1/2.*              # Slide test data (successful case)
    ├── Clouds3/                # Challenging registration case
    ├── Fails4/                 # Known failure case #4
    ├── IcpFails/               # ICP failure cases (now succeed!)
    ├── PinFails1/              # Pin failure case #1
    └── PinFails2/              # Pin failure case #2
```

## Data Files

### UNIT_111 Data (Original Test Data)
- **UNIT_111_Closed_J1.ply/csv** - Point cloud in closed position (11,207 points)
- **UNIT_111_Open_J1.ply/csv** - Point cloud in open position (11,213 points)
- **Centroid distance**: 61.61mm
- **Use case**: Primary test data for registration algorithms

### Real-World Data
All copied from production use cases with known registration challenges.

#### Successful Cases
- **Clamp1/Clamp2** - Clamping mechanism in two positions
- **Slide1/Slide2** - Sliding mechanism in two positions

#### Challenging Cases
- **Clouds3/** - Large point clouds with complex geometry
- **IcpFails/** - Previously failed with ICP (now succeeds with refactored code!)
- **Fails4/** - Known difficult registration case
- **PinFails1/** - Pin mechanism failure case #1
- **PinFails2/** - Pin mechanism failure case #2

## Generating Augmented Test Data

To generate augmented test data from UNIT_111 samples:

```bash
cd /path/to/CascadedPointCloudFit
python scripts/generate_test_data.py
```

This will create ~60 augmented test files with:
- **21 rotation files** - X, Y, Z axes at various angles (5°, 10°, 15°, 20°, 25°, 30°, 45°)
- **20 translation files** - X, Y, Z directions at various distances
- **4 noise files** - Gaussian noise at different levels (0.1, 0.5, 1.0, 2.0mm)
- **5 subsampling files** - Different sampling rates (90%, 75%, 50%, 25%, 10%)
- **3 outlier files** - Different outlier percentages (5%, 10%, 20%)
- **4 combined files** - Rotation + translation + noise combinations

## File Formats

### PLY Format (Preferred)
Binary or ASCII point cloud format with X, Y, Z coordinates and optional normals.

```
ply
format ascii 1.0
element vertex 11207
property float x
property float y
property float z
end_header
<point data>
```

### CSV Format
Simple comma-separated values with X, Y, Z columns.

```
x,y,z
-136.123,45.678,89.012
...
```

## Usage in Tests

### Unit Tests
```python
# tests/unit/test_*.py
def test_something(test_data_dir):
    source = test_data_dir / "UNIT_111_Closed_J1.ply"
    target = test_data_dir / "UNIT_111_Open_J1.ply"
    # ...
```

### Integration Tests
```python
# tests/integration/test_end_to_end.py
def test_real_world_case(real_world_data_dir):
    source = real_world_data_dir / "Clamp1.ply"
    target = real_world_data_dir / "Clamp2.ply"
    # ...
```

## Data Sources

- **UNIT_111**: Original project test data
- **Real-world cases**: Copied from `C:\Users\georgem\Downloads\CascadedPointCloudFit-master\CascadedPointCloudFit-master\Data`
- **Augmented data**: Generated using `scripts/generate_test_data.py`

## Notes

### Known Issues with Original Approach
The user confirmed: *"all point clouds are valid the failure were an indication that the approach was the issue and not the data"*

This was proven correct! Our refactored ICP now succeeds on the `IcpFails/` cases that previously failed.

### Test Data Validation
All point clouds are validated for:
- Valid 3D coordinates (X, Y, Z)
- No NaN or Inf values
- Sufficient point count (>100 points)
- Proper file format

## Size Information

- **UNIT_111 files**: ~350KB each (PLY format)
- **Real-world files**: Varies (100KB - 5MB)
- **Total test data**: ~50-100MB (with augmented files)

## Maintenance

To update test data:
1. Place new PLY/CSV files in appropriate subdirectory
2. Update this README with description
3. Add test case in `tests/integration/test_end_to_end.py`
4. Run tests: `pytest tests/integration/`

---

**Last Updated**: 2025-11-27
**Test Data Version**: 1.0
