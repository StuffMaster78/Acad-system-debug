"""
API views for service page website-level content metrics.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser

from ..models.enhanced_models import ServiceWebsiteContentMetrics
from ..serializers.metrics_serializers import ServiceWebsiteContentMetricsSerializer
from websites.models import Website


class ServiceWebsiteContentMetricsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Exposes aggregated metrics for service pages per website.

    Endpoints:
    - GET /service-website-metrics/?website_id=... → list snapshots for a website
    - GET /service-website-metrics/latest/?website_id=... → latest snapshot only
    - POST /service-website-metrics/recalculate/ { website_id } → force recalculation
    """

    queryset = ServiceWebsiteContentMetrics.objects.all().select_related("website")
    serializer_class = ServiceWebsiteContentMetricsSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        qs = super().get_queryset()
        website_id = self.request.query_params.get("website_id")
        if website_id:
            qs = qs.filter(website_id=website_id)
        return qs

    @action(detail=False, methods=["get"])
    def latest(self, request):
        """
        Return the latest service-page metrics snapshot for a given website.
        """
        website_id = request.query_params.get("website_id")
        if not website_id:
            return Response(
                {"detail": "website_id query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            website = Website.objects.get(id=website_id)
        except Website.DoesNotExist:
            return Response(
                {"detail": "Website not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        snapshot = (
            ServiceWebsiteContentMetrics.objects.filter(website=website)
            .order_by("-calculated_at")
            .first()
        )
        if not snapshot:
            return Response(
                {"detail": "No metrics snapshot found for this website."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.get_serializer(snapshot)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"])
    def recalculate(self, request):
        """
        Force recalculation of service-page metrics for a website and return the new snapshot.
        """
        website_id = request.data.get("website_id")
        if not website_id:
            return Response(
                {"detail": "website_id is required in request body."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            website = Website.objects.get(id=website_id)
        except Website.DoesNotExist:
            return Response(
                {"detail": "Website not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        from ..models.enhanced_models import ServiceWebsiteContentMetrics as MetricsModel

        snapshot = MetricsModel.calculate_for_website(website)

        serializer = self.get_serializer(snapshot)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


