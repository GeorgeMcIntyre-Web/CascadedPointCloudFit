"""Cascaded fitter combining ICP and FGR."""

import time
import open3d as o3d
import copy
from typing import Dict, Any, Optional
from cascaded_fit.utils.logger import Logger
from cascaded_fit.utils.exceptions import RegistrationError, ConvergenceError
from cascaded_fit.io.readers import PointCloudReader

logger = Logger.get(__name__)


class CascadedFitter:
    """Orchestrates cascaded registration using ICP and FGR."""

    def __init__(self, icp_fitter=None, fgr_fitter=None, visualise: bool = False,
                 visualize: bool = False, **kwargs):
        """
        Initialize cascaded fitter.

        Args:
            icp_fitter: ICP fitter instance (created if None)
            fgr_fitter: FGR fitter instance (created if None)
            visualise: Whether to visualize results (British spelling)
            visualize: Whether to visualize results (American spelling)
            **kwargs: Additional parameters passed to fitters
        """
        # Import here to avoid circular dependency
        from cascaded_fit.fitters.icp_fitter import IcpFitter
        from cascaded_fit.fitters.fgr_fitter import FgrFitter

        # Create fitters if not provided
        self.icp_fitter = icp_fitter or IcpFitter(**kwargs)
        self.fgr_fitter = fgr_fitter or FgrFitter(**kwargs)

        # Support both spellings of visualize
        self.visualise = visualise or visualize

        logger.info("CascadedFitter initialized")

    def run(self, source_file: str, target_file: str) -> Dict[str, Any]:
        """
        Run cascaded registration pipeline.

        Args:
            source_file: Path to source point cloud file
            target_file: Path to target point cloud file

        Returns:
            Registration result dictionary

        Raises:
            RegistrationError: If registration fails
        """
        logger.info(f"Starting cascaded registration: {source_file} -> {target_file}")
        self.start_time = time.time()

        try:
            self._read_point_clouds(source_file, target_file)

            # Try ICP first
            icp_result = self._try_icp_fit()
            if icp_result.is_success:
                self._print_result(icp_result, "ICP")
                return self._create_result_dict(icp_result, "ICP")

            # Try FGR if ICP fails
            logger.warning("ICP failed, trying FGR")
            fgr_result = self._try_fgr_fit()
            if fgr_result.is_success:
                self._print_result(fgr_result, "FGR+ICP")
                return self._create_result_dict(fgr_result, "FGR+ICP")

            # Both failed
            logger.error("Both ICP and FGR fits failed")
            raise ConvergenceError("ICP and FGR fits failed. RMSE threshold could not be achieved.")

        except Exception as e:
            logger.error(f"Cascaded registration failed: {e}", exc_info=True)
            if isinstance(e, (RegistrationError, ConvergenceError)):
                raise
            raise RegistrationError(f"Registration failed: {e}")

    def _read_point_clouds(self, source_file: str, target_file: str):
        """Read source and target point clouds."""
        logger.debug(f"Reading source: {source_file}")
        self.source_cloud = PointCloudReader.read_point_cloud_file(source_file)

        logger.debug(f"Reading target: {target_file}")
        self.target_cloud = PointCloudReader.read_point_cloud_file(target_file)

        logger.info(f"Loaded {len(self.source_cloud.points)} source and "
                   f"{len(self.target_cloud.points)} target points")

    def _try_icp_fit(self):
        """Try ICP fit."""
        logger.debug("Attempting ICP fit")
        result = self.icp_fitter.fit(self.source_cloud, self.target_cloud)
        return result

    def _try_fgr_fit(self):
        """Try FGR fit."""
        logger.debug("Attempting FGR fit")
        result = self.fgr_fitter.fit(self.source_cloud, self.target_cloud)
        return result

    def _print_result(self, fit_result, method_name: str):
        """Print registration result."""
        from cascaded_fit.core.transformations import TransformationUtils

        transformation_string = TransformationUtils.array_to_csv_string(fit_result.transformation)

        total_time = time.time() - self.start_time
        logger.info(f"Registration succeeded using {method_name}")
        logger.info(f"Total execution time: {total_time:.3f}s")
        logger.info(f"RMSE: {fit_result.inlier_rmse:.6f}")

        print(f"\n<Transformation matrix>")
        print(transformation_string)
        print(f"<\\Transformation matrix>")
        print(f"\nRMS: {fit_result.inlier_rmse:.50f}")

        if self.visualise:
            self._visualise_results(fit_result)

    def _visualise_results(self, fit_result):
        """Visualize registration results."""
        logger.debug("Visualizing results")

        # Visualize before registration
        source_temp = copy.deepcopy(self.source_cloud)
        target_temp = copy.deepcopy(self.target_cloud)
        source_temp.paint_uniform_color([1, 0.706, 0])  # Orange
        target_temp.paint_uniform_color([0, 0.651, 0.929])  # Blue
        o3d.visualization.draw_geometries([source_temp, target_temp])

        # Visualize after registration
        source_temp = copy.deepcopy(self.source_cloud)
        target_temp = copy.deepcopy(self.target_cloud)
        source_temp.paint_uniform_color([1, 0.706, 0])
        target_temp.paint_uniform_color([0, 0.651, 0.929])
        source_temp.transform(fit_result.transformation)
        o3d.visualization.draw_geometries([source_temp, target_temp])

    def _create_result_dict(self, fit_result, method: str = "Unknown") -> Dict[str, Any]:
        """Create result dictionary."""
        if fit_result is None:
            return {
                "transformation": None,
                "inlier_rmse": None,
                "max_error": None,
                "is_success": False,
                "method": method
            }

        return {
            "transformation": fit_result.transformation.tolist(),
            "inlier_rmse": fit_result.inlier_rmse,
            "max_error": fit_result.max_error,
            "is_success": fit_result.is_success,
            "method": method
        }
