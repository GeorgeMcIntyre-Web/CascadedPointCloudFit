#!/usr/bin/env python3
"""
Test PinFails2 dataset with Python implementation
Compare with TypeScript results
"""

import sys
import numpy as np
from pathlib import Path

# Add cascaded_fit to path
sys.path.insert(0, str(Path(__file__).parent / 'cascaded_fit'))

try:
    from cascaded_fit.core.registration import RegistrationAlgorithm
    from cascaded_fit.io.readers import PointCloudReader
    from cascaded_fit.core.metrics import RegistrationMetrics
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Attempting direct import...")

    # Try importing Open3D directly to test
    try:
        import open3d as o3d
        print(f"Open3D version: {o3d.__version__}")
    except ImportError:
        print("Open3D not installed")
        sys.exit(1)

def main():
    # Load PinFails2 dataset
    source_path = Path("test_data/external/PinFails2/file1.ply")
    target_path = Path("test_data/external/PinFails2/file2.ply")

    print("=" * 60)
    print("  Python Implementation - PinFails2 Test")
    print("=" * 60)
    print()

    if not source_path.exists() or not target_path.exists():
        print(f"Error: Files not found")
        print(f"  Source: {source_path}")
        print(f"  Target: {target_path}")
        sys.exit(1)

    try:
        # Import Open3D
        import open3d as o3d

        # Read point clouds using Open3D directly
        print(f"Loading point clouds...")
        source = o3d.io.read_point_cloud(str(source_path))
        target = o3d.io.read_point_cloud(str(target_path))

        print(f"   Source: {len(source.points)} points")
        print(f"   Target: {len(target.points)} points")
        print()

        # Compute centroids
        source_centroid = np.mean(np.asarray(source.points), axis=0)
        target_centroid = np.mean(np.asarray(target.points), axis=0)

        print(f"Centroids:")
        print(f"   Source: ({source_centroid[0]:.2f}, {source_centroid[1]:.2f}, {source_centroid[2]:.2f})")
        print(f"   Target: ({target_centroid[0]:.2f}, {target_centroid[1]:.2f}, {target_centroid[2]:.2f})")
        print()

        # Translation vector
        translation = target_centroid - source_centroid
        magnitude = np.linalg.norm(translation)

        print(f"Translation Vector (Target - Source):")
        print(f"   dX = {translation[0]:.3f}mm")
        print(f"   dY = {translation[1]:.3f}mm")
        print(f"   dZ = {translation[2]:.3f}mm")
        print(f"   Magnitude = {magnitude:.3f}mm")
        print()

        # Run ICP using Open3D
        print(f"Running ICP registration (Open3D)...")

        # Initial alignment (identity)
        init_transform = np.eye(4)

        # ICP parameters (matching Open3D defaults)
        threshold = 0.02  # 20mm max correspondence distance

        # Run ICP
        reg_result = o3d.pipelines.registration.registration_icp(
            source, target,
            threshold,
            init_transform,
            o3d.pipelines.registration.TransformationEstimationPointToPoint(),
            o3d.pipelines.registration.ICPConvergenceCriteria(max_iteration=50)
        )

        print(f"   ICP Complete")
        print(f"   Fitness: {reg_result.fitness:.6f}")
        print(f"   RMSE: {reg_result.inlier_rmse:.6f}mm")
        print()

        # Extract transformation
        T = reg_result.transformation
        R = T[:3, :3]
        t = T[:3, 3]

        print(f"Transformation Matrix:")
        print(f"   Rotation:")
        for i in range(3):
            print(f"     [{R[i,0]:8.4f}, {R[i,1]:8.4f}, {R[i,2]:8.4f}]")
        print(f"   Translation:")
        print(f"     [{t[0]:8.3f}, {t[1]:8.3f}, {t[2]:8.3f}]")
        print()

        # Check if rotation is close to identity
        I = np.eye(3)
        rotation_error = np.linalg.norm(R - I, 'fro')
        print(f"Rotation Analysis:")
        print(f"   Frobenius norm |R - I|: {rotation_error:.6f}")
        print(f"   Is identity (< 0.01): {rotation_error < 0.01}")
        print()

        print("=" * 60)
        print("  COMPARISON WITH TYPESCRIPT")
        print("=" * 60)
        print()
        print("TypeScript Results:")
        print("  ΔX = -4.392mm")
        print("  ΔY = 33.747mm")
        print("  ΔZ = 12.568mm")
        print("  Magnitude = 36.278mm")
        print("  RMSE: 0.000000mm")
        print()
        print("Python Results:")
        print(f"  ΔX = {translation[0]:.3f}mm (centroid diff)")
        print(f"  ΔY = {translation[1]:.3f}mm (centroid diff)")
        print(f"  ΔZ = {translation[2]:.3f}mm (centroid diff)")
        print(f"  Magnitude = {magnitude:.3f}mm (centroid diff)")
        print(f"  RMSE: {reg_result.inlier_rmse:.6f}mm (ICP result)")
        print()

        # Translation from transformation matrix
        print(f"  ICP Translation:")
        print(f"    ΔX = {t[0]:.3f}mm")
        print(f"    ΔY = {t[1]:.3f}mm")
        print(f"    ΔZ = {t[2]:.3f}mm")
        print(f"    Magnitude = {np.linalg.norm(t):.3f}mm")
        print()

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
