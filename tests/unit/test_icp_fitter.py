"""Unit tests for IcpFitter."""

import pytest
import numpy as np
import open3d as o3d
from unittest.mock import Mock, patch
from cascaded_fit.fitters.icp_fitter import IcpFitter, FitResult
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


class TestIcpFitterInitialization:
    """Test IcpFitter initialization."""

    def test_init_default(self):
        """Test initialization with default values."""
        fitter = IcpFitter()
        assert fitter.rmse_threshold is not None
        assert fitter.max_iteration is not None

    def test_init_custom_params(self):
        """Test initialization with custom parameters."""
        fitter = IcpFitter(
            rmse_threshold=0.001,
            max_correspondence_distance=50.0,
            max_iteration=100
        )
        assert fitter.rmse_threshold == 0.001
        assert fitter.max_correspondence_distance == 50.0
        assert fitter.max_iteration == 100


class TestIcpFitterFit:
    """Test IcpFitter.fit() method."""

    @patch('cascaded_fit.fitters.icp_fitter.o3d.pipelines.registration.registration_icp')
    def test_fit_success_forward(self, mock_icp, sample_point_clouds):
        """Test successful forward ICP fit."""
        source_cloud, target_cloud = sample_point_clouds
        
        # Mock ICP result
        mock_result = Mock()
        mock_result.transformation = np.eye(4)
        mock_result.inlier_rmse = 0.001
        mock_result.fitness = 0.99
        mock_icp.return_value = mock_result
        
        fitter = IcpFitter(rmse_threshold=0.01)
        result = fitter.fit(source_cloud, target_cloud)
        
        assert result.is_success is True
        assert result.inlier_rmse == 0.001

    @patch('cascaded_fit.fitters.icp_fitter.o3d.pipelines.registration.registration_icp')
    def test_fit_with_initial_guess(self, mock_icp, sample_point_clouds):
        """Test fit with initial transformation guess."""
        source_cloud, target_cloud = sample_point_clouds
        
        initial_transform = np.eye(4)
        initial_transform[0, 3] = 1.0  # Translation
        
        mock_result = Mock()
        mock_result.transformation = initial_transform
        mock_result.inlier_rmse = 0.001
        mock_result.fitness = 0.99
        mock_icp.return_value = mock_result
        
        fitter = IcpFitter()
        result = fitter.fit(source_cloud, target_cloud, initial_transform)
        
        assert result.is_success is True

    @patch('cascaded_fit.fitters.icp_fitter.o3d.pipelines.registration.registration_icp')
    def test_fit_swaps_when_source_larger(self, mock_icp, sample_point_clouds):
        """Test fit swaps clouds when source is larger than target."""
        source_cloud, target_cloud = sample_point_clouds
        
        # Make source larger
        large_source = o3d.geometry.PointCloud()
        large_points = np.random.rand(200, 3) * 10.0
        large_source.points = o3d.utility.Vector3dVector(large_points)
        
        mock_result = Mock()
        mock_result.transformation = np.eye(4)
        mock_result.inlier_rmse = 0.001
        mock_result.fitness = 0.99
        mock_icp.return_value = mock_result
        
        fitter = IcpFitter()
        result = fitter.fit(large_source, target_cloud)
        
        # Should have swapped and inverted transformation
        assert result.is_success is True

    @patch('cascaded_fit.fitters.icp_fitter.o3d.pipelines.registration.registration_icp')
    def test_fit_forward_then_reverse(self, mock_icp, sample_point_clouds):
        """Test fit tries forward then reverse if forward fails."""
        source_cloud, target_cloud = sample_point_clouds
        
        # First call (forward) fails, second (reverse) succeeds
        failed_result = Mock()
        failed_result.transformation = np.eye(4)
        failed_result.inlier_rmse = 0.1  # Above threshold
        failed_result.fitness = 0.5
        
        success_result = Mock()
        success_result.transformation = np.eye(4)
        success_result.inlier_rmse = 0.001
        success_result.fitness = 0.99
        
        mock_icp.side_effect = [failed_result, success_result]
        
        fitter = IcpFitter(rmse_threshold=0.01)
        result = fitter.fit(source_cloud, target_cloud)
        
        assert result.is_success is True
        assert mock_icp.call_count == 2

    @patch('cascaded_fit.fitters.icp_fitter.o3d.pipelines.registration.registration_icp')
    def test_fit_error_handling(self, mock_icp, sample_point_clouds):
        """Test fit error handling."""
        source_cloud, target_cloud = sample_point_clouds
        mock_icp.side_effect = Exception("ICP error")
        
        fitter = IcpFitter()
        
        with pytest.raises(RegistrationError):
            fitter.fit(source_cloud, target_cloud)


class TestIcpFitterMethods:
    """Test IcpFitter helper methods."""

    @patch('cascaded_fit.fitters.icp_fitter.o3d.pipelines.registration.registration_icp')
    def test_forward_icp(self, mock_icp, sample_point_clouds):
        """Test forward_icp method."""
        source_cloud, target_cloud = sample_point_clouds
        
        mock_result = Mock()
        mock_result.transformation = np.eye(4)
        mock_result.inlier_rmse = 0.001
        mock_result.fitness = 0.99
        mock_icp.return_value = mock_result
        
        fitter = IcpFitter()
        fitter.source_cloud = source_cloud
        fitter.target_cloud = target_cloud
        fitter.initial_guess_transformation = np.eye(4)
        
        result = fitter.forward_icp()
        assert result.is_success is True

    @patch('cascaded_fit.fitters.icp_fitter.o3d.pipelines.registration.registration_icp')
    def test_reverse_icp(self, mock_icp, sample_point_clouds):
        """Test reverse_icp method."""
        source_cloud, target_cloud = sample_point_clouds
        
        mock_result = Mock()
        mock_result.transformation = np.eye(4)
        mock_result.inlier_rmse = 0.001
        mock_result.fitness = 0.99
        mock_icp.return_value = mock_result
        
        fitter = IcpFitter()
        fitter.source_cloud = source_cloud
        fitter.target_cloud = target_cloud
        fitter.initial_guess_transformation = np.eye(4)
        
        result = fitter.reverse_icp()
        assert result.is_success is True


class TestFitResult:
    """Test FitResult class."""

    def test_fit_result_success(self):
        """Test FitResult with successful registration."""
        result = FitResult(
            transformation=np.eye(4),
            inlier_rmse=0.001,
            rmse_threshold=0.01,
            max_error=0.003
        )
        assert result.is_success is True
        assert result.inlier_rmse == 0.001

    def test_fit_result_failure(self):
        """Test FitResult with failed registration."""
        result = FitResult(
            transformation=np.eye(4),
            inlier_rmse=0.1,  # Above threshold
            rmse_threshold=0.01,
            max_error=0.3
        )
        assert result.is_success is False

    def test_fit_result_to_dict(self):
        """Test FitResult.to_dict() method."""
        result = FitResult(
            transformation=np.eye(4),
            inlier_rmse=0.001,
            rmse_threshold=0.01,
            max_error=0.003
        )
        result_dict = result.to_dict()
        
        assert result_dict['is_success'] is True
        assert result_dict['inlier_rmse'] == 0.001
        assert isinstance(result_dict['transformation'], list)

