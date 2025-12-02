"""
Writer Management Serializers Package
Main serializers are in writer_management.serializers (parent file)
This package contains additional serializers for capacity, feedback, portfolio
"""
# Import all from parent serializers.py
import importlib.util
from pathlib import Path

_parent_serializers = Path(__file__).parent.parent / 'serializers.py'
if _parent_serializers.exists():
    spec = importlib.util.spec_from_file_location("writer_management.serializers_main", _parent_serializers)
    if spec and spec.loader:
        serializers_main = importlib.util.module_from_spec(spec)
        serializers_main.__package__ = 'writer_management'
        spec.loader.exec_module(serializers_main)
        # Export all serializers from parent - get all classes ending in Serializer
        for attr_name in dir(serializers_main):
            if attr_name.endswith('Serializer') and not attr_name.startswith('_'):
                globals()[attr_name] = getattr(serializers_main, attr_name)

# Import from this package
from .capacity import (
    WriterCapacitySerializer,
    WriterCapacityUpdateSerializer,
    EditorWorkloadSerializer,
)
from .feedback import (
    FeedbackSerializer,
    FeedbackCreateSerializer,
    FeedbackHistorySerializer,
)
from .portfolio import (
    WriterPortfolioSerializer,
    WriterPortfolioUpdateSerializer,
    PortfolioSampleSerializer,
    PortfolioSampleCreateSerializer,
)

# Build __all__ dynamically
_all_list = [
    # Capacity
    'WriterCapacitySerializer',
    'WriterCapacityUpdateSerializer',
    'EditorWorkloadSerializer',
    # Feedback
    'FeedbackSerializer',
    'FeedbackCreateSerializer',
    'FeedbackHistorySerializer',
    # Portfolio
    'WriterPortfolioSerializer',
    'WriterPortfolioUpdateSerializer',
    'PortfolioSampleSerializer',
    'PortfolioSampleCreateSerializer',
]
# Add all serializers from parent
if _parent_serializers.exists() and spec and spec.loader:
    for attr_name in dir(serializers_main):
        if attr_name.endswith('Serializer') and not attr_name.startswith('_'):
            if attr_name not in _all_list:
                _all_list.append(attr_name)

__all__ = _all_list

