"""
Custom exceptions for the order_pricing_core app.
"""

from __future__ import annotations

from rest_framework.exceptions import PermissionDenied
from rest_framework.exceptions import ValidationError


class PricingConfigError(ValidationError):
    """
    Raised when pricing configuration is invalid.
    """


class PricingQuoteError(ValidationError):
    """
    Raised when quote operations fail validation.
    """


class PricingPermissionDenied(PermissionDenied):
    """
    Raised when a user cannot manage pricing resources.
    """