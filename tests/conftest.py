"""Pytest configuration and fixtures."""

import pytest
import numpy as np
from pathlib import Path


@pytest.fixture(scope="session")
def test_data_dir():
    """Return path to test data directory."""
    return Path(__file__).parent / "test_data"


@pytest.fixture(scope="session")
def original_data_dir(test_data_dir):
    """Return path to original test data."""
    return test_data_dir / "original"


@pytest.fixture
def simple_point_cloud():
    """Generate a simple test point cloud."""
    np.random.seed(42)
    return np.random.rand(1000, 3) * 100


@pytest.fixture
def identity_transform():
    """Return 4x4 identity transformation matrix."""
    return np.eye(4)


@pytest.fixture
def sample_rotation():
    """Return a simple rotation matrix (45 degrees around Z axis)."""
    angle = np.pi / 4
    c, s = np.cos(angle), np.sin(angle)
    R = np.array([
        [c, -s, 0, 0],
        [s, c, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ])
    return R


@pytest.fixture
def sample_translation():
    """Return a simple translation matrix."""
    T = np.eye(4)
    T[:3, 3] = [10, 20, 30]
    return T
