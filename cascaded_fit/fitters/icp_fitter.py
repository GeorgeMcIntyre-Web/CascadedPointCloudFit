"""ICP (Iterative Closest Point) fitter."""

import time
import numpy as np
import open3d as o3d
from cascaded_fit.utils.logger import Logger
from cascaded_fit.utils.config import Config
from cascaded_fit.utils.exceptions import RegistrationError

logger = Logger.get(__name__)


class FitResult:
    """Result from point cloud fitting."""

    def __init__(self, transformation: np.ndarray, inlier_rmse: float,
                 rmse_threshold: float, max_error: float):
        self.transformation = transformation
        self.inlier_rmse = inlier_rmse
        self.max_error = max_error
        self.rmse_threshold = rmse_threshold
        self.is_success = self.inlier_rmse < self.rmse_threshold

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "transformation": self.transformation.tolist() if isinstance(self.transformation, np.ndarray) else self.transformation,
            "inlier_rmse": float(self.inlier_rmse),
            "max_error": float(self.max_error),
            "rmse_threshold": float(self.rmse_threshold),
            "is_success": bool(self.is_success)
        }


class IcpFitter:
    """ICP-based point cloud fitter."""

    def __init__(self, rmse_threshold: float = None,
                 max_correspondence_distance: float = None,
                 relative_fitness: float = None,
                 relative_rmse: float = None,
                 max_iteration: int = None):
        """
        Initialize ICP fitter.

        Args:
            rmse_threshold: RMSE threshold for success
            max_correspondence_distance: Maximum correspondence distance
            relative_fitness: Relative fitness threshold
            relative_rmse: Relative RMSE threshold
            max_iteration: Maximum iterations
        """
        # Load from config if not provided
        config = Config()
        reg_config = config.get_registration_config()
        icp_config = config.get_icp_config()

        self.rmse_threshold = rmse_threshold or reg_config.rmse_threshold
        self.max_correspondence_distance = max_correspondence_distance or icp_config.max_correspondence_distance
        self.relative_fitness = relative_fitness or icp_config.relative_fitness
        self.relative_rmse = relative_rmse or icp_config.relative_rmse
        self.max_iteration = max_iteration or reg_config.max_iterations

        logger.info(f"IcpFitter initialized: threshold={self.rmse_threshold}, max_iter={self.max_iteration}")

    def fit(self, source_cloud, target_cloud, initial_guess_transformation=None):
        """
        Fit source cloud to target cloud using ICP.

        Args:
            source_cloud: Source point cloud (Open3D)
            target_cloud: Target point cloud (Open3D)
            initial_guess_transformation: Initial 4x4 transformation matrix

        Returns:
            FitResult object
        """
        if initial_guess_transformation is None:
            initial_guess_transformation = np.identity(4)

        self.source_cloud = source_cloud
        self.target_cloud = target_cloud
        self.initial_guess_transformation = initial_guess_transformation

        # Check if we should swap for efficiency
        source_size = len(np.asarray(source_cloud.points))
        target_size = len(np.asarray(target_cloud.points))

        if source_size > target_size:
            logger.warning(f"Source cloud ({source_size} pts) larger than target ({target_size} pts), swapping for efficiency")
            # Swap and invert transformation
            result = self._fit_swapped()
            return result

        # Forward ICP
        forward_result = self.forward_icp()
        if forward_result.is_success:
            return forward_result

        # Reverse ICP if forward fails
        reverse_result = self.reverse_icp()
        return reverse_result

    def _fit_swapped(self):
        """Fit with swapped source and target."""
        initial_inv = np.linalg.inv(self.initial_guess_transformation)
        result = self._execute_icp(self.target_cloud, self.source_cloud, initial_inv)
        result.transformation = np.linalg.inv(result.transformation)
        return result

    def forward_icp(self):
        """Execute forward ICP."""
        logger.info("Trying forward ICP fit...")
        result = self._execute_icp(self.source_cloud, self.target_cloud,
                                   self.initial_guess_transformation)
        return result

    def reverse_icp(self):
        """Execute reverse ICP."""
        logger.info("Trying reverse ICP fit...")
        initial_guess_transformation_reversed = np.linalg.inv(self.initial_guess_transformation)
        result = self._execute_icp(self.target_cloud, self.source_cloud,
                                   initial_guess_transformation_reversed)
        result.transformation = np.linalg.inv(result.transformation)
        return result

    def _execute_icp(self, source_cloud, target_cloud, initial_guess_transformation):
        """Execute ICP registration."""
        start_time = time.time()

        try:
            criteria = o3d.pipelines.registration.ICPConvergenceCriteria(
                relative_fitness=self.relative_fitness,
                relative_rmse=self.relative_rmse,
                max_iteration=self.max_iteration
            )

            registration_icp = o3d.pipelines.registration.registration_icp(
                source_cloud,
                target_cloud,
                max_correspondence_distance=self.max_correspondence_distance,
                init=initial_guess_transformation,
                criteria=criteria
            )

            icp_time = time.time() - start_time

            logger.info(f"ICP completed in {icp_time:.3f}s")
            logger.debug(f"ICP Fitness: {registration_icp.fitness:.6f}")
            logger.debug(f"ICP RMSE: {registration_icp.inlier_rmse:.6f}")

            # Estimate max error (using 3x RMSE as proxy)
            max_error = registration_icp.inlier_rmse * 3

            result = FitResult(
                registration_icp.transformation,
                registration_icp.inlier_rmse,
                self.rmse_threshold,
                max_error
            )
            return result

        except Exception as e:
            logger.error(f"ICP execution failed: {e}", exc_info=True)
            raise RegistrationError(f"ICP failed: {e}")
