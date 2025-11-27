"""Unit tests for registration algorithms."""

import pytest
import numpy as np
from cascaded_fit.core.registration import RegistrationAlgorithms
from cascaded_fit.utils.exceptions import RegistrationError, ConvergenceError
from cascaded_fit.utils.logger import Logger

# Setup logger for tests
Logger.setup(level="DEBUG", log_to_console=False)


class TestPCARegistration:
    """Test PCA registration algorithm."""

    def test_identity_case(self, simple_point_cloud):
        """Test PCA with identical point clouds returns identity."""
        transform = RegistrationAlgorithms.pca_registration(
            simple_point_cloud, simple_point_cloud
        )

        # Should be close to identity
        assert np.allclose(transform, np.eye(4), atol=1e-6)

    def test_translation_only(self, simple_point_cloud):
        """Test PCA recovers pure translation."""
        translation = np.array([10, 20, 30])
        target = simple_point_cloud + translation

        transform = RegistrationAlgorithms.pca_registration(
            simple_point_cloud, target
        )

        # Extract translation component
        recovered_translation = transform[:3, 3]

        # Should recover the translation
        assert np.allclose(recovered_translation, translation, atol=1.0)

    def test_rotation_recovery(self, simple_point_cloud, sample_rotation):
        """Test PCA can recover rotation."""
        # Apply rotation to create target
        rotated = RegistrationAlgorithms.apply_transformation(
            simple_point_cloud, sample_rotation
        )

        # Recover transformation
        transform = RegistrationAlgorithms.pca_registration(
            simple_point_cloud, rotated
        )

        # Should be close to the original rotation
        assert np.allclose(transform[:3, :3], sample_rotation[:3, :3], atol=0.1)


class TestICPRefinement:
    """Test ICP refinement algorithm."""

    def test_converges_on_perfect_match(self, simple_point_cloud, identity_transform):
        """Test ICP converges immediately for identical clouds."""
        transform, iterations, error = RegistrationAlgorithms.icp_refinement(
            simple_point_cloud,
            simple_point_cloud,
            identity_transform,
            max_iterations=50,
            tolerance=1e-7
        )

        # Should converge in few iterations
        assert iterations < 5
        assert error < 1e-6

    def test_refines_translation(self, simple_point_cloud):
        """Test ICP refines an initial estimate."""
        # Create target with small translation
        target = simple_point_cloud + np.array([1, 1, 1])

        # Start with identity
        initial = np.eye(4)

        transform, iterations, error = RegistrationAlgorithms.icp_refinement(
            simple_point_cloud,
            target,
            initial,
            max_iterations=50,
            tolerance=1e-7
        )

        # Should have low error after refinement
        assert error < 0.5

    def test_max_iterations_exceeded(self, simple_point_cloud):
        """Test ICP raises error when max iterations exceeded."""
        # Create very different clouds
        target = simple_point_cloud * 100 + 1000

        with pytest.raises(ConvergenceError, match="did not converge"):
            RegistrationAlgorithms.icp_refinement(
                simple_point_cloud,
                target,
                np.eye(4),
                max_iterations=5,  # Low limit
                tolerance=1e-7
            )


class TestApplyTransformation:
    """Test apply_transformation utility."""

    def test_identity_transformation(self, simple_point_cloud, identity_transform):
        """Test identity transformation leaves points unchanged."""
        transformed = RegistrationAlgorithms.apply_transformation(
            simple_point_cloud, identity_transform
        )

        assert np.allclose(transformed, simple_point_cloud)

    def test_translation(self, simple_point_cloud):
        """Test translation transformation."""
        T = np.eye(4)
        translation = np.array([5, 10, 15])
        T[:3, 3] = translation

        transformed = RegistrationAlgorithms.apply_transformation(
            simple_point_cloud, T
        )

        expected = simple_point_cloud + translation
        assert np.allclose(transformed, expected)

    def test_rotation(self, simple_point_cloud, sample_rotation):
        """Test rotation transformation."""
        transformed = RegistrationAlgorithms.apply_transformation(
            simple_point_cloud, sample_rotation
        )

        # Shape should be preserved
        assert transformed.shape == simple_point_cloud.shape

        # Points should be different (unless all at origin)
        assert not np.allclose(transformed, simple_point_cloud)
