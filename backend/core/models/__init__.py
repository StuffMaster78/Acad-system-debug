from .base import BaseModel, WebsiteSpecificBaseModel

try:
    from .config_versioning import ConfigVersion
    __all__ = [
        "BaseModel",
        "WebsiteSpecificBaseModel",
        "ConfigVersion",
    ]
except ImportError:
    __all__ = [
        "BaseModel",
        "WebsiteSpecificBaseModel",
    ]
