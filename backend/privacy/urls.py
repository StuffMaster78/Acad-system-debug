"""
Privacy & data rights endpoints.
"""
from django.urls import path

from privacy.api.views import (
    AdminExitIntentPopupConfigView,
    CookieConfigView,
    CookieConsentCurrentView,
    CookieConsentRevokeView,
    CookieConsentView,
    PublicExitIntentPopupConfigView,
)

app_name = "privacy"

urlpatterns = [
    path("cookie-config/", CookieConfigView.as_view(), name="cookie-config"),
    path("cookie-consent/", CookieConsentView.as_view(), name="cookie-consent"),
    path("exit-popup/", PublicExitIntentPopupConfigView.as_view(), name="exit-popup"),
    path(
        "admin/exit-popup/",
        AdminExitIntentPopupConfigView.as_view(),
        name="admin-exit-popup",
    ),
    path(
        "cookie-consent/current/",
        CookieConsentCurrentView.as_view(),
        name="cookie-consent-current",
    ),
    path(
        "cookie-consent/revoke/",
        CookieConsentRevokeView.as_view(),
        name="cookie-consent-revoke",
    ),
]
