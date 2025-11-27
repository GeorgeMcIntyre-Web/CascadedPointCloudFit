"""Custom exceptions for error handling."""


class CascadedFitError(Exception):
    """Base exception for all cascaded fit errors."""
    pass


class PointCloudLoadError(CascadedFitError):
    """Error loading point cloud file."""
    pass


class PointCloudValidationError(CascadedFitError):
    """Point cloud validation failed."""
    pass


class RegistrationError(CascadedFitError):
    """Registration algorithm failed."""
    pass


class ConvergenceError(RegistrationError):
    """Registration did not converge."""
    pass


class ConfigurationError(CascadedFitError):
    """Invalid configuration."""
    pass


class InsufficientPointsError(PointCloudValidationError):
    """Not enough points for registration."""
    def __init__(self, actual: int, required: int):
        self.actual = actual
        self.required = required
        super().__init__(
            f"Insufficient points: got {actual}, need at least {required}"
        )
