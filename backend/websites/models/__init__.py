"""
Websites Models Package
Main models are in websites.models (parent file)
This package contains additional models like TenantBranding, TenantFeatureToggle
"""
# Import from parent models.py
import sys
from pathlib import Path

_parent_models = Path(__file__).parent.parent / 'models.py'
if _parent_models.exists():
    import importlib.util
    spec = importlib.util.spec_from_file_location("websites.models_main", _parent_models)
    if spec and spec.loader:
        models_main = importlib.util.module_from_spec(spec)
        models_main.__package__ = 'websites'
        spec.loader.exec_module(models_main)
        # Re-export all models from parent
        Website = models_main.Website
        WebsiteActionLog = getattr(models_main, 'WebsiteActionLog', None)
        WebsiteStaticPage = getattr(models_main, 'WebsiteStaticPage', None)
        WebsiteSettings = getattr(models_main, 'WebsiteSettings', None)
        WebsiteTermsAcceptance = getattr(models_main, 'WebsiteTermsAcceptance', None)
        ExternalReviewLink = getattr(models_main, 'ExternalReviewLink', None)
        GuestAccessToken = getattr(models_main, 'GuestAccessToken', None)
        User = getattr(models_main, 'User', None)  # User is an alias for AUTH_USER_MODEL
    else:
        Website = None
        WebsiteActionLog = None
        WebsiteStaticPage = None
else:
    Website = None
    WebsiteActionLog = None
    WebsiteStaticPage = None

# Import from this package
try:
    from .tenant_features import TenantBranding, TenantFeatureToggle
except ImportError:
    TenantBranding = None
    TenantFeatureToggle = None

__all__ = [
    'Website',
    'WebsiteActionLog',
    'WebsiteStaticPage',
    'WebsiteSettings',
    'WebsiteTermsAcceptance',
    'ExternalReviewLink',
    'GuestAccessToken',
    'User',
    'TenantBranding',
    'TenantFeatureToggle',
]

