"""Point cloud file readers."""

import os
import numpy as np
import open3d as o3d
from pathlib import Path
from typing import Tuple, Optional
from cascaded_fit.utils.logger import Logger
from cascaded_fit.utils.exceptions import PointCloudLoadError

logger = Logger.get(__name__)


class PointCloudReader:
    """Read point cloud files in various formats."""

    @staticmethod
    def read_point_cloud_file(file_path: str) -> o3d.geometry.PointCloud:
        """
        Read point cloud from file (CSV or PLY).

        Args:
            file_path: Path to point cloud file

        Returns:
            open3d.geometry.PointCloud object

        Raises:
            PointCloudLoadError: If file cannot be loaded
        """
        logger.info(f"Reading point cloud from {file_path}")

        try:
            extension = os.path.splitext(file_path)[1].lower()

            if extension == '.csv':
                ply_filepath = PointCloudReader._convert_csv_to_ply(file_path)
            elif extension == '.ply':
                ply_filepath = file_path
            else:
                raise PointCloudLoadError(f'Unsupported file format: {extension}')

            point_cloud = o3d.io.read_point_cloud(ply_filepath)

            if len(point_cloud.points) == 0:
                raise PointCloudLoadError(f"No points loaded from {file_path}")

            logger.info(f"Loaded {len(point_cloud.points)} points")
            return point_cloud

        except Exception as e:
            logger.error(f"Failed to read point cloud: {e}", exc_info=True)
            raise PointCloudLoadError(f"Failed to read {file_path}: {e}")

    @staticmethod
    def _convert_csv_to_ply(csv_filename: str) -> str:
        """
        Convert CSV to PLY format.

        Args:
            csv_filename: Path to CSV file

        Returns:
            Path to generated PLY file
        """
        logger.debug(f"Converting CSV to PLY: {csv_filename}")

        with open(csv_filename, 'r') as csv_file:
            csv_content = csv_file.read()

        ply_content = csv_content.replace(',', ' ')
        ply_content = ply_content.rstrip("\n")
        point_count = ply_content.count('\n')

        header = f"""ply
format ascii 1.0
comment PYTHON generated
element vertex {point_count}
property float x
property float y
property float z
end_header
"""

        ply_content = header + ply_content

        ply_filename = csv_filename.replace('.csv', '.ply')
        with open(ply_filename, 'w') as ply_file:
            ply_file.write(ply_content)

        logger.debug(f"Created PLY file: {ply_filename}")
        return ply_filename

    @staticmethod
    def load_ply(file_path: str) -> Tuple[np.ndarray, Optional[np.ndarray]]:
        """
        Load PLY file and return numpy arrays.

        Args:
            file_path: Path to PLY file

        Returns:
            Tuple of (points, normals) as numpy arrays
        """
        logger.debug(f"Loading PLY as numpy: {file_path}")

        pcd = o3d.io.read_point_cloud(file_path)
        points = np.asarray(pcd.points)
        normals = np.asarray(pcd.normals) if pcd.has_normals() else None

        return points, normals

    @staticmethod
    def align_cloud_sizes(source_points: np.ndarray,
                         target_points: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Ensure both point clouds have the same number of points by truncating to minimum size.

        Args:
            source_points: Nx3 numpy array of source points
            target_points: Mx3 numpy array of target points

        Returns:
            Tuple of (source_points, target_points) with equal number of points
        """
        min_size = min(len(source_points), len(target_points))
        if len(source_points) != len(target_points):
            logger.debug(f"Aligning cloud sizes: {len(source_points)} and {len(target_points)} -> {min_size}")
        return source_points[:min_size], target_points[:min_size]
