"""Unit tests for CascadedFitter."""

import pytest
import numpy as np
import open3d as o3d
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from cascaded_fit.fitters.cascaded_fitter import CascadedFitter
from cascaded_fit.fitters.icp_fitter import IcpFitter, FitResult
from cascaded_fit.fitters.fgr_fitter import FgrFitter
from cascaded_fit.utils.exceptions import RegistrationError, ConvergenceError


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


@pytest.fixture
def mock_fit_result():
    """Create a mock FitResult."""
    return FitResult(
        transformation=np.eye(4),
        inlier_rmse=0.001,
        rmse_threshold=0.01,
        max_error=0.003
    )


class TestCascadedFitterInitialization:
    """Test CascadedFitter initialization."""

    def test_init_with_default_fitters(self):
        """Test initialization with default fitters."""
        fitter = CascadedFitter()
        assert fitter.icp_fitter is not None
        assert fitter.fgr_fitter is not None
        assert fitter.visualize is False

    def test_init_with_custom_fitters(self, sample_point_clouds):
        """Test initialization with custom fitters."""
        icp = IcpFitter()
        fgr = FgrFitter()
        fitter = CascadedFitter(icp_fitter=icp, fgr_fitter=fgr)
        assert fitter.icp_fitter is icp
        assert fitter.fgr_fitter is fgr

    def test_init_with_visualize(self):
        """Test initialization with visualize flag."""
        fitter = CascadedFitter(visualize=True)
        assert fitter.visualize is True
        assert fitter.visualise is True  # Backward compatibility

    def test_init_with_visualise_deprecated(self):
        """Test initialization with deprecated visualise flag."""
        fitter = CascadedFitter(visualise=True)
        assert fitter.visualize is True
        assert fitter.visualise is True


class TestCascadedFitterRun:
    """Test CascadedFitter.run() method."""

    @patch('cascaded_fit.fitters.cascaded_fitter.PointCloudReader')
    def test_run_success_with_icp(self, mock_reader, sample_point_clouds, mock_fit_result):
        """Test successful run with ICP."""
        source_cloud, target_cloud = sample_point_clouds
        mock_reader.read_point_cloud_file.side_effect = [source_cloud, target_cloud]
        
        fitter = CascadedFitter()
        fitter.icp_fitter.fit = Mock(return_value=mock_fit_result)
        
        result = fitter.run('source.ply', 'target.ply')
        
        assert result['is_success'] is True
        assert result['method'] == 'ICP'
        assert 'transformation' in result

    @patch('cascaded_fit.fitters.cascaded_fitter.PointCloudReader')
    def test_run_success_with_fgr_fallback(self, mock_reader, sample_point_clouds, mock_fit_result):
        """Test successful run with FGR fallback."""
        source_cloud, target_cloud = sample_point_clouds
        mock_reader.read_point_cloud_file.side_effect = [source_cloud, target_cloud]
        
        # ICP fails, FGR succeeds
        failed_result = FitResult(
            transformation=np.eye(4),
            inlier_rmse=0.1,  # Above threshold
            rmse_threshold=0.01,
            max_error=0.3
        )
        
        fitter = CascadedFitter()
        fitter.icp_fitter.fit = Mock(return_value=failed_result)
        fitter.fgr_fitter.fit = Mock(return_value=mock_fit_result)
        
        result = fitter.run('source.ply', 'target.ply')
        
        assert result['is_success'] is True
        assert result['method'] == 'FGR+ICP'

    @patch('cascaded_fit.fitters.cascaded_fitter.PointCloudReader')
    def test_run_both_fail(self, mock_reader, sample_point_clouds):
        """Test run when both ICP and FGR fail."""
        source_cloud, target_cloud = sample_point_clouds
        mock_reader.read_point_cloud_file.side_effect = [source_cloud, target_cloud]
        
        failed_result = FitResult(
            transformation=np.eye(4),
            inlier_rmse=0.1,  # Above threshold
            rmse_threshold=0.01,
            max_error=0.3
        )
        
        fitter = CascadedFitter()
        fitter.icp_fitter.fit = Mock(return_value=failed_result)
        fitter.fgr_fitter.fit = Mock(return_value=failed_result)
        
        with pytest.raises(ConvergenceError):
            fitter.run('source.ply', 'target.ply')

    @patch('cascaded_fit.fitters.cascaded_fitter.PointCloudReader')
    def test_run_file_error(self, mock_reader):
        """Test run with file reading error."""
        mock_reader.read_point_cloud_file.side_effect = FileNotFoundError("File not found")
        
        fitter = CascadedFitter()
        
        with pytest.raises(RegistrationError):
            fitter.run('nonexistent.ply', 'target.ply')


class TestCascadedFitterHelpers:
    """Test CascadedFitter helper methods."""

    def test_create_result_dict_success(self, mock_fit_result):
        """Test _create_result_dict with successful result."""
        fitter = CascadedFitter()
        result = fitter._create_result_dict(mock_fit_result, "ICP")
        
        assert result['is_success'] is True
        assert result['method'] == 'ICP'
        assert result['transformation'] is not None
        assert result['inlier_rmse'] == 0.001

    def test_create_result_dict_none(self):
        """Test _create_result_dict with None result."""
        fitter = CascadedFitter()
        result = fitter._create_result_dict(None, "Failed")
        
        assert result['is_success'] is False
        assert result['method'] == 'Failed'
        assert result['transformation'] is None

    @patch('cascaded_fit.fitters.cascaded_fitter.PointCloudReader')
    def test_read_point_clouds(self, mock_reader, sample_point_clouds):
        """Test _read_point_clouds method."""
        source_cloud, target_cloud = sample_point_clouds
        mock_reader.read_point_cloud_file.side_effect = [source_cloud, target_cloud]
        
        fitter = CascadedFitter()
        fitter._read_point_clouds('source.ply', 'target.ply')
        
        assert fitter.source_cloud is source_cloud
        assert fitter.target_cloud is target_cloud

    def test_try_icp_fit(self, sample_point_clouds, mock_fit_result):
        """Test _try_icp_fit method."""
        source_cloud, target_cloud = sample_point_clouds
        fitter = CascadedFitter()
        fitter.source_cloud = source_cloud
        fitter.target_cloud = target_cloud
        fitter.icp_fitter.fit = Mock(return_value=mock_fit_result)
        
        result = fitter._try_icp_fit()
        assert result is mock_fit_result

    def test_try_fgr_fit(self, sample_point_clouds, mock_fit_result):
        """Test _try_fgr_fit method."""
        source_cloud, target_cloud = sample_point_clouds
        fitter = CascadedFitter()
        fitter.source_cloud = source_cloud
        fitter.target_cloud = target_cloud
        fitter.fgr_fitter.fit = Mock(return_value=mock_fit_result)
        
        result = fitter._try_fgr_fit()
        assert result is mock_fit_result

    @patch('cascaded_fit.fitters.cascaded_fitter.o3d.visualization.draw_geometries')
    def test_visualize_results(self, mock_draw, sample_point_clouds, mock_fit_result):
        """Test _visualize_results method."""
        source_cloud, target_cloud = sample_point_clouds
        fitter = CascadedFitter(visualize=True)
        fitter.source_cloud = source_cloud
        fitter.target_cloud = target_cloud
        
        fitter._visualize_results(mock_fit_result)
        
        # Should be called twice (before and after registration)
        assert mock_draw.call_count == 2

    def test_visualise_results_deprecated(self, sample_point_clouds, mock_fit_result):
        """Test deprecated _visualise_results method."""
        source_cloud, target_cloud = sample_point_clouds
        fitter = CascadedFitter()
        fitter.source_cloud = source_cloud
        fitter.target_cloud = target_cloud
        
        # Should call _visualize_results
        with patch.object(fitter, '_visualize_results') as mock_viz:
            fitter._visualise_results(mock_fit_result)
            mock_viz.assert_called_once_with(mock_fit_result)

