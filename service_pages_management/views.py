from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.timezone import now, timedelta
from drf_spectacular.utils import (
    extend_schema, OpenApiParameter, OpenApiExample
)
from .models import (
    ServicePage, ServicePageCategory,
    ServicePageClick, ServicePageConversion
)
from .serializers import (
    ServicePageSerializer, ServicePageCategorySerializer
)
from .permissions import IsAdminOrSuperAdmin


@extend_schema(tags=["Service Page Categories"])
class ServicePageCategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing service page categories.
    """
    queryset = ServicePageCategory.objects.all()
    serializer_class = ServicePageCategorySerializer
    permission_classes = [IsAdminOrSuperAdmin]


@extend_schema(tags=["Service Pages"])
class ServicePageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing service pages and related analytics.
    """
    serializer_class = ServicePageSerializer
    permission_classes = [IsAdminOrSuperAdmin]

    def get_queryset(self):
        """
        Returns all non-deleted service pages.
        """
        return ServicePage.objects.filter(
            is_deleted=False
        ).select_related('website', 'category')

    def perform_create(self, serializer):
        """
        Adds creator and updater on create.
        """
        serializer.save(
            created_by=self.request.user,
            updated_by=self.request.user
        )

    def perform_update(self, serializer):
        """
        Updates `updated_by` on update.
        """
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, instance):
        """
        Soft delete the service page instead of hard delete.
        """
        instance.delete()

    @extend_schema(
        summary="Track a click (view)",
        description="Records a view (click) event for analytics tracking.",
        methods=["POST"]
    )
    @action(
        detail=True,
        methods=['post'],
        permission_classes=[permissions.AllowAny]
    )
    def track_click(self, request, pk=None):
        """
        Tracks a click on the service page.
        """
        try:
            page = self.get_queryset().get(pk=pk)
        except ServicePage.DoesNotExist:
            return Response(
                {"detail": "Service page not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        ServicePageClick.objects.create(
            service_page=page,
            website=page.website,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            session_id=request.session.session_key or ''
        )
        return Response({"status": "click recorded"})

    @extend_schema(
        summary="Track a conversion (e.g. order)",
        description="Records a conversion tied to the service page.",
        methods=["POST"],
        examples=[
            OpenApiExample(
                'Conversion Example',
                value={"type": "order", "referral_url": "https://example.com"},
                request_only=True
            )
        ]
    )
    @action(
        detail=True,
        methods=['post'],
        permission_classes=[permissions.AllowAny]
    )
    def track_conversion(self, request, pk=None):
        """
        Tracks a conversion for the service page.
        """
        try:
            page = self.get_queryset().get(pk=pk)
        except ServicePage.DoesNotExist:
            return Response(
                {"detail": "Service page not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        conversion_type = request.data.get('type', 'order')
        referral_url = request.data.get('referral_url', '')

        ServicePageConversion.objects.create(
            service_page=page,
            website=page.website,
            conversion_type=conversion_type,
            referral_url=referral_url
        )
        return Response({"status": "conversion recorded"})

    @extend_schema(
        summary="Get service page analytics",
        description="Returns click and conversion counts over N days.",
        parameters=[
            OpenApiParameter(
                name='days',
                description='Number of days for historical data (default: 30)',
                required=False,
                type=int
            )
        ],
        methods=["GET"]
    )
    @action(
        detail=True,
        methods=['get'],
        permission_classes=[IsAdminOrSuperAdmin]
    )
    def analytics(self, request, pk=None):
        """
        Returns analytics data for the service page.
        """
        try:
            page = self.get_queryset().get(pk=pk)
        except ServicePage.DoesNotExist:
            return Response(
                {"detail": "Service page not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        days = int(request.query_params.get('days', 30))
        since = now() - timedelta(days=days)

        click_count = ServicePageClick.objects.filter(
            service_page=page,
            timestamp__gte=since
        ).count()

        conversion_count = ServicePageConversion.objects.filter(
            service_page=page,
            timestamp__gte=since
        ).count()

        return Response({
            "service_page_id": pk,
            "clicks": click_count,
            "conversions": conversion_count,
            "since": since
        })