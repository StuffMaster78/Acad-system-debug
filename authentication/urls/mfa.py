from django.urls import path
from authentication.views.mfa_views import (
    EnableMFA, VerifyMFA,
    RequestMFARecovery, VerifyMFARecovery
)

urlpatterns = [
    path(
        'mfa/enable/',
        EnableMFA.as_view(),
        name='enable-mfa'
    ),
    path(
        'mfa/verify/',
        VerifyMFA.as_view(),
        name='verify-mfa'
    ),
    path(
        'mfa/recovery/request/',
        RequestMFARecovery.as_view(),
        name='request-mfa-recovery'
    ),
    path(
        'mfa/recovery/verify/',
        VerifyMFARecovery.as_view(),
        name='verify-mfa-recovery'
    ),
]