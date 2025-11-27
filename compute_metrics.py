import numpy as np
from scipy.spatial import cKDTree


def compute_metrics(source_points, target_points, transform):
    transformed_source = np.dot(source_points, transform[:3, :3].T) + transform[:3, 3]
    tree = cKDTree(target_points)
    distances, _ = tree.query(transformed_source)

    rmse = np.sqrt(np.mean(distances**2))
    max_error = np.max(distances)
    mean_error = np.mean(distances)
    median_error = np.median(distances)

    return {
        'Transformation': transform.tolist(),  # Convert ndarray to list
        'RMSE': float(rmse),  # Ensure it's a Python float, not numpy.float64
        'Max Error': float(max_error),
        'Mean Error': float(mean_error),
        'Median Error': float(median_error)
    }