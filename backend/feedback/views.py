from __future__ import annotations

import logging

from django.db import transaction
from django.utils import timezone
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import FeedbackRequest, FeedbackStatusEvent, FeedbackVote
from .permissions import CanTriageFeedback, FeedbackObjectPermission, _is_staff
from .serializers import (
    SURFACE_CATEGORIES,
    FeedbackRequestCreateSerializer,
    FeedbackRequestDetailSerializer,
    FeedbackRequestListSerializer,
    FeedbackRequesterUpdateSerializer,
    FeedbackTriageUpdateSerializer,
)

log = logging.getLogger(__name__)


class FeedbackPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = "page_size"
    max_page_size = 100


def _detect_surface(user) -> str:
    role = getattr(user, "role", "")
    if role in {"admin", "superadmin", "support", "editor"} or getattr(user, "is_staff", False):
        return "staff"
    if role == "writer":
        return "writer"
    return "client"


class FeedbackRequestViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """
    Feedback & Requests board.

    Clients and writers submit requests; staff triage them.
    Website-scoped throughout.
    """

    pagination_class = FeedbackPagination
    permission_classes = [IsAuthenticated, FeedbackObjectPermission]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "upvote_count", "status", "priority"]
    ordering = ["-created_at"]
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_queryset(self):
        user = self.request.user
        qs = FeedbackRequest.objects.select_related(
            "requester", "staff_owner", "responded_by", "duplicate_of",
        ).prefetch_related("status_history", "status_history__changed_by")

        if _is_staff(user):
            # Staff sees all requests on their website(s)
            website = getattr(user, "website", None)
            if getattr(user, "role", "") == "superadmin" or user.is_superuser:
                # Superadmin can filter by website via query param
                website_id = self.request.query_params.get("website")
                if website_id:
                    qs = qs.filter(website_id=website_id)
            elif website:
                qs = qs.filter(website=website)
            # Apply staff triage filters
            if self.action in ("list", "triage"):
                s = self.request.query_params.get("status")
                cat = self.request.query_params.get("category")
                surface = self.request.query_params.get("surface")
                prio = self.request.query_params.get("priority")
                req_type = self.request.query_params.get("request_type")
                owner = self.request.query_params.get("owner")
                if s:
                    qs = qs.filter(status=s)
                if cat:
                    qs = qs.filter(category=cat)
                if surface:
                    qs = qs.filter(portal_surface=surface)
                if prio:
                    qs = qs.filter(priority=prio)
                if req_type:
                    qs = qs.filter(request_type=req_type)
                if owner == "me":
                    qs = qs.filter(staff_owner=user)
                elif owner == "unassigned":
                    qs = qs.filter(staff_owner__isnull=True)
        else:
            # Clients and writers see only their own submissions
            qs = qs.filter(requester=user)

        return qs

    def get_serializer_class(self):
        if self.action == "create":
            return FeedbackRequestCreateSerializer
        if self.action == "partial_update":
            user = self.request.user
            if _is_staff(user):
                return FeedbackTriageUpdateSerializer
            return FeedbackRequesterUpdateSerializer
        if self.action in ("retrieve", "triage_detail"):
            return FeedbackRequestDetailSerializer
        return FeedbackRequestListSerializer

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["portal_surface"] = _detect_surface(self.request.user)
        return ctx

    # ── Create ────────────────────────────────────────────────────────────────

    def perform_create(self, serializer):
        serializer.save()

    # ── Vote ─────────────────────────────────────────────────────────────────

    @action(detail=True, methods=["post"])
    @transaction.atomic
    def vote(self, request, pk=None):
        """Toggle upvote. Returns {voted: bool, upvote_count: int}."""
        fb = self.get_object()
        vote, created = FeedbackVote.objects.get_or_create(
            request=fb, voter=request.user
        )
        if not created:
            vote.delete()
            FeedbackRequest.objects.filter(pk=fb.pk).update(
                upvote_count=FeedbackRequest.objects.filter(pk=fb.pk).values_list(
                    "upvote_count", flat=True
                ).first() - 1
            )
            fb.refresh_from_db(fields=["upvote_count"])
            return Response({"voted": False, "upvote_count": max(fb.upvote_count, 0)})
        FeedbackRequest.objects.filter(pk=fb.pk).update(
            upvote_count=FeedbackRequest.objects.filter(pk=fb.pk).values_list(
                "upvote_count", flat=True
            ).first() + 1
        )
        fb.refresh_from_db(fields=["upvote_count"])
        return Response({"voted": True, "upvote_count": fb.upvote_count})

    # ── Staff: public response ────────────────────────────────────────────────

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated, CanTriageFeedback])
    def respond(self, request, pk=None):
        """Post a public response visible to the requester."""
        fb = self.get_object()
        text = request.data.get("response", "").strip()
        if not text:
            return Response(
                {"detail": "Response text is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        fb.public_response = text
        fb.public_response_at = timezone.now()
        fb.responded_by = request.user
        fb.save(update_fields=["public_response", "public_response_at", "responded_by", "updated_at"])

        # Notify the requester
        try:
            from notifications_system.services.notification_service import NotificationService
            NotificationService.notify(
                event_key="feedback.staff_responded",
                recipient=fb.requester,
                website=fb.website,
                context={"title": fb.title, "response": text},
                triggered_by=request.user,
            )
        except Exception:
            pass

        return Response(FeedbackRequestDetailSerializer(fb, context={"request": request}).data)

    # ── Staff: mark duplicate ─────────────────────────────────────────────────

    @action(
        detail=True,
        methods=["post"],
        url_path="mark-duplicate",
        permission_classes=[IsAuthenticated, CanTriageFeedback],
    )
    def mark_duplicate(self, request, pk=None):
        """Link this request as a duplicate of another."""
        fb = self.get_object()
        parent_id = request.data.get("duplicate_of")
        if not parent_id:
            return Response(
                {"detail": "duplicate_of is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            parent = FeedbackRequest.objects.get(pk=parent_id)
        except FeedbackRequest.DoesNotExist:
            return Response(
                {"detail": "Parent request not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        if parent.pk == fb.pk:
            return Response(
                {"detail": "A request cannot be a duplicate of itself."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        old_status = fb.status
        fb.duplicate_of = parent
        fb.status = "duplicate"
        fb.save(update_fields=["duplicate_of", "status", "updated_at"])

        FeedbackStatusEvent.objects.create(
            request=fb,
            from_status=old_status,
            to_status="duplicate",
            changed_by=request.user,
            note=f"Marked as duplicate of #{parent.pk}: {parent.title}",
        )
        return Response(FeedbackRequestDetailSerializer(fb, context={"request": request}).data)

    # ── Staff: triage board (same as list but named route for clarity) ────────

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated, CanTriageFeedback],
    )
    def triage(self, request):
        """Staff triage board with all filters applied (same queryset as list)."""
        qs = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = FeedbackRequestListSerializer(
                page, many=True, context=self.get_serializer_context()
            )
            return self.get_paginated_response(serializer.data)
        serializer = FeedbackRequestListSerializer(
            qs, many=True, context=self.get_serializer_context()
        )
        return Response(serializer.data)

    # ── Categories available for current surface ──────────────────────────────

    @action(detail=False, methods=["get"])
    def categories(self, request):
        """Return category choices available for the caller's portal surface."""
        surface = _detect_surface(request.user)
        allowed_codes = set(SURFACE_CATEGORIES.get(surface, []))
        choices = [
            {"value": code, "label": label}
            for code, label in FeedbackRequest.CATEGORY_CHOICES
            if code in allowed_codes
        ]
        return Response({"surface": surface, "categories": choices})

    # ── Summary counts for dashboard widgets ─────────────────────────────────

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated, CanTriageFeedback],
    )
    def summary(self, request):
        """Status and category counts for staff dashboard widgets."""
        qs = self.get_queryset()
        from django.db.models import Count

        status_counts = dict(
            qs.values_list("status").annotate(n=Count("id")).values_list("status", "n")
        )
        category_counts = dict(
            qs.values_list("category").annotate(n=Count("id")).values_list("category", "n")
        )
        surface_counts = dict(
            qs.values_list("portal_surface").annotate(n=Count("id")).values_list("portal_surface", "n")
        )
        top = qs.order_by("-upvote_count").values("id", "title", "upvote_count", "status")[:10]
        return Response({
            "total": qs.count(),
            "by_status": status_counts,
            "by_category": category_counts,
            "by_surface": surface_counts,
            "top_voted": list(top),
        })
