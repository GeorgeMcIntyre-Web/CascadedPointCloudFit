"""Configuration management using YAML files."""

import yaml
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass


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
        """Load configuration from YAML file."""
        if config_path is None:
            # Default to config/default.yaml in project root
            config_path = Path(__file__).parent.parent.parent / "config" / "default.yaml"
        else:
            config_path = Path(config_path)

        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        with open(config_path, 'r') as f:
            cls._config = yaml.safe_load(f)

        return cls._instance

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
        """Get typed registration configuration."""
        if not cls._config:
            cls.load()

        reg_cfg = cls._config['registration']

        return RegistrationConfig(
            rmse_threshold=reg_cfg['rmse_threshold'],
            max_iterations=reg_cfg['max_iterations'],
            tolerance=reg_cfg['tolerance']
        )

    @classmethod
    def get_icp_config(cls) -> ICPConfig:
        """Get typed ICP configuration."""
        if not cls._config:
            cls.load()

        icp_cfg = cls._config['icp']

        return ICPConfig(**icp_cfg)

    @classmethod
    def get_fgr_config(cls) -> FGRConfig:
        """Get typed FGR configuration."""
        if not cls._config:
            cls.load()

        fgr_cfg = cls._config['fgr']

        return FGRConfig(**fgr_cfg)

    @classmethod
    def get_api_config(cls) -> APIConfig:
        """Get typed API configuration."""
        if not cls._config:
            cls.load()

        api_cfg = cls._config['api']

        return APIConfig(**api_cfg)
