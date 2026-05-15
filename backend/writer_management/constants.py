"""
Static constants for the writer_management app.

DO NOT put business logic here.
DO NOT put database-driven values here — those live in
WriterConfig, WriterLevelSettings, and WriterWarningEscalationConfig.

These are hardcoded platform defaults used as model field defaults
and as fallbacks when no per-level or per-writer override is set.
"""

# ----------------------------------------------------------------
# CAPACITY DEFAULTS
# Used as model field defaults on WriterProfile and WriterCapacity.
# The live ceiling is resolved by WriterEligibilityService in order:
#   1. WriterCapacity.override_max_active_orders  (per-writer admin override)
#   2. WriterLevelSettings.max_active_orders       (per-level default)
#   3. DEFAULT_MAX_ACTIVE_ORDERS                   (this constant — last resort)
# ----------------------------------------------------------------

DEFAULT_MAX_ACTIVE_ORDERS: int = 10

DEFAULT_MAX_REQUESTS_PER_WRITER: int = 5

DEFAULT_MAX_TAKES_PER_WRITER: int = 10

# ----------------------------------------------------------------
# REGISTRATION ID
# ----------------------------------------------------------------

REGISTRATION_ID_PREFIX: str = "WR"
REGISTRATION_ID_RANDOM_LENGTH: int = 6

# ----------------------------------------------------------------
# ONBOARDING
# ----------------------------------------------------------------

# Portal code granted to writers during onboarding.
# Must match a PortalDefinition.code in the accounts app.
WRITER_PORTAL_CODE: str = "writer_portal"

# ----------------------------------------------------------------
# AVAILABILITY
# ----------------------------------------------------------------

# Minutes of inactivity before auto-offline triggers.
# Used as default on WriterAvailabilityPreference.
DEFAULT_AUTO_OFFLINE_MINUTES: int = 30

# ----------------------------------------------------------------
# WARNINGS
# ----------------------------------------------------------------

# Default warning duration in days.
# Used when WriterWarningEscalationConfig does not exist for a site.
DEFAULT_WARNING_DURATION_DAYS: int = 30

# ----------------------------------------------------------------
# PERFORMANCE
# ----------------------------------------------------------------

# Number of recent snapshots fetched during level progression
# evaluation. Covers enough history for multi-period criteria.
LEVEL_EVALUATION_SNAPSHOT_COUNT: int = 10

# ----------------------------------------------------------------
# REGISTRATION ID GENERATION
# ----------------------------------------------------------------

import string  # noqa: E402 — kept here for co-location with constants

REGISTRATION_ID_CHARS: str = string.ascii_uppercase + string.digits
REGISTRATION_ID_MAX_RETRIES: int = 10