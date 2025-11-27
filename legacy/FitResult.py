import numpy as np

class FitResult:
    def __init__(self, transformation, inlier_rmse, rmse_threshold,max_error):
        self.transformation = transformation        
        self.inlier_rmse = inlier_rmse  
        self.max_error=max_error
        self.rmse_threshold = rmse_threshold        
        self.is_success = self.is_rms_below_threshold()        

    def is_rms_below_threshold(self):        
        # Assuming inlier_rmse is a single value now
        return self.inlier_rmse < self.rmse_threshold

    def to_dict(self):        
        return {
            "transformation": self.transformation.tolist() if isinstance(self.transformation, np.ndarray) else self.transformation,
            "inlier_rmse": float(self.inlier_rmse),
            "max_error": float(self.max_error),
            "rmse_threshold": float(self.rmse_threshold),
            "is_success": bool(self.is_success)
        }