from __future__ import annotations


class GovernanceError(Exception):
    """
    Base governance exception.
    """


class PermissionDeniedError(GovernanceError):
    """
    Permission denied by governance layer.
    """


class PolicyDeniedError(GovernanceError):
    """
    Policy engine denied execution.
    """


class ApprovalRequiredError(GovernanceError):
    """
    Command requires approval workflow.
    """


class RiskThresholdExceededError(GovernanceError):
    """
    Risk score exceeded safe threshold.
    """


class IdempotencyConflictError(GovernanceError):
    """
    Duplicate execution attempt detected.
    """


class RollbackExecutionError(GovernanceError):
    """
    Rollback execution failed.
    """