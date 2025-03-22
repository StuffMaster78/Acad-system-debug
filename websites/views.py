from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Website, WebsiteActionLog, WebsiteStaticPage
from rest_framework.permissions import AllowAny
from .serializers import (
    WebsiteSerializer, WebsiteSEOUpdateSerializer,
    WebsiteSoftDeleteSerializer, WebsiteActionLogSerializer,
     WebsiteStaticPageSerializer
)
from .permissions import IsAdminOrSuperadmin
from rest_framework.pagination import PageNumberPagination
from django.core.cache import cache
from rest_framework.throttling import AnonRateThrottle

class StaticPageThrottle(AnonRateThrottle):
    rate = '5/min'  
class LogPagination(PageNumberPagination):
    page_size = 25 
class WebsiteViewSet(viewsets.ModelViewSet):
    """Handles website CRUD, SEO updates, and soft deletion."""
    
    queryset = Website.objects.all()
    serializer_class = WebsiteSerializer
    permission_classes = [IsAdminOrSuperadmin]  # 🔥 Restrict all actions to superadmins/admins

    def get_serializer_class(self):
        if self.action == "update_seo_settings":
            return WebsiteSEOUpdateSerializer
        if self.action in ["soft_delete", "restore"]:
            return WebsiteSoftDeleteSerializer
        return super().get_serializer_class()

    @swagger_auto_schema(
        operation_description="Update website SEO settings (Google Analytics, Bing Webmaster, etc.).",
        request_body=WebsiteSEOUpdateSerializer,
        responses={200: "SEO settings updated successfully."},
    )
    @action(detail=True, methods=["patch"], permission_classes=[IsAdminOrSuperadmin])
    def update_seo_settings(self, request, pk=None):
        """Allows only superadmins & admins to update SEO & Analytics settings."""
        website = self.get_object()
        serializer = WebsiteSEOUpdateSerializer(website, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            WebsiteActionLog.objects.create(
                website=website,
                user=request.user,
                action="SEO_UPDATED",
                details=f"Updated SEO settings: {serializer.data}",
            )
            return Response({"message": "SEO settings updated successfully!", "data": serializer.data})
        
        return Response(serializer.errors, status=400)

    @swagger_auto_schema(
        operation_description="Soft delete a website (mark as inactive instead of deleting permanently).",
        responses={200: "Website soft-deleted successfully."},
    )
    @action(detail=True, methods=["post"], permission_classes=[IsAdminOrSuperadmin])  # 🔥 Restrict to Superadmins/Admins
    def soft_delete(self, request, pk=None):
        """Allows only admins to soft delete a website."""
        website = self.get_object()
        website.soft_delete()
        WebsiteActionLog.objects.create(
            website=website,
            user=request.user,
            action="SOFT_DELETED",
            details="Website was soft deleted.",
        )
        return Response({"message": "Website soft-deleted successfully!"})

    @swagger_auto_schema(
        operation_description="Restore a soft-deleted website.",
        responses={200: "Website restored successfully."},
    )
    @action(detail=True, methods=["post"], permission_classes=[IsAdminOrSuperadmin])  # 🔥 Restrict to Superadmins/Admins
    def restore(self, request, pk=None):
        """Allows only admins to restore a soft-deleted website."""
        website = self.get_object()
        website.restore()
        WebsiteActionLog.objects.create(
            website=website,
            user=request.user,
            action="RESTORED",
            details="Website was restored.",
        )
        return Response({"message": "Website restored successfully!"})

class WebsiteActionLogViewSet(viewsets.ReadOnlyModelViewSet):
    """Handles retrieving admin action logs for website updates."""
    
    serializer_class = WebsiteActionLogSerializer
    permission_classes = [permissions.IsAdminUser]
    pagination_class = LogPagination  # 🔥 Enable pagination

    def get_queryset(self):
        """Filter logs based on website query param and limit to recent 100 logs."""
        website_id = self.request.query_params.get("website_id")
        queryset = WebsiteActionLog.objects.all().order_by("-timestamp")

        if website_id:
            queryset = queryset.filter(website_id=website_id)

        return queryset[:100]  # 🔥 Limit logs to the last 100 records for performance

    @swagger_auto_schema(
        operation_description="Retrieve all website update logs (SEO updates, deletions, restorations).",
        responses={200: WebsiteActionLogSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        """Retrieve all logs for admin actions on websites."""
        return super().list(request, *args, **kwargs)



class WebsiteStaticPageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint to retrieve static pages for websites.
    
    - Retrieves static pages by `slug`
    - Filters by `website` domain and `language`
    - Excludes pages from soft-deleted websites
    - Implements throttling to prevent bot abuse
    - Increments unique page views while preventing multiple increments within 1 minute
    """

    queryset = WebsiteStaticPage.objects.filter(website__is_deleted=False)  # 🔥 Exclude deleted websites
    serializer_class = WebsiteStaticPageSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "slug"
    throttle_classes = [StaticPageThrottle]  # 🔥 Prevent abuse by bots

    @swagger_auto_schema(
        operation_description="Retrieve all static pages filtered by website domain and language.",
        manual_parameters=[
            openapi.Parameter(
                "website",
                openapi.IN_QUERY,
                description="Domain of the website (e.g., example.com)",
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                "lang",
                openapi.IN_QUERY,
                description="Language code for the static page (e.g., en, fr, es). Default is English (en).",
                type=openapi.TYPE_STRING,
                required=False,
                default="en",
            ),
        ],
        responses={
            200: WebsiteStaticPageSerializer(many=True),
            400: "Invalid request parameters",
        },
    )
    def get_queryset(self):
        """Filters static pages by website and language."""
        website = self.request.query_params.get("website")
        language = self.request.query_params.get("lang", "en")  # Default to English

        if website:
            return WebsiteStaticPage.objects.filter(
                website__domain=website,
                language=language,
                website__is_deleted=False,
            )
        return self.queryset.none()

    @swagger_auto_schema(
        operation_description="Retrieve a static page by its slug. Increments view count (rate-limited).",
        responses={
            200: WebsiteStaticPageSerializer(),
            404: "Page not found",
        },
    )
    def retrieve(self, request, *args, **kwargs):
        """Retrieves a specific static page by slug and increments views (rate-limited)."""
        instance = self.get_object()

        # 🔥 Rate limit views (Only increment if not counted in cache)
        cache_key = f"page_view_{instance.slug}_{request.META['REMOTE_ADDR']}"
        if not cache.get(cache_key):
            instance.increment_views()  # Increase views count
            cache.set(cache_key, "viewed", timeout=60)  # Prevent multiple increments within 1 minute

        serializer = self.get_serializer(instance)
        return Response(serializer.data)