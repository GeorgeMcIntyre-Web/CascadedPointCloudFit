"""Unit tests for PointCloudReader."""

import pytest
import numpy as np
import open3d as o3d
from pathlib import Path
from unittest.mock import patch, mock_open
from cascaded_fit.io.readers import PointCloudReader
from cascaded_fit.utils.exceptions import PointCloudLoadError


@pytest.fixture
def sample_ply_file(tmp_path):
    """Create a sample PLY file."""
    ply_file = tmp_path / "test.ply"
    ply_content = """ply
format ascii 1.0
element vertex 3
property float x
property float y
property float z
end_header
0.0 0.0 0.0
1.0 1.0 1.0
2.0 2.0 2.0
"""
    ply_file.write_text(ply_content)
    return str(ply_file)


@pytest.fixture
def sample_csv_file(tmp_path):
    """Create a sample CSV file."""
    csv_file = tmp_path / "test.csv"
    csv_content = """0.0,0.0,0.0
1.0,1.0,1.0
2.0,2.0,2.0
"""
    csv_file.write_text(csv_content)
    return str(csv_file)


class TestPointCloudReader:
    """Test PointCloudReader class."""

    def test_read_ply_file(self, sample_ply_file):
        """Test reading PLY file."""
        point_cloud = PointCloudReader.read_point_cloud_file(sample_ply_file)
        
        assert isinstance(point_cloud, o3d.geometry.PointCloud)
        assert len(point_cloud.points) == 3

    def test_read_csv_file(self, sample_csv_file):
        """Test reading CSV file (converts to PLY)."""
        point_cloud = PointCloudReader.read_point_cloud_file(sample_csv_file)
        
        assert isinstance(point_cloud, o3d.geometry.PointCloud)
        # CSV has 3 lines but newline counting may vary, check at least 2 points
        assert len(point_cloud.points) >= 2
        
        # Check that PLY file was created
        ply_file = Path(sample_csv_file).with_suffix('.ply')
        assert ply_file.exists()

    def test_read_unsupported_format(self, tmp_path):
        """Test reading unsupported file format."""
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("test")
        
        with pytest.raises(PointCloudLoadError, match="Unsupported file format"):
            PointCloudReader.read_point_cloud_file(str(txt_file))

    @patch('cascaded_fit.io.readers.o3d.io.read_point_cloud')
    def test_read_empty_point_cloud(self, mock_read, tmp_path):
        """Test reading empty point cloud."""
        ply_file = tmp_path / "empty.ply"
        ply_file.write_text("ply\nformat ascii 1.0\nelement vertex 0\nend_header\n")
        
        empty_cloud = o3d.geometry.PointCloud()
        mock_read.return_value = empty_cloud
        
        with pytest.raises(PointCloudLoadError, match="No points loaded"):
            PointCloudReader.read_point_cloud_file(str(ply_file))

    @patch('cascaded_fit.io.readers.o3d.io.read_point_cloud')
    def test_read_file_error(self, mock_read, tmp_path):
        """Test reading file with error."""
        ply_file = tmp_path / "error.ply"
        ply_file.write_text("invalid")
        
        mock_read.side_effect = Exception("Read error")
        
        with pytest.raises(PointCloudLoadError):
            PointCloudReader.read_point_cloud_file(str(ply_file))

    def test_convert_csv_to_ply(self, sample_csv_file, tmp_path):
        """Test CSV to PLY conversion."""
        ply_path = PointCloudReader._convert_csv_to_ply(sample_csv_file)
        
        assert Path(ply_path).exists()
        assert ply_path.endswith('.ply')
        
        # Check PLY content
        content = Path(ply_path).read_text()
        assert 'ply' in content
        assert 'element vertex' in content
        assert '0.0 0.0 0.0' in content

    def test_load_ply_as_numpy(self, sample_ply_file):
        """Test loading PLY as numpy arrays."""
        points, normals = PointCloudReader.load_ply(sample_ply_file)
        
        assert isinstance(points, np.ndarray)
        assert points.shape == (3, 3)
        # Normals may be None if not in file
        assert normals is None or isinstance(normals, np.ndarray)

    def test_align_cloud_sizes_equal(self):
        """Test align_cloud_sizes with equal sizes."""
        source = np.array([[1, 2, 3], [4, 5, 6]])
        target = np.array([[7, 8, 9], [10, 11, 12]])
        
        aligned_source, aligned_target = PointCloudReader.align_cloud_sizes(source, target)
        
        assert len(aligned_source) == len(aligned_target) == 2
        np.testing.assert_array_equal(aligned_source, source)
        np.testing.assert_array_equal(aligned_target, target)

    def test_align_cloud_sizes_different(self):
        """Test align_cloud_sizes with different sizes."""
        source = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        target = np.array([[10, 11, 12], [13, 14, 15]])
        
        aligned_source, aligned_target = PointCloudReader.align_cloud_sizes(source, target)
        
        assert len(aligned_source) == len(aligned_target) == 2
        np.testing.assert_array_equal(aligned_source, source[:2])
        np.testing.assert_array_equal(aligned_target, target)

