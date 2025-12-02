"""
Websites Serializers
"""
# Import from main serializers.py file
import importlib.util
from pathlib import Path

_parent_serializers = Path(__file__).parent.parent / 'serializers.py'
if _parent_serializers.exists():
    spec = importlib.util.spec_from_file_location("websites.serializers_main", _parent_serializers)
    if spec and spec.loader:
        serializers_main = importlib.util.module_from_spec(spec)
        serializers_main.__package__ = 'websites'
        spec.loader.exec_module(serializers_main)
        # Export all serializers from parent - get all classes ending in Serializer
        for attr_name in dir(serializers_main):
            if attr_name.endswith('Serializer') and not attr_name.startswith('_'):
                globals()[attr_name] = getattr(serializers_main, attr_name)
    else:
        WebsiteSerializer = None
        WebsiteActionLogSerializer = None
        WebsiteStaticPageSerializer = None
        WebsiteSettingsSerializer = None
        WebsiteTermsAcceptanceSerializer = None
else:
    WebsiteSerializer = None
    WebsiteActionLogSerializer = None
    WebsiteStaticPageSerializer = None
    WebsiteSettingsSerializer = None
    WebsiteTermsAcceptanceSerializer = None

# Import from this package
try:
    from .tenant_features import (
        TenantBrandingSerializer, TenantBrandingUpdateSerializer,
        TenantFeatureToggleSerializer, TenantFeatureToggleUpdateSerializer
    )
except ImportError:
    TenantBrandingSerializer = None
    TenantBrandingUpdateSerializer = None
    TenantFeatureToggleSerializer = None
    TenantFeatureToggleUpdateSerializer = None

# Build __all__ dynamically
_all_list = [
    'TenantBrandingSerializer',
    'TenantBrandingUpdateSerializer',
    'TenantFeatureToggleSerializer',
    'TenantFeatureToggleUpdateSerializer',
]
# Add all serializers from parent
if _parent_serializers.exists() and spec and spec.loader:
    for attr_name in dir(serializers_main):
        if attr_name.endswith('Serializer') and not attr_name.startswith('_'):
            _all_list.append(attr_name)

__all__ = _all_list

