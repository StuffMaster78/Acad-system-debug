from django.urls import path
from authentication.views.passkey_views import (
    PasskeyRegistrationOptions,
    PasskeyRegistrationVerify,
    PasskeyLoginOptions,
    PasskeyLoginVerify,
)

urlpatterns = [
    path(
        "register/options/",
        PasskeyRegistrationOptions.as_view(),
        name="passkey-register-options"
    ),
    path(
        "register/verify/",
        PasskeyRegistrationVerify.as_view(),
        name="passkey-register-verify"
    ),
    path(
        "login/options/",
        PasskeyLoginOptions.as_view(),
        name="passkey-login-options"
    ),
    path(
        "login/verify/",
        PasskeyLoginVerify.as_view(),
        name="passkey-login-verify"
    ),
]
