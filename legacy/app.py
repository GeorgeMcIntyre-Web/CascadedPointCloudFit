# app.py
from flask import Flask, request, jsonify
import numpy as np
import tempfile
from scipy.spatial import cKDTree
from CascadedPointCloudFit import PointCloudProcessor
from FitResult import FitResult
from load_ply import load_ply

app = Flask(__name__)

def align_cloud_sizes(source_points, target_points):
    # Ensure both clouds have the same number of points
    min_size = min(len(source_points), len(target_points))
    return source_points[:min_size], target_points[:min_size]

def pca_registration(source_points, target_points):
    source_mean = np.mean(source_points, axis=0)
    target_mean = np.mean(target_points, axis=0)
    source_centered = source_points - source_mean
    target_centered = target_points - target_mean
    
    cov = np.dot(source_centered.T, target_centered)
    U, _, Vt = np.linalg.svd(cov)
    R = np.dot(Vt.T, U.T)
    if np.linalg.det(R) < 0:
        Vt[-1,:] *= -1
        R = np.dot(Vt.T, U.T)
    
    t = target_mean - np.dot(R, source_mean)
    
    T = np.eye(4)
    T[:3, :3] = R
    T[:3, 3] = t
    return T

def process_with_point_cloud_processor(source_points, target_points):
    with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as source_temp, \
         tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as target_temp:
        
        np.savetxt(source_temp.name, source_points)
        np.savetxt(target_temp.name, target_points)
        
        processor = PointCloudProcessor(
            visualise=False,
            rmse_threshold= 0.001,
            fgr_distance_threshold= 0.0003,
            fgr_voxel_size= 10,
            icp_max_correspondence_distance= 100,
            icp_relative_fitness= 0.0000001,
            icp_relative_rmse= 0.0000001,
            icp_max_iteration= 200
        )
        result = processor.process(source_temp.name, target_temp.name)
        
    return result

def create_result_dict(fit_result):     
        if fit_result is None:
            return {
                "transformation": None,
                "inlier_rmse": None,
                "max_error": None,
                "is_success": False
            }
        return {
            "transformation": fit_result.transformation.tolist(),
            "inlier_rmse": fit_result.inlier_rmse,
            "max_error": fit_result.max_error,
            "is_success": fit_result.is_success
        }

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

def icp_refinement(source_points, target_points, initial_transform, max_iterations=50, tolerance=1e-7):
    def closest_point(A, B):
        tree = cKDTree(B)
        distances, indices = tree.query(A)
        return B[indices], distances
    
    current_transform = initial_transform
    prev_error = np.inf
    
    for _ in range(max_iterations):
        transformed_source = np.dot(source_points, current_transform[:3, :3].T) + current_transform[:3, 3]
        corresponding_points, distances = closest_point(transformed_source, target_points)
        
        error = np.mean(distances)
        if np.abs(error - prev_error) < tolerance:
            break
        prev_error = error
        
        # Compute new transformation
        source_mean = np.mean(transformed_source, axis=0)
        target_mean = np.mean(corresponding_points, axis=0)
        source_centered = transformed_source - source_mean
        target_centered = corresponding_points - target_mean
        
        cov = np.dot(source_centered.T, target_centered)
        U, _, Vt = np.linalg.svd(cov)
        R = np.dot(Vt.T, U.T)
        if np.linalg.det(R) < 0:
            Vt[-1,:] *= -1
            R = np.dot(Vt.T, U.T)
        
        t = target_mean - np.dot(R, source_mean)
        
        current_transform[:3, :3] = np.dot(R, current_transform[:3, :3])
        current_transform[:3, 3] = np.dot(R, current_transform[:3, 3]) + t
    
    return current_transform

def custom_icp(source_points, target_points):
    # Align the point cloud sizes
    #source_points, target_points = align_cloud_sizes(source_points, target_points)
                
    initial_transform = pca_registration(source_points, target_points)        
    initial_metrics = compute_metrics(source_points, target_points, initial_transform)
        
    for key, value in initial_metrics.items():
        print(f"{key}: {value}")

    refined_transform = icp_refinement(source_points, target_points, initial_transform)        
    refined_metrics = compute_metrics(source_points, target_points, refined_transform)
        
    rmse=1000
    max_error=1000
    
    print("\nRefined Registration Metrics:")
    for key, value in refined_metrics.items():
        if(key=='RMSE'):
            rmse=value               
            print(f"{key}: {value}")
        if(key=='Max Error'):
            max_error=value       
        
    transformed_source = np.dot(source_points, refined_transform[:3, :3].T) + refined_transform[:3, 3]   
    return transformed_source, rmse,max_error

def calculate_transformation_matrix(source_points, transformed_points):
    """Calculate the transformation matrix from source to transformed points."""
    # Center the point sets
    source_center = np.mean(source_points, axis=0)
    transformed_center = np.mean(transformed_points, axis=0)
    
    # Calculate the rotation matrix
    H = np.dot((source_points - source_center).T, (transformed_points - transformed_center))
    U, S, Vt = np.linalg.svd(H)
    R = np.dot(Vt.T, U.T)
    
    # Ensure a right-handed coordinate system
    if np.linalg.det(R) < 0:
        Vt[-1,:] *= -1
        R = np.dot(Vt.T, U.T)
    
    # Calculate the translation
    t = transformed_center - np.dot(R, source_center)
    
    # Construct the 4x4 transformation matrix
    transform = np.eye(4)
    transform[:3, :3] = R
    transform[:3, 3] = t
    
    return transform


def apply_transformation(points, transform):
    return np.dot(points, transform[:3, :3].T) + transform[:3, 3]

def run_icp_methods(source_points, target_points, rmse_threshold):
    ## Method 1: Custom ICP
    
    transformed_source, rmse_custom, max_error = custom_icp(source_points, target_points)
   
    if rmse_custom <= rmse_threshold:   
        # Calculate the transformation matrix from custom ICP
        custom_transform = calculate_transformation_matrix(source_points, transformed_source)        
        return transformed_source, rmse_custom,max_error, "Custom ICP", custom_transform    
    # Method 2: PointCloudProcessor
    result = process_with_point_cloud_processor(source_points, target_points)    
    rmse = result["inlier_rmse"]
    
    if rmse <= rmse_threshold:                
        # Extract the transformation matrix from the result
        transformed=result["transformation"]        
        refined_metrics = compute_metrics(source_points, target_points, transformed)
        for key, value in refined_metrics.items():        
            if(key=='Max Error'):
                max_error=value                  
        return transformed, rmse,max_error, "PointCloudProcessor"
    
     # If both methods fail, return the identity matrix as transformation
    identity_transform = np.eye(4)
    return None, max(rmse_custom, rmse), "Both methods failed", identity_transform

# @app.route('/cloud_fit/process_point_clouds', methods=['POST'])
@app.route('/process_point_clouds', methods=['POST'])
def process_point_clouds():   
    try:
        data = request.get_json()
        source_points = np.array(data['source_points'])
        target_points = np.array(data['target_points'])
                       
        print(f"Loaded source cloud with {len(source_points)} points")
        print(f"Loaded target cloud with {len(target_points)} points")
        
        source_points, target_points = align_cloud_sizes(source_points, target_points)
        
        rmse_threshold = 0.001        
        # Forward alignment
        transformed_source, rmse_forward, max_error, method_forward, custom_transform = run_icp_methods(source_points, target_points, rmse_threshold)
     
        # Reverse alignment
        transformed_target, rmse_reverse, max_error, method_reverse, custom_transform = run_icp_methods(target_points, source_points, rmse_threshold)
      
        # Choose the best result
        if rmse_forward <= rmse_reverse:
            best_rmse = rmse_forward
            best_method = f"Forward {method_forward}"
            best_transformed = custom_transform
        else:
            best_rmse = rmse_reverse
            best_method = f"Reverse {method_reverse}"
            best_transformed = custom_transform
                
        result_message = f"Best method: {best_method}\nRMSE: {best_rmse:.6f}\n"      
        
        fit_result = FitResult(
            transformation=best_transformed,
            inlier_rmse=best_rmse,
            max_error=max_error,
            rmse_threshold=rmse_threshold
        )            
        result_dict = create_result_dict(fit_result)
        return jsonify(result_dict)            
    except Exception as e:
        print(f"Exception {e} points")
        return jsonify({'error': str(e)}), 500
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')     