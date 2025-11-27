import os
import open3d
import copy
import numpy as np

class PointCloudHelper:
    
    @staticmethod
    def read_point_cloud_file(file_path):
        extension = os.path.splitext(file_path)[1].lower()

        if extension == '.csv':
            ply_filepath = PointCloudHelper.convert_csv_to_ply(file_path)
        elif extension == '.ply':
            ply_filepath = file_path
        else:
            raise ValueError('Unsupported file format')

        point_cloud = open3d.io.read_point_cloud(ply_filepath)
        return point_cloud

    @staticmethod
    def convert_csv_to_ply(csv_filename):
        with open(csv_filename, 'r') as csv_file:
            csv_content = csv_file.read() # Read the CSV file into a string
    
        ply_content = csv_content.replace(',', ' ')
    
        ply_content.rstrip("\n") # remove trailing \n
        point_count = ply_content.count('\n')
    
        header = """ply
format ascii 1.0
comment PYTHON generated
element vertex <point_count>
property float x
property float y
property float z
end_header
"""

        header = header.replace("<point_count>", str(point_count))
        ply_content = header + ply_content
    
        ply_filename = csv_filename.replace('.csv', '.ply')
        with open(ply_filename, 'w') as ply_file:
            ply_file.write(ply_content)
        
        return ply_filename

    @staticmethod
    def visualise_clouds(source, target):
        source_temp = copy.deepcopy(source)
        target_temp = copy.deepcopy(target)
        source_temp.paint_uniform_color([1, 0.706, 0])
        target_temp.paint_uniform_color([0, 0.651, 0.929])
        open3d.visualization.draw_geometries([source_temp, target_temp])

    @staticmethod
    def visualise_cloud_registration(source, target, transformation):
        source_temp = copy.deepcopy(source)
        target_temp = copy.deepcopy(target)
        source_temp.paint_uniform_color([1, 0.706, 0])
        target_temp.paint_uniform_color([0, 0.651, 0.929])
        source_temp.transform(transformation)
        open3d.visualization.draw_geometries([source_temp, target_temp])

    @staticmethod
    def align_cloud_sizes(source_points, target_points):
        """
        Ensure both point clouds have the same number of points by truncating to minimum size.

        Args:
            source_points: Nx3 numpy array of source points
            target_points: Mx3 numpy array of target points

        Returns:
            Tuple of (source_points, target_points) with equal number of points
        """
        min_size = min(len(source_points), len(target_points))
        return source_points[:min_size], target_points[:min_size]

    @staticmethod
    def apply_transformation(points, transform):
        """
        Apply a 4x4 transformation matrix to 3D points.

        Args:
            points: Nx3 numpy array of points
            transform: 4x4 transformation matrix

        Returns:
            Nx3 numpy array of transformed points
        """
        return np.dot(points, transform[:3, :3].T) + transform[:3, 3]