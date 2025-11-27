#CascadedFitter.py
import time
import open3d
import numpy as np
import csv

from IcpFitter import IcpFitter
from FgrFitter import FgrFitter
from PointCloudHelper import PointCloudHelper
from FitResult import FitResult
from TypeConverter import TypeConverter

class CascadedFitter:

    def __init__(self, icp_fitter, fgr_fitter, visualise):
        self.icp_fitter = icp_fitter
        self.fgr_fitter = fgr_fitter
        self.visualise = visualise

    def run(self, source_file, target_file):
        self.start_time = time.time()
        self.read_point_clouds(source_file, target_file)
        
        icp_result = self.try_icp_fit()
        if(icp_result.is_success):
            self.print_result(icp_result)
            return self.create_result_dict(icp_result)

        fgr_result = self.try_fgr_fit()
        if(fgr_result.is_success):
            self.print_result(fgr_result)
            return self.create_result_dict(fgr_result)

        print("\n:: Warning. ICP and FGR fits failed. RMSE threshold could not be achieved.")
        return self.create_result_dict(None)
    
    def read_point_clouds(self, source_file, target_file):
        self.source_cloud = PointCloudHelper.read_point_cloud_file(source_file)
        self.target_cloud = PointCloudHelper.read_point_cloud_file(target_file)
    
    def try_icp_fit(self):
        result = self.icp_fitter.fit(self.source_cloud, self.target_cloud)
        return result

    def try_fgr_fit(self):
        result = self.fgr_fitter.fit(self.source_cloud, self.target_cloud)
        return result
    
    def print_result(self, fit_result):
        transformation_string = TypeConverter.array_to_csv_string(fit_result.transformation)
        
        total_time = time.time() - self.start_time
        print(":: Total Execution Time: {}".format(total_time))
        
        print("\n<Transformation matrix>")
        print(transformation_string)
        print("<\\Transformation matrix>")
    
        print("\nRMS: {}".format(TypeConverter.float_to_max_decimals_string(fit_result.inlier_rmse)))
    
        if(self.visualise):
            PointCloudHelper.visualise_clouds(self.source_cloud, self.target_cloud)
            PointCloudHelper.visualise_cloud_registration(self.source_cloud, self.target_cloud, fit_result.transformation)
            
    def create_result_dict(self, fit_result):
        if fit_result is None:
            return {
                "transformation": None,
                "inlier_rmse": None,
                "is_success": False
            }
        return {
            "transformation": fit_result.transformation.tolist(),
            "inlier_rmse": fit_result.inlier_rmse,
            "is_success": fit_result.is_success
        }
