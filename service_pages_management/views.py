from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiExample
)
from .models import (
    ServicePage,
    ServicePageClick,
    ServicePageConversion
)
from .serializers import (
    ServicePageSerializer,
    ServicePageAnalyticsSerializer
)
from .permissions import IsAdminOrSuperAdmin


@extend_schema(tags=["Service Pages"])
class ServicePageViewSet(viewsets.ModelViewSet):
    """
    Handles CRUD operations, tracking,
    and analytics for service pages.
    """
    serializer_class = ServicePageSerializer
    permission_classes = [IsAdminOrSuperAdmin]

    def get_queryset(self):
        """
        Return all non-deleted service pages.
        """
        return ServicePage.objects.filter(
            is_deleted=False
        ).select_related('website')

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user,
            updated_by=self.request.user
        )

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, instance):
        instance.delete()

    @extend_schema(
        summary="Track a view/click",
        methods=["POST"]
    )
    @action(
        detail=True,
        methods=['post'],
        permission_classes=[permissions.AllowAny]
    )
    def track_click(self, request, pk=None):
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
        summary="Track a conversion event",
        methods=["POST"],
        examples=[
            OpenApiExample(
                name="Example",
                value={
                    "type": "order",
                    "referral_url": "https://client.com/order-page"
                },
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
        try:
            page = self.get_queryset().get(pk=pk)
        except ServicePage.DoesNotExist:
            return Response(
                {"detail": "Service page not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        ServicePageConversion.objects.create(
            service_page=page,
            website=page.website,
            conversion_type=request.data.get("type", "order"),
            referral_url=request.data.get("referral_url", "")
        )
        return Response({"status": "conversion recorded"})

    @extend_schema(
        summary="View analytics for this service page",
        parameters=[
            OpenApiParameter(
                name='days',
                description='How many days back to look (default: 30)',
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
        try:
            page = self.get_queryset().get(pk=pk)
        except ServicePage.DoesNotExist:
            return Response(
                {"detail": "Service page not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        days = request.query_params.get("days", 30)
        serializer = ServicePageAnalyticsSerializer(
            page,
            context={'days': days}
        )
        return Response(serializer.data)