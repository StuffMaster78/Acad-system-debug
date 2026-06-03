from __future__ import annotations

from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from websites.models.websites import Website
from websites.models.website_branding import (
    PaymentDisclosureAcknowledgement,
    WebsiteBranding,
)
from websites.serializers.payment_disclosure import (
    PaymentDisclosureAcknowledgementRecordSerializer,
    PaymentDisclosureAcknowledgementSerializer,
    PaymentDisclosureConfigSerializer,
)


def can_manage_payment_disclosure(user) -> bool:
    role = getattr(user, "role", None)
    return bool(user and user.is_authenticated and (user.is_superuser or role in {"superadmin", "admin"}))


def request_website(request):
    requested_website_id = request.query_params.get("website_id")
    role = getattr(request.user, "role", None)
    if requested_website_id and (request.user.is_superuser or role == "superadmin"):
        website = Website.objects.filter(pk=requested_website_id).first()
        if website is None:
            raise NotFound("Website not found.")
        return website
    website = getattr(request, "website", None) or getattr(request.user, "website", None)
    if website is None:
        raise NotFound("Website not found.")
    return website


def default_branding_values(website):
    return {
        "brand_name": website.name,
        "primary_color": getattr(website, "theme_color", "") or "#2563eb",
    }


class PaymentDisclosureConfigView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not can_manage_payment_disclosure(request.user):
            return Response({"detail": "Admin only."}, status=status.HTTP_403_FORBIDDEN)
        website = request_website(request)
        branding, _created = WebsiteBranding.objects.get_or_create(
            website=website,
            defaults=default_branding_values(website),
        )
        return Response(PaymentDisclosureConfigSerializer(branding).data)

    def patch(self, request):
        if not can_manage_payment_disclosure(request.user):
            return Response({"detail": "Admin only."}, status=status.HTTP_403_FORBIDDEN)
        website = request_website(request)
        branding, _created = WebsiteBranding.objects.get_or_create(
            website=website,
            defaults=default_branding_values(website),
        )
        serializer = PaymentDisclosureConfigSerializer(
            branding,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(PaymentDisclosureConfigSerializer(branding).data)


class PaymentDisclosureAcknowledgementView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        website = getattr(request, "website", None) or getattr(request.user, "website", None)
        if website is None:
            raise NotFound("Website not found.")

        branding = getattr(website, "public_branding", None)
        if not branding or not getattr(branding, "payment_processor_name", ""):
            return Response({"detail": "Payment disclosure is not configured."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = PaymentDisclosureAcknowledgementSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        now = timezone.now()
        event = data["event"]

        record = PaymentDisclosureAcknowledgement.objects.create(
            website=website,
            user=request.user,
            processor_display_name=branding.payment_processor_name,
            statement_descriptor=branding.payment_statement_descriptor,
            client_disclosure_text=branding.payment_client_disclosure_text,
            support_contact=branding.payment_support_contact,
            context=data.get("context", ""),
            reference_type=data.get("reference_type", ""),
            reference_id=data.get("reference_id", ""),
            shown_at=now,
            acknowledged_at=now if event == "acknowledged" else None,
            ip_address=self._client_ip(request),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
        )
        return Response(
            PaymentDisclosureAcknowledgementRecordSerializer(record).data,
            status=status.HTTP_201_CREATED,
        )

    @staticmethod
    def _client_ip(request):
        forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")
