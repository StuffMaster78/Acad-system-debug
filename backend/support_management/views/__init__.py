"""
Support Management Views Package
Main views are in support_management.views (parent file)
This package contains additional views for enhanced disputes
"""
# Import all from parent views.py
import importlib.util
from pathlib import Path

_parent_views = Path(__file__).parent.parent / 'views.py'
if _parent_views.exists():
    spec = importlib.util.spec_from_file_location("support_management.views_main", _parent_views)
    if spec and spec.loader:
        views_main = importlib.util.module_from_spec(spec)
        views_main.__package__ = 'support_management'
        spec.loader.exec_module(views_main)
        # Export all ViewSets from parent - get all classes ending in ViewSet
        for attr_name in dir(views_main):
            if attr_name.endswith('ViewSet') and not attr_name.startswith('_'):
                globals()[attr_name] = getattr(views_main, attr_name)

# Import from this package
try:
    from .enhanced_disputes import OrderDisputeViewSet, DisputeMessageViewSet
except ImportError:
    OrderDisputeViewSet = None
    DisputeMessageViewSet = None

# Build __all__ dynamically
_all_list = [
    'OrderDisputeViewSet',
    'DisputeMessageViewSet',
]
# Add all ViewSets from parent
if _parent_views.exists() and spec and spec.loader:
    for attr_name in dir(views_main):
        if attr_name.endswith('ViewSet') and not attr_name.startswith('_'):
            if attr_name not in _all_list:
                _all_list.append(attr_name)

__all__ = _all_list

