"""
Websites Views Package
"""
# Import from parent views.py
import importlib.util
from pathlib import Path

_parent_views = Path(__file__).parent.parent / 'views.py'
if _parent_views.exists():
    spec = importlib.util.spec_from_file_location("websites.views_main", _parent_views)
    if spec and spec.loader:
        views_main = importlib.util.module_from_spec(spec)
        views_main.__package__ = 'websites'
        spec.loader.exec_module(views_main)
        # Export all views from parent
        WebsiteViewSet = getattr(views_main, 'WebsiteViewSet', None)
        WebsiteActionLogViewSet = getattr(views_main, 'WebsiteActionLogViewSet', None)
        WebsiteStaticPageViewSet = getattr(views_main, 'WebsiteStaticPageViewSet', None)
    else:
        WebsiteViewSet = None
        WebsiteActionLogViewSet = None
        WebsiteStaticPageViewSet = None
else:
    WebsiteViewSet = None
    WebsiteActionLogViewSet = None
    WebsiteStaticPageViewSet = None

# Import from this package
try:
    from .tenant_features import TenantBrandingViewSet, TenantFeatureToggleViewSet
except ImportError:
    TenantBrandingViewSet = None
    TenantFeatureToggleViewSet = None

__all__ = [
    'WebsiteViewSet',
    'WebsiteActionLogViewSet',
    'WebsiteStaticPageViewSet',
    'TenantBrandingViewSet',
    'TenantFeatureToggleViewSet',
]

