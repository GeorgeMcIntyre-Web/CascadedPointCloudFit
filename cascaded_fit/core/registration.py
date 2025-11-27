"""Core registration algorithms with logging and validation."""

import numpy as np
from scipy.spatial import cKDTree
from typing import Tuple
from cascaded_fit.utils.logger import Logger
from cascaded_fit.utils.exceptions import RegistrationError, ConvergenceError
from cascaded_fit.core.validators import PointCloudValidator, TransformationValidator

logger = Logger.get(__name__)


class RegistrationAlgorithms:
    """Point cloud registration algorithms."""

    @staticmethod
    def pca_registration(source: np.ndarray, target: np.ndarray) -> np.ndarray:
        """
        PCA-based initial alignment.

        Args:
            source: Source point cloud (Nx3)
            target: Target point cloud (Mx3)

        Returns:
            4x4 transformation matrix

        Raises:
            RegistrationError: If registration fails
        """
        logger.info("Starting PCA registration")

        try:
            # Validate inputs
            validator = PointCloudValidator()
            validator.validate_pair(source, target)

            # Compute centroids
            source_mean = np.mean(source, axis=0)
            target_mean = np.mean(target, axis=0)
            logger.debug(f"Source centroid: {source_mean}")
            logger.debug(f"Target centroid: {target_mean}")

            # Center point clouds
            source_centered = source - source_mean
            target_centered = target - target_mean

            # Compute covariance and SVD
            cov = np.dot(source_centered.T, target_centered)
            U, _, Vt = np.linalg.svd(cov)
            R = np.dot(Vt.T, U.T)

            # Ensure right-handed coordinate system
            if np.linalg.det(R) < 0:
                logger.debug("Flipping rotation matrix to ensure right-handed system")
                Vt[-1, :] *= -1
                R = np.dot(Vt.T, U.T)

            # Compute translation
            t = target_mean - np.dot(R, source_mean)

            # Build 4x4 transform
            T = np.eye(4)
            T[:3, :3] = R
            T[:3, 3] = t

            # Validate output
            TransformationValidator.validate(T)

            logger.info("PCA registration completed successfully")
            return T

        except Exception as e:
            logger.error(f"PCA registration failed: {e}", exc_info=True)
            raise RegistrationError(f"PCA registration failed: {e}")

    @staticmethod
    def icp_refinement(
        source: np.ndarray,
        target: np.ndarray,
        initial_transform: np.ndarray,
        max_iterations: int = 50,
        tolerance: float = 1e-7
    ) -> Tuple[np.ndarray, int, float]:
        """
        ICP refinement with detailed progress tracking.

        Args:
            source: Source point cloud
            target: Target point cloud
            initial_transform: Initial transformation
            max_iterations: Maximum iterations
            tolerance: Convergence tolerance

        Returns:
            Tuple of (final_transform, num_iterations, final_error)

        Raises:
            RegistrationError: If ICP fails
            ConvergenceError: If ICP doesn't converge
        """
        logger.info(f"Starting ICP refinement (max_iter={max_iterations}, tol={tolerance})")

        try:
            # Validate inputs
            validator = PointCloudValidator()
            validator.validate_pair(source, target)
            TransformationValidator.validate(initial_transform)

            # Build KD-Tree from target
            logger.debug("Building KD-Tree from target points")
            tree = cKDTree(target)

            current_transform = initial_transform.copy()
            prev_error = np.inf

            for iteration in range(max_iterations):
                # Transform source points
                transformed_source = np.dot(
                    source, current_transform[:3, :3].T
                ) + current_transform[:3, 3]

                # Find nearest neighbors
                distances, indices = tree.query(transformed_source)
                corresponding_points = target[indices]

                # Compute error
                error = np.mean(distances)

                if iteration % 10 == 0:
                    logger.debug(f"Iteration {iteration}: error = {error:.6f}")

                # Check convergence
                if np.abs(error - prev_error) < tolerance:
                    logger.info(f"ICP converged after {iteration + 1} iterations (error={error:.6f})")
                    return current_transform, iteration + 1, error

                prev_error = error

                # Compute incremental transformation via SVD
                source_mean = np.mean(transformed_source, axis=0)
                target_mean = np.mean(corresponding_points, axis=0)
                source_centered = transformed_source - source_mean
                target_centered = corresponding_points - target_mean

                cov = np.dot(source_centered.T, target_centered)
                U, _, Vt = np.linalg.svd(cov)
                R = np.dot(Vt.T, U.T)

                if np.linalg.det(R) < 0:
                    Vt[-1, :] *= -1
                    R = np.dot(Vt.T, U.T)

                t = target_mean - np.dot(R, source_mean)

                # Update cumulative transformation
                current_transform[:3, :3] = np.dot(R, current_transform[:3, :3])
                current_transform[:3, 3] = np.dot(R, current_transform[:3, 3]) + t

            # Didn't converge within max iterations
            logger.warning(f"ICP did not converge after {max_iterations} iterations (error={prev_error:.6f})")
            raise ConvergenceError(
                f"ICP did not converge after {max_iterations} iterations"
            )

        except ConvergenceError:
            raise
        except Exception as e:
            logger.error(f"ICP refinement failed: {e}", exc_info=True)
            raise RegistrationError(f"ICP refinement failed: {e}")

    @staticmethod
    def calculate_transformation_matrix(source_points: np.ndarray,
                                      transformed_points: np.ndarray) -> np.ndarray:
        """
        Calculate the transformation matrix from source to transformed points.

        Args:
            source_points: Nx3 numpy array of original points
            transformed_points: Nx3 numpy array of transformed points

        Returns:
            4x4 transformation matrix
        """
        # Center the point sets
        source_center = np.mean(source_points, axis=0)
        transformed_center = np.mean(transformed_points, axis=0)

        # Calculate the rotation matrix using SVD
        H = np.dot((source_points - source_center).T, (transformed_points - transformed_center))
        U, S, Vt = np.linalg.svd(H)
        R = np.dot(Vt.T, U.T)

        # Ensure a right-handed coordinate system
        if np.linalg.det(R) < 0:
            Vt[-1, :] *= -1
            R = np.dot(Vt.T, U.T)

        # Calculate the translation
        t = transformed_center - np.dot(R, source_center)

        # Construct the 4x4 transformation matrix
        transform = np.eye(4)
        transform[:3, :3] = R
        transform[:3, 3] = t

        return transform

    @staticmethod
    def apply_transformation(points: np.ndarray, transform: np.ndarray) -> np.ndarray:
        """
        Apply a 4x4 transformation matrix to a set of 3D points.

        Args:
            points: Nx3 numpy array of points
            transform: 4x4 transformation matrix

        Returns:
            Nx3 numpy array of transformed points
        """
        return np.dot(points, transform[:3, :3].T) + transform[:3, 3]
