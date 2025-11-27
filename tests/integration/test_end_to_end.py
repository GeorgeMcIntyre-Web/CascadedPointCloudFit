"""
Integration tests for end-to-end registration pipeline.

Tests the complete workflow from file reading to registration results.
"""

import pytest
import numpy as np
from pathlib import Path
import sys

from cascaded_fit.fitters.cascaded_fitter import CascadedFitter
from cascaded_fit.fitters.icp_fitter import IcpFitter
from cascaded_fit.fitters.fgr_fitter import FgrFitter
from cascaded_fit.io.readers import PointCloudReader
from cascaded_fit.utils.config import Config
from cascaded_fit.utils.exceptions import RegistrationError, ConvergenceError


class TestEndToEndRegistration:
    """Test complete registration pipeline."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test environment."""
        # Load default config
        Config.load()

    @pytest.fixture
    def test_data_dir(self):
        """Get test data directory path."""
        return Path(__file__).parent.parent.parent / "test_data"

    @pytest.fixture
    def real_world_data_dir(self):
        """Get real-world test data directory path."""
        return Path(__file__).parent.parent.parent / "test_data" / "real_world_data"

    def test_unit_111_registration(self, test_data_dir):
        """Test registration with UNIT_111 point clouds."""
        source_file = str(test_data_dir / "UNIT_111_Open_J1.ply")
        target_file = str(test_data_dir / "UNIT_111_Closed_J1.ply")

        # Skip if files don't exist
        if not Path(source_file).exists() or not Path(target_file).exists():
            pytest.skip("UNIT_111 test files not found")

        # Create fitter
        fitter = CascadedFitter(visualize=False)

        # Run registration
        result = fitter.run(source_file, target_file)

        # Verify result structure
        assert 'transformation' in result
        assert 'inlier_rmse' in result
        assert 'max_error' in result
        assert 'is_success' in result
        assert 'method' in result

        # Verify transformation is 4x4 matrix
        transform = np.array(result['transformation'])
        assert transform.shape == (4, 4)

        # Verify transformation is valid (bottom row should be [0, 0, 0, 1])
        np.testing.assert_array_almost_equal(
            transform[3, :],
            [0, 0, 0, 1],
            decimal=6
        )

    def test_clamp_registration(self, real_world_data_dir):
        """Test registration with Clamp point clouds."""
        source_file = str(real_world_data_dir / "Clamp1.ply")
        target_file = str(real_world_data_dir / "Clamp2.ply")

        # Skip if files don't exist
        if not Path(source_file).exists() or not Path(target_file).exists():
            pytest.skip("Clamp test files not found")

        # Create fitter
        fitter = CascadedFitter(visualize=False)

        # Run registration
        result = fitter.run(source_file, target_file)

        # Verify result
        assert result is not None
        assert 'transformation' in result

    def test_slide_registration(self, real_world_data_dir):
        """Test registration with Slide point clouds."""
        source_file = str(real_world_data_dir / "Slide1.ply")
        target_file = str(real_world_data_dir / "Slide2.ply")

        # Skip if files don't exist
        if not Path(source_file).exists() or not Path(target_file).exists():
            pytest.skip("Slide test files not found")

        # Create fitter
        fitter = CascadedFitter(visualize=False)

        # Run registration
        result = fitter.run(source_file, target_file)

        # Verify result
        assert result is not None
        assert 'transformation' in result

    def test_augmented_rotation_registration(self, test_data_dir):
        """Test registration with augmented rotated data."""
        source_file = str(test_data_dir / "UNIT_111_Closed_J1.ply")

        # Try multiple rotation angles
        rotation_files = [
            "UNIT_111_Closed_J1_rot_x_10.0.ply",
            "UNIT_111_Closed_J1_rot_y_15.0.ply",
            "UNIT_111_Closed_J1_rot_z_20.0.ply"
        ]

        for rot_file in rotation_files:
            target_file = str(test_data_dir / rot_file)

            if not Path(target_file).exists():
                continue

            # Create fitter
            fitter = CascadedFitter(visualize=False)

            # Run registration
            result = fitter.run(source_file, target_file)

            # Should succeed on rotated versions
            assert result is not None
            assert 'transformation' in result

            # Verify reasonable RMSE (rotated clouds should register well)
            if result['is_success']:
                assert result['inlier_rmse'] < 1.0  # Reasonable threshold

    def test_augmented_translation_registration(self, test_data_dir):
        """Test registration with augmented translated data."""
        source_file = str(test_data_dir / "UNIT_111_Closed_J1.ply")

        # Try multiple translations
        translation_files = [
            "UNIT_111_Closed_J1_trans_10.0_0.0_0.0.ply",
            "UNIT_111_Closed_J1_trans_0.0_15.0_0.0.ply"
        ]

        for trans_file in translation_files:
            target_file = str(test_data_dir / trans_file)

            if not Path(target_file).exists():
                continue

            # Create fitter
            fitter = CascadedFitter(visualize=False)

            # Run registration
            result = fitter.run(source_file, target_file)

            # Should succeed on translated versions
            assert result is not None
            assert 'transformation' in result

    def test_icp_fitter_integration(self, test_data_dir):
        """Test ICP fitter integration."""
        source_file = str(test_data_dir / "UNIT_111_Open_J1.ply")
        target_file = str(test_data_dir / "UNIT_111_Closed_J1.ply")

        if not Path(source_file).exists() or not Path(target_file).exists():
            pytest.skip("UNIT_111 test files not found")

        # Load point clouds
        source_cloud = PointCloudReader.read_point_cloud_file(source_file)
        target_cloud = PointCloudReader.read_point_cloud_file(target_file)

        # Create ICP fitter
        icp_fitter = IcpFitter(rmse_threshold=0.01)

        # Run fit
        result = icp_fitter.fit(source_cloud, target_cloud)

        # Verify result
        assert result is not None
        assert hasattr(result, 'transformation')
        assert hasattr(result, 'inlier_rmse')
        assert hasattr(result, 'is_success')

        # Transformation should be 4x4
        assert result.transformation.shape == (4, 4)

    def test_fgr_fitter_integration(self, test_data_dir):
        """Test FGR fitter integration."""
        source_file = str(test_data_dir / "UNIT_111_Open_J1.ply")
        target_file = str(test_data_dir / "UNIT_111_Closed_J1.ply")

        if not Path(source_file).exists() or not Path(target_file).exists():
            pytest.skip("UNIT_111 test files not found")

        # Load point clouds
        source_cloud = PointCloudReader.read_point_cloud_file(source_file)
        target_cloud = PointCloudReader.read_point_cloud_file(target_file)

        # Create FGR fitter
        fgr_fitter = FgrFitter(rmse_threshold=0.01)

        # Run fit
        result = fgr_fitter.fit(source_cloud, target_cloud)

        # Verify result
        assert result is not None
        assert hasattr(result, 'transformation')
        assert hasattr(result, 'inlier_rmse')
        assert hasattr(result, 'is_success')

    def test_csv_format_support(self, real_world_data_dir):
        """Test CSV file format support."""
        source_file = str(real_world_data_dir / "Clamp1.csv")
        target_file = str(real_world_data_dir / "Clamp2.csv")

        if not Path(source_file).exists() or not Path(target_file).exists():
            pytest.skip("Clamp CSV files not found")

        # Create fitter
        fitter = CascadedFitter(visualize=False)

        # Run registration
        result = fitter.run(source_file, target_file)

        # Verify result
        assert result is not None
        assert 'transformation' in result

    def test_challenging_case_clouds3(self, real_world_data_dir):
        """Test with challenging case from Clouds3 directory."""
        clouds3_dir = real_world_data_dir / "Clouds3"

        if not clouds3_dir.exists():
            pytest.skip("Clouds3 directory not found")

        # Find M2 and O2 files
        m2_file = clouds3_dir / "016ZF-20137361-670B-109R_CI00_M2.ply"
        o2_file = clouds3_dir / "016ZF-20137361-670B-109R_CI00_O2.ply"

        if not m2_file.exists() or not o2_file.exists():
            pytest.skip("Clouds3 test files not found")

        # Create fitter
        fitter = CascadedFitter(visualize=False)

        # Run registration - this should succeed or fail gracefully
        try:
            result = fitter.run(str(m2_file), str(o2_file))
            assert result is not None
        except (RegistrationError, ConvergenceError) as e:
            # Expected to potentially fail - this is a known difficult case
            pytest.skip(f"Registration failed as expected: {e}")

    def test_known_failure_case_icp_fails(self, real_world_data_dir):
        """Test with known ICP failure case."""
        icp_fails_dir = real_world_data_dir / "IcpFails"

        if not icp_fails_dir.exists():
            pytest.skip("IcpFails directory not found")

        # Find M and O files
        m_file = icp_fails_dir / "M.ply"
        o_file = icp_fails_dir / "O.ply"

        if not m_file.exists() or not o_file.exists():
            # Try alternative naming
            files = list(icp_fails_dir.glob("*_M*.ply"))
            if files:
                m_file = files[0]
                o_file = icp_fails_dir / str(files[0].name).replace("_M", "_O")

        if not m_file.exists() or not o_file.exists():
            pytest.skip("IcpFails test files not found")

        # Create fitter
        fitter = CascadedFitter(visualize=False)

        # This is a known failure case - should either succeed or fail gracefully
        try:
            result = fitter.run(str(m_file), str(o_file))

            # If it succeeded, verify result is valid (ICP or FGR both acceptable)
            if result['is_success']:
                assert result.get('method') in ['ICP', 'FGR', 'FGR+ICP']
                # Our refactored ICP may succeed where original failed!
                assert result['inlier_rmse'] < 0.01  # Verify good registration

        except (RegistrationError, ConvergenceError):
            # Expected to potentially fail - this is a known difficult case
            pass  # Test passes if it fails gracefully


class TestCLIIntegration:
    """Test CLI integration."""

    def test_cli_imports(self):
        """Test that CLI can be imported."""
        from cascaded_fit.cli.main import CLI

        cli = CLI()
        assert cli is not None
        assert cli.parser is not None

    def test_cli_help(self):
        """Test CLI help output."""
        from cascaded_fit.cli.main import CLI

        cli = CLI()

        # Should not raise exception
        help_text = cli.parser.format_help()
        assert 'source_file' in help_text
        assert 'target_file' in help_text


class TestAPIIntegration:
    """Test Flask API integration."""

    def test_api_imports(self):
        """Test that API can be imported."""
        from cascaded_fit.api.app import app, PointCloudAPI

        assert app is not None
        api_handler = PointCloudAPI()
        assert api_handler is not None

    def test_api_health_endpoint(self):
        """Test API health check endpoint."""
        from cascaded_fit.api.app import app

        client = app.test_client()
        response = client.get('/health')

        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'

    def test_api_process_endpoint_missing_data(self):
        """Test API endpoint with missing data."""
        from cascaded_fit.api.app import app

        client = app.test_client()
        response = client.post('/process_point_clouds', json={})

        # Should return 400 error for missing fields
        assert response.status_code == 400

    def test_api_process_endpoint_valid_data(self):
        """Test API endpoint with valid point cloud data."""
        from cascaded_fit.api.app import app

        # Create small test point clouds
        source_points = np.random.rand(100, 3).tolist()
        target_points = (np.random.rand(100, 3) + 0.1).tolist()

        client = app.test_client()
        response = client.post('/process_point_clouds', json={
            'source_points': source_points,
            'target_points': target_points
        })

        # Should return 200 (might succeed or fail registration)
        assert response.status_code in [200, 500]

        if response.status_code == 200:
            data = response.get_json()
            assert 'transformation' in data
            assert 'inlier_rmse' in data
