# Pyodide Quick Start Guide

## TL;DR - What You Need to Know

1. **Your codebase has mixed compatibility**: Core algorithms (PCA/ICP) work in Pyodide, but Open3D-dependent code doesn't.
2. **Solution**: Create a Pyodide-compatible API that uses only `core/registration.py` and `core/metrics.py`.
3. **Deployment**: Use Cloudflare Pages for browser-based Pyodide, or Cloudflare Workers for server-side Python.

---

## Quick Setup (5 Steps)

### Step 1: Create React App

```bash
npx create-react-app kinetiCORE --template typescript
cd kinetiCORE
npm install pyodide
```

### Step 2: Copy Python Code

Copy these directories to `public/python/cascaded_fit/`:
- `core/` (registration.py, metrics.py, transformations.py, validators.py)
- Create `api/wasm_api.py` (see below)

### Step 3: Create WASM API

**File: `public/python/cascaded_fit/api/wasm_api.py`**

```python
import json
import numpy as np
from typing import Dict, Any, List
from cascaded_fit.core.registration import RegistrationAlgorithms
from cascaded_fit.core.metrics import MetricsCalculator
from cascaded_fit.core.validators import PointCloudValidator

def run_core(args_json: str) -> str:
    """Entry point for Pyodide - JSON in, JSON out."""
    args = json.loads(args_json)
    source = np.array(args['source_points'])
    target = np.array(args['target_points'])
    
    # Validate
    validator = PointCloudValidator()
    validator.validate_pair(source, target)
    
    # Align sizes
    min_size = min(len(source), len(target))
    source = source[:min_size]
    target = target[:min_size]
    
    # Register
    initial = RegistrationAlgorithms.pca_registration(source, target)
    refined = RegistrationAlgorithms.icp_refinement(source, target, initial)
    metrics = MetricsCalculator.compute_metrics(source, target, refined)
    
    return json.dumps({
        "transformation": refined.tolist(),
        "inlier_rmse": float(metrics['RMSE']),
        "max_error": float(metrics['Max Error']),
        "is_success": metrics['RMSE'] < args.get('rmse_threshold', 1.0),
        "method": "PCA + ICP (Pyodide)"
    })
```

### Step 4: TypeScript Client

**File: `src/python/pyodideClient.ts`**

```typescript
import { loadPyodide, PyodideInterface } from 'pyodide';

let pyodide: PyodideInterface | null = null;

export async function initializePyodide() {
  if (pyodide) return pyodide;
  
  pyodide = await loadPyodide({
    indexURL: 'https://cdn.jsdelivr.net/pyodide/v0.26.0/full/',
  });
  
  await pyodide.loadPackage(['numpy', 'scipy']);
  await loadPythonFiles(pyodide);
  
  return pyodide;
}

async function loadPythonFiles(py: PyodideInterface) {
  const files = [
    '/python/cascaded_fit/core/registration.py',
    '/python/cascaded_fit/core/metrics.py',
    '/python/cascaded_fit/core/transformations.py',
    '/python/cascaded_fit/core/validators.py',
    '/python/cascaded_fit/api/wasm_api.py',
  ];
  
  for (const file of files) {
    const response = await fetch(file);
    const code = await response.text();
    py.FS.writeFile(file.replace('/python/', '/'), code);
  }
  
  py.runPython(`import sys; sys.path.append('/')`);
}

export async function processPointClouds(args: any) {
  const py = await initializePyodide();
  const argsJson = JSON.stringify(args);
  
  const resultJson = await py.runPythonAsync(`
from cascaded_fit.api.wasm_api import run_core
run_core(${JSON.stringify(argsJson)})
  `);
  
  return JSON.parse(resultJson as string);
}
```

### Step 5: Use in React

```typescript
import { processPointClouds } from './python/pyodideClient';

const result = await processPointClouds({
  source_points: [[0,0,0], [1,1,1]],
  target_points: [[0.1,0.1,0.1], [1.1,1.1,1.1]],
  rmse_threshold: 1.0
});
```

---

## Cloudflare Deployment

### Option A: Cloudflare Pages (Recommended)

```bash
npm run build
npx wrangler pages deploy build
```

That's it! Pyodide runs in the browser, no server needed.

### Option B: Cloudflare Workers (Python)

```bash
# Install Wrangler
npm install -g wrangler

# Create worker
wrangler init cascaded-fit-worker

# Deploy
wrangler deploy
```

**Note**: This uses Cloudflare's native Python runtime, not Pyodide.

---

## What Works / Doesn't Work

| Component | Status | Notes |
|-----------|--------|-------|
| `core/registration.py` | ✅ Works | Pure NumPy/SciPy |
| `core/metrics.py` | ✅ Works | Pure NumPy/SciPy |
| `fitters/icp_fitter.py` | ❌ No | Uses Open3D |
| `fitters/fgr_fitter.py` | ❌ No | Uses Open3D |
| `io/readers.py` | ⚠️ Partial | PLY reader needs replacement |

---

## Testing Locally

```bash
# Start dev server
npm start

# Open http://localhost:3000
# Check browser console for Pyodide loading messages
```

---

## Common Issues

### Issue: "Module not found"
**Solution**: Make sure Python files are in `public/python/` and paths are correct.

### Issue: "NumPy not available"
**Solution**: Wait for `loadPackage(['numpy', 'scipy'])` to complete.

### Issue: Slow loading
**Solution**: Normal - Pyodide is ~20MB. Use loading indicators.

---

## Next Steps

1. Test locally with sample data
2. Add file upload for point clouds
3. Deploy to Cloudflare Pages
4. Monitor performance

See `PYODIDE_CLOUDFLARE_RESEARCH.md` for full details.

