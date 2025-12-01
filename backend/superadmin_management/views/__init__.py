"""
Superadmin Management Views Package
"""
# Import ViewSets from parent views.py module
# We need to import from the parent directory's views.py file
import sys
from pathlib import Path

# Get the parent directory
parent_dir = Path(__file__).parent.parent
views_py_path = parent_dir / 'views.py'

# Import the parent views.py module
if views_py_path.exists():
    import importlib.util
    spec = importlib.util.spec_from_file_location("superadmin_management.views_main", views_py_path)
    views_main = importlib.util.module_from_spec(spec)
    sys.modules["superadmin_management.views_main"] = views_main
    spec.loader.exec_module(views_main)
    
    # Export ViewSets from parent views.py
    SuperadminProfileViewSet = views_main.SuperadminProfileViewSet
    UserManagementViewSet = views_main.UserManagementViewSet
    SuperadminLogViewSet = views_main.SuperadminLogViewSet
    SuperadminDashboardViewSet = views_main.SuperadminDashboardViewSet
    AppealViewSet = views_main.AppealViewSet
else:
    # Fallback: try direct import (won't work if views/ directory exists)
    from ..views import (
        SuperadminProfileViewSet,
        UserManagementViewSet,
        SuperadminLogViewSet,
        SuperadminDashboardViewSet,
        AppealViewSet,
    )

# Import from tenant_management
from .tenant_management import SuperadminTenantManagementViewSet

__all__ = [
    'SuperadminProfileViewSet',
    'UserManagementViewSet',
    'SuperadminLogViewSet',
    'SuperadminDashboardViewSet',
    'AppealViewSet',
    'SuperadminTenantManagementViewSet',
]

