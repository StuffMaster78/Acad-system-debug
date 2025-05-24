from django.urls import path
from authentication.views.password_reset_views import (
    PasswordResetRequestView,
    PasswordResetTokenValidateView,
    RequestPasswordResetView,
    SetNewPasswordView,
    PasswordResetConfirmView
)

app_name = "authentication"

urlpatterns = [
    path(
        "password-reset/request/",
        PasswordResetRequestView.as_view(),
        name="password_reset_request",
    ),
    path(
        "password-reset/validate-token/",
        PasswordResetTokenValidateView.as_view(),
        name="password_reset_validate_token",
    ),
    path(
        "password-reset/set-new/",
        SetNewPasswordView.as_view(),
        name="password_reset_set_new",
    ),
    path(
        "auth/password-reset-request/",
        RequestPasswordResetView.as_view(),
         name="password-reset-request"
    ),
    path(
        "auth/password-reset-confirm/",
        PasswordResetConfirmView.as_view(),
        name="password-reset-confirm"
    ),
]