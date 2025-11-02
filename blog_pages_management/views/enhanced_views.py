"""
Enhanced API views for CMS features - CTAs, Content Blocks, SEO, Edit History.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend

from ..models.content_blocks import (
    CTABlock, BlogCTAPlacement, ContentBlockTemplate, BlogContentBlock, BlogEditHistory
)
from ..models.seo_models import BlogSEOMetadata, FAQSchema, AuthorSchema
try:
    from ..models import BlogPost
except ImportError:
    from blog_pages_management.models import BlogPost
from ..services.cta_service import CTAService, ContentBlockService
from ..services.seo_service import SEOService
from ..serializers.enhanced_serializers import (
    CTABlockSerializer, BlogCTAPlacementSerializer,
    ContentBlockTemplateSerializer, BlogContentBlockSerializer,
    BlogEditHistorySerializer, BlogSEOMetadataSerializer,
    FAQSchemaSerializer, AuthorSchemaSerializer,
)


class CTABlockViewSet(viewsets.ModelViewSet):
    """ViewSet for managing CTA blocks."""
    queryset = CTABlock.objects.all()
    serializer_class = CTABlockSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['website', 'cta_type', 'is_active']
    
    @action(detail=False, methods=['post'])
    def auto_place_in_blog(self, request):
        """Auto-place CTAs in a blog post."""
        blog_id = request.data.get('blog_id')
        cta_block_ids = request.data.get('cta_block_ids', [])
        
        try:
            blog = BlogPost.objects.get(id=blog_id)
        except BlogPost.DoesNotExist:
            return Response(
                {'error': 'Blog not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        cta_blocks = CTABlock.objects.filter(
            id__in=cta_block_ids,
            website=blog.website
        ) if cta_block_ids else None
        
        placements = CTAService.auto_insert_ctas(blog=blog, cta_blocks=list(cta_blocks) if cta_blocks else None)
        
        serializer = BlogCTAPlacementSerializer(placements, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def track_click(self, request, pk=None):
        """Track a click on a CTA placement."""
        placement_id = request.data.get('placement_id')
        ip_address = request.META.get('REMOTE_ADDR')
        
        try:
            placement = BlogCTAPlacement.objects.get(id=placement_id)
        except BlogCTAPlacement.DoesNotExist:
            return Response(
                {'error': 'CTA placement not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        CTAService.track_cta_click(
            placement=placement,
            user=request.user if request.user.is_authenticated else None,
            ip_address=ip_address
        )
        
        return Response({'success': True}, status=status.HTTP_200_OK)


class BlogCTAPlacementViewSet(viewsets.ModelViewSet):
    """ViewSet for managing CTA placements in blogs."""
    queryset = BlogCTAPlacement.objects.all()
    serializer_class = BlogCTAPlacementSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['blog', 'cta_block', 'placement_type', 'is_active']


class ContentBlockTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet for managing content block templates."""
    queryset = ContentBlockTemplate.objects.all()
    serializer_class = ContentBlockTemplateSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['website', 'block_type', 'is_active']


class BlogContentBlockViewSet(viewsets.ModelViewSet):
    """ViewSet for managing content blocks in blog posts."""
    queryset = BlogContentBlock.objects.all()
    serializer_class = BlogContentBlockSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['blog', 'template', 'is_active']
    
    @action(detail=False, methods=['get'])
    def rendered_content(self, request):
        """Get rendered blog content with all content blocks inserted."""
        blog_id = request.query_params.get('blog_id')
        
        try:
            blog = BlogPost.objects.get(id=blog_id)
        except BlogPost.DoesNotExist:
            return Response(
                {'error': 'Blog not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        rendered = ContentBlockService.get_rendered_content(blog)
        return Response({'rendered_content': rendered}, status=status.HTTP_200_OK)


class BlogEditHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing blog edit history."""
    queryset = BlogEditHistory.objects.all()
    serializer_class = BlogEditHistorySerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['blog', 'edited_by']


class BlogSEOMetadataViewSet(viewsets.ModelViewSet):
    """ViewSet for managing blog SEO metadata."""
    queryset = BlogSEOMetadata.objects.all()
    serializer_class = BlogSEOMetadataSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['blog']


class FAQSchemaViewSet(viewsets.ModelViewSet):
    """ViewSet for managing FAQs with Schema.org support."""
    queryset = FAQSchema.objects.all()
    serializer_class = FAQSchemaSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['blog', 'is_featured']


class AuthorSchemaViewSet(viewsets.ModelViewSet):
    """ViewSet for managing author schema data."""
    queryset = AuthorSchema.objects.all()
    serializer_class = AuthorSchemaSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['author']


class EnhancedBlogPostViewSet(viewsets.ModelViewSet):
    """Enhanced blog post ViewSet with CMS features."""
    queryset = BlogPost.objects.all()
    serializer_class = None  # Will use EnhancedBlogPostSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        """Use enhanced serializer for detail view, standard for list."""
        if self.action == 'retrieve':
            from ..serializers.enhanced_serializers import EnhancedBlogPostSerializer
            return EnhancedBlogPostSerializer
        from ..serializers import BlogPostSerializer
        return BlogPostSerializer
    
    @action(detail=True, methods=['get'])
    def schema(self, request, pk=None):
        """Get Schema.org structured data for this blog."""
        blog = self.get_object()
        schemas = SEOService.get_all_schemas_for_blog(blog)
        script_tags = SEOService.render_schema_script_tags(blog)
        
        return Response({
            'schemas': schemas,
            'script_tags': script_tags
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'])
    def og_tags(self, request, pk=None):
        """Get Open Graph meta tags."""
        blog = self.get_object()
        og_tags = SEOService.get_open_graph_tags(blog)
        return Response(og_tags, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'])
    def twitter_tags(self, request, pk=None):
        """Get Twitter Card meta tags."""
        blog = self.get_object()
        twitter_tags = SEOService.get_twitter_card_tags(blog)
        return Response(twitter_tags, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'])
    def ctas(self, request, pk=None):
        """Get all CTAs for this blog."""
        blog = self.get_object()
        ctas = ContentBlockService.get_rendered_ctas(blog)
        return Response(ctas, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'])
    def edit_history(self, request, pk=None):
        """Get edit history for this blog."""
        blog = self.get_object()
        history = BlogEditHistory.objects.filter(blog=blog).order_by('-edited_at')
        serializer = BlogEditHistorySerializer(history, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def place_cta(self, request, pk=None):
        """Place a CTA in this blog."""
        blog = self.get_object()
        cta_block_id = request.data.get('cta_block_id')
        placement_type = request.data.get('placement_type', 'manual')
        position = request.data.get('position', 0)
        
        try:
            cta_block = CTABlock.objects.get(id=cta_block_id, website=blog.website)
        except CTABlock.DoesNotExist:
            return Response(
                {'error': 'CTA block not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        placement = CTAService.place_cta_in_blog(
            blog=blog,
            cta_block=cta_block,
            placement_type=placement_type,
            position=position
        )
        
        serializer = BlogCTAPlacementSerializer(placement)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def insert_content_block(self, request, pk=None):
        """Insert a content block into this blog."""
        blog = self.get_object()
        template_id = request.data.get('template_id')
        position = request.data.get('position', 0)
        custom_data = request.data.get('custom_data', {})
        
        try:
            template = ContentBlockTemplate.objects.get(id=template_id, website=blog.website)
        except ContentBlockTemplate.DoesNotExist:
            return Response(
                {'error': 'Content block template not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        block = ContentBlockService.insert_content_block(
            blog=blog,
            template=template,
            position=position,
            custom_data=custom_data
        )
        
        serializer = BlogContentBlockSerializer(block)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

