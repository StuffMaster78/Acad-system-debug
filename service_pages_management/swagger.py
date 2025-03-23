from drf_spectacular.views import (
    SpectacularSwaggerView,
    SpectacularRedocView
)
from rest_framework.permissions import IsAdminUser


class SecureSwaggerView(SpectacularSwaggerView):
    """
    Restricts Swagger UI to admin users only.
    """
    permission_classes = [IsAdminUser]


class SecureRedocView(SpectacularRedocView):
    """
    Restricts Redoc UI to admin users only.
    """
    permission_classes = [IsAdminUser]