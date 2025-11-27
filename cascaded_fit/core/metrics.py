"""Metrics calculation for point cloud registration."""

import numpy as np
from scipy.spatial import cKDTree
from typing import Dict
from cascaded_fit.utils.logger import Logger

logger = Logger.get(__name__)


class MetricsCalculator:
    """Calculate registration quality metrics."""

    @staticmethod
    def compute_metrics(source: np.ndarray, target: np.ndarray,
                       transform: np.ndarray) -> Dict[str, float]:
        """
        Compute registration metrics.

        Args:
            source: Source point cloud (Nx3)
            target: Target point cloud (Mx3)
            transform: 4x4 transformation matrix

        Returns:
            Dictionary with metrics: RMSE, Max Error, Mean Error, Median Error
        """
        logger.debug(f"Computing metrics for {len(source)} points")

        # Transform source points
        transformed_source = np.dot(source, transform[:3, :3].T) + transform[:3, 3]

        # Build KD-Tree and find nearest neighbors
        tree = cKDTree(target)
        distances, _ = tree.query(transformed_source)

        # Calculate metrics
        rmse = np.sqrt(np.mean(distances**2))
        max_error = np.max(distances)
        mean_error = np.mean(distances)
        median_error = np.median(distances)

        logger.debug(f"Metrics computed - RMSE: {rmse:.6f}, Max: {max_error:.6f}")

        return {
            'Transformation': transform.tolist(),
            'RMSE': float(rmse),
            'Max Error': float(max_error),
            'Mean Error': float(mean_error),
            'Median Error': float(median_error)
        }
