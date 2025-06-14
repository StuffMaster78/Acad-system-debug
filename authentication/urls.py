from django.urls import path, include
from rest_framework.routers import DefaultRouter
from authentication.views.impersonation_views import ImpersonationTokenViewSet
from authentication.views.account_lockout_viewset import (
    AccountLockoutViewSet,
)
from authentication.views.login_session_viewset import LoginSessionViewSet
from authentication.views.logout_event_viewset import LogoutEventViewSet
from authentication.views.admin_kickout_viewset import AdminKickoutViewSet
from authentication.views.session_management_viewset import SessionManagementViewSet
from authentication.views.otp_viewset import OTPViewSet
from authentication.views.backup_code_viewset import BackupCodeViewSet
from authentication.views.registration_token_viewset import RegistrationTokenViewSet
from authentication.views.mfa import MFASettingsViewSet
from authentication.views.user_session import UserSessionViewSet
from authentication.views.secure_token_viewset import (
    SecureTokenViewSet,
    EncryptedRefreshTokenViewSet
)
from authentication.views.totp import TOTPViewSet
from authentication.views.totp_login_sfa import TOTPLogin2FAView
from authentication.views.magic_links_viewsets import (
    MagicLinkRequestViewSet,
    MagicLinkVerifyViewSet
)

router = DefaultRouter()
router.register(r"impersonate", ImpersonationTokenViewSet, basename="impersonate")
router.register(r'lockouts', AccountLockoutViewSet, basename='lockout')
router.register(r"sessions", LoginSessionViewSet, basename="session")
router.register(r'logout-events', LogoutEventViewSet, basename='logout-event')
router.register(r'kickout', AdminKickoutViewSet, basename='kickout')
router.register(r"session-management", SessionManagementViewSet, basename="session-management")
router.register("otp", OTPViewSet, basename="otp")
router.register(r'backup-codes', BackupCodeViewSet, basename='backup-code')
router.register(r"registration-tokens", RegistrationTokenViewSet, basename="registration-token")
router.register(r'mfa', MFASettingsViewSet, basename='mfa-settings')
router.register(r'sessions', UserSessionViewSet, basename='user-session')
router.register(r'secure-tokens', SecureTokenViewSet, basename='secure-tokens')
router.register(r'refresh-tokens', EncryptedRefreshTokenViewSet, basename='refresh-tokens')

totp = TOTPViewSet.as_view({
    "post": "setup"
})
verify = TOTPViewSet.as_view({
    "post": "verify"
})

magic_link_request = MagicLinkRequestViewSet.as_view({'post': 'create'})
magic_link_verify = MagicLinkVerifyViewSet.as_view({'post': 'create'})

urlpatterns = [
    # path('account-unlock/', include('authentication.urls.account_unlock')),        # views/account_unlock_views.py
    # path('account/', include('authentication.urls.account')),                      # views/account.py
    # path('auth/', include('authentication.urls.authentication')),                  # views/authentication.py
    # path('deletion/', include('authentication.urls.deletion')),                    # views/deletion.py
    # path('forbidden/', include('authentication.urls.forbidden_access')),           # views/forbidden_access.py
    # path('mfa/settings/', include('authentication.urls.mfa_settings')),            # views/mfa_settings.py
    # path('mfa/', include('authentication.urls.mfa')),                              # views/mfa.py
    # path('mfa-views/', include('authentication.urls.mfa_views')),                  # views/mfa_views.py
    # path('passkey/', include('authentication.urls.passkey_views')),                # views/passkey_views.py
    # path('sessions/', include('authentication.urls.sessions_management')),         # views/sessions_management.py
    # path('passkeys/devices/', include('urls.devices')), #views/devices.py
    # path("auth/password-reset/", include("authentication.urls.password_reset")),


    path(
        "auth/registration/confirm/",
        RegistrationTokenViewSet.as_view({"post": "create"}),
        name="registration-confirm"
    ),
    path("2fa/totp/setup/", totp, name="2fa-totp-setup"),
    path("2fa/totp/verify/", verify, name="2fa-totp-verify"),
    path("2fa/totp/login/", TOTPLogin2FAView.as_view(), name="2fa-totp-login"),
    path("magic-link/request/", magic_link_request, name="magic-link-request"),
    path("magic-link/verify/", magic_link_verify, name="magic-link-verify"),

]
