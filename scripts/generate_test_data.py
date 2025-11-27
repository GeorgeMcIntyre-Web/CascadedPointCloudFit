"""Generate augmented test datasets from UNIT_111 samples."""

import numpy as np
import sys
from pathlib import Path
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from load_ply import load_ply


def save_ply(points, filepath):
    """Save points to PLY file."""
    with open(filepath, 'w') as f:
        f.write("ply\n")
        f.write("format ascii 1.0\n")
        f.write("comment PYTHON generated\n")
        f.write(f"element vertex {len(points)}\n")
        f.write("property float x\n")
        f.write("property float y\n")
        f.write("property float z\n")
        f.write("end_header\n")
        for point in points:
            f.write(f"{point[0]} {point[1]} {point[2]}\n")


def rotate_points(points, angle_deg, axis='z'):
    """Rotate points around specified axis."""
    angle_rad = np.deg2rad(angle_deg)
    cos_a, sin_a = np.cos(angle_rad), np.sin(angle_rad)

    if axis == 'x':
        R = np.array([
            [1, 0, 0],
            [0, cos_a, -sin_a],
            [0, sin_a, cos_a]
        ])
    elif axis == 'y':
        R = np.array([
            [cos_a, 0, sin_a],
            [0, 1, 0],
            [-sin_a, 0, cos_a]
        ])
    else:  # z
        R = np.array([
            [cos_a, -sin_a, 0],
            [sin_a, cos_a, 0],
            [0, 0, 1]
        ])

    # Center, rotate, uncenter
    center = np.mean(points, axis=0)
    centered = points - center
    rotated = np.dot(centered, R.T)
    return rotated + center


def translate_points(points, direction, distance):
    """Translate points in specified direction."""
    direction = np.array(direction)
    direction = direction / np.linalg.norm(direction)
    return points + direction * distance


def add_noise(points, noise_std):
    """Add Gaussian noise to points."""
    noise = np.random.normal(0, noise_std, points.shape)
    return points + noise


def subsample_points(points, ratio):
    """Randomly subsample points."""
    n_points = int(len(points) * ratio)
    indices = np.random.choice(len(points), n_points, replace=False)
    return points[indices]


def add_outliers(points, outlier_ratio):
    """Add outliers to point cloud."""
    points_with_outliers = points.copy()
    n_outliers = int(len(points) * outlier_ratio)

    # Select random points to make outliers
    outlier_indices = np.random.choice(len(points), n_outliers, replace=False)

    # Add large random offset
    bounds = np.max(points, axis=0) - np.min(points, axis=0)
    outlier_offset = np.random.uniform(-bounds * 2, bounds * 2, (n_outliers, 3))
    points_with_outliers[outlier_indices] += outlier_offset

    return points_with_outliers


def generate_rotations(points, output_dir, base_name):
    """Generate rotation variants."""
    angles = [5, 10, 15, 30, 45, 60, 90]
    axes = ['x', 'y', 'z']

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    count = 0
    for angle in angles:
        for axis in axes:
            rotated = rotate_points(points, angle, axis)
            filename = f"{base_name}_rot_{axis}_{angle}deg.ply"
            save_ply(rotated, output_dir / filename)
            count += 1
            print(f"Generated {filename}")

    print(f"Generated {count} rotation variants")
    return count


def generate_translations(points, output_dir, base_name):
    """Generate translation variants."""
    distances = [10, 25, 50, 100, 200]
    directions = [
        (1, 0, 0),  # x
        (0, 1, 0),  # y
        (0, 0, 1),  # z
        (1, 1, 1),  # diagonal
    ]
    direction_names = ['x', 'y', 'z', 'diag']

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    count = 0
    for dist in distances:
        for direction, name in zip(directions, direction_names):
            translated = translate_points(points, direction, dist)
            filename = f"{base_name}_trans_{name}_{dist}mm.ply"
            save_ply(translated, output_dir / filename)
            count += 1
            print(f"Generated {filename}")

    print(f"Generated {count} translation variants")
    return count


def generate_noise_variants(points, output_dir, base_name):
    """Generate noise variants."""
    noise_levels = [0.001, 0.01, 0.1, 0.5]

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    count = 0
    for noise_std in noise_levels:
        noisy = add_noise(points, noise_std)
        filename = f"{base_name}_noise_{noise_std}.ply"
        save_ply(noisy, output_dir / filename)
        count += 1
        print(f"Generated {filename}")

    print(f"Generated {count} noise variants")
    return count


def generate_subsampled_variants(points, output_dir, base_name):
    """Generate subsampled variants."""
    ratios = [0.1, 0.25, 0.5, 0.75, 0.9]

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    count = 0
    for ratio in ratios:
        subsampled = subsample_points(points, ratio)
        filename = f"{base_name}_subsample_{int(ratio*100)}pct.ply"
        save_ply(subsampled, output_dir / filename)
        count += 1
        print(f"Generated {filename}")

    print(f"Generated {count} subsampled variants")
    return count


def generate_outlier_variants(points, output_dir, base_name):
    """Generate outlier variants."""
    outlier_ratios = [0.01, 0.05, 0.1]

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    count = 0
    for ratio in outlier_ratios:
        with_outliers = add_outliers(points, ratio)
        filename = f"{base_name}_outliers_{int(ratio*100)}pct.ply"
        save_ply(with_outliers, output_dir / filename)
        count += 1
        print(f"Generated {filename}")

    print(f"Generated {count} outlier variants")
    return count


def generate_combined_scenarios(points, output_dir, base_name):
    """Generate realistic combined scenarios."""
    scenarios = [
        {
            'name': 'slight_misalignment',
            'rotation': (5, 'z'),
            'translation': ((1, 0, 0), 10),
            'noise': 0.01,
        },
        {
            'name': 'moderate_misalignment',
            'rotation': (30, 'y'),
            'translation': ((1, 1, 0), 50),
            'noise': 0.1,
        },
        {
            'name': 'severe_misalignment',
            'rotation': (90, 'x'),
            'translation': ((1, 1, 1), 200),
            'noise': 0.5,
        },
        {
            'name': 'sparse_with_noise',
            'subsample': 0.25,
            'noise': 0.1,
            'outliers': 0.05,
        },
    ]

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    count = 0
    for scenario in scenarios:
        modified = points.copy()

        # Apply transformations
        if 'rotation' in scenario:
            angle, axis = scenario['rotation']
            modified = rotate_points(modified, angle, axis)

        if 'translation' in scenario:
            direction, dist = scenario['translation']
            modified = translate_points(modified, direction, dist)

        if 'subsample' in scenario:
            modified = subsample_points(modified, scenario['subsample'])

        if 'noise' in scenario:
            modified = add_noise(modified, scenario['noise'])

        if 'outliers' in scenario:
            modified = add_outliers(modified, scenario['outliers'])

        # Save
        filename = f"{base_name}_{scenario['name']}.ply"
        save_ply(modified, output_dir / filename)

        # Save metadata
        meta_file = output_dir / f"{base_name}_{scenario['name']}.json"
        with open(meta_file, 'w') as f:
            json.dump(scenario, f, indent=2)

        count += 1
        print(f"Generated {filename}")

    print(f"Generated {count} combined scenarios")
    return count


def main():
    """Generate all augmented test datasets."""
    # Load original data
    project_root = Path(__file__).parent.parent
    original_dir = project_root / "tests" / "test_data" / "original"

    closed_file = original_dir / "UNIT_111_Closed_J1.ply"
    open_file = original_dir / "UNIT_111_Open_J1.ply"

    if not closed_file.exists():
        # Try root directory
        closed_file = project_root / "UNIT_111_Closed_J1.ply"
        open_file = project_root / "UNIT_111_Open_J1.ply"

    if not closed_file.exists():
        print(f"ERROR: Could not find UNIT_111 files")
        print(f"Looked in: {original_dir}")
        print(f"And: {project_root}")
        return

    print("Loading UNIT_111 point clouds...")
    closed_points, _ = load_ply(str(closed_file))
    open_points, _ = load_ply(str(open_file))

    print(f"Loaded {len(closed_points)} closed points")
    print(f"Loaded {len(open_points)} open points")

    # Generate augmented data
    test_data_dir = project_root / "tests" / "test_data"
    total_count = 0

    print("\n=== Generating Rotations ===")
    total_count += generate_rotations(closed_points, test_data_dir / "rotations", "closed")

    print("\n=== Generating Translations ===")
    total_count += generate_translations(closed_points, test_data_dir / "translations", "closed")

    print("\n=== Generating Noise Variants ===")
    total_count += generate_noise_variants(closed_points, test_data_dir / "noise", "closed")

    print("\n=== Generating Subsampled Variants ===")
    total_count += generate_subsampled_variants(closed_points, test_data_dir / "subsampled", "closed")

    print("\n=== Generating Outlier Variants ===")
    total_count += generate_outlier_variants(closed_points, test_data_dir / "outliers", "closed")

    print("\n=== Generating Combined Scenarios ===")
    total_count += generate_combined_scenarios(closed_points, test_data_dir / "combined", "closed")

    print(f"\n{'='*60}")
    print(f"TOTAL: Generated {total_count} augmented test files")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
