# Contributing to CascadedPointCloudFit

Thank you for your interest in contributing to CascadedPointCloudFit! This document provides guidelines and instructions for contributing.

## Development Setup

### Prerequisites

- Python 3.10 or higher
- Git
- Virtual environment (recommended)

### Setup Steps

1. **Fork and clone the repository**:
   ```bash
   git clone https://github.com/yourusername/CascadedPointCloudFit.git
   cd CascadedPointCloudFit
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Linux/macOS:
   source venv/bin/activate
   ```

3. **Install in development mode**:
   ```bash
   pip install -e ".[dev]"
   ```

4. **Run tests to verify setup**:
   ```bash
   pytest tests/ -v
   ```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 2. Make Changes

- Follow the existing code style
- Add type hints to all new functions
- Write docstrings for all public functions/classes
- Add tests for new functionality

### 3. Run Tests and Linters

Before committing, ensure:

```bash
# Run all tests
pytest tests/ -v

# Check test coverage (should be 88%+)
pytest tests/ --cov=cascaded_fit --cov-report=term-missing

# Format code with black
black cascaded_fit/ tests/

# Check with flake8
flake8 cascaded_fit/ tests/

# Type checking with mypy
mypy cascaded_fit/
```

### 4. Commit Changes

Use clear, descriptive commit messages:

```bash
git add .
git commit -m "Add feature: description of what was added"
```

### 5. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub.

## Code Style Guidelines

### Python Style

- Follow PEP 8
- Use type hints for all function signatures
- Maximum line length: 100 characters (black default)
- Use descriptive variable names
- Add docstrings to all public functions/classes

### Type Hints

Always include type hints:

```python
def process_point_cloud(
    source: np.ndarray,
    target: np.ndarray,
    threshold: float = 0.01
) -> Dict[str, Any]:
    """Process point cloud registration.
    
    Args:
        source: Source point cloud (Nx3)
        target: Target point cloud (Mx3)
        threshold: RMSE threshold
        
    Returns:
        Registration result dictionary
    """
    ...
```

### Testing

- Write tests for all new functionality
- Aim for 80%+ test coverage
- Use descriptive test names: `test_function_name_scenario`
- Group related tests in classes

### Documentation

- Update README.md if adding new features
- Add docstrings to all public APIs
- Update CHANGELOG.md for user-facing changes

## Project Structure

```
cascaded_fit/
├── core/          # Core algorithms (PCA, ICP)
├── fitters/       # Registration fitters
├── io/            # File I/O
├── utils/         # Utilities (config, logging, exceptions)
├── api/           # REST API
└── cli/           # Command-line interface
```

## Areas for Contribution

### High Priority

- [ ] Increase test coverage to 90%+
- [ ] Add configuration validation
- [ ] Add OpenAPI/Swagger documentation
- [ ] Improve error messages with more context

### Medium Priority

- [ ] Add performance benchmarks
- [ ] Add memory profiling
- [ ] Support additional file formats (XYZ, PCD)
- [ ] Add CI/CD pipeline

### Low Priority

- [ ] Add web UI
- [ ] GPU acceleration support
- [ ] Multi-cloud batch processing

## Reporting Issues

When reporting issues, please include:

1. **Description**: Clear description of the issue
2. **Steps to Reproduce**: Detailed steps to reproduce
3. **Expected Behavior**: What you expected to happen
4. **Actual Behavior**: What actually happened
5. **Environment**: Python version, OS, package versions
6. **Error Messages**: Full error traceback if applicable

## Code Review Process

1. All pull requests require review
2. Tests must pass
3. Code coverage must not decrease
4. Code must be formatted with black
5. No linter errors

## Questions?

Feel free to open an issue for questions or discussions about contributions.

Thank you for contributing! 🎉

