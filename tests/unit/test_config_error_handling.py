"""Unit tests for Config error handling."""

import pytest
import yaml
from pathlib import Path
from cascaded_fit.utils.config import Config
from cascaded_fit.utils.exceptions import ConfigurationError


class TestConfigErrorHandling:
    """Test Config error handling for edge cases."""

    def test_get_config_missing_key(self):
        """Test get() with missing key returns default."""
        Config._config = {}
        value = Config.get('nonexistent.key', default='default')
        assert value == 'default'

    def test_get_registration_config_missing_section(self):
        """Test get_registration_config with missing section."""
        Config._config = {'other': 'section'}  # Config loaded but missing registration
        
        with pytest.raises(ConfigurationError, match="missing 'registration' section"):
            Config.get_registration_config()

    def test_get_icp_config_missing_section(self):
        """Test get_icp_config with missing section."""
        Config._config = {'other': 'section'}  # Config loaded but missing icp
        
        with pytest.raises(ConfigurationError, match="missing 'icp' section"):
            Config.get_icp_config()

    def test_get_fgr_config_missing_section(self):
        """Test get_fgr_config with missing section."""
        Config._config = {'other': 'section'}  # Config loaded but missing fgr
        
        with pytest.raises(ConfigurationError, match="missing 'fgr' section"):
            Config.get_fgr_config()

    def test_get_api_config_missing_section(self):
        """Test get_api_config with missing section."""
        Config._config = {'other': 'section'}  # Config loaded but missing api
        
        with pytest.raises(ConfigurationError, match="missing 'api' section"):
            Config.get_api_config()

    def test_get_config_nested_missing_key(self):
        """Test get() with nested missing key."""
        Config._config = {
            'registration': {
                'rmse_threshold': 0.01
                # Missing max_iterations
            }
        }
        
        value = Config.get('registration.max_iterations', default=200)
        assert value == 200

