from django.urls import path
from authentication.views.mfa_settings import MFASettingsView

urlpatterns = [
    path(
        "auth/mfa/settings/",
        MFASettingsView.as_view(),
        name="mfa-settings"
    ),
]