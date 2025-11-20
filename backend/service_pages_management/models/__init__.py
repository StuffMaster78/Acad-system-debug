"""
Service pages management models package.
Contains both legacy models (from _legacy_models.py) and new models from submodules.
"""
import os
import sys
import importlib.util

# Import new models from submodules
from .enhanced_models import (
    ServicePageFAQ,
    ServicePageCTA,
    ServicePageResource,
)
from .pdf_samples import (
    ServicePagePDFSampleSection,
    ServicePagePDFSample,
    ServicePagePDFSampleDownload,
)

# Import legacy models from _legacy_models.py
def _import_legacy_models():
    """Import legacy models from _legacy_models.py"""
    # Get the path to _legacy_models.py
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)  # service_pages_management/
    legacy_models_path = os.path.join(parent_dir, '_legacy_models.py')
    
    if not os.path.exists(legacy_models_path):
        raise FileNotFoundError(f"Could not find _legacy_models.py at {legacy_models_path}")
    
    # Import using importlib with proper module naming
    spec = importlib.util.spec_from_file_location("service_pages_management._legacy_models", legacy_models_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not create spec for {legacy_models_path}")
    
    # Create module and set __package__ so Django recognizes it
    module = importlib.util.module_from_spec(spec)
    module.__package__ = "service_pages_management"
    module.__name__ = "service_pages_management._legacy_models"
    
    # Execute the module
    spec.loader.exec_module(module)
    
    return module

# Import legacy models
_legacy_module = _import_legacy_models()

# Extract and assign legacy models
ServicePage = _legacy_module.ServicePage
ServicePageClick = _legacy_module.ServicePageClick
ServicePageConversion = _legacy_module.ServicePageConversion

# Update __module__ attribute for legacy models so Django knows they belong to this app
for model in [ServicePage, ServicePageClick, ServicePageConversion]:
    if hasattr(model, '_meta'):
        model._meta.app_label = 'service_pages_management'
        model.__module__ = 'service_pages_management.models'

__all__ = [
    # New models from submodules
    'ServicePageFAQ',
    'ServicePageCTA',
    'ServicePageResource',
    'ServicePagePDFSampleSection',
    'ServicePagePDFSample',
    'ServicePagePDFSampleDownload',
    # Legacy models from _legacy_models.py
    'ServicePage',
    'ServicePageClick',
    'ServicePageConversion',
]

