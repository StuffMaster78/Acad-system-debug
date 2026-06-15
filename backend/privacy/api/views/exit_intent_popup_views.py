from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from admin_management.permissions import IsAdmin
from privacy.api.serializers.exit_intent_popup import (
    ExitIntentPopupConfigSerializer,
    PublicExitIntentPopupConfigSerializer,
)
from privacy.models import ExitIntentPopupConfig
from websites.models.websites import Website


def _is_superadmin(user) -> bool:
    return bool(getattr(user, "is_superuser", False) or getattr(user, "role", None) == "superadmin")


def _resolve_staff_website(request):
    website_id = request.query_params.get("website_id") or request.data.get("website_id")
    if website_id and _is_superadmin(request.user):
        return Website.objects.filter(pk=website_id, is_deleted=False).first()
    return getattr(request, "website", None)


class PublicExitIntentPopupConfigView(APIView):
    authentication_classes = []
    permission_classes = []
    throttle_classes = []

    def get(self, request):
        website = getattr(request, "website", None)
        config = None
        if website:
            config = ExitIntentPopupConfig.objects.filter(website=website, is_enabled=True).first()

        if not config:
            return Response({"is_enabled": False})

        return Response(PublicExitIntentPopupConfigSerializer(config).data)


class AdminExitIntentPopupConfigView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        website = _resolve_staff_website(request)
        if not website:
            return Response({"detail": "Website context required."}, status=status.HTTP_400_BAD_REQUEST)

        config, _ = ExitIntentPopupConfig.objects.get_or_create(website=website)
        return Response(ExitIntentPopupConfigSerializer(config).data)

    def put(self, request):
        website = _resolve_staff_website(request)
        if not website:
            return Response({"detail": "Website context required."}, status=status.HTTP_400_BAD_REQUEST)

        config, _ = ExitIntentPopupConfig.objects.get_or_create(website=website)
        serializer = ExitIntentPopupConfigSerializer(config, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    patch = put
