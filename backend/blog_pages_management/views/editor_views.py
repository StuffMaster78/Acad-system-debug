"""
Editor tooling API views - templates, snippets, health checks, etc.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from ..models.workflow_models import ContentTemplate, ContentSnippet
from ..models.content_blocks import ContentBlockTemplate
from ..services.content_health_service import ContentHealthService
from ..serializers.workflow_serializers import ContentTemplateSerializer, ContentSnippetSerializer


class EditorToolingViewSet(viewsets.ViewSet):
    """
    Editor tooling endpoints for real-time assistance.
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def health_check(self, request):
        """
        Real-time content health check.
        
        Body:
        {
            "title": "...",
            "meta_title": "...",
            "meta_description": "...",
            "content": "...",
            "slug": "...",
            "min_words": 300
        }
        """
        title = request.data.get('title', '')
        meta_title = request.data.get('meta_title', '')
        meta_description = request.data.get('meta_description', '')
        content = request.data.get('content', '')
        slug = request.data.get('slug', '')
        min_words = int(request.data.get('min_words', 300))
        
        result = ContentHealthService.check_full_content(
            title=title,
            meta_title=meta_title,
            meta_description=meta_description,
            content=content,
            slug=slug,
            min_words=min_words
        )
        
        return Response(result, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def quick_templates(self, request):
        """
        Get quick access templates for editor.
        Query params: website_id, template_type
        """
        website_id = request.query_params.get('website_id')
        template_type = request.query_params.get('template_type', 'blog_post')
        
        if not website_id:
            return Response(
                {'error': 'website_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        templates = ContentTemplate.objects.filter(
            website_id=website_id,
            template_type=template_type,
            is_active=True
        ).order_by('-usage_count', 'name')[:10]
        
        serializer = ContentTemplateSerializer(templates, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def quick_snippets(self, request):
        """
        Get quick access snippets for editor.
        Query params: website_id, snippet_type, search
        """
        website_id = request.query_params.get('website_id')
        snippet_type = request.query_params.get('snippet_type')
        search = request.query_params.get('search', '')
        
        if not website_id:
            return Response(
                {'error': 'website_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        snippets = ContentSnippet.objects.filter(
            website_id=website_id,
            is_active=True
        )
        
        if snippet_type:
            snippets = snippets.filter(snippet_type=snippet_type)
        
        if search:
            snippets = snippets.filter(
                name__icontains=search
            ) | snippets.filter(
                tags__icontains=search
            )
        
        snippets = snippets.order_by('-usage_count', 'name')[:20]
        
        serializer = ContentSnippetSerializer(snippets, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def quick_blocks(self, request):
        """
        Get quick access content blocks for editor.
        Query params: website_id, block_type
        """
        website_id = request.query_params.get('website_id')
        block_type = request.query_params.get('block_type')
        
        if not website_id:
            return Response(
                {'error': 'website_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        blocks = ContentBlockTemplate.objects.filter(
            website_id=website_id,
            is_active=True
        )
        
        if block_type:
            blocks = blocks.filter(block_type=block_type)
        
        blocks = blocks.order_by('name')[:20]
        
        from ..serializers.enhanced_serializers import ContentBlockTemplateSerializer
        serializer = ContentBlockTemplateSerializer(blocks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'])
    def insert_snippet(self, request):
        """
        Insert a snippet into content and return rendered content.
        
        Body:
        {
            "snippet_id": 123,
            "current_content": "...",
            "cursor_position": 100,
            "format": "html"
        }
        """
        snippet_id = request.data.get('snippet_id')
        current_content = request.data.get('current_content', '')
        cursor_position = int(request.data.get('cursor_position', len(current_content)))
        format_type = request.data.get('format', 'html')
        
        try:
            snippet = ContentSnippet.objects.get(id=snippet_id)
        except ContentSnippet.DoesNotExist:
            return Response(
                {'error': 'Snippet not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Increment usage
        snippet.increment_usage()
        
        # Insert snippet content at cursor position
        snippet_content = snippet.content
        
        # For HTML format, insert as-is
        if format_type == 'html':
            new_content = (
                current_content[:cursor_position] +
                snippet_content +
                current_content[cursor_position:]
            )
        else:
            # For other formats, might need conversion
            new_content = (
                current_content[:cursor_position] +
                snippet_content +
                current_content[cursor_position:]
            )
        
        return Response({
            'content': new_content,
            'new_cursor_position': cursor_position + len(snippet_content),
            'snippet': ContentSnippetSerializer(snippet).data
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'])
    def insert_block(self, request):
        """
        Insert a content block into content.
        
        Body:
        {
            "block_id": 123,
            "current_content": "...",
            "cursor_position": 100
        }
        """
        block_id = request.data.get('block_id')
        current_content = request.data.get('current_content', '')
        cursor_position = int(request.data.get('cursor_position', len(current_content)))
        
        try:
            block = ContentBlockTemplate.objects.get(id=block_id)
        except ContentBlockTemplate.DoesNotExist:
            return Response(
                {'error': 'Content block not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Insert block HTML
        block_html = block.content
        new_content = (
            current_content[:cursor_position] +
            block_html +
            current_content[cursor_position:]
        )
        
        return Response({
            'content': new_content,
            'new_cursor_position': cursor_position + len(block_html),
            'block': {
                'id': block.id,
                'name': block.name,
                'block_type': block.block_type
            }
        }, status=status.HTTP_200_OK)

