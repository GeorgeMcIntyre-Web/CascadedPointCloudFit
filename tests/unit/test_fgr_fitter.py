"""Unit tests for FgrFitter."""

import pytest
import numpy as np
import open3d as o3d
from unittest.mock import Mock, patch
from cascaded_fit.fitters.fgr_fitter import FgrFitter
from cascaded_fit.fitters.icp_fitter import IcpFitter
from cascaded_fit.utils.exceptions import RegistrationError


@pytest.fixture
def sample_point_clouds():
    """Create sample Open3D point clouds."""
    np.random.seed(42)
    source_points = np.random.rand(100, 3) * 10.0
    target_points = source_points + np.array([1.0, 1.0, 1.0])
    
    source_cloud = o3d.geometry.PointCloud()
    source_cloud.points = o3d.utility.Vector3dVector(source_points)
    
    target_cloud = o3d.geometry.PointCloud()
    target_cloud.points = o3d.utility.Vector3dVector(target_points)
    
    return source_cloud, target_cloud


class TestFgrFitterInitialization:
    """Test FgrFitter initialization."""

    def test_init_default(self):
        """Test initialization with default values."""
        fitter = FgrFitter()
        assert fitter.rmse_threshold is not None
        assert fitter.voxel_size is not None
        assert fitter.icp_fitter is None

    def test_init_custom_params(self):
        """Test initialization with custom parameters."""
        icp = IcpFitter()
        fitter = FgrFitter(
            rmse_threshold=0.001,
            distance_threshold=0.01,
            voxel_size=5.0,
            icp_fitter=icp
        )
        assert fitter.rmse_threshold == 0.001
        assert fitter.distance_threshold == 0.01
        assert fitter.voxel_size == 5.0
        assert fitter.icp_fitter is icp


class TestFgrFitterFit:
    """Test FgrFitter.fit() method."""

    @patch('cascaded_fit.fitters.fgr_fitter.o3d.pipelines.registration.registration_fgr_based_on_feature_matching')
    def test_fit_success_with_icp(self, mock_fgr, sample_point_clouds):
        """Test successful fit with ICP refinement."""
        source_cloud, target_cloud = sample_point_clouds
        
        # Mock FGR result
        mock_fgr_result = Mock()
        mock_fgr_result.transformation = np.eye(4)
        mock_fgr.return_value = mock_fgr_result
        
        # Mock ICP fitter
        from cascaded_fit.fitters.icp_fitter import FitResult
        icp_result = FitResult(
            transformation=np.eye(4),
            inlier_rmse=0.001,
            rmse_threshold=0.01,
            max_error=0.003
        )
        
        icp_fitter = Mock()
        icp_fitter.fit.return_value = icp_result
        
        fitter = FgrFitter(icp_fitter=icp_fitter)
        result = fitter.fit(source_cloud, target_cloud)
        
        assert result.is_success is True
        assert icp_fitter.fit.called

    @patch('cascaded_fit.fitters.fgr_fitter.o3d.pipelines.registration.registration_fgr_based_on_feature_matching')
    def test_fit_without_icp_fitter(self, mock_fgr, sample_point_clouds):
        """Test fit without ICP fitter (returns FGR result only)."""
        source_cloud, target_cloud = sample_point_clouds
        
        mock_fgr_result = Mock()
        mock_fgr_result.transformation = np.eye(4)
        mock_fgr.return_value = mock_fgr_result
        
        fitter = FgrFitter(icp_fitter=None)
        result = fitter.fit(source_cloud, target_cloud)
        
        assert result is not None
        assert result.inlier_rmse == 0.0  # FGR doesn't provide RMSE

    @patch('cascaded_fit.fitters.fgr_fitter.o3d.pipelines.registration.registration_fgr_based_on_feature_matching')
    def test_fit_error_handling(self, mock_fgr, sample_point_clouds):
        """Test fit error handling."""
        source_cloud, target_cloud = sample_point_clouds
        mock_fgr.side_effect = Exception("FGR error")
        
        fitter = FgrFitter()
        
        with pytest.raises(RegistrationError, match="FGR\+ICP failed"):
            fitter.fit(source_cloud, target_cloud)


class TestFgrFitterHelpers:
    """Test FgrFitter helper methods."""

    @patch('cascaded_fit.fitters.fgr_fitter.o3d.pipelines.registration.compute_fpfh_feature')
    @patch('cascaded_fit.fitters.fgr_fitter.o3d.geometry.PointCloud.estimate_normals')
    def test_calculate_fpfh(self, mock_normals, mock_fpfh, sample_point_clouds):
        """Test _calculate_fpfh method."""
        source_cloud, _ = sample_point_clouds
        
        mock_fpfh.return_value = Mock()
        
        fitter = FgrFitter(voxel_size=10.0)
        result = fitter._calculate_fpfh(source_cloud)
        
        assert result is not None
        mock_normals.assert_called_once()
        mock_fpfh.assert_called_once()

