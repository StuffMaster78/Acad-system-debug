from __future__ import annotations


class ClassManagementError(Exception):
    """
    Base exception for class management domain errors.
    """


class ClassOrderStateError(ClassManagementError):
    """
    Raised when a class order is moved through an invalid transition.
    """


class ClassAccessDeniedError(ClassManagementError):
    """
    Raised when a user cannot access protected class details.
    """


class ClassPricingError(ClassManagementError):
    """
    Raised when pricing or proposal rules are violated.
    """


class ClassPaymentError(ClassManagementError):
    """
    Raised when a class payment operation is invalid.
    """


class ClassAssignmentError(ClassManagementError):
    """
    Raised when assignment or reassignment is invalid.
    """


class ClassWriterCompensationError(ClassManagementError):
    """
    Raised when writer compensation rules are violated.
    """