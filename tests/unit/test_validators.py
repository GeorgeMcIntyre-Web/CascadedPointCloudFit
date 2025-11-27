"""Unit tests for validators."""

import pytest
import numpy as np
from cascaded_fit.core.validators import PointCloudValidator, TransformationValidator
from cascaded_fit.utils.exceptions import (
    PointCloudValidationError,
    InsufficientPointsError
)


class TestPointCloudValidator:
    """Test PointCloudValidator class."""

    def test_valid_point_cloud(self, simple_point_cloud):
        """Test validation of valid point cloud."""
        validator = PointCloudValidator()
        validator.validate(simple_point_cloud)  # Should not raise

    def test_invalid_type(self):
        """Test validation fails for non-numpy array."""
        validator = PointCloudValidator()
        with pytest.raises(PointCloudValidationError, match="must be numpy array"):
            validator.validate([[1, 2, 3]], "test")

    def test_wrong_dimensions(self):
        """Test validation fails for wrong number of dimensions."""
        validator = PointCloudValidator()
        points_1d = np.array([1, 2, 3])
        with pytest.raises(PointCloudValidationError, match="must be 2D array"):
            validator.validate(points_1d)

    def test_wrong_column_count(self):
        """Test validation fails for wrong column count."""
        validator = PointCloudValidator()
        points_2col = np.random.rand(100, 2)
        with pytest.raises(PointCloudValidationError, match="must have 3 columns"):
            validator.validate(points_2col)

    def test_insufficient_points(self):
        """Test validation fails for too few points."""
        validator = PointCloudValidator()
        points_few = np.random.rand(50, 3)
        with pytest.raises(InsufficientPointsError):
            validator.validate(points_few)

    def test_nan_values(self):
        """Test validation fails for NaN values."""
        validator = PointCloudValidator()
        points_nan = np.random.rand(200, 3)
        points_nan[10, 1] = np.nan
        with pytest.raises(PointCloudValidationError, match="NaN or Inf"):
            validator.validate(points_nan)

    def test_inf_values(self):
        """Test validation fails for Inf values."""
        validator = PointCloudValidator()
        points_inf = np.random.rand(200, 3)
        points_inf[15, 2] = np.inf
        with pytest.raises(PointCloudValidationError, match="NaN or Inf"):
            validator.validate(points_inf)

    def test_all_zeros(self):
        """Test validation fails for all-zero point cloud."""
        validator = PointCloudValidator()
        points_zeros = np.zeros((200, 3))
        with pytest.raises(PointCloudValidationError, match="all zeros"):
            validator.validate(points_zeros)

    def test_validate_pair(self, simple_point_cloud):
        """Test pair validation."""
        validator = PointCloudValidator()
        target = simple_point_cloud + 10
        validator.validate_pair(simple_point_cloud, target)  # Should not raise


class TestTransformationValidator:
    """Test TransformationValidator class."""

    def test_valid_identity(self, identity_transform):
        """Test validation of identity matrix."""
        TransformationValidator.validate(identity_transform)  # Should not raise

    def test_valid_rotation(self, sample_rotation):
        """Test validation of rotation matrix."""
        TransformationValidator.validate(sample_rotation)  # Should not raise

    def test_valid_translation(self, sample_translation):
        """Test validation of translation matrix."""
        TransformationValidator.validate(sample_translation)  # Should not raise

    def test_invalid_type(self):
        """Test validation fails for non-numpy array."""
        with pytest.raises(PointCloudValidationError, match="must be numpy array"):
            TransformationValidator.validate([[1, 0], [0, 1]])

    def test_wrong_shape(self):
        """Test validation fails for wrong shape."""
        transform_3x3 = np.eye(3)
        with pytest.raises(PointCloudValidationError, match="must be 4x4"):
            TransformationValidator.validate(transform_3x3)

    def test_nan_values(self, identity_transform):
        """Test validation fails for NaN values."""
        transform = identity_transform.copy()
        transform[0, 0] = np.nan
        with pytest.raises(PointCloudValidationError, match="NaN or Inf"):
            TransformationValidator.validate(transform)

    def test_invalid_bottom_row(self, identity_transform):
        """Test validation fails for invalid bottom row."""
        transform = identity_transform.copy()
        transform[3, 0] = 1.0
        with pytest.raises(PointCloudValidationError, match="bottom row must be"):
            TransformationValidator.validate(transform)

    def test_non_orthogonal_rotation(self, identity_transform):
        """Test validation fails for non-orthogonal rotation."""
        transform = identity_transform.copy()
        transform[0, 0] = 2.0  # Not orthogonal
        with pytest.raises(PointCloudValidationError, match="not orthogonal"):
            TransformationValidator.validate(transform)

    def test_wrong_determinant(self, identity_transform):
        """Test validation fails for reflection (det=-1)."""
        transform = identity_transform.copy()
        transform[0, 0] = -1.0  # Reflection
        with pytest.raises(PointCloudValidationError, match="determinant must be 1"):
            TransformationValidator.validate(transform)
