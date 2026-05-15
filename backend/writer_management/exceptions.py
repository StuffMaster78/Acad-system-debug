"""
All exceptions for the writer_management app.

CONVENTION
----------
All exceptions inherit from WriterManagementError so callers
can catch the base class if needed:

    try:
        WriterEligibilityService.is_eligible(profile)
    except WriterManagementError as exc:
        logger.error("Writer management error: %s", exc)

Services raise the most specific exception available.
Views catch specific exceptions and map them to HTTP responses.
"""


class WriterManagementError(Exception):
    """Base exception for all writer_management errors."""


# ----------------------------------------------------------------
# PROFILE
# ----------------------------------------------------------------

class WriterProfileNotFoundError(WriterManagementError):
    """
    No WriterProfile found for the given user, registration_id,
    public_uuid, or account_profile.
    """


class WriterDeletedException(WriterManagementError):
    """
    Operation attempted on a soft-deleted WriterProfile.
    Restore the profile before retrying.
    """


# ----------------------------------------------------------------
# ELIGIBILITY
# ----------------------------------------------------------------

class WriterNotEligibleError(WriterManagementError):
    """
    Writer does not meet assignment eligibility requirements.
    Check WriterEligibilityService.explain() for specific reasons.
    """


class WriterCapacityExceededError(WriterManagementError):
    """
    Writer has reached their maximum active order count.
    Wait for an order to complete or increase the ceiling.
    """


class WriterNotVerifiedError(WriterManagementError):
    """
    Order type requires a verified writer.
    Complete verification before assigning this order type.
    """


# ----------------------------------------------------------------
# DISCIPLINE
# ----------------------------------------------------------------

class WriterSuspendedError(WriterManagementError):
    """
    Operation attempted on or for a suspended writer.
    Raised when:
        - Trying to suspend an already-suspended writer
        - Trying to lift a suspension that does not exist
    """


class WriterBlacklistedError(WriterManagementError):
    """
    Operation attempted on or for a blacklisted writer.
    Raised when:
        - Trying to suspend a blacklisted writer
          (blacklist supersedes suspension)
        - Trying to lift a blacklist that does not exist
    """


# ----------------------------------------------------------------
# LEVEL
# ----------------------------------------------------------------

class LevelSettingsMissingError(WriterManagementError):
    """
    WriterLevel has no associated WriterLevelSettings.

    Cannot compute rate card, earnings, or evaluate progression
    without settings. Ensure every active WriterLevel has a linked
    WriterLevelSettings row before routing writers at that level.
    """


class WriterLevelNotFoundError(WriterManagementError):
    """
    No WriterLevel matches the given criteria for this website.

    Check that the level name exists and is_active=True.
    Use LevelSelector.get_active_levels(website) to list valid levels.
    """


# ----------------------------------------------------------------
# RATE CARD / COMPENSATION
# ----------------------------------------------------------------

class RateCardSnapshotMissingError(WriterManagementError):
    """
    Order has no RateCardSnapshot.

    Earnings cannot be calculated without a snapshot.
    Ensure RateCardSnapshotService.capture() was called at
    assignment time. This error indicates a data integrity issue.
    """


# ----------------------------------------------------------------
# APPLICATION
# ----------------------------------------------------------------

class ApplicationNotApprovableError(WriterManagementError):
    """
    WriterApplication cannot be approved from its current status.
    Only PENDING and UNDER_REVIEW applications can be approved.
    """


class DuplicateApplicationError(WriterManagementError):
    """
    An active application already exists for this email on this website.
    Withdraw the existing application before reapplying.
    """