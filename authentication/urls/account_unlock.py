from django.urls import path
from authentication.views.account_unlock_views import (
    AccountUnlockAPIView,
    AdminUnlockAccountAPIView,
    MFALoginAPIView,
    LogoutAPIView
)

urlpatterns = [
    path(
        'account/unlock/',
        AccountUnlockAPIView.as_view(),
        name='account-unlock'
    ),
    path(
        'account/admin-unlock/<int:pk>/',
        AdminUnlockAccountAPIView.as_view(),
        name='admin-unlock-account'
    ),
    path(
        'auth/mfa-login/',
        MFALoginAPIView.as_view(),
        name='mfa-login'
    ),
    path(
        'auth/logout/',
        LogoutAPIView.as_view(),
        name='logout'
    ),
]