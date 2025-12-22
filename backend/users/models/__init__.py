"""
Users Models Package
This __init__.py re-exports all models from the parent models.py file
and additional models from submodules.
"""
# Import all from parent models.py using a direct import
# We need to import from the parent file, not create a circular import
import sys
from pathlib import Path

# Get the parent directory
_parent_dir = Path(__file__).parent.parent
_parent_models_file = _parent_dir / 'models.py'

# Import the parent models.py as a module
if _parent_models_file.exists():
    # Use importlib to load the parent file
    import importlib.util
    spec = importlib.util.spec_from_file_location("users.models_file", _parent_models_file)
    if spec and spec.loader:
        # Load the module
        models_file = importlib.util.module_from_spec(spec)
        # Set the package to avoid circular imports
        models_file.__package__ = 'users'
        # Execute the module to load all models
        try:
            spec.loader.exec_module(models_file)
            # Export all models from the parent file
            # Get all classes that end with Model or are User
            for name in dir(models_file):
                if not name.startswith('_'):
                    obj = getattr(models_file, name)
                    # Export model classes
                    if (isinstance(obj, type) and 
                        (name == 'User' or name.endswith('Model') or 
                         hasattr(obj, '_meta'))):
                        globals()[name] = obj
        except Exception as e:
            # If import fails, we'll handle it gracefully
            # Django will raise its own error if User is missing
            pass

# Import from submodules
try:
    from .login_alerts import LoginAlertPreference
except ImportError:
    LoginAlertPreference = None

try:
    from .user_edit_requests import UserEditRequest
except ImportError:
    UserEditRequest = None

# Build __all__ with all exported models
_all_list = ['LoginAlertPreference']
if 'UserEditRequest' in globals() and UserEditRequest:
    _all_list.append('UserEditRequest')
# Explicitly export common models
if 'User' in globals():
    _all_list.insert(0, 'User')
if 'UserProfile' in globals():
    _all_list.append('UserProfile')
if 'WebsiteTermsAcceptance' in globals():
    _all_list.append('WebsiteTermsAcceptance')
if 'PrivacySettings' in globals():
    _all_list.append('PrivacySettings')
if 'DataAccessLog' in globals():
    _all_list.append('DataAccessLog')
if 'UserAuditLog' in globals():
    _all_list.append('UserAuditLog')
if 'ProfileUpdateRequest' in globals():
    _all_list.append('ProfileUpdateRequest')
if 'DeletionSettings' in globals():
    _all_list.append('DeletionSettings')
if 'UserActivity' in globals():
    _all_list.append('UserActivity')
if 'EmailVerification' in globals():
    _all_list.append('EmailVerification')
# Add any other model classes found
# Collect names first to avoid modifying dict during iteration
_model_names = []
for name in list(globals().keys()):
    if (name not in _all_list and not name.startswith('_') and 
        name not in ['sys', 'Path', 'importlib', 'spec', 'models_file', 'e', '_all_list', '_model_names']):
        obj = globals()[name]
        if isinstance(obj, type) and hasattr(obj, '_meta'):
            _model_names.append(name)
_all_list.extend(_model_names)

__all__ = _all_list

