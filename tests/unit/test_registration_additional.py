"""Additional unit tests for registration algorithms."""

import pytest
import numpy as np
from cascaded_fit.core.registration import RegistrationAlgorithms
from cascaded_fit.utils.exceptions import RegistrationError


class TestRegistrationAlgorithmsAdditional:
    """Additional tests for RegistrationAlgorithms."""

    def test_calculate_transformation_matrix(self):
        """Test calculate_transformation_matrix method."""
        # Create source and transformed points
        source = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
        transformed = source + np.array([1, 1, 1])  # Translation
        
        transform = RegistrationAlgorithms.calculate_transformation_matrix(
            source, transformed
        )
        
        assert transform.shape == (4, 4)
        # Check translation component
        assert np.allclose(transform[:3, 3], [1, 1, 1])

    def test_apply_transformation(self):
        """Test apply_transformation method."""
        points = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
        transform = np.eye(4)
        transform[:3, 3] = [1, 1, 1]  # Translation
        
        transformed = RegistrationAlgorithms.apply_transformation(points, transform)
        
        assert transformed.shape == points.shape
        expected = points + np.array([1, 1, 1])
        np.testing.assert_allclose(transformed, expected)

    def test_apply_transformation_rotation(self):
        """Test apply_transformation with rotation."""
        points = np.array([[1, 0, 0], [0, 1, 0]])
        # 90 degree rotation around Z axis
        transform = np.eye(4)
        transform[:3, :3] = np.array([[0, -1, 0], [1, 0, 0], [0, 0, 1]])
        
        transformed = RegistrationAlgorithms.apply_transformation(points, transform)
        
        assert transformed.shape == points.shape
        # [1,0,0] should become [0,1,0]
        np.testing.assert_allclose(transformed[0], [0, 1, 0], atol=1e-6)

