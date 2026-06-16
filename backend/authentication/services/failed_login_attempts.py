# Compat shim — FailedLoginService is now LoginSecurityService.
from authentication.services.login_security_service import LoginSecurityService as FailedLoginService

__all__ = ["FailedLoginService"]
