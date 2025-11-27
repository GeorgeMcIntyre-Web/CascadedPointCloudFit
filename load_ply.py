import numpy as np
import open3d as o3d


def load_ply(file_path):
    pcd = o3d.io.read_point_cloud(file_path)
    return np.asarray(pcd.points), np.asarray(pcd.normals)