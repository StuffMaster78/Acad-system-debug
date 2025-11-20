"""
Service pages management serializers - import all serializers here.
"""
import os
import sys
import importlib.util

# Import new serializers from submodules
from .enhanced_serializers import (
    ServicePageFAQSerializer,
    ServicePageCTASerializer,
    ServicePageResourceSerializer,
    ServicePageSEOMetadataSerializer,
    ServicePageEditHistorySerializer,
)
from .pdf_serializers import (
    ServicePagePDFSampleSectionSerializer,
    ServicePagePDFSampleSerializer,
)

# Import legacy serializers from _legacy_serializers.py file
def _import_legacy_serializers():
    """Import legacy serializers from _legacy_serializers.py"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)  # service_pages_management/
    legacy_serializers_path = os.path.join(parent_dir, '_legacy_serializers.py')
    
    if not os.path.exists(legacy_serializers_path):
        return None
    
    spec = importlib.util.spec_from_file_location("service_pages_management._legacy_serializers", legacy_serializers_path)
    if spec is None or spec.loader is None:
        return None
    
    module = importlib.util.module_from_spec(spec)
    module.__package__ = "service_pages_management"
    module.__name__ = "service_pages_management._legacy_serializers"
    spec.loader.exec_module(module)
    
    return module

# Import legacy serializers
_legacy_serializers_module = _import_legacy_serializers()

if _legacy_serializers_module:
    # Import all serializers from legacy module dynamically
    for name in dir(_legacy_serializers_module):
        if not name.startswith('_') and name.endswith('Serializer'):
            globals()[name] = getattr(_legacy_serializers_module, name)
else:
    # Legacy serializers optional - may not exist
    pass

__all__ = [
    # New serializers from submodules
    'ServicePageFAQSerializer',
    'ServicePageCTASerializer',
    'ServicePageResourceSerializer',
    'ServicePageSEOMetadataSerializer',
    'ServicePageEditHistorySerializer',
    'ServicePagePDFSampleSectionSerializer',
    'ServicePagePDFSampleSerializer',
    # Legacy serializers (dynamically imported)
]

