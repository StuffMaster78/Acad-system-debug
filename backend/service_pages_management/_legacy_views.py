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
from .serializers.enhanced_serializers import ServicePageContentBlockSerializer
from .models.enhanced_models import ServicePageContentBlock
from .permissions import IsAdminOrSuperAdmin
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

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
        Return all non-deleted service pages with website filtering.
        """
        queryset = ServicePage.objects.filter(
            is_deleted=False
        ).select_related('website')
        
        # Filter by website if not superadmin or admin
        if self.request.user.role not in ['superadmin', 'admin']:
            website = getattr(self.request.user, 'website', None)
            if website:
                queryset = queryset.filter(website=website)
        
        return queryset

    def perform_create(self, serializer):
        """Create service page with website selection and permission validation."""
        user = self.request.user
        website_id = self.request.data.get('website_id') or self.request.data.get('website')
        
        # Get website
        if website_id:
            try:
                from websites.models import Website
                website = Website.objects.get(id=website_id)
            except Website.DoesNotExist:
                from rest_framework.exceptions import ValidationError
                raise ValidationError({"website_id": "Invalid website ID."})
        else:
            # Auto-assign website based on user
            website = getattr(user, 'website', None)
            if not website:
                from rest_framework.exceptions import ValidationError
                raise ValidationError({
                    "website_id": "Website is required. Please select a website."
                })
        
        # Validate permissions - admins and superadmins can create for any website
        # Other roles are restricted to their assigned website
        if user.role not in ['superadmin', 'admin']:
            user_website = getattr(user, 'website', None)
            if user_website and website != user_website:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied("You can only create service pages for your assigned website.")
        
        serializer.save(
            website=website,
            created_by=user,
            updated_by=user
        )

    def perform_update(self, serializer):
        """Update service page with website validation."""
        user = self.request.user
        instance = serializer.instance
        
        # Check if website is being changed
        website_id = self.request.data.get('website_id') or self.request.data.get('website')
        if website_id:
            try:
                from websites.models import Website
                new_website = Website.objects.get(id=website_id)
            except Website.DoesNotExist:
                from rest_framework.exceptions import ValidationError
                raise ValidationError({"website_id": "Invalid website ID."})
            
            # Validate permissions for website change - admins and superadmins can change to any website
            if user.role not in ['superadmin', 'admin']:
                user_website = getattr(user, 'website', None)
                if user_website and new_website != user_website:
                    from rest_framework.exceptions import PermissionDenied
                    raise PermissionDenied("You can only assign service pages to your assigned website.")
            
            serializer.save(website=new_website, updated_by=user)
        else:
            serializer.save(updated_by=user)
    
    @action(detail=True, methods=['post'])
    def apply_template(self, request, pk=None):
        """
        Apply a content template (template_type='service_page') to this service page.

        Body:
        {
            "template_id": ...,
            "variables": { ...optional substitutions... }
        }
        """
        page = self.get_object()
        template_id = request.data.get('template_id')
        if not template_id:
            return Response(
                {"detail": "template_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from blog_pages_management.models.workflow_models import ContentTemplate
        try:
            template = ContentTemplate.objects.get(
                id=template_id, website=page.website, template_type='service_page'
            )
        except ContentTemplate.DoesNotExist:
            return Response(
                {"detail": "Template not found or not a service_page template."},
                status=status.HTTP_404_NOT_FOUND,
            )

        from blog_pages_management.services.template_service import TemplateService
        template_variables = request.data.get('variables', {})

        page = TemplateService.create_service_page_from_template(
            page, template, template_variables
        )
        page.save()

        serializer = self.get_serializer(page)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def available_websites(self, request):
        """Get list of websites available for service page creation."""
        from websites.serializers import WebsiteSerializer
        from websites.models import Website
        
        user = request.user
        
        if user.role in ['superadmin', 'admin']:
            # Superadmins and admins can see all active websites
            websites = Website.objects.filter(is_active=True, is_deleted=False).order_by('name')
            can_select = True
        else:
            # Other roles see only their assigned website (if any)
            user_website = getattr(user, 'website', None)
            if user_website:
                websites = Website.objects.filter(id=user_website.id, is_active=True, is_deleted=False)
                can_select = True
            else:
                websites = Website.objects.none()
                can_select = False
        
        serializer = WebsiteSerializer(websites, many=True)
        return Response({
            "websites": serializer.data,
            "can_select_website": can_select
        })

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
    
    @action(detail=True, methods=['get'])
    def content_blocks(self, request, pk=None):
        """Get all content blocks for this service page."""
        page = self.get_object()
        blocks = ServicePageContentBlock.objects.filter(
            service_page=page, is_active=True
        ).order_by('position')
        serializer = ServicePageContentBlockSerializer(blocks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def insert_content_block(self, request, pk=None):
        """Insert a content block into this service page."""
        page = self.get_object()
        template_id = request.data.get('template_id')
        position = request.data.get('position', 0)
        custom_data = request.data.get('custom_data', {})
        
        try:
            from blog_pages_management.models.content_blocks import ContentBlockTemplate
            template = ContentBlockTemplate.objects.get(
                id=template_id, website=page.website
            )
        except Exception as e:
            return Response(
                {'error': f'Content block template not found: {str(e)}'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        block = ServicePageContentBlock.objects.create(
            service_page=page,
            template=template,
            position=position,
            custom_data=custom_data
        )
        
        serializer = ServicePageContentBlockSerializer(block)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

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