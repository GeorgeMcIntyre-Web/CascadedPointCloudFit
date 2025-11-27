"""Input validation for point clouds and parameters."""

import numpy as np
from typing import Tuple
from cascaded_fit.utils.exceptions import (
    PointCloudValidationError,
    InsufficientPointsError
)
from cascaded_fit.utils.config import Config


class PointCloudValidator:
    """Validate point cloud data."""

    def __init__(self):
        self.min_points = Config.get('validation.min_points', 100)
        self.max_points = Config.get('validation.max_points', 10_000_000)
        self.check_nan = Config.get('validation.check_nan', True)
        self.check_inf = Config.get('validation.check_inf', True)

    def validate(self, points: np.ndarray, name: str = "point cloud") -> None:
        """
        Validate point cloud array.

        Args:
            points: Nx3 numpy array
            name: Name for error messages

        Raises:
            PointCloudValidationError: If validation fails
        """
        # Check type
        if not isinstance(points, np.ndarray):
            raise PointCloudValidationError(
                f"{name} must be numpy array, got {type(points)}"
            )

        # Check shape
        if points.ndim != 2:
            raise PointCloudValidationError(
                f"{name} must be 2D array, got shape {points.shape}"
            )

        if points.shape[1] != 3:
            raise PointCloudValidationError(
                f"{name} must have 3 columns (x,y,z), got {points.shape[1]}"
            )

        # Check point count
        n_points = len(points)
        if n_points < self.min_points:
            raise InsufficientPointsError(n_points, self.min_points)

        if n_points > self.max_points:
            raise PointCloudValidationError(
                f"{name} has too many points: {n_points} > {self.max_points}"
            )

        # Check for NaN or Inf
        if self.check_nan and self.check_inf:
            if not np.isfinite(points).all():
                raise PointCloudValidationError(
                    f"{name} contains NaN or Inf values"
                )

        # Check for empty point cloud (all zeros)
        if np.allclose(points, 0):
            raise PointCloudValidationError(
                f"{name} appears to be all zeros"
            )

    def validate_pair(self, source: np.ndarray, target: np.ndarray) -> None:
        """Validate source and target point clouds for registration."""
        self.validate(source, "source")
        self.validate(target, "target")

        # Check size compatibility
        if len(source) < 10 or len(target) < 10:
            raise InsufficientPointsError(
                min(len(source), len(target)), 10
            )


class TransformationValidator:
    """Validate transformation matrices."""

    @staticmethod
    def validate(transform: np.ndarray) -> None:
        """
        Validate 4x4 transformation matrix.

        Args:
            transform: 4x4 transformation matrix

        Raises:
            PointCloudValidationError: If validation fails
        """
        if not isinstance(transform, np.ndarray):
            raise PointCloudValidationError(
                f"Transform must be numpy array, got {type(transform)}"
            )

        if transform.shape != (4, 4):
            raise PointCloudValidationError(
                f"Transform must be 4x4, got shape {transform.shape}"
            )

        if not np.isfinite(transform).all():
            raise PointCloudValidationError(
                "Transform contains NaN or Inf values"
            )

        # Check bottom row is [0, 0, 0, 1]
        expected_bottom = np.array([0, 0, 0, 1])
        if not np.allclose(transform[3, :], expected_bottom):
            raise PointCloudValidationError(
                f"Transform bottom row must be [0,0,0,1], got {transform[3,:]}"
            )

        # Check rotation matrix properties (top-left 3x3)
        R = transform[:3, :3]

        # Check orthogonality: R @ R.T should be identity
        I = np.eye(3)
        if not np.allclose(R @ R.T, I, atol=1e-6):
            raise PointCloudValidationError(
                "Rotation matrix is not orthogonal"
            )

        # Check determinant is +1 (proper rotation)
        det = np.linalg.det(R)
        if not np.isclose(det, 1.0, atol=1e-6):
            raise PointCloudValidationError(
                f"Rotation matrix determinant must be 1, got {det}"
            )
