"""FGR (Fast Global Registration) fitter."""

import time
import open3d as o3d
from cascaded_fit.utils.logger import Logger
from cascaded_fit.utils.config import Config
from cascaded_fit.utils.exceptions import RegistrationError

logger = Logger.get(__name__)


class FgrFitter:
    """FGR-based point cloud fitter with ICP refinement."""

    def __init__(self, rmse_threshold: float = None,
                 distance_threshold: float = None,
                 voxel_size: float = None,
                 icp_fitter=None,
                 radius_normal_factor: int = None,
                 radius_feature_factor: int = None,
                 max_nn_normal: int = None,
                 max_nn_feature: int = None):
        """
        Initialize FGR fitter.

        Args:
            rmse_threshold: RMSE threshold for success
            distance_threshold: FGR distance threshold
            voxel_size: Voxel size for downsampling
            icp_fitter: ICP fitter for refinement
            radius_normal_factor: Factor for normal radius (radius = voxel_size * factor)
            radius_feature_factor: Factor for feature radius (radius = voxel_size * factor)
            max_nn_normal: Maximum nearest neighbors for normal estimation
            max_nn_feature: Maximum nearest neighbors for feature computation
        """
        # Load from config if not provided
        config = Config()
        reg_config = config.get_registration_config()
        fgr_config = config.get_fgr_config()

        self.rmse_threshold = rmse_threshold or reg_config.rmse_threshold
        self.distance_threshold = distance_threshold or fgr_config.distance_threshold
        self.voxel_size = voxel_size or fgr_config.voxel_size
        self.icp_fitter = icp_fitter

        # NEW: Configurable parameters (FIXED TODO)
        self.radius_normal_factor = radius_normal_factor or fgr_config.radius_normal_factor
        self.radius_feature_factor = radius_feature_factor or fgr_config.radius_feature_factor
        self.max_nn_normal = max_nn_normal or fgr_config.max_nn_normal
        self.max_nn_feature = max_nn_feature or fgr_config.max_nn_feature

        logger.info(f"FgrFitter initialized: voxel_size={self.voxel_size}, "
                   f"normal_factor={self.radius_normal_factor}, "
                   f"feature_factor={self.radius_feature_factor}")

    def fit(self, source_cloud, target_cloud):
        """
        Fit source cloud to target cloud using FGR + ICP.

        Args:
            source_cloud: Source point cloud (Open3D)
            target_cloud: Target point cloud (Open3D)

        Returns:
            FitResult from ICP refinement
        """
        logger.info("Trying FGR and ICP combination fit...")

        try:
            fgr_result = self._execute_fgr(source_cloud, target_cloud)

            # Improve fit using ICP with initial guess from FGR
            if self.icp_fitter is None:
                logger.warning("No ICP fitter provided, returning FGR result only")
                # Create a simple result
                from cascaded_fit.fitters.icp_fitter import FitResult
                return FitResult(
                    fgr_result.transformation,
                    0.0,  # FGR doesn't provide RMSE
                    self.rmse_threshold,
                    0.0
                )

            icp_result = self.icp_fitter.fit(source_cloud, target_cloud,
                                            fgr_result.transformation)
            return icp_result

        except Exception as e:
            logger.error(f"FGR+ICP fit failed: {e}", exc_info=True)
            raise RegistrationError(f"FGR+ICP failed: {e}")

    def _execute_fgr(self, source_cloud, target_cloud):
        """Execute FGR registration."""
        start_time = time.time()

        # Calculate FPFH features
        source_fpfh = self._calculate_fpfh(source_cloud)
        target_fpfh = self._calculate_fpfh(target_cloud)

        # FGR options
        fgr_option = o3d.pipelines.registration.FastGlobalRegistrationOption(
            maximum_correspondence_distance=self.distance_threshold
        )

        # Run FGR
        result = o3d.pipelines.registration.registration_fgr_based_on_feature_matching(
            source_cloud,
            target_cloud,
            source_fpfh,
            target_fpfh,
            fgr_option
        )

        execution_time = time.time() - start_time
        logger.info(f"FGR completed in {execution_time:.3f}s")
        logger.debug(f"FGR Distance Threshold: {self.distance_threshold}")

        return result

    def _calculate_fpfh(self, point_cloud):
        """
        Calculate FPFH (Fast Point Feature Histogram) features.

        Args:
            point_cloud: Open3D point cloud

        Returns:
            FPFH features
        """
        # Calculate radii using configurable factors (FIXED TODO)
        radius_normal = self.voxel_size * self.radius_normal_factor
        radius_feature = self.voxel_size * self.radius_feature_factor

        logger.debug(f"Estimating normals with radius {radius_normal:.3f}")
        point_cloud.estimate_normals(
            o3d.geometry.KDTreeSearchParamHybrid(
                radius=radius_normal,
                max_nn=self.max_nn_normal
            )
        )

        logger.debug(f"Computing FPFH features with radius {radius_feature:.3f}")
        kdTreeSearchParams = o3d.geometry.KDTreeSearchParamHybrid(
            radius=radius_feature,
            max_nn=self.max_nn_feature
        )
        fpfh = o3d.pipelines.registration.compute_fpfh_feature(
            point_cloud,
            kdTreeSearchParams
        )

        return fpfh
