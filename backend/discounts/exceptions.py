from __future__ import annotations


class DiscountError(Exception):
    """
    Base exception for discount domain errors.
    """


class DiscountValidationError(DiscountError):
    """
    Raised when a discount cannot be used.
    """


class DiscountAlreadyAppliedError(DiscountError):
    """
    Raised when a payable object already has a discount.
    """


class DiscountConfigurationError(DiscountError):
    """
    Raised when a discount is misconfigured.
    """


class DiscountUsageError(DiscountError):
    """
    Raised when discount usage cannot be recorded.
    """