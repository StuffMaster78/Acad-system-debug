from rest_framework import viewsets, mixins, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import action
from rest_framework.response import Response

from reviews_system.models import WebsiteReview, WriterReview, OrderReview
from reviews_system.serializers import (
    WebsiteReviewSerializer,
    WriterReviewSerializer,
    OrderReviewSerializer,
    ReviewModerationSerializer,
    ReviewDisputeSerializer,
)
from reviews_system.permissions import IsReviewOwnerOrAdmin
from reviews_system.services.review_moderation_service import ReviewModerationService


class WebsiteReviewViewSet(viewsets.ModelViewSet):
    """
    API viewset for creating and moderating website reviews.
    """

    queryset = WebsiteReview.objects.all().select_related("reviewer", "website")
    serializer_class = WebsiteReviewSerializer
    permission_classes = [IsAuthenticated, IsReviewOwnerOrAdmin]

    def get_permissions(self):
        if self.action in ["moderate", "destroy"]:
            return [IsAdminUser()]
        elif self.action in ["dispute"]:
            return [IsAuthenticated()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(
            reviewer=self.request.user,
            origin="client_panel"
        )

    @action(detail=True, methods=["post"])
    def moderate(self, request, pk=None):
        review = self.get_object()
        serializer = ReviewModerationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ReviewModerationService.moderate_review(review, serializer.validated_data)
        return Response({"detail": "Review moderation successful."})

    @action(detail=True, methods=["post"])
    def dispute(self, request, pk=None):
        review = self.get_object()
        serializer = ReviewDisputeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        review.dispute_reason = serializer.validated_data["reason"]
        review.is_flagged = True
        review.flag_reason = "Dispute submitted by writer"
        review.save(update_fields=["dispute_reason", "is_flagged", "flag_reason"])
        return Response({"detail": "Dispute submitted."})


class WriterReviewViewSet(viewsets.ModelViewSet):
    """
    API viewset for writer reviews (submitted by clients, disputed by writers).
    """

    queryset = WriterReview.objects.all().select_related("reviewer", "writer")
    serializer_class = WriterReviewSerializer
    permission_classes = [IsAuthenticated, IsReviewOwnerOrAdmin]

    def get_permissions(self):
        if self.action in ["moderate", "destroy"]:
            return [IsAdminUser()]
        elif self.action in ["dispute"]:
            return [IsAuthenticated()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(
            reviewer=self.request.user,
            origin="client_panel"
        )

    @action(detail=True, methods=["post"])
    def moderate(self, request, pk=None):
        review = self.get_object()
        serializer = ReviewModerationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ReviewModerationService.moderate_review(review, serializer.validated_data)
        return Response({"detail": "Review moderation successful."})

    @action(detail=True, methods=["post"])
    def dispute(self, request, pk=None):
        review = self.get_object()
        serializer = ReviewDisputeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        review.dispute_reason = serializer.validated_data["reason"]
        review.is_flagged = True
        review.flag_reason = "Dispute submitted by writer"
        review.save(update_fields=["dispute_reason", "is_flagged", "flag_reason"])
        return Response({"detail": "Dispute submitted."})


class OrderReviewViewSet(viewsets.ModelViewSet):
    """
    API viewset for reviews tied to specific orders.
    """

    queryset = OrderReview.objects.all().select_related("reviewer", "order", "writer")
    serializer_class = OrderReviewSerializer
    permission_classes = [IsAuthenticated, IsReviewOwnerOrAdmin]

    def get_permissions(self):
        if self.action in ["moderate", "destroy"]:
            return [IsAdminUser()]
        elif self.action in ["dispute"]:
            return [IsAuthenticated()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(
            reviewer=self.request.user,
            origin="client_panel"
        )

    @action(detail=True, methods=["post"])
    def moderate(self, request, pk=None):
        review = self.get_object()
        serializer = ReviewModerationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ReviewModerationService.moderate_review(review, serializer.validated_data)
        return Response({"detail": "Review moderation successful."})

    @action(detail=True, methods=["post"])
    def dispute(self, request, pk=None):
        review = self.get_object()
        serializer = ReviewDisputeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        review.dispute_reason = serializer.validated_data["reason"]
        review.is_flagged = True
        review.flag_reason = "Dispute submitted by writer"
        review.save(update_fields=["dispute_reason", "is_flagged", "flag_reason"])
        return Response({"detail": "Dispute submitted."})