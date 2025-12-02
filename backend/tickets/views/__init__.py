"""
Tickets Views Package
Main views are in tickets.views (parent file)
This package contains additional views for SLA timers
"""
# Import all from parent views.py
import importlib.util
from pathlib import Path

_parent_views = Path(__file__).parent.parent / 'views.py'
if _parent_views.exists():
    spec = importlib.util.spec_from_file_location("tickets.views_main", _parent_views)
    if spec and spec.loader:
        views_main = importlib.util.module_from_spec(spec)
        views_main.__package__ = 'tickets'
        spec.loader.exec_module(views_main)
        # Export all ViewSets from parent - get all classes ending in ViewSet
        for attr_name in dir(views_main):
            if attr_name.endswith('ViewSet') and not attr_name.startswith('_'):
                globals()[attr_name] = getattr(views_main, attr_name)

# Import from this package
try:
    from .sla_timers import TicketSLAViewSet
except ImportError:
    TicketSLAViewSet = None

# Build __all__ dynamically
_all_list = [
    'TicketSLAViewSet',
]
# Add all ViewSets from parent
if _parent_views.exists() and spec and spec.loader:
    for attr_name in dir(views_main):
        if attr_name.endswith('ViewSet') and not attr_name.startswith('_'):
            if attr_name not in _all_list:
                _all_list.append(attr_name)

__all__ = _all_list

