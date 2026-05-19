from .login_session import LoginSession
from .secure_token import SecureToken
from .audit import AuthSecurityEvent
from .trusted_devices import TrustedDevice
from .magic_links import MagicLink
from .blocked_ip import BlockedIP
from .account_deletion_request import AccountDeletionRequest
from .failed_login_attempts import FailedLoginAttempt
from .security_events import SecurityEvent
from .password_security import PasswordHistory, PasswordExpirationPolicy, PasswordBreachCheck
from .account_suspension import AccountSuspension
from .ip_whitelist import IPWhitelist, UserIPWhitelistSettings
from .email_change_request import EmailChangeRequest
from .phone_verification import PhoneVerification
from .session_limits import SessionLimitPolicy
from .security_questions import SecurityQuestion, UserSecurityQuestion

UserSession = LoginSession
AuditLog = AuthSecurityEvent
