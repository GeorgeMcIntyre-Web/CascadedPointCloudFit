# CascadedPointCloudFit.py
import argparse
from CascadedFitter import CascadedFitter
from IcpFitter import IcpFitter
from FgrFitter import FgrFitter

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Description of your program')
    parser.add_argument('source_file',              type=str,                       help='Path to the source file')
    parser.add_argument('target_file',              type=str,                       help='Path to the target file')
    parser.add_argument('--visualise',              type=bool,  default=False,      help='Visualize the results if set to true (default: False)')
    parser.add_argument('--rmse_threshold',         type=float, default=0.01,       help='Registration RMS threshold (default: 0.01)')
    parser.add_argument('--fgr_distance_threshold', type=float, default=0.01,       help='FGR Distance threshold (default: 0.01)')
    parser.add_argument('--fgr_voxel_size',         type=float, default=10,         help='Voxel size (default: 10)')
    parser.add_argument('--icp_max_correspondence_distance', type=float, default=100,   help='Max correspondence distance (default: 100)')
    parser.add_argument('--icp_relative_fitness',       type=float, default=0.0000001,  help='Relative fitness (default: 0.0000001)')
    parser.add_argument('--icp_relative_rmse',          type=float, default=0.0000001,  help='Relative RMSE (default: 0.0000001)')
    parser.add_argument('--icp_max_iteration',          type=int,   default=200,        help='Max iteration (default: 200)')

    args = parser.parse_args()
    
    icp_fitter = IcpFitter(
        args.rmse_threshold, 
        args.icp_max_correspondence_distance, 
        args.icp_relative_fitness, 
        args.icp_relative_rmse, 
        args.icp_max_iteration
    )
    
    fgr_fitter = FgrFitter(
        args.rmse_threshold, 
        args.fgr_distance_threshold, 
        args.fgr_voxel_size, 
        icp_fitter
    )
    
    Cascaded_fitter = CascadedFitter(
        icp_fitter, 
        fgr_fitter,
        args.visualise, 
    )
    
    Cascaded_fitter.run(args.source_file, args.target_file)
    
class PointCloudProcessor:
    def __init__(self, visualise=False, rmse_threshold=0.01, fgr_distance_threshold=0.01,
                 fgr_voxel_size=10, icp_max_correspondence_distance=100, 
                 icp_relative_fitness=0.0000001, icp_relative_rmse=0.0000001, 
                 icp_max_iteration=200):
        self.visualise = visualise
        self.rmse_threshold = rmse_threshold
        self.fgr_distance_threshold = fgr_distance_threshold
        self.fgr_voxel_size = fgr_voxel_size
        self.icp_max_correspondence_distance = icp_max_correspondence_distance
        self.icp_relative_fitness = icp_relative_fitness
        self.icp_relative_rmse = icp_relative_rmse
        self.icp_max_iteration = icp_max_iteration

    def process(self, source_file, target_file):
        icp_fitter = IcpFitter(self.rmse_threshold, self.icp_max_correspondence_distance,
                               self.icp_relative_fitness, self.icp_relative_rmse, 
                               self.icp_max_iteration)
        fgr_fitter = FgrFitter(self.rmse_threshold, self.fgr_distance_threshold,
                               self.fgr_voxel_size, icp_fitter)
        cascaded_fitter = CascadedFitter(icp_fitter, fgr_fitter, self.visualise)
        return cascaded_fitter.run(source_file, target_file)
    