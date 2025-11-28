# Test Suite Documentation

Comprehensive testing for the CascadedPointCloudFit TypeScript implementation.

## Test Statistics

- **Total Tests**: 82
- **Test Files**: 11
- **Pass Rate**: 100%
- **Code Coverage**: Target 70%+

## Test Structure

```
tests/
├── core/                    # Unit tests for core algorithms
│   ├── RegistrationAlgorithms.test.ts    # PCA, ICP, downsampling (5 tests)
│   ├── RANSACHelper.test.ts              # RANSAC outlier rejection (15 tests)
│   ├── KDTreeHelper.test.ts              # K-D tree operations (4 tests)
│   ├── MetricsCalculator.test.ts         # Quality metrics (3 tests)
│   └── TransformationUtils.test.ts       # Matrix operations (8 tests)
├── io/                      # I/O operations tests
│   └── PointCloudReader.test.ts          # File loading (11 tests)
├── integration/             # Integration tests
│   ├── registration.test.ts              # Full pipeline (6 tests)
│   ├── api.test.ts                       # REST API (4 tests)
│   └── real-data.test.ts                 # Real UNIT_111 data (3 tests)
├── e2e/                     # End-to-end workflows
│   └── complete-workflow.test.ts         # Complete scenarios (9 tests)
└── performance/             # Performance benchmarks
    └── benchmarks.test.ts                # Performance targets (14 tests)
```

## Test Categories

### 1. Unit Tests (35 tests)

Test individual components in isolation.

**Core Algorithms** (`tests/core/RegistrationAlgorithms.test.ts`)
- PCA registration
- ICP refinement
- Downsampling
- Convergence behavior
- Edge cases

**RANSAC Helper** (`tests/core/RANSACHelper.test.ts`)
- Outlier rejection
- Inlier ratio calculation
- Sample size handling
- Parameter validation
- Performance characteristics
- Edge cases (small clouds, tight thresholds)

**KD-Tree** (`tests/core/KDTreeHelper.test.ts`)
- Nearest neighbor search
- Tree construction
- Distance calculations
- Large cloud handling

**Metrics** (`tests/core/MetricsCalculator.test.ts`)
- RMSE calculation
- Error statistics
- Metric accuracy

**Transformations** (`tests/core/TransformationUtils.test.ts`)
- Matrix operations
- Transform application
- Composition
- Inversion

**File I/O** (`tests/io/PointCloudReader.test.ts`)
- PLY loading (binary/ASCII)
- CSV loading
- Format detection
- Cloud alignment
- Error handling

### 2. Integration Tests (13 tests)

Test component interactions.

**Registration Pipeline** (`tests/integration/registration.test.ts`)
- PCA + ICP workflow
- Multi-stage alignment
- Transform chaining

**REST API** (`tests/integration/api.test.ts`)
- Endpoint functionality
- Request/response handling
- Error responses

**Real Data** (`tests/integration/real-data.test.ts`)
- UNIT_111 dataset (11K points)
- Performance validation
- Accuracy verification

### 3. End-to-End Tests (9 tests)

Test complete user workflows.

**Complete Workflow** (`tests/e2e/complete-workflow.test.ts`)
- File loading → Registration → Metrics
- Validation of all pipeline stages
- Error handling (empty clouds, mismatched sizes)
- Degenerate data handling
- Downsampling integration
- Performance benchmarks

### 4. Performance Tests (14 tests)

Validate performance targets.

**Benchmarks** (`tests/performance/benchmarks.test.ts`)

| Test | Target | Actual (Typical) |
|------|--------|------------------|
| PCA 1K points | 100ms | ~5ms ✅ |
| PCA 10K points | 500ms | ~32ms ✅ |
| PCA 100K points | 2000ms | ~11ms ✅ |
| ICP 1K points | 500ms | ~17ms ✅ |
| ICP 10K points | 3000ms | ~117ms ✅ |
| ICP 100K points | 15000ms | ~8600ms ✅ |
| Full Pipeline 10K | 5000ms | ~48ms ✅ |
| RANSAC 1K points | 5000ms | ~142ms ✅ |
| Metrics 10K | 1000ms | ~50ms ✅ |
| Metrics 100K | 30000ms | ~20s ✅ |

**Real-World Performance**:
- UNIT_111 (11K points): < 5s ✅ (actual: ~1.3s)

## Running Tests

### Run All Tests
```bash
npm test
```

### Watch Mode
```bash
npm run test:watch
```

### Coverage Report
```bash
npm run test:coverage
```

### Run Specific Test File
```bash
npx vitest run tests/core/RegistrationAlgorithms.test.ts
```

### Run E2E Tests Only
```bash
npx vitest run tests/e2e/
```

### Run Performance Benchmarks
```bash
npx vitest run tests/performance/
```

## Test Data

### Synthetic Data
Most unit and integration tests use programmatically generated point clouds:
- Grid patterns
- Random noise
- Controlled offsets
- Outliers (for RANSAC tests)

### Real-World Data
Located in `../test_data/`:
- **UNIT_111**: Hinge mechanism (11,207 points each)
  - `UNIT_111_Closed_J1.ply` - Closed position
  - `UNIT_111_Open_J1.ply` - Open position
  - Perfect registration: RMSE = 0.000000

## Coverage Targets

- **Overall**: 70%+
- **Core Algorithms**: 90%+
- **Registration**: 95%+
- **File I/O**: 80%+
- **Utilities**: 70%+

## Test Utilities

### Helper Functions

**Creating Test Clouds**:
```typescript
function createTestCloud(count: number, offset = 0): PointCloud {
  const points = new Float32Array(count * 3);
  for (let i = 0; i < count; i++) {
    points[i * 3] = i + offset;
    points[i * 3 + 1] = i + offset;
    points[i * 3 + 2] = i + offset;
  }
  return { points, count };
}
```

**Identity Transform**:
```typescript
function identityTransform(): Transform4x4 {
  return {
    matrix: [
      [1, 0, 0, 0],
      [0, 1, 0, 0],
      [0, 0, 1, 0],
      [0, 0, 0, 1],
    ],
  };
}
```

## Continuous Integration

Tests run automatically on:
- Pull requests
- Commits to main
- Pre-publish hooks

### CI Configuration
```json
{
  "scripts": {
    "prepublishOnly": "npm run build && npm test"
  }
}
```

## Test-Driven Development

### Adding New Features

1. **Write failing test first**
   ```typescript
   it('should handle new feature', () => {
     const result = newFeature(input);
     expect(result).toBeDefined();
   });
   ```

2. **Implement minimum code to pass**

3. **Refactor while keeping tests green**

4. **Add edge case tests**

### Test Naming Convention

```typescript
describe('ComponentName', () => {
  describe('methodName', () => {
    it('should do expected behavior', () => {
      // Test implementation
    });

    it('should handle edge case', () => {
      // Edge case test
    });
  });
});
```

## Debugging Tests

### Run Single Test
```bash
npx vitest run tests/core/RegistrationAlgorithms.test.ts -t "should complete PCA"
```

### Debug Mode
```bash
node --inspect-brk ./node_modules/vitest/vitest.mjs run
```

### Skip Tests Temporarily
```typescript
it.skip('test to skip', () => {
  // This test won't run
});
```

### Run Only Specific Tests
```typescript
it.only('test to focus on', () => {
  // Only this test runs
});
```

## Known Issues & Limitations

### Performance Variations
- Metrics calculation for 100K points can vary (15-25s)
- Scaling tests depend on system performance
- First test run may be slower (JIT warmup)

### Platform Differences
- Windows paths require proper escaping
- File permissions may differ
- Performance targets are averages

### Test Data Dependencies
- Real-world tests skip if `test_data/` not available
- Use `.skipIf()` for conditional tests

## RANSAC Testing Notes

RANSAC tests are inherently stochastic:
- Results may vary between runs
- Use loose tolerances for inlier ratios
- Focus on behavior, not exact values
- Test parameter ranges, not specific outputs

Example:
```typescript
// Good: Tests behavior
expect(result.inlierCount).toBeGreaterThanOrEqual(0);

// Bad: Tests exact value (will be flaky)
expect(result.inlierRatio).toBe(0.75);
```

## Contributing

### Before Submitting PR

1. Run full test suite: `npm test`
2. Check coverage: `npm run test:coverage`
3. Run linter: `npm run lint`
4. Format code: `npm run format`

### Adding New Tests

1. Place in appropriate directory (`core/`, `integration/`, etc.)
2. Follow naming conventions
3. Add to this README if new category
4. Ensure tests are deterministic (avoid random values)
5. Use realistic timeouts (consider CI environment)

## Performance Testing Best Practices

1. **Warm up JIT** - Run once before measuring
2. **Use `performance.now()`** - More accurate than `Date.now()`
3. **Set realistic targets** - Based on hardware capabilities
4. **Allow variance** - Performance varies by system
5. **Test scaling** - Verify sub-linear growth with optimizations

## Test Metrics

### Current Status (All Passing ✅)

```
Test Files: 11 passed (11)
Tests:      82 passed (82)
Duration:   ~80 seconds
Pass Rate:  100%
```

### Historical Performance

| Date | Tests | Pass Rate | Duration |
|------|-------|-----------|----------|
| 2025-11-28 | 82 | 100% | 80s |
| 2025-11-27 | 44 | 100% | 3s |

## Future Test Additions

### Planned
- [ ] Stress tests (1M+ points)
- [ ] Parallel processing tests
- [ ] Memory leak detection
- [ ] Fuzzing tests
- [ ] Property-based testing

### Nice to Have
- [ ] Visual regression tests
- [ ] Browser compatibility tests
- [ ] WebAssembly performance comparison
- [ ] Multi-threaded worker tests

---

**Last Updated**: 2025-11-28
**Test Framework**: Vitest v1.6.1
**Node Version**: >= 14.0.0
