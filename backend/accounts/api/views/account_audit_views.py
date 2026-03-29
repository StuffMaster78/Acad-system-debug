from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.api.serializers.account_audit_log_serializer import (
    AccountAuditLogSerializer,
)
from accounts.api.serializers.onboarding_session_serializer import (
    OnboardingSessionSerializer,
)
from accounts.models import AccountAuditLog, OnboardingSession
from accounts.permissions import IsAdminOrSuperAdminRole
from accounts.selectors.account_selector import AccountSelector


class AccountAuditLogListView(APIView):
    """List audit logs for an account profile."""

    permission_classes = [IsAdminOrSuperAdminRole]

    def get(self, request, account_profile_id, *args, **kwargs):
        """Return account audit logs ordered newest first."""
        profile = AccountSelector.get_account_profile_by_id(
            website=request.website,
            account_profile_id=account_profile_id,
        )
        logs = AccountAuditLog.objects.filter(
            website=request.website,
            account_profile=profile,
        ).order_by("-created_at")

        response_serializer = AccountAuditLogSerializer(logs, many=True)
        return Response(response_serializer.data)


class OnboardingSessionListView(APIView):
    """List onboarding sessions for an account profile."""

    permission_classes = [IsAdminOrSuperAdminRole]

    def get(self, request, account_profile_id, *args, **kwargs):
        """Return onboarding sessions ordered newest first."""
        profile = AccountSelector.get_account_profile_by_id(
            website=request.website,
            account_profile_id=account_profile_id,
        )
        sessions = OnboardingSession.objects.filter(
            website=request.website,
            account_profile=profile,
        ).order_by("-started_at")

        response_serializer = OnboardingSessionSerializer(
            sessions,
            many=True,
        )
        return Response(response_serializer.data)