"""Serializers package for users app."""
import importlib.util
import sys
from pathlib import Path

# Import from the serializers_legacy.py file directly (not the package)
_parent_dir = Path(__file__).parent.parent
_legacy_path = _parent_dir / 'serializers_legacy.py'

SimpleUserSerializer = None
UserSerializer = None
UserListSerializer = None
UserDetailSerializer = None

if _legacy_path.exists():
    try:
        spec = importlib.util.spec_from_file_location("users.serializers_legacy", _legacy_path)
        if spec and spec.loader:
            _legacy_module = importlib.util.module_from_spec(spec)
            # Set the package context so relative imports work
            _legacy_module.__package__ = 'users'
            _legacy_module.__name__ = 'users.serializers_legacy'
            sys.modules["users.serializers_legacy"] = _legacy_module
            spec.loader.exec_module(_legacy_module)
            
            # Import all serializers from the legacy file
            SimpleUserSerializer = getattr(_legacy_module, 'SimpleUserSerializer', None)
            UserSerializer = getattr(_legacy_module, 'UserSerializer', None)
            UserListSerializer = getattr(_legacy_module, 'UserListSerializer', None)
            UserDetailSerializer = getattr(_legacy_module, 'UserDetailSerializer', None)
            # Import any other commonly used serializers
            for name in dir(_legacy_module):
                if not name.startswith('_') and name.endswith('Serializer'):
                    attr = getattr(_legacy_module, name, None)
                    if attr is not None and callable(attr):
                        setattr(sys.modules[__name__], name, attr)
    except Exception as e:
        # If loading fails, we'll just use None values
        # This allows the package to still be importable
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Failed to load legacy serializers from {_legacy_path}: {e}")

from .privacy import (
    PrivacyAwareWriterSerializer,
    PrivacyAwareClientSerializer,
    get_privacy_aware_serializer,
)

__all__ = [
    'SimpleUserSerializer',
    'UserSerializer',
    'UserListSerializer',
    'UserDetailSerializer',
    'PrivacyAwareWriterSerializer',
    'PrivacyAwareClientSerializer',
    'get_privacy_aware_serializer',
]
