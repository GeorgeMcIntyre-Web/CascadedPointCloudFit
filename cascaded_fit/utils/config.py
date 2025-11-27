"""Configuration management using YAML files."""

import yaml
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass
from cascaded_fit.utils.exceptions import ConfigurationError


@dataclass
class ICPConfig:
    """ICP algorithm configuration."""
    max_correspondence_distance: float
    relative_fitness: float
    relative_rmse: float


@dataclass
class FGRConfig:
    """FGR algorithm configuration."""
    distance_threshold: float
    voxel_size: float
    max_correspondence_distance: float
    radius_normal_factor: int = 2
    radius_feature_factor: int = 5
    max_nn_normal: int = 30
    max_nn_feature: int = 100


@dataclass
class RegistrationConfig:
    """Overall registration configuration."""
    rmse_threshold: float
    max_iterations: int
    tolerance: float


@dataclass
class APIConfig:
    """REST API configuration."""
    host: str
    port: int
    debug: bool
    max_points: int
    timeout: int
    rmse_threshold: float
    enable_bidirectional: bool


class Config:
    """Global configuration manager."""

    _instance = None
    _config: Dict[str, Any] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def load(cls, config_path: Optional[str] = None) -> "Config":
        """Load configuration from YAML file.
        
        Args:
            config_path: Optional path to configuration file. If None, loads default.yaml
            
        Returns:
            Config instance
            
        Raises:
            FileNotFoundError: If configuration file doesn't exist
            yaml.YAMLError: If YAML parsing fails
        """
        if config_path is None:
            # Default to config/default.yaml in project root
            config_path = Path(__file__).parent.parent.parent / "config" / "default.yaml"
        else:
            config_path = Path(config_path)

        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        try:
            with open(config_path, 'r') as f:
                cls._config = yaml.safe_load(f)
                
            # Validate required sections exist
            cls._validate_config()
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Failed to parse YAML configuration: {e}") from e

        return cls._instance
    
    @classmethod
    def _validate_config(cls) -> None:
        """Validate configuration has required sections."""
        required_sections = ['registration', 'icp', 'fgr', 'api']
        missing = [section for section in required_sections if section not in cls._config]
        
        if missing:
            raise ConfigurationError(
                f"Configuration missing required sections: {', '.join(missing)}"
            )

    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """Get configuration value by dot-separated key."""
        if not cls._config:
            cls.load()  # Auto-load default config

        keys = key.split('.')
        value = cls._config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default

        return value if value is not None else default

    @classmethod
    def get_registration_config(cls) -> RegistrationConfig:
        """Get typed registration configuration.
        
        Returns:
            RegistrationConfig instance
            
        Raises:
            ConfigurationError: If registration section is missing
        """
        if not cls._config:
            cls.load()

        if 'registration' not in cls._config:
            raise ConfigurationError("Configuration missing 'registration' section")

        reg_cfg = cls._config['registration']

        return RegistrationConfig(
            rmse_threshold=reg_cfg['rmse_threshold'],
            max_iterations=reg_cfg['max_iterations'],
            tolerance=reg_cfg['tolerance']
        )

    @classmethod
    def get_icp_config(cls) -> ICPConfig:
        """Get typed ICP configuration.
        
        Returns:
            ICPConfig instance
            
        Raises:
            KeyError: If icp section is missing
            ConfigurationError: If required keys are missing
        """
        if not cls._config:
            cls.load()

        if 'icp' not in cls._config:
            raise ConfigurationError("Configuration missing 'icp' section")

        icp_cfg = cls._config['icp']

        return ICPConfig(**icp_cfg)

    @classmethod
    def get_fgr_config(cls) -> FGRConfig:
        """Get typed FGR configuration.
        
        Returns:
            FGRConfig instance
            
        Raises:
            KeyError: If fgr section is missing
            ConfigurationError: If required keys are missing
        """
        if not cls._config:
            cls.load()

        if 'fgr' not in cls._config:
            raise ConfigurationError("Configuration missing 'fgr' section")

        fgr_cfg = cls._config['fgr']

        return FGRConfig(**fgr_cfg)

    @classmethod
    def get_api_config(cls) -> APIConfig:
        """Get typed API configuration.
        
        Returns:
            APIConfig instance
            
        Raises:
            KeyError: If api section is missing
            ConfigurationError: If required keys are missing
        """
        if not cls._config:
            cls.load()

        if 'api' not in cls._config:
            raise ConfigurationError("Configuration missing 'api' section")

        api_cfg = cls._config['api']

        return APIConfig(**api_cfg)
