import time
import open3d
import numpy as np
from FitResult import FitResult

class IcpFitter:

    def __init__(self, rmse_threshold, max_correspondence_distance, relative_fitness, relative_rmse, max_iteration):
        self.rmse_threshold = rmse_threshold
        self.max_correspondence_distance = max_correspondence_distance
        self.relative_fitness = relative_fitness
        self.relative_rmse = relative_rmse
        self.max_iteration = max_iteration

    def fit(self, source_cloud, target_cloud, initial_guess_transformation=np.identity(4)):
        # TODO: check small cloud large cloud
        
        self.source_cloud = source_cloud
        self.target_cloud = target_cloud
        self.initial_guess_transformation = initial_guess_transformation

        forward_result = self.forward_icp()
        if(forward_result.is_success):
            return forward_result

        reverse_result = self.reverse_icp()
        return reverse_result
    
    def forward_icp(self):
        print("\n:: Trying forward ICP fit...")
        result = self.__execute_icp(self.source_cloud, self.target_cloud, self.initial_guess_transformation)
        return result

    def reverse_icp(self):
        print("\n:: Trying reverse ICP fit...")
        initial_guess_transformation_reversed = np.linalg.inv(self.initial_guess_transformation)
        result = self.__execute_icp(self.target_cloud, self.source_cloud, initial_guess_transformation_reversed) # order reversed
        result.transformation = np.linalg.inv(result.transformation) # reverse transformation
        return result

    def __execute_icp(self, source_cloud, target_cloud, initial_guess_transformation=np.identity(4)):
        # TODO: expose all parameters for cli tuning
        start_time = time.time()
        
        criteria = open3d.pipelines.registration.ICPConvergenceCriteria(
            relative_fitness = self.relative_fitness,
            relative_rmse = self.relative_rmse,
            max_iteration = self.max_iteration)

        registration_icp = open3d.pipelines.registration.registration_icp(
            source_cloud, 
            target_cloud,
            max_correspondence_distance=self.max_correspondence_distance,
            init=initial_guess_transformation,
            criteria=criteria)

        icp_time = time.time() - start_time

        print(":: ICP Execution time: ", icp_time)
        print(":: ICP Inlier Fitness: ", registration_icp.fitness)
        print(":: ICP Inlier RMSE: ", registration_icp.inlier_rmse)

        # TODO: Calculate actual max error from point correspondences
        # For now, using inlier_rmse as a proxy for max_error
        max_error = registration_icp.inlier_rmse * 3  # Rough estimate

        result = FitResult(registration_icp.transformation, registration_icp.inlier_rmse, self.rmse_threshold, max_error)
        return result
