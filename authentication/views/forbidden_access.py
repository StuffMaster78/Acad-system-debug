# authentication/views/forbidden_access.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from authentication.utilsy import log_audit_action  # Optional: log attempts
from django.utils.translation import gettext_lazy as _


class ForbiddenAccessView(APIView):
    """
    Handles forbidden access attempts — can be used for unauthorized MFA routes,
    locked accounts, or revoked sessions.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        user = request.user if request.user.is_authenticated else None

        # Optional: Audit logging
        if user:
            log_audit_action(user, "FORBIDDEN_ACCESS_ATTEMPT", request)

        return Response(
            {
                "error": _("You do not have permission to access this resource."),
                "code": "forbidden",
                "detail": "Access denied. Please contact support if this is unexpected."
            },
            status=status.HTTP_403_FORBIDDEN
        )