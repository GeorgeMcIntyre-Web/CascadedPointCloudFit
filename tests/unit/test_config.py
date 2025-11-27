"""Unit tests for Config utility."""

import pytest
import yaml
from pathlib import Path
from unittest.mock import patch, mock_open
from cascaded_fit.utils.config import Config, ICPConfig, FGRConfig, RegistrationConfig, APIConfig
from cascaded_fit.utils.exceptions import ConfigurationError


class TestConfig:
    """Test Config class."""

    def test_singleton_pattern(self):
        """Test Config is a singleton."""
        config1 = Config()
        config2 = Config()
        assert config1 is config2

    def test_load_default_config(self):
        """Test loading default configuration."""
        config = Config()
        # Reset for test
        Config._config = {}
        Config._configured = False
        
        config.load()
        assert Config._config is not None
        assert 'registration' in Config._config

    def test_load_custom_config(self, tmp_path):
        """Test loading custom configuration file."""
        config_file = tmp_path / "custom.yaml"
        # Include all required sections for validation
        config_data = {
            'registration': {
                'rmse_threshold': 0.001,
                'max_iterations': 100,
                'tolerance': 1e-8
            },
            'icp': {
                'max_correspondence_distance': 100.0,
                'relative_fitness': 1e-7,
                'relative_rmse': 1e-7
            },
            'fgr': {
                'distance_threshold': 0.01,
                'voxel_size': 10.0,
                'max_correspondence_distance': 0.0003
            },
            'api': {
                'host': '0.0.0.0',
                'port': 5000,
                'debug': False,
                'max_points': 1000000,
                'timeout': 300,
                'rmse_threshold': 0.001,
                'enable_bidirectional': True
            }
        }
        config_file.write_text(yaml.dump(config_data))
        
        Config._config = {}
        config = Config()
        config.load(str(config_file))
        
        assert Config._config['registration']['rmse_threshold'] == 0.001

    def test_load_nonexistent_file(self):
        """Test loading nonexistent configuration file."""
        Config._config = {}
        config = Config()
        
        with pytest.raises(FileNotFoundError):
            config.load('nonexistent.yaml')

    def test_get_config_value(self):
        """Test getting configuration value."""
        Config._config = {
            'registration': {
                'rmse_threshold': 0.01
            }
        }
        
        value = Config.get('registration.rmse_threshold')
        assert value == 0.01

    def test_get_config_value_default(self):
        """Test getting configuration value with default."""
        Config._config = {}
        
        value = Config.get('nonexistent.key', default='default_value')
        assert value == 'default_value'

    def test_get_registration_config(self):
        """Test getting typed registration configuration."""
        Config._config = {
            'registration': {
                'rmse_threshold': 0.01,
                'max_iterations': 200,
                'tolerance': 1e-7
            }
        }
        
        reg_config = Config.get_registration_config()
        assert isinstance(reg_config, RegistrationConfig)
        assert reg_config.rmse_threshold == 0.01
        assert reg_config.max_iterations == 200

    def test_get_icp_config(self):
        """Test getting typed ICP configuration."""
        Config._config = {
            'icp': {
                'max_correspondence_distance': 100.0,
                'relative_fitness': 1e-7,
                'relative_rmse': 1e-7
            }
        }
        
        icp_config = Config.get_icp_config()
        assert isinstance(icp_config, ICPConfig)
        assert icp_config.max_correspondence_distance == 100.0

    def test_get_fgr_config(self):
        """Test getting typed FGR configuration."""
        Config._config = {
            'fgr': {
                'distance_threshold': 0.01,
                'voxel_size': 10.0,
                'max_correspondence_distance': 0.0003,
                'radius_normal_factor': 2,
                'radius_feature_factor': 5,
                'max_nn_normal': 30,
                'max_nn_feature': 100
            }
        }
        
        fgr_config = Config.get_fgr_config()
        assert isinstance(fgr_config, FGRConfig)
        assert fgr_config.voxel_size == 10.0
        assert fgr_config.radius_normal_factor == 2

    def test_get_api_config(self):
        """Test getting typed API configuration."""
        Config._config = {
            'api': {
                'host': '0.0.0.0',
                'port': 5000,
                'debug': False,
                'max_points': 1000000,
                'timeout': 300,
                'rmse_threshold': 0.001,
                'enable_bidirectional': True
            }
        }
        
        api_config = Config.get_api_config()
        assert isinstance(api_config, APIConfig)
        assert api_config.host == '0.0.0.0'
        assert api_config.port == 5000
        assert api_config.debug is False

