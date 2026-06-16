# Compat shim — AuthenticationViewSet moved to authentication.api.views.auth_views
from authentication.api.views.auth_views import (
    LoginView as AuthenticationViewSet,
)

__all__ = ["AuthenticationViewSet"]
