from django.urls import path, include
from rest_framework.routers import DefaultRouter
from authentication.views import (
    impersonation_views,
    account_lockout_viewset,
    login_session_viewset,
    logout_event_viewset,
    admin_kickout_viewset,
    session_management_viewset,
    otp_viewset,
    backup_code_viewset,
    registration_token_viewset,
    mfa,
    user_session,
    secure_token_viewset,
    totp,
    totp_login_sfa,
    magic_links_viewsets,
    authentication,
    account_unlock_views,
    admin_account_unlock_view,
    account_unlock_confirm_view,
    auth_viewset
)

router = DefaultRouter()

# Unified authentication routes (production-grade)
router.register(r"auth", auth_viewset.AuthenticationViewSet, basename="auth")

# Impersonation routes
router.register(r"impersonate", impersonation_views.ImpersonationTokenViewSet, basename="impersonate")

# Session and security management
router.register(r"lockouts", account_lockout_viewset.AccountLockoutViewSet, basename="lockout")
router.register(r"user-sessions", user_session.UserSessionViewSet, basename="user-session")
router.register(r"logout-events", logout_event_viewset.LogoutEventViewSet, basename="logout-event")
router.register(r"admin-kickout", admin_kickout_viewset.AdminKickoutViewSet, basename="admin-kickout")
router.register(r"session-management", session_management_viewset.SessionManagementViewSet, basename="session-management")
router.register(r"user-login-sessions", login_session_viewset.LoginSessionViewSet, basename="user-login-session")

# MFA / OTP
router.register(r"otp", otp_viewset.OTPViewSet, basename="otp")
router.register(r"backup-codes", backup_code_viewset.BackupCodeViewSet, basename="backup-code")
router.register(r"mfa-settings", mfa.MFASettingsViewSet, basename="mfa-settings")
router.register(r"totp", totp.TOTPViewSet, basename="totp")
# Note: TOTPLogin2FAView is an APIView, not a ViewSet, so it's registered in custom_urlpatterns below

# Registration & Token-based flows
router.register(
    r"registration-tokens",
    registration_token_viewset.RegistrationTokenViewSet,
    basename="registration-token"
)
router.register(
    r"secure-tokens",
    secure_token_viewset.SecureTokenViewSet,
    basename="secure-token"
)
router.register(
    r"refresh-tokens",
    secure_token_viewset.EncryptedRefreshTokenViewSet,
    basename="refresh-tokens"
)

# Magic links
router.register(
    r"magic-links",
    magic_links_viewsets.MagicLinkRequestViewSet,
    basename="magic-link-request"
)
router.register(
    r"magic-link-verification",
    magic_links_viewsets.MagicLinkVerifyViewSet,
    basename="magic-link-verify"
)
# Admin account unlock
router.register(
    r"admin/unlock",
    admin_account_unlock_view.AdminAccountUnlockViewSet,
    basename="admin-unlock"
)

# Custom actions (non-ViewSet method-bound)
custom_urlpatterns = [
    path(
        "registration/confirm/",
        registration_token_viewset.RegistrationTokenViewSet.as_view({"post": "create"}),
        name="registration-confirm"
    ),
    path(
        "2fa/totp/setup/",
        totp.TOTPViewSet.as_view({"post": "setup"}),
        name="2fa-totp-setup"
    ),
    path(
        "2fa/totp/verify/",
        totp.TOTPViewSet.as_view({"post": "verify"}),
        name="2fa-totp-verify"
    ),
    path(
        "2fa/totp/login/",
        totp_login_sfa.TOTPLogin2FAView.as_view(),
        name="2fa-totp-login"
    ),
    path(
        "magic-link/request/",
        magic_links_viewsets.MagicLinkRequestViewSet.as_view({'post': 'create'}),
        name="magic-link-request"
    ),
    path(
        "magic-link/verify/",
        magic_links_viewsets.MagicLinkVerifyViewSet.as_view({'post': 'create'}),
        name="magic-link-verify"
    ),
    path(
        "auth/account-unlock/",
        account_unlock_views.AccountUnlockRequestView.as_view(),
        name="account-unlock"
    ),
    path(
        "auth/account-unlock/confirm/",
        account_unlock_confirm_view.AccountUnlockConfirmView.as_view(),
        name="account-unlock-confirm"
    ),
]

urlpatterns = [
    # Main router (includes unified auth endpoints)
    path("", include(router.urls)),

    # Custom actions
    path("", include(custom_urlpatterns)),

    # Optional future includes
    # path("auth/deletion/", include("authentication.urls.deletion")),
    # path("auth/password-reset/", include("authentication.urls.password_reset")),
]
