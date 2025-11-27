"""
Shared registration algorithms for point cloud alignment.
Contains PCA registration, ICP refinement, and transformation utilities.
"""

import numpy as np
from scipy.spatial import cKDTree


class RegistrationAlgorithms:
    """Collection of point cloud registration algorithms."""

    @staticmethod
    def pca_registration(source_points, target_points):
        """
        Perform PCA-based initial alignment between source and target point clouds.

        Args:
            source_points: Nx3 numpy array of source points
            target_points: Nx3 numpy array of target points

        Returns:
            4x4 transformation matrix
        """
        source_mean = np.mean(source_points, axis=0)
        target_mean = np.mean(target_points, axis=0)
        source_centered = source_points - source_mean
        target_centered = target_points - target_mean

        cov = np.dot(source_centered.T, target_centered)
        U, _, Vt = np.linalg.svd(cov)
        R = np.dot(Vt.T, U.T)

        # Ensure right-handed coordinate system
        if np.linalg.det(R) < 0:
            Vt[-1,:] *= -1
            R = np.dot(Vt.T, U.T)

        t = target_mean - np.dot(R, source_mean)

        T = np.eye(4)
        T[:3, :3] = R
        T[:3, 3] = t
        return T

    @staticmethod
    def icp_refinement(source_points, target_points, initial_transform,
                      max_iterations=50, tolerance=1e-7):
        """
        Refine alignment using Iterative Closest Point (ICP) algorithm.

        Args:
            source_points: Nx3 numpy array of source points
            target_points: Nx3 numpy array of target points
            initial_transform: 4x4 initial transformation matrix
            max_iterations: Maximum number of iterations
            tolerance: Convergence tolerance

        Returns:
            4x4 refined transformation matrix
        """
        def closest_point(A, B):
            """Find closest points in B for each point in A."""
            tree = cKDTree(B)
            distances, indices = tree.query(A)
            return B[indices], distances

        current_transform = initial_transform.copy()
        prev_error = np.inf

        for _ in range(max_iterations):
            # Transform source points
            transformed_source = np.dot(source_points, current_transform[:3, :3].T) + current_transform[:3, 3]

            # Find closest points
            corresponding_points, distances = closest_point(transformed_source, target_points)

            # Check convergence
            error = np.mean(distances)
            if np.abs(error - prev_error) < tolerance:
                break
            prev_error = error

            # Compute new transformation using SVD
            source_mean = np.mean(transformed_source, axis=0)
            target_mean = np.mean(corresponding_points, axis=0)
            source_centered = transformed_source - source_mean
            target_centered = corresponding_points - target_mean

            cov = np.dot(source_centered.T, target_centered)
            U, _, Vt = np.linalg.svd(cov)
            R = np.dot(Vt.T, U.T)

            # Ensure right-handed coordinate system
            if np.linalg.det(R) < 0:
                Vt[-1,:] *= -1
                R = np.dot(Vt.T, U.T)

            t = target_mean - np.dot(R, source_mean)

            # Update cumulative transformation
            current_transform[:3, :3] = np.dot(R, current_transform[:3, :3])
            current_transform[:3, 3] = np.dot(R, current_transform[:3, 3]) + t

        return current_transform

    @staticmethod
    def calculate_transformation_matrix(source_points, transformed_points):
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
            Vt[-1,:] *= -1
            R = np.dot(Vt.T, U.T)

        # Calculate the translation
        t = transformed_center - np.dot(R, source_center)

        # Construct the 4x4 transformation matrix
        transform = np.eye(4)
        transform[:3, :3] = R
        transform[:3, 3] = t

        return transform

    @staticmethod
    def apply_transformation(points, transform):
        """
        Apply a 4x4 transformation matrix to a set of 3D points.

        Args:
            points: Nx3 numpy array of points
            transform: 4x4 transformation matrix

        Returns:
            Nx3 numpy array of transformed points
        """
        return np.dot(points, transform[:3, :3].T) + transform[:3, 3]
