"""
Fines views - import all views here.
"""
import os
import sys
import importlib.util

# Import new views from submodules
from .lateness_rule_views import (
    LatenessFineRuleViewSet,
    FineTypeConfigViewSet,
)

# Import legacy views from _legacy_views.py file
def _import_legacy_views():
    """Import legacy views from _legacy_views.py"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)  # fines/
    legacy_views_path = os.path.join(parent_dir, '_legacy_views.py')
    
    if not os.path.exists(legacy_views_path):
        return None
    
    spec = importlib.util.spec_from_file_location("fines._legacy_views", legacy_views_path)
    if spec is None or spec.loader is None:
        return None
    
    module = importlib.util.module_from_spec(spec)
    module.__package__ = "fines"
    module.__name__ = "fines._legacy_views"
    spec.loader.exec_module(module)
    
    return module

# Import legacy views
_legacy_views_module = _import_legacy_views()

if _legacy_views_module:
    # Import all ViewSets and views from legacy module dynamically
    for name in dir(_legacy_views_module):
        if not name.startswith('_') and (name.endswith('ViewSet') or name.endswith('View')):
            globals()[name] = getattr(_legacy_views_module, name)
    
    # Verify critical views exist
    if not hasattr(_legacy_views_module, 'FineViewSet'):
        raise ImportError("Could not import FineViewSet from _legacy_views.py")
else:
    raise ImportError("Could not import legacy views from _legacy_views.py")

__all__ = [
    # New views from submodules
    'LatenessFineRuleViewSet',
    'FineTypeConfigViewSet',
    # Legacy views (dynamically imported)
]

