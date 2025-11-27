import time
import open3d
from PointCloudHelper import PointCloudHelper

class FgrFitter:

    def __init__(self, rmse_threshold, distance_threshold, voxel_size, icp_fitter):
        self.rmse_threshold = rmse_threshold
        self.distance_threshold = distance_threshold
        self.voxel_size = voxel_size
        self.icp_fitter = icp_fitter
    
    def fit(self, source_cloud, target_cloud):
        print("\n:: Trying FGR and ICP combination fit...")
        fgr_result = self.__execute_fgr(source_cloud, target_cloud)
        icp_result = self.icp_fitter.fit(source_cloud, target_cloud, fgr_result.transformation) # improve fit using ICP with initial guess from FGR
        return icp_result

    def __execute_fgr(self, source_cloud, target_cloud):
        start_time = time.time()
        source_fpfh = self.__calculate_fpfh(source_cloud)
        target_fpfh = self.__calculate_fpfh(target_cloud)

        fgr_option = open3d.pipelines.registration.FastGlobalRegistrationOption(maximum_correspondence_distance=self.distance_threshold)

        result = open3d.pipelines.registration.registration_fgr_based_on_feature_matching(
            source_cloud, 
            target_cloud, 
            source_fpfh, 
            target_fpfh,
            fgr_option)
    
        execution_time = time.time() - start_time
        print("\n:: FGR Execution time: {}".format(execution_time))
        print(":: FGR Distance Threshold: {}".format(self.distance_threshold))
        return result

    def __calculate_fpfh(self, point_cloud):
        # TODO: make these params self.param
        radius_normal = self.voxel_size * 2
        print(":: Estimate normal with search radius %.3f." % radius_normal)
        point_cloud.estimate_normals(
            open3d.geometry.KDTreeSearchParamHybrid(radius=radius_normal, max_nn=30))

        radius_feature = self.voxel_size * 5
        print(":: Compute FPFH feature with search radius %.3f." % radius_feature)
        kdTreeSearchParams = open3d.geometry.KDTreeSearchParamHybrid(radius=radius_feature, max_nn=100)
        fpfh = open3d.pipelines.registration.compute_fpfh_feature(point_cloud, kdTreeSearchParams)
        return fpfh

