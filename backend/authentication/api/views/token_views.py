from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenRefreshView

from authentication.api.serializers.token_refresh_serializers import (
    SessionAwareTokenRefreshSerializer,
)


class SessionAwareTokenRefreshView(TokenRefreshView):
    """
    Refresh JWT tokens only if the backing LoginSession is still valid.
    """

    permission_classes = [AllowAny]
    serializer_class = SessionAwareTokenRefreshSerializer