"""Type hints and type aliases for the codebase."""

from typing import TYPE_CHECKING, Union, Tuple, Dict, Any, Optional
from pathlib import Path
import numpy as np
import numpy.typing as npt

if TYPE_CHECKING:
    import open3d as o3d

# Path types
PathLike = Union[str, Path]

# Point cloud types
PointCloud = "o3d.geometry.PointCloud"  # Open3D point cloud
PointCloudArray = npt.NDArray[np.float64]  # Nx3 numpy array
Transform4x4 = npt.NDArray[np.float64]  # 4x4 transformation matrix
Transform3x3 = npt.NDArray[np.float64]  # 3x3 transformation matrix
Vector3 = npt.NDArray[np.float64]  # (3,) array

# Result types
RegistrationResult = Dict[str, Any]
MetricsDict = Dict[str, float]

# Config types
ConfigDict = Dict[str, Any]

