"""
Payment reminder models
"""
# Import payment reminder models
from .payment_reminders import (
    PaymentReminderConfig,
    PaymentReminderSent,
    PaymentReminderDeletionMessage
)

# Import all models from the parent models.py file
# This is needed because Django treats this directory as a package
# and other code imports from order_payments_management.models
import sys
import os

# Get the parent directory and import models.py
parent_dir = os.path.dirname(os.path.dirname(__file__))
models_py_path = os.path.join(parent_dir, 'models.py')

if os.path.exists(models_py_path):
    # Import the models module
    import importlib.util
    spec = importlib.util.spec_from_file_location("order_payments_management.models_main", models_py_path)
    if spec and spec.loader:
        models_main = importlib.util.module_from_spec(spec)
        sys.modules["order_payments_management.models_main"] = models_main
        spec.loader.exec_module(models_main)
        
        # Re-export all public names from models.py (including functions like generate_reference_id)
        for name in dir(models_main):
            if not name.startswith('_'):
                obj = getattr(models_main, name)
                # Export everything: classes, functions, constants
                setattr(sys.modules[__name__], name, obj)

__all__ = [
    'PaymentReminderConfig',
    'PaymentReminderSent',
    'PaymentReminderDeletionMessage',
    'generate_reference_id',
]

