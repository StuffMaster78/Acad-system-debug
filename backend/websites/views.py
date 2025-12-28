from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Website, WebsiteActionLog, WebsiteStaticPage, WebsiteTermsAcceptance
from .models_integrations import WebsiteIntegrationConfig
from rest_framework.permissions import AllowAny
from .serializers import (
    WebsiteSerializer,
    WebsiteSEOUpdateSerializer,
    WebsiteSoftDeleteSerializer,
    WebsiteActionLogSerializer,
    WebsiteStaticPageSerializer,
    WebsiteTermsAcceptanceSerializer,
    WebsiteTermsUpdateSerializer,
)
from .serializers_integrations import (
    WebsiteIntegrationConfigSerializer,
    WebsiteIntegrationConfigCreateUpdateSerializer,
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
    
    # Default ordering by id to avoid UnorderedObjectListWarning with pagination
    queryset = Website.objects.all().order_by('id')
    serializer_class = WebsiteSerializer
    permission_classes = [IsAdminOrSuperadmin]  # 🔥 Restrict all actions to superadmins/admins
    
    def get_queryset(self):
        """Filter websites based on user's role and website assignment."""
        queryset = Website.objects.all().order_by('id')
        
        # Superadmins see all websites
        if self.request.user.role == 'superadmin':
            return queryset
        
        # Regular admins see only their assigned website
        user_website = getattr(self.request.user, 'website', None)
        if user_website:
            queryset = queryset.filter(id=user_website.id)
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        """List websites with error handling."""
        try:
            return super().list(request, *args, **kwargs)
        except Exception as e:
            from rest_framework import status
            from rest_framework.response import Response
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error listing websites: {e}", exc_info=True)
            return Response(
                {"error": "Failed to retrieve websites", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

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

    @swagger_auto_schema(
        operation_description=(
            "Create or update the Terms & Conditions page (slug='terms') for this website.\n\n"
            "Fields:\n"
            "- title (optional, default: 'Terms & Conditions')\n"
            "- content (required): HTML or text content of the terms\n"
            "- language (optional, default: 'en')\n"
            "- meta_title (optional)\n"
            "- meta_description (optional)\n\n"
            "Notes:\n"
            "- This action is restricted to Admin/Superadmin.\n"
            "- Version is incremented automatically when content changes."
        ),
        request_body=WebsiteTermsUpdateSerializer,
        responses={200: WebsiteStaticPageSerializer()},
    )
    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAdminOrSuperadmin],
    )
    def update_terms(self, request, pk=None):
        """Create or update the Terms & Conditions static page for a website."""
        website = self.get_object()
        serializer = WebsiteTermsUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        title = data.get("title") or "Terms & Conditions"
        language = data.get("language", "en")
        content = data["content"]
        meta_title = data.get("meta_title", "") or title
        meta_description = data.get("meta_description", "")

        # Upsert terms page (slug='terms')
        terms_page, created = WebsiteStaticPage.objects.get_or_create(
            website=website,
            slug="terms",
            language=language,
            defaults={
                "title": title,
                "content": content,
                "meta_title": meta_title,
                "meta_description": meta_description,
            },
        )

        if not created:
            terms_page.title = title
            terms_page.content = content
            terms_page.meta_title = meta_title
            terms_page.meta_description = meta_description
            terms_page.save()

        response_serializer = WebsiteStaticPageSerializer(terms_page)
        return Response(
            {
                "message": "Terms & Conditions updated successfully.",
                "page": response_serializer.data,
            },
            status=status.HTTP_200_OK,
        )

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
        """
        Filters static pages by website and language.

        Priority:
        1) Explicit ?website=<domain> query param
        2) Fallback to X-Website header (website ID) if present
        """
        website_param = self.request.query_params.get("website")
        language = self.request.query_params.get("lang", "en")  # Default to English

        # 1) If explicit domain is provided, use it as-is
        if website_param:
            return WebsiteStaticPage.objects.filter(
                website__domain=website_param,
                language=language,
                website__is_deleted=False,
            )

        # 2) Fallback to X-Website header (we store website ID there in the frontend)
        website_header = self.request.META.get("HTTP_X_WEBSITE")
        if website_header:
            try:
                website_id = int(website_header)
            except (TypeError, ValueError):
                return self.queryset.none()

            return WebsiteStaticPage.objects.filter(
                website_id=website_id,
                language=language,
                website__is_deleted=False,
            )

        # No website context – return empty queryset for safety
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

    @swagger_auto_schema(
        method="post",
        operation_description=(
            "Record acceptance of the current website terms.\n\n"
            "Expected usage:\n"
            "- This should be called when the user explicitly clicks "
            "\"I agree\" on the Terms & Conditions page.\n\n"
            "Notes:\n"
            "- This action assumes slug='terms' for the terms page.\n"
            "- Website is resolved from ?website=<domain> or X-Website header."
        ),
        responses={200: WebsiteTermsAcceptanceSerializer()},
    )
    @action(
        detail=False,
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        url_path="terms/accept",
    )
    def accept_terms(self, request):
        """
        Record that the authenticated user accepted the current Terms & Conditions
        for this website.
        """
        # Resolve website (by domain query param or X-Website header with ID)
        website_param = request.query_params.get("website")
        website_obj = None

        if website_param:
            website_obj = Website.objects.filter(domain=website_param, is_deleted=False).first()

        if not website_obj:
            website_header = request.META.get("HTTP_X_WEBSITE")
            if website_header:
                try:
                    website_id = int(website_header)
                    website_obj = Website.objects.filter(
                        id=website_id,
                        is_deleted=False,
                    ).first()
                except (TypeError, ValueError):
                    website_obj = None

        if not website_obj:
            return Response(
                {"error": "Website context is required to accept terms."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get terms static page (slug='terms')
        try:
            terms_page = WebsiteStaticPage.objects.get(
                website=website_obj,
                slug="terms",
                website__is_deleted=False,
            )
        except WebsiteStaticPage.DoesNotExist:
            return Response(
                {"error": "Terms page (slug='terms') not configured for this website."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Create or update acceptance record
        terms_version = terms_page.version
        ip_address = request.META.get("REMOTE_ADDR")
        user_agent = request.META.get("HTTP_USER_AGENT", "")

        acceptance, _created = WebsiteTermsAcceptance.objects.update_or_create(
            website=website_obj,
            user=request.user,
            static_page=terms_page,
            terms_version=terms_version,
            defaults={
                "ip_address": ip_address,
                "user_agent": user_agent,
            },
        )

        serializer = WebsiteTermsAcceptanceSerializer(acceptance)
        return Response(serializer.data, status=status.HTTP_200_OK)


class WebsiteIntegrationConfigViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing website integration configurations.
    Only admins and superadmins can manage integrations.
    """
    permission_classes = [IsAdminOrSuperadmin]
    
    def get_queryset(self):
        """Filter integrations by website if specified."""
        queryset = WebsiteIntegrationConfig.objects.all()
        website_id = self.request.query_params.get('website', None)
        if website_id:
            queryset = queryset.filter(website_id=website_id)
        return queryset.order_by('-created_at')
    
    def get_serializer_class(self):
        """Use different serializers for read vs write operations."""
        if self.action in ['create', 'update', 'partial_update']:
            return WebsiteIntegrationConfigCreateUpdateSerializer
        return WebsiteIntegrationConfigSerializer
    
    def perform_create(self, serializer):
        """Set created_by user on creation."""
        serializer.save(created_by=self.request.user)