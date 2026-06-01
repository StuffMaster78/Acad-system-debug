"""
Re-exports all views from admin_views.
The canonical implementation lives in config_system/api/admin_views.py.
"""
from config_system.api.admin_views import ( # noqa: F401
    ConfigDeleteView,
    ConfigDetailView,
    ConfigListView,
    ConfigRegistryView,
    ConfigUpdateView,
    FeatureCheckView,
    IsConfigAdmin,
)
