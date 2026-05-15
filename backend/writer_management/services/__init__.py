"""
Exports all services in writer_management so callers can import
from the package directly:

    from writer_management.services import DisciplineService

Rather than from the individual module:

    from writer_management.services.discipline_service import DisciplineService

LAZY IMPORTS
------------
All imports are lazy (inside __all__ only, not at module level).
This prevents circular import issues at Django startup because
services import models and models trigger the app registry.

Callers should import from the full module path for type safety:

    from writer_management.services.discipline_service import DisciplineService

Or from this package for convenience:

    from writer_management.services import DisciplineService
"""

# ----------------------------------------------------------------
# DISCIPLINE
# ----------------------------------------------------------------
from writer_management.services.discipline_service import (  # noqa: F401
    DisciplineService,
)
from writer_management.services.discipline_notification_service import (  # noqa: F401
    DisciplineNotificationService,
)
from writer_management.services.writer_warning_service import (  # noqa: F401
    WriterWarningService,
)
from writer_management.services.writer_status_service import (  # noqa: F401
    WriterStatusService,
)

# ----------------------------------------------------------------
# ELIGIBILITY AND AVAILABILITY
# ----------------------------------------------------------------
from writer_management.services.assignment_eligibility_service import (  # noqa: F401
    WriterEligibilityService,
)
from writer_management.services.availability_service import (  # noqa: F401
    AvailabilityService,
)

# ----------------------------------------------------------------
# CONFIGURATION
# ----------------------------------------------------------------
from writer_management.services.writer_config_service import (  # noqa: F401
    WriterConfigService,
)

# ----------------------------------------------------------------
# PERFORMANCE
# ----------------------------------------------------------------
from writer_management.services.composite_score_service import (  # noqa: F401
    CompositeScoreService,
)
from writer_management.services.performance_tracker_service import (  # noqa: F401
    PerformanceTrackerService,
)
from writer_management.services.writer_metrics_snapshot_service import (  # noqa: F401
    WriterMetricsSnapshotService,
)
from writer_management.services.performance_aggregator_service import (  # noqa: F401
    PerformanceAggregatorService,
)
from writer_management.services.level_progression_service import (  # noqa: F401
    LevelProgressionService,
)

# ----------------------------------------------------------------
# REWARDS
# ----------------------------------------------------------------
from writer_management.services.reward_evaluation_service import (  # noqa: F401
    RewardEvaluationService,
)

# ----------------------------------------------------------------
# PROFILE AND APPLICATION
# ----------------------------------------------------------------
from writer_management.services.writer_profile_service import (  # noqa: F401
    WriterProfileService,
)
from writer_management.services.writer_application_service import (  # noqa: F401
    WriterApplicationService,
)

# ----------------------------------------------------------------
# NOTES
# ----------------------------------------------------------------
from writer_management.services.writer_note_service import (  # noqa: F401
    WriterNoteService,
)

__all__ = [
    # Discipline
    "DisciplineService",
    "DisciplineNotificationService",
    "WriterWarningService",
    "WriterStatusService",
    # Eligibility and availability
    "WriterEligibilityService",
    "AvailabilityService",
    # Configuration
    "WriterConfigService",
    # Performance
    "CompositeScoreService",
    "PerformanceTrackerService",
    "WriterMetricsSnapshotService",
    "PerformanceAggregatorService",
    "LevelProgressionService",
    # Rewards
    "RewardEvaluationService",
    # Profile and application
    "WriterProfileService",
    "WriterApplicationService",
    # Notes
    "WriterNoteService",
]