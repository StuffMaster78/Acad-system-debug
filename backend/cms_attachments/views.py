"""
Attachment API Views
======================

Public listing, detail, download (with gating), and rating endpoints.
"""

from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import HttpResponseRedirect

from cms_attachments.models import Attachment, AttachmentRating
from cms_attachments.serializers import (
    AttachmentDetailSerializer,
    AttachmentListSerializer,
)


class AttachmentViewSet(viewsets.ReadOnlyModelViewSet):
    """Public attachment API — listing and detail."""

    permission_classes = [permissions.AllowAny]
    lookup_field = "slug"

    def get_serializer_class(self):
        if self.action == "retrieve":
            return AttachmentDetailSerializer
        return AttachmentListSerializer

    def get_queryset(self):
        site = getattr(self.request, "site", None)
        qs = Attachment.objects.filter(status="published")
        if site:
            qs = qs.filter(site=site)

        # Optional filters
        params = self.request.query_params
        if params.get("type"):
            qs = qs.filter(attachment_type=params["type"])
        if params.get("category"):
            qs = qs.filter(category__slug=params["category"])
        if params.get("level"):
            qs = qs.filter(academic_level=params["level"])
        if params.get("style"):
            qs = qs.filter(formatting_style=params["style"])
        if params.get("featured"):
            qs = qs.filter(is_featured=True)

        return qs.select_related("category", "author", "managed_file")

    @action(detail=True, methods=["get"])
    def check_access(self, request, slug=None):
        """GET /cms-api/attachments/{slug}/check_access/
        Check if the current user can download this attachment."""
        attachment = self.get_object()
        from cms_attachments.services.download_service import DownloadService

        result = DownloadService.check_access(attachment, request)
        return Response(result)

    @action(detail=True, methods=["post"])
    def download(self, request, slug=None):
        """POST /cms-api/attachments/{slug}/download/
        Process download — handles free and gated flows.

        For email-gated:
            {"email": "user@example.com", "consent_marketing": true}
        For free/account/customer:
            {} (empty body)
        """
        attachment = self.get_object()
        from cms_attachments.services.download_service import DownloadService

        # Check access first
        access = DownloadService.check_access(attachment, request)

        if access["allowed"]:
            # Direct download
            url = DownloadService.track_and_get_url(attachment, request)
            return Response({"download_url": url})

        # Handle email gate
        if access.get("requires_email"):
            email = request.data.get("email", "").strip()
            if not email or "@" not in email:
                return Response(
                    {"error": "Valid email required for this download"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            result = DownloadService.capture_email_and_download(
                attachment=attachment,
                email=email,
                request=request,
                consent_marketing=request.data.get("consent_marketing", False),
                consent_newsletter=request.data.get("consent_newsletter", False),
            )
            return Response(result)

        # Other gate types not fulfilled
        return Response(
            {"error": access.get("reason", "Access denied")},
            status=status.HTTP_403_FORBIDDEN,
        )

    @action(detail=True, methods=["post"])
    def rate(self, request, slug=None):
        """POST /cms-api/attachments/{slug}/rate/ {"rating": 5}"""
        attachment = self.get_object()
        rating_value = request.data.get("rating")

        if not rating_value or int(rating_value) not in range(1, 6):
            return Response(
                {"error": "Rating must be 1-5"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        rating, created = AttachmentRating.objects.update_or_create(
            attachment=attachment,
            user=request.user if request.user.is_authenticated else None,
            session_id=request.session.session_key or "",
            defaults={"rating": int(rating_value)},
        )

        # Recalculate average
        from django.db.models import Avg

        agg = AttachmentRating.objects.filter(
            attachment=attachment
        ).aggregate(avg=Avg("rating"), count=Avg("id"))

        attachment.average_rating = agg["avg"] or 0
        attachment.rating_count = AttachmentRating.objects.filter(
            attachment=attachment
        ).count()
        attachment.save(update_fields=["average_rating", "rating_count"])

        return Response({
            "rating": rating.rating,
            "average_rating": attachment.average_rating,
            "rating_count": attachment.rating_count,
        })

    @action(detail=True, methods=["get"], url_path="serve")
    def serve(self, request, slug=None):
        """GET /cms-api/attachments/{slug}/serve/?token=<signed-token>
        Validates a signed download token and redirects to the file URL.
        Used for email-delivered download links.
        """
        from cms_attachments.services.download_service import DownloadService

        token = request.query_params.get("token", "")
        if not token:
            return Response({"error": "Token required."}, status=status.HTTP_400_BAD_REQUEST)

        attachment = DownloadService.redeem_token(token)
        if not attachment:
            return Response(
                {"error": "This link has expired or is invalid. Please request a new download."},
                status=status.HTTP_410_GONE,
            )

        file_url = None
        if attachment.managed_file:
            file_url = attachment.managed_file.public_url

        if not file_url:
            return Response(
                {"error": "File is not available. Please contact support."},
                status=status.HTTP_404_NOT_FOUND,
            )

        attachment.download_count += 1
        attachment.save(update_fields=["download_count"])

        return HttpResponseRedirect(file_url)