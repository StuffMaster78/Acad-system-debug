from django.urls import path
from authentication.views.authentication import (
    RegisterView,
    LoginView,
    LogoutView,
    CustomTokenRefreshView
)

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="auth-register"),
    path("auth/login/", LoginView.as_view(), name="auth-login"),
    path("auth/logout/", LogoutView.as_view(), name="auth-logout"),
    path("auth/token/refresh/", CustomTokenRefreshView.as_view(), name="token-refresh"),
]