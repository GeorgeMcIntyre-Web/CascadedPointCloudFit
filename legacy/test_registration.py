"""
Comprehensive test script for point cloud registration.
Tests the refactored code with UNIT_111 sample data.
"""

import time
import numpy as np
from CascadedPointCloudFit import PointCloudProcessor
from registration_algorithms import RegistrationAlgorithms
from compute_metrics import compute_metrics
from load_ply import load_ply
from PointCloudHelper import PointCloudHelper


def test_cascaded_processor():
    """Test the PointCloudProcessor with UNIT_111 data."""
    print("=" * 60)
    print("Testing PointCloudProcessor (Open3D-based)")
    print("=" * 60)

    source_file = "UNIT_111_Closed_J1.csv"
    target_file = "UNIT_111_Open_J1.csv"

    start_time = time.time()

    processor = PointCloudProcessor(
        visualise=False,
        rmse_threshold=0.001,
        fgr_distance_threshold=0.0003,
        fgr_voxel_size=10,
        icp_max_correspondence_distance=100,
        icp_relative_fitness=0.0000001,
        icp_relative_rmse=0.0000001,
        icp_max_iteration=200
    )

    result = processor.process(source_file, target_file)

    elapsed = time.time() - start_time

    print(f"\n[OK] Completed in {elapsed:.2f} seconds")
    if result and result.get('inlier_rmse') is not None:
        print(f"  RMSE: {result['inlier_rmse']:.6f}")
        print(f"  Success: {result['is_success']}")
    else:
        print(f"  RMSE: N/A (failed to converge below threshold)")
        print(f"  Success: False")

    return result


def test_custom_icp():
    """Test custom ICP implementation with shared registration algorithms."""
    print("\n" + "=" * 60)
    print("Testing Custom ICP (registration_algorithms.py)")
    print("=" * 60)

    # Load point clouds
    source_file = "UNIT_111_Closed_J1.ply"
    target_file = "UNIT_111_Open_J1.ply"

    source_points, _ = load_ply(source_file)
    target_points, _ = load_ply(target_file)

    print(f"Source points: {len(source_points)}")
    print(f"Target points: {len(target_points)}")

    # Align cloud sizes
    source_points, target_points = PointCloudHelper.align_cloud_sizes(source_points, target_points)

    start_time = time.time()

    # Step 1: PCA initial alignment
    print("\nStep 1: PCA Registration...")
    initial_transform = RegistrationAlgorithms.pca_registration(source_points, target_points)
    initial_metrics = compute_metrics(source_points, target_points, initial_transform)

    print(f"  Initial RMSE: {initial_metrics['RMSE']:.6f}")
    print(f"  Initial Max Error: {initial_metrics['Max Error']:.6f}")

    # Step 2: ICP refinement
    print("\nStep 2: ICP Refinement...")
    refined_transform = RegistrationAlgorithms.icp_refinement(
        source_points,
        target_points,
        initial_transform,
        max_iterations=50,
        tolerance=1e-7
    )
    refined_metrics = compute_metrics(source_points, target_points, refined_transform)

    elapsed = time.time() - start_time

    print(f"\n[OK] Completed in {elapsed:.2f} seconds")
    print(f"  Refined RMSE: {refined_metrics['RMSE']:.6f}")
    print(f"  Refined Max Error: {refined_metrics['Max Error']:.6f}")
    print(f"  Mean Error: {refined_metrics['Mean Error']:.6f}")
    print(f"  Median Error: {refined_metrics['Median Error']:.6f}")

    return refined_metrics


def test_forward_reverse():
    """Test both forward and reverse ICP to find best alignment."""
    print("\n" + "=" * 60)
    print("Testing Forward/Reverse ICP")
    print("=" * 60)

    source_file = "UNIT_111_Closed_J1.ply"
    target_file = "UNIT_111_Open_J1.ply"

    source_points, _ = load_ply(source_file)
    target_points, _ = load_ply(target_file)

    source_points, target_points = PointCloudHelper.align_cloud_sizes(source_points, target_points)

    # Forward direction
    print("\nForward Alignment (Source -> Target):")
    initial_fwd = RegistrationAlgorithms.pca_registration(source_points, target_points)
    refined_fwd = RegistrationAlgorithms.icp_refinement(source_points, target_points, initial_fwd)
    metrics_fwd = compute_metrics(source_points, target_points, refined_fwd)
    print(f"  RMSE: {metrics_fwd['RMSE']:.6f}")

    # Reverse direction
    print("\nReverse Alignment (Target -> Source):")
    initial_rev = RegistrationAlgorithms.pca_registration(target_points, source_points)
    refined_rev = RegistrationAlgorithms.icp_refinement(target_points, source_points, initial_rev)
    metrics_rev = compute_metrics(target_points, source_points, refined_rev)
    print(f"  RMSE: {metrics_rev['RMSE']:.6f}")

    # Choose best
    if metrics_fwd['RMSE'] <= metrics_rev['RMSE']:
        print(f"\n[OK] Forward alignment is better: RMSE = {metrics_fwd['RMSE']:.6f}")
        return 'forward', metrics_fwd
    else:
        print(f"\n[OK] Reverse alignment is better: RMSE = {metrics_rev['RMSE']:.6f}")
        return 'reverse', metrics_rev


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("POINT CLOUD REGISTRATION TEST SUITE")
    print("=" * 60)
    print(f"Test Data:")
    print(f"  - UNIT_111_Closed_J1 (11,207 points)")
    print(f"  - UNIT_111_Open_J1 (11,213 points)")
    print("=" * 60)

    try:
        # Test 1: Cascaded Processor (Open3D)
        result1 = test_cascaded_processor()

        # Test 2: Custom ICP (Shared algorithms)
        result2 = test_custom_icp()

        # Test 3: Forward/Reverse comparison
        direction, result3 = test_forward_reverse()

        # Summary
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        if result1 and result1.get('inlier_rmse') is not None:
            print(f"Open3D CascadedProcessor:    RMSE = {result1['inlier_rmse']:.6f}")
        else:
            print(f"Open3D CascadedProcessor:    RMSE = N/A (did not converge)")
        print(f"Custom ICP (shared):          RMSE = {result2['RMSE']:.6f}")
        print(f"Best direction ({direction}):     RMSE = {result3['RMSE']:.6f}")
        print("=" * 60)
        print("\n[SUCCESS] All tests completed successfully!")

    except Exception as e:
        print(f"\n[FAILED] Test failed with error: {e}")
        import traceback
        traceback.print_exc()
