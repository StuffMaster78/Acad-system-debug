"""
Exports every model in writer_management so callers can import
from the package directly:

    from writer_management.models import WriterProfile, WriterLevel

Rather than from the individual module:

    from writer_management.models.writer_profile import WriterProfile

IMPORT ORDER
------------
Order matters. Models that are referenced as ForeignKey targets
by other models in this package must be imported first so Django's
app registry resolves them correctly.

Dependency order (rough):
    1. Enums (no models)
    2. WriterLevel, WriterLevelSettings, WriterLevelCriteria
    3. WriterProfile
    4. Everything that FKs to WriterProfile
"""

# ----------------------------------------------------------------
# LEVEL
# ----------------------------------------------------------------
from writer_management.models.writer_level import WriterLevel # noqa: F401
from writer_management.models.writer_level_settings import ( # noqa: F401
    WriterLevelSettings,
)
from writer_management.models.writer_level_criteria import ( # noqa: F401
    WriterLevelCriteria,
)
from writer_management.models.writer_level_history import ( # noqa: F401
    WriterLevelChangeLog,
)

# ----------------------------------------------------------------
# PROFILE (core identity anchor)
# ----------------------------------------------------------------
from writer_management.models.writer_profile import ( # noqa: F401
    WriterProfile,
    WriterOnboardingStatus,
    WriterVerificationStatus,
)

# ----------------------------------------------------------------
# RUNTIME STATE
# (all OneToOne on WriterProfile — created by signal on profile save)
# ----------------------------------------------------------------
from writer_management.models.writer_status import WriterStatus # noqa: F401
from writer_management.models.writer_discipline_state import ( # noqa: F401
    WriterDisciplineState,
)
from writer_management.models.writer_capacity import WriterCapacity # noqa: F401
from writer_management.models.writer_availability import ( # noqa: F401
    WriterAvailabilityWindow,
    WriterAvailabilityPreference,
    UnavailabilityReason,
)

# ----------------------------------------------------------------
# DISCIPLINE SOURCE RECORDS
# ----------------------------------------------------------------
from writer_management.models.writer_discipline import ( # noqa: F401
    WriterDisciplineConfig,
    WriterSuspension,
    WriterSuspensionHistory,
    WriterBlacklist,
    WriterBlacklistHistory,
    WriterProbation,
    WriterPenalty,
)
from writer_management.models.writer_warning import WriterWarning # noqa: F401
from writer_management.models.writer_strike import WriterStrike # noqa: F401

# ----------------------------------------------------------------
# CONFIGURATION
# ----------------------------------------------------------------
from writer_management.models.configs import ( # noqa: F401
    WriterConfig,
    WriterConfigHistory,
    WriterWarningEscalationConfig,
)

# ----------------------------------------------------------------
# PERFORMANCE
# ----------------------------------------------------------------
from writer_management.models.writer_performance import ( # noqa: F401
    WriterPerformance,
    WriterPerformanceSnapshot,
    WriterPerformanceMetrics,
)

# ----------------------------------------------------------------
# REWARDS
# ----------------------------------------------------------------
from writer_management.models.writer_reward import ( # noqa: F401
    WriterReward,
    WriterRewardCriteria,
)

# ----------------------------------------------------------------
# RESOURCES
# ----------------------------------------------------------------
from writer_management.models.resources import ( # noqa: F401
    WriterResourceCategory,
    WriterResource,
    WriterResourceView,
)

# ----------------------------------------------------------------
# PEN NAME
# ----------------------------------------------------------------
from writer_management.models.pen_name import ( # noqa: F401
    WriterPenNameChangeRequest,
)

# ----------------------------------------------------------------
# LOGS
# ----------------------------------------------------------------
from writer_management.models.logs import ( # noqa: F401
    WriterActionLog,
    WriterActivityLog,
    WriterActivityTracking,
    WriterIPLog,
    WriterProfileUpdateLog,
    WriterFileDownloadLog,
)

# ----------------------------------------------------------------
# INTERNAL NOTES
# ----------------------------------------------------------------
from writer_management.models.writer_note import WriterNote # noqa: F401

# ----------------------------------------------------------------
# APPLICATION (pre-onboarding)
# ----------------------------------------------------------------
from writer_management.models.writer_application import ( # noqa: F401
    WriterApplication,
)

# ----------------------------------------------------------------
# NOTE: WriterStrike exists in two places during migration:
# discipline.py — the old location (being retired)
# writer_strike.py — the new canonical location
# Once discipline.py's WriterStrike is fully removed, drop the
# _WriterStrikeFromDiscipline alias above.
# ----------------------------------------------------------------

__all__ = [
    # Level
    "WriterLevel",
    "WriterLevelSettings",
    "WriterLevelCriteria",
    "WriterLevelChangeLog",
    # Profile
    "WriterProfile",
    "WriterOnboardingStatus",
    "WriterVerificationStatus",
    # Runtime state
    "WriterStatus",
    "WriterDisciplineState",
    "WriterCapacity",
    "WriterAvailabilityWindow",
    "WriterAvailabilityPreference",
    "UnavailabilityReason",
    # Discipline
    "WriterDisciplineConfig",
    "WriterSuspension",
    "WriterSuspensionHistory",
    "WriterBlacklist",
    "WriterBlacklistHistory",
    "WriterProbation",
    "WriterPenalty",
    "WriterWarning",
    "WriterStrike",
    # Config
    "WriterConfig",
    "WriterConfigHistory",
    "WriterWarningEscalationConfig",
    # Performance
    "WriterPerformance",
    "WriterPerformanceSnapshot",
    "WriterPerformanceMetrics",
    # Rewards
    "WriterReward",
    "WriterRewardCriteria",
    # Resources
    "WriterResourceCategory",
    "WriterResource",
    "WriterResourceView",
    # Pen name
    "WriterPenNameChangeRequest",
    # Logs
    "WriterActionLog",
    "WriterActivityLog",
    "WriterActivityTracking",
    "WriterIPLog",
    "WriterProfileUpdateLog",
    "WriterFileDownloadLog",
    # Notes
    "WriterNote",
    # Application
    "WriterApplication",
]
from writer_management.models.badges import Badge, WriterBadge  # noqa: F401
