# icp_test.py
import numpy as np
from scipy.spatial import cKDTree
import tkinter as tk
from tkinter import filedialog
import time
from FitResult import FitResult
from compute_metrics import compute_metrics
from load_ply import load_ply
from save_results_to_json import save_results_to_json
import tempfile
from CascadedPointCloudFit import PointCloudProcessor
import threading
from tkinter import messagebox

def show_message(title, message):
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    messagebox.showinfo(title, message)
    root.destroy()  # Destroy the root window after the message is closed
    
def threaded_message(title, message):
    threading.Thread(target=show_message, args=(title, message)).start()
    
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

def align_cloud_sizes(source_points, target_points):
    # Ensure both clouds have the same number of points
    min_size = min(len(source_points), len(target_points))
    return source_points[:min_size], target_points[:min_size]

def custom_icp(source_points, target_points):
    # Align the point cloud sizes
    source_points, target_points = align_cloud_sizes(source_points, target_points)
                
    initial_transform = pca_registration(source_points, target_points)        
    initial_metrics = compute_metrics(source_points, target_points, initial_transform)
        
    for key, value in initial_metrics.items():
        print(f"{key}: {value}")

    refined_transform = icp_refinement(source_points, target_points, initial_transform)        
    refined_metrics = compute_metrics(source_points, target_points, refined_transform)
        
    rmse=1000
    print("\nRefined Registration Metrics:")
    for key, value in refined_metrics.items():
        if(key=='RMSE'):
            rmse=value               
            print(f"{key}: {value}")

    transformed_source = np.dot(source_points, refined_transform[:3, :3].T) + refined_transform[:3, 3]   
    return transformed_source, rmse
def apply_transformation(points, transform):
    return np.dot(points, transform[:3, :3].T) + transform[:3, 3]

def run_icp_methods(source_points, target_points, rmse_threshold):
    ## Method 1: Custom ICP
    transformed_source, rmse_custom = custom_icp(source_points, target_points)
    
    if rmse_custom <= rmse_threshold:
        # Use the transformed points from custom ICP for the next method
        source_points_for_processor = transformed_source
    else:
        # If custom ICP didn't meet the threshold, use original source points
        source_points_for_processor = source_points
    
    # Method 2: PointCloudProcessor
    result = process_with_point_cloud_processor(source_points_for_processor, target_points)
    rmse = result["inlier_rmse"]
    
    if rmse <= rmse_threshold:
        # Extract the transformation matrix from the result
        transformation = np.array(result["transformation"]).reshape(4, 4)
        transformed_source = apply_transformation(source_points, transformation)
        return transformed_source, rmse, "PointCloudProcessor"
    
    return None, rmse, "Both methods failed"

if __name__ == "__main__":
    try:    
        root = tk.Tk()
        root.withdraw()  # Hides the main window

        source_file = filedialog.askopenfilename(title="Select the source file")
        target_file = filedialog.askopenfilename(title="Select the target file")
        
        start_time = time.perf_counter()
              
        source_points, source_normals = load_ply(source_file)      
        target_points, target_normals = load_ply(target_file)
        
        rmse_threshold = 0.001
        
        # Forward alignment
        transformed_source, rmse_forward, method_forward = run_icp_methods(source_points, target_points, rmse_threshold)
        
        # Reverse alignment
        transformed_target, rmse_reverse, method_reverse = run_icp_methods(target_points, source_points, rmse_threshold)
        
        # Choose the best result
        if rmse_forward <= rmse_reverse:
            best_rmse = rmse_forward
            best_method = f"Forward {method_forward}"
            best_transformed = transformed_source
        else:
            best_rmse = rmse_reverse
            best_method = f"Reverse {method_reverse}"
            best_transformed = transformed_target
        
        end_time = time.perf_counter()
        execution_time = end_time - start_time
        
        result_message = f"Best method: {best_method}\nRMSE: {best_rmse:.6f}\nExecution time: {execution_time:.2f} seconds"
        show_message("Result", result_message)
        
        # Save results (you may want to modify this based on your needs)
        save_results_to_json({
            "best_method": best_method,
            "rmse": best_rmse,
            "execution_time": execution_time,
            # Add any other relevant information
        }, "icp_results.json") 
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        import traceback
        print(traceback.format_exc())
    
    print("Script execution completed.")
    input("Press any key to exit...")