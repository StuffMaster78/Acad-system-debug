from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.api.serializers.account_profile_serializer import (
    AccountProfileSerializer,
)
from accounts.api.serializers.account_summary_serializer import (
    AccountSummarySerializer,
)
from accounts.selectors.account_selector import AccountSelector
from accounts.services.account_service import AccountService


class MyAccountSummaryView(APIView):
    """Return the current user's account summary for the website."""

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """Return account summary for the current website user."""
        summary = AccountService.get_account_summary(
            website=request.website,
            user=request.user,
        )
        response_serializer = AccountSummarySerializer(summary)
        return Response(response_serializer.data)


class MyAccountProfileView(APIView):
    """Return the current user's account profile for the website."""

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """Return the account profile for the current website user."""
        profile = AccountSelector.get_account_profile(
            website=request.website,
            user=request.user,
        )
        response_serializer = AccountProfileSerializer(profile)
        return Response(response_serializer.data)