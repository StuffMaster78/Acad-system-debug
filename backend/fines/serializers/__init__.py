"""
Fines serializers - import all serializers here.
"""
import os
import sys
import importlib.util

# Import new serializers from submodules
from .lateness_rule_serializers import (
    LatenessFineRuleSerializer,
)
from .fine_type_config_serializers import (
    FineTypeConfigSerializer,
)

# Import legacy serializers from serializers_legacy.py file
def _import_legacy_serializers():
    """Import legacy serializers from serializers_legacy.py"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)  # fines/
    legacy_serializers_path = os.path.join(parent_dir, 'serializers_legacy.py')
    
    if not os.path.exists(legacy_serializers_path):
        return None
    
    spec = importlib.util.spec_from_file_location("fines.serializers_legacy", legacy_serializers_path)
    if spec is None or spec.loader is None:
        return None
    
    module = importlib.util.module_from_spec(spec)
    module.__package__ = "fines"
    module.__name__ = "fines.serializers_legacy"
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
    raise ImportError("Could not import legacy serializers from serializers_legacy.py")

__all__ = [
    # New serializers from submodules
    'LatenessFineRuleSerializer',
    'FineTypeConfigSerializer',
    # Legacy serializers (dynamically imported)
]

