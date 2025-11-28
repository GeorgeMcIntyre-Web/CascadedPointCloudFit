# Optimization Quick Reference

## Quick Performance Checks

### Run All Datasets
```bash
cd typescript
npx tsx scripts/validateExternalData.ts
```

### Run Specific Dataset
```bash
npx tsx scripts/validateExternalData.ts Clouds3
npx tsx scripts/validateExternalData.ts Slide
```

### Build & Test
```bash
npm run build
npm test
```

## Common Optimization Patterns

### 1. Profile a Function
```typescript
const start = performance.now();
// ... your code ...
const duration = performance.now() - start;
console.log(`Duration: ${duration.toFixed(2)}ms`);
```

### 2. Check Memory Usage
```typescript
const memBefore = process.memoryUsage().heapUsed;
// ... your code ...
const memAfter = process.memoryUsage().heapUsed;
console.log(`Memory: ${((memAfter - memBefore) / 1024 / 1024).toFixed(2)}MB`);
```

### 3. Iterate Over PointCloud (Fast)
```typescript
const points = cloud.points;
for (let i = 0; i < cloud.count; i++) {
  const x = points[i * 3];
  const y = points[i * 3 + 1];
  const z = points[i * 3 + 2];
  // ... work with x, y, z ...
}
```

### 4. Create PointCloud from Float32Array
```typescript
const points = new Float32Array(count * 3);
// ... populate points ...
const cloud: PointCloud = { points, count };
```

## Performance Targets

| Operation | Target | Current |
|-----------|--------|---------|
| KD-tree build (50k) | < 500ms | ~800ms |
| Nearest neighbor (50k) | < 1ms | ~2ms |
| ICP iteration (50k) | < 100ms | ~150ms |
| Full registration (50k) | < 5s | 6s |

## Key Metrics to Track

1. **Total Duration** - End-to-end processing time
2. **PCA Time** - Initial alignment time
3. **ICP Time** - Refinement time
4. **KD-tree Build Time** - Tree construction time
5. **Nearest Neighbor Time** - Query time per iteration
6. **Memory Usage** - Peak heap usage
7. **RMSE** - Must remain < 1e-6

## Debugging Commands

### Enable Debug Logging
```bash
DEBUG=true npx tsx scripts/validateExternalData.ts Clouds3
```

### Run with Node Inspector
```bash
node --inspect-brk node_modules/.bin/tsx scripts/validateExternalData.ts Clouds3
# Open chrome://inspect in Chrome
```

### Check Stack Size
```bash
node --max-old-space-size=4096 --stack-size=8192 node_modules/.bin/tsx scripts/validateExternalData.ts Slide
```

## File Locations

| Component | File |
|-----------|------|
| PCA + ICP | `src/core/RegistrationAlgorithms.ts` |
| KD-tree | `src/core/KDTreeHelper.ts` |
| SpatialGrid | `src/core/SpatialGrid.ts` |
| SVD | `src/core/SVDHelper.ts` |
| Metrics | `src/core/MetricsCalculator.ts` |
| Validation | `scripts/validateExternalData.ts` |

## Common Issues & Fixes

### Stack Overflow
- **Symptom**: "Maximum call stack size exceeded"
- **Cause**: Recursive functions on large datasets
- **Fix**: Convert to iterative with explicit stack

### Slow Performance
- **Symptom**: Processing time > target
- **Cause**: Creating too many objects or inefficient algorithms
- **Fix**: Use Float32Array directly, avoid Point3D creation

### High Memory Usage
- **Symptom**: Process crashes or slows down
- **Cause**: Creating copies of large arrays
- **Fix**: Use indices instead of slicing, work in-place

## Testing Checklist

Before committing optimizations:

- [ ] All tests pass: `npm test`
- [ ] Clouds3 processes in < 10s
- [ ] Clamp processes in < 5s
- [ ] Slide processes without stack overflow
- [ ] All RMSE values < 1e-6
- [ ] No memory leaks (run multiple times)
- [ ] Code compiles without warnings: `npm run build`

