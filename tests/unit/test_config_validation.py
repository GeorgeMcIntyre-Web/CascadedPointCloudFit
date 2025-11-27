"""Unit tests for Config validation."""

import pytest
import yaml
from pathlib import Path
from cascaded_fit.utils.config import Config
from cascaded_fit.utils.exceptions import ConfigurationError


class TestConfigValidation:
    """Test Config validation."""

    def test_validate_missing_section(self, tmp_path):
        """Test validation fails when required section is missing."""
        config_file = tmp_path / "incomplete.yaml"
        config_data = {
            'registration': {
                'rmse_threshold': 0.01,
                'max_iterations': 200,
                'tolerance': 1e-7
            }
            # Missing icp, fgr, api sections
        }
        config_file.write_text(yaml.dump(config_data))
        
        Config._config = {}
        
        with pytest.raises(ConfigurationError, match="missing required sections"):
            Config.load(str(config_file))

    def test_validate_invalid_yaml(self, tmp_path):
        """Test validation fails with invalid YAML."""
        config_file = tmp_path / "invalid.yaml"
        config_file.write_text("invalid: yaml: content: [")
        
        Config._config = {}
        
        with pytest.raises(ConfigurationError, match="Failed to parse YAML"):
            Config.load(str(config_file))

