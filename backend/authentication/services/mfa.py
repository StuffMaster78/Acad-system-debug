# Compatibility shim — MFAService was split into focused services.
# Tests referencing MFAService need to be updated to use:
#   - MFAOrchestrationService  (login/verify flow)
#   - MFADeviceService         (device management)
#   - MFAChallengeService      (challenge/OTP)
#   - MFASettingsService       (settings)
from authentication.services.mfa_orchestration_service import MFAOrchestrationService as MFAService

__all__ = ["MFAService"]
