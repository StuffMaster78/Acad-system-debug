"""
Notification templates package.

This package contains all notification templates organized by category:
- base.py: Base template classes and utilities
- order_templates.py: Order-related notification templates
- user_templates.py: User-related notification templates
- wallet_templates.py: Wallet-related notification templates
- system_templates.py: System-related notification templates
"""

# Import all template modules to ensure they are registered
from . import base
from . import order_templates
from . import user_templates
from . import wallet_templates
from . import system_templates

__all__ = [
    "base",
    "order_templates", 
    "user_templates",
    "wallet_templates",
    "system_templates",
]
