from __future__ import annotations

from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions.base import BasePlatformPermission
from payments_processor.api.serializers.gateway_config_serializers import (
    PaymentGatewayConfigSerializer,
    PaymentNotificationEmailSerializer,
)
from payments_processor.models.gateway_config import (
    PaymentGatewayConfig,
    PaymentNotificationEmail,
)
from websites.models.websites import Website


class CanManageGateway(BasePlatformPermission):
    required_portal = "internal_admin"
    required_permission = "payments.manage_gateway"
    require_tenant = False  # superadmin operates across all tenants


# ── Gateway config ─────────────────────────────────────────────────────────────

class PaymentGatewayConfigListView(APIView):
    """
    List all per-website gateway configurations.
    Superadmin: all sites. Admin: own site only.
    """

    permission_classes = [permissions.IsAuthenticated, CanManageGateway]

    def get(self, request: Request) -> Response:
        if request.user.role == "superadmin":
            qs = PaymentGatewayConfig.objects.select_related("website").order_by("website__name")
        else:
            from core.utils.request_context import get_request_website
            website = get_request_website(request)
            qs = PaymentGatewayConfig.objects.filter(website=website).select_related("website")

        serializer = PaymentGatewayConfigSerializer(qs, many=True)
        return Response(serializer.data)


class PaymentGatewayConfigDetailView(APIView):
    """
    Retrieve and update a single gateway config.
    Also handles creation when a website doesn't have one yet.
    """

    permission_classes = [permissions.IsAuthenticated, CanManageGateway]

    @staticmethod
    def _get_config(config_id: int) -> PaymentGatewayConfig:
        return get_object_or_404(
            PaymentGatewayConfig.objects.select_related("website"),
            pk=config_id,
        )

    def get(self, request: Request, config_id: int) -> Response:
        config = self._get_config(config_id)
        return Response(PaymentGatewayConfigSerializer(config).data)

    def patch(self, request: Request, config_id: int) -> Response:
        config = self._get_config(config_id)
        serializer = PaymentGatewayConfigSerializer(config, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=request.user)
        return Response(serializer.data)


class PaymentGatewayConfigCreateView(APIView):
    """
    Create a gateway config for a website that doesn't have one yet.
    """

    permission_classes = [permissions.IsAuthenticated, CanManageGateway]

    def post(self, request: Request) -> Response:
        website_id = request.data.get("website")
        website = get_object_or_404(Website, pk=website_id)
        if PaymentGatewayConfig.objects.filter(website=website).exists():
            return Response(
                {"detail": "A gateway config already exists for this website."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = PaymentGatewayConfigSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# ── Notification emails ────────────────────────────────────────────────────────

class PaymentNotificationEmailListView(APIView):
    """
    List all payment notification email addresses.
    Superadmin: all sites. Admin: own site only.
    """

    permission_classes = [permissions.IsAuthenticated, CanManageGateway]

    def get(self, request: Request) -> Response:
        if request.user.role == "superadmin":
            qs = PaymentNotificationEmail.objects.select_related("website").order_by("website__name", "email")
        else:
            from core.utils.request_context import get_request_website
            website = get_request_website(request)
            qs = PaymentNotificationEmail.objects.filter(website=website).select_related("website")

        serializer = PaymentNotificationEmailSerializer(qs, many=True)
        return Response(serializer.data)

    def post(self, request: Request) -> Response:
        serializer = PaymentNotificationEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PaymentNotificationEmailDetailView(APIView):
    """
    Update or delete a single payment notification email.
    """

    permission_classes = [permissions.IsAuthenticated, CanManageGateway]

    @staticmethod
    def _get_entry(entry_id: int) -> PaymentNotificationEmail:
        return get_object_or_404(
            PaymentNotificationEmail.objects.select_related("website"),
            pk=entry_id,
        )

    def patch(self, request: Request, entry_id: int) -> Response:
        entry = self._get_entry(entry_id)
        serializer = PaymentNotificationEmailSerializer(entry, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request: Request, entry_id: int) -> Response:
        entry = self._get_entry(entry_id)
        entry.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
