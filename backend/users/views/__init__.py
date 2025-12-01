"""
Users views package.
"""
# Import account management views
from .account_management import AccountManagementViewSet

# Import UserViewSet from the main views.py file
# Since users/views.py exists alongside users/views/ package, we need to import it dynamically
import importlib.util
from pathlib import Path

_parent_dir = Path(__file__).parent.parent
_views_py_path = _parent_dir / 'views.py'

if _views_py_path.exists():
    spec = importlib.util.spec_from_file_location("users.views_main", _views_py_path)
    if spec and spec.loader:
        views_main = importlib.util.module_from_spec(spec)
        views_main.__package__ = "users"
        views_main.__name__ = "users.views_main"
        spec.loader.exec_module(views_main)
        UserViewSet = getattr(views_main, 'UserViewSet', None)
        if UserViewSet:
            # Make UserViewSet available at package level
            globals()['UserViewSet'] = UserViewSet
            __all__ = [
                'AccountManagementViewSet',
                'UserViewSet',
            ]
        else:
            __all__ = ['AccountManagementViewSet']
    else:
        __all__ = ['AccountManagementViewSet']
else:
    __all__ = ['AccountManagementViewSet']
