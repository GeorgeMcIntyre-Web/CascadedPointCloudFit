"""
Refactored Flask REST API for point cloud registration.

This module provides a REST API endpoint for point cloud registration.
All code duplication has been removed - uses shared modules from cascaded_fit.
"""

from flask import Flask, request, jsonify
import numpy as np
from typing import Dict, Any, Tuple

from cascaded_fit.utils.logger import Logger
from cascaded_fit.utils.config import Config
from cascaded_fit.utils.exceptions import (
    CascadedFitError,
    PointCloudValidationError,
    RegistrationError
)
from cascaded_fit.core.validators import PointCloudValidator
from cascaded_fit.core.registration import RegistrationAlgorithms
from cascaded_fit.core.metrics import MetricsCalculator
from cascaded_fit.fitters.icp_fitter import IcpFitter, FitResult
from cascaded_fit.fitters.fgr_fitter import FgrFitter

# Initialize logger and config
logger = Logger.get(__name__)
config = Config()

# Create Flask app
app = Flask(__name__)


class PointCloudAPI:
    """
    Point cloud registration API handler.

    Handles bidirectional registration (forward and reverse) and returns
    the best result based on RMSE.
    """

    def __init__(self):
        """Initialize API with configuration."""
        api_config = config.get_api_config()
        self.rmse_threshold = api_config.rmse_threshold
        self.enable_bidirectional = api_config.enable_bidirectional

        # Initialize validators
        self.validator = PointCloudValidator()

        # Initialize fitters
        self.icp_fitter = IcpFitter()
        self.fgr_fitter = FgrFitter()

        logger.info(
            f"API initialized with RMSE threshold: {self.rmse_threshold}, "
            f"bidirectional: {self.enable_bidirectional}"
        )

    def align_cloud_sizes(
        self,
        source: np.ndarray,
        target: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Align point cloud sizes by truncating to minimum size.

        Args:
            source: Source point cloud (N, 3)
            target: Target point cloud (M, 3)

        Returns:
            Tuple of (aligned_source, aligned_target) with same size
        """
        min_size = min(len(source), len(target))

        if len(source) != len(target):
            logger.warning(
                f"Cloud size mismatch: source={len(source)}, "
                f"target={len(target)}. Aligning to {min_size} points."
            )

        return source[:min_size], target[:min_size]

    def register_with_fallback(
        self,
        source: np.ndarray,
        target: np.ndarray
    ) -> Tuple[np.ndarray, float, float, str]:
        """
        Register point clouds using custom ICP with FGR fallback.

        Tries custom PCA+ICP refinement first. If RMSE exceeds threshold,
        falls back to FGR+ICP pipeline.

        Args:
            source: Source point cloud (N, 3)
            target: Target point cloud (N, 3)

        Returns:
            Tuple of (transformation, rmse, max_error, method_name)
        """
        # Method 1: Custom PCA + ICP refinement
        logger.info("Attempting custom PCA + ICP refinement")

        try:
            # PCA initial alignment
            initial_transform = RegistrationAlgorithms.pca_registration(
                source, target
            )

            # ICP refinement
            refined_transform = RegistrationAlgorithms.icp_refinement(
                source, target, initial_transform
            )

            # Compute metrics
            metrics = MetricsCalculator.compute_metrics(
                source, target, refined_transform
            )

            rmse_custom = metrics['RMSE']
            max_error_custom = metrics['Max Error']

            logger.info(f"Custom ICP: RMSE={rmse_custom:.6f}")

            if rmse_custom <= self.rmse_threshold:
                logger.info("Custom ICP succeeded")
                return (
                    refined_transform,
                    rmse_custom,
                    max_error_custom,
                    "Custom ICP"
                )

        except RegistrationError as e:
            logger.warning(f"Custom ICP failed: {e}")

        # Method 2: FGR + ICP fallback
        logger.info("Falling back to FGR + ICP pipeline")

        try:
            # Try FGR first
            fgr_result = self.fgr_fitter.fit(source, target)

            if fgr_result.is_success:
                logger.info("FGR registration succeeded")
                metrics = MetricsCalculator.compute_metrics(
                    source, target, fgr_result.transformation
                )
                return (
                    fgr_result.transformation,
                    fgr_result.inlier_rmse,
                    metrics['Max Error'],
                    "FGR"
                )

            # Try ICP as last resort
            icp_result = self.icp_fitter.fit(source, target)

            if icp_result.is_success:
                logger.info("ICP registration succeeded")
                metrics = MetricsCalculator.compute_metrics(
                    source, target, icp_result.transformation
                )
                return (
                    icp_result.transformation,
                    icp_result.inlier_rmse,
                    metrics['Max Error'],
                    "ICP"
                )

            # Both failed - return identity
            logger.warning("All registration methods failed")
            identity = np.eye(4)
            metrics = MetricsCalculator.compute_metrics(
                source, target, identity
            )
            return (
                identity,
                metrics['RMSE'],
                metrics['Max Error'],
                "Failed (Identity)"
            )

        except Exception as e:
            logger.error(f"Fallback registration failed: {e}")
            raise RegistrationError(f"All registration methods failed: {e}")

    def process_point_clouds(
        self,
        source_points: np.ndarray,
        target_points: np.ndarray
    ) -> Dict[str, Any]:
        """
        Process point cloud registration request.

        Performs bidirectional registration if enabled and returns best result.

        Args:
            source_points: Source point cloud (N, 3)
            target_points: Target point cloud (M, 3)

        Returns:
            Dictionary with transformation, RMSE, max_error, and success flag
        """
        logger.info(
            f"Processing point clouds: source={len(source_points)} pts, "
            f"target={len(target_points)} pts"
        )

        # Validate inputs
        self.validator.validate_pair(source_points, target_points)

        # Align cloud sizes
        source_aligned, target_aligned = self.align_cloud_sizes(
            source_points, target_points
        )

        # Forward registration
        logger.info("Starting forward registration (source -> target)")
        (
            transform_fwd,
            rmse_fwd,
            max_error_fwd,
            method_fwd
        ) = self.register_with_fallback(source_aligned, target_aligned)

        best_transform = transform_fwd
        best_rmse = rmse_fwd
        best_max_error = max_error_fwd
        best_method = f"Forward {method_fwd}"

        # Reverse registration (if enabled)
        if self.enable_bidirectional:
            logger.info("Starting reverse registration (target -> source)")
            try:
                (
                    transform_rev,
                    rmse_rev,
                    max_error_rev,
                    method_rev
                ) = self.register_with_fallback(target_aligned, source_aligned)

                # Choose best result
                if rmse_rev < rmse_fwd:
                    logger.info(
                        f"Reverse registration better: "
                        f"{rmse_rev:.6f} < {rmse_fwd:.6f}"
                    )
                    # Invert transformation for reverse
                    best_transform = np.linalg.inv(transform_rev)
                    best_rmse = rmse_rev
                    best_max_error = max_error_rev
                    best_method = f"Reverse {method_rev}"
                else:
                    logger.info(
                        f"Forward registration better: "
                        f"{rmse_fwd:.6f} <= {rmse_rev:.6f}"
                    )

            except Exception as e:
                logger.warning(f"Reverse registration failed: {e}")

        logger.info(
            f"Registration complete: method={best_method}, "
            f"RMSE={best_rmse:.6f}, max_error={best_max_error:.6f}"
        )

        # Create result
        fit_result = FitResult(
            transformation=best_transform,
            inlier_rmse=best_rmse,
            rmse_threshold=self.rmse_threshold,
            max_error=best_max_error
        )

        return {
            "transformation": fit_result.transformation.tolist(),
            "inlier_rmse": float(fit_result.inlier_rmse),
            "max_error": float(fit_result.max_error),
            "is_success": fit_result.is_success,
            "method": best_method
        }


# Initialize API handler
api_handler = PointCloudAPI()


@app.route('/process_point_clouds', methods=['POST'])
def process_point_clouds_endpoint():
    """
    REST API endpoint for point cloud registration.

    Request JSON format:
    {
        "source_points": [[x1, y1, z1], [x2, y2, z2], ...],
        "target_points": [[x1, y1, z1], [x2, y2, z2], ...]
    }

    Response JSON format:
    {
        "transformation": [[4x4 matrix]],
        "inlier_rmse": float,
        "max_error": float,
        "is_success": bool,
        "method": str
    }

    Returns:
        JSON response with registration results or error
    """
    try:
        # Parse request
        data = request.get_json()

        if not data:
            logger.error("No JSON data in request")
            return jsonify({'error': 'No JSON data provided'}), 400

        if 'source_points' not in data or 'target_points' not in data:
            logger.error("Missing required fields in request")
            return jsonify({
                'error': 'Missing required fields: source_points, target_points'
            }), 400

        # Convert to numpy arrays
        source_points = np.array(data['source_points'])
        target_points = np.array(data['target_points'])

        # Process registration
        result = api_handler.process_point_clouds(source_points, target_points)

        return jsonify(result)

    except PointCloudValidationError as e:
        logger.error(f"Validation error: {e}")
        return jsonify({'error': f'Validation error: {str(e)}'}), 400

    except RegistrationError as e:
        logger.error(f"Registration error: {e}")
        return jsonify({'error': f'Registration error: {str(e)}'}), 500

    except CascadedFitError as e:
        logger.error(f"Application error: {e}")
        return jsonify({'error': str(e)}), 500

    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'point-cloud-registration-api'
    })


def create_app(config_path: str = None) -> Flask:
    """
    Factory function to create Flask app.

    Args:
        config_path: Optional path to configuration file

    Returns:
        Configured Flask app
    """
    if config_path:
        config.load_config(config_path)

    logger.info("Flask app created successfully")
    return app


if __name__ == '__main__':
    # Setup logging
    Logger.setup(log_file='logs/api.log', level='INFO')

    # Get API configuration
    api_config = config.get_api_config()

    logger.info(
        f"Starting Flask API on {api_config.host}:{api_config.port}, "
        f"debug={api_config.debug}"
    )

    # Run Flask app
    app.run(
        debug=api_config.debug,
        host=api_config.host,
        port=api_config.port
    )
