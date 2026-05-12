from __future__ import annotations


class ActivityError(Exception):
    """
    Base exception for activity related failures.
    """


class InvalidActivityAudienceError(ActivityError):
    """
    Raised when an invalid activity audience is supplied.
    """


class InvalidActivityVerbError(ActivityError):
    """
    Raised when an invalid activity verb is supplied.
    """


class ActivityPermissionError(ActivityError):
    """
    Raised when a user cannot access an activity event.
    """