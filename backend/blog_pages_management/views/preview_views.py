"""
Preview views for blog posts and SEO pages.
Includes both public token-based previews and internal authenticated previews.
"""
from django.shortcuts import get_object_or_404
from django.http import Http404
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets

from ..models.draft_editing import BlogPostPreview
from ..models import BlogPost
from ..models.security_models import PreviewTokenRateLimit
from ..serializers import BlogPostSerializer


@api_view(['GET'])
@permission_classes([AllowAny])
def preview_blog_post(request, token):
    """
    Public preview endpoint for blog posts using preview token.
    Allows viewing draft/scheduled posts without publishing.
    Includes rate limiting.
    """
    preview = BlogPostPreview.objects.filter(token=token, is_active=True).first()
    
    if not preview or not preview.is_valid():
        raise Http404("Preview not found or expired")
    
    # Check rate limit (max 100 views per 24 hours)
    if not PreviewTokenRateLimit.check_rate_limit(token, max_views=100, time_window_hours=24):
        return Response(
            {'error': 'Preview token rate limit exceeded. Please request a new preview link.'},
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )
    
    # Increment view count
    preview.increment_view()
    PreviewTokenRateLimit.increment_view(token)
    
    # Get blog post
    blog = preview.blog
    
    # Use enhanced serializer to include all features
    try:
        from ..serializers.enhanced_serializers import EnhancedBlogPostSerializer
        serializer = EnhancedBlogPostSerializer(
            blog,
            context={'request': request}
        )
    except ImportError:
        serializer = BlogPostSerializer(blog, context={'request': request})
    
    return Response({
        'preview': True,
        'expires_at': preview.expires_at,
        'blog': serializer.data
    }, status=status.HTTP_200_OK)


class InternalPreviewViewSet(viewsets.ViewSet):
    """
    Internal preview endpoints for authenticated users.
    Allows admins and content creators to preview how blog/SEO pages will appear publicly.
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'], url_path='blog/(?P<blog_id>[^/.]+)')
    def preview_blog(self, request, blog_id=None):
        """
        Preview a blog post as it will appear publicly.
        Accessible to authenticated users (admins, content creators).
        Works for both published and draft posts.
        """
        try:
            blog = BlogPost.objects.get(id=blog_id, is_deleted=False)
        except BlogPost.DoesNotExist:
            return Response(
                {'error': 'Blog post not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check permissions - user must have access to this blog's website
        user = request.user
        if user.role not in ['superadmin', 'admin']:
            user_website = getattr(user, 'website', None)
            if user_website and blog.website != user_website:
                return Response(
                    {'error': 'You do not have permission to preview this blog post'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Use enhanced serializer to include all features (same as public view)
        try:
            from ..serializers.enhanced_serializers import EnhancedBlogPostSerializer
            serializer = EnhancedBlogPostSerializer(
                blog,
                context={'request': request}
            )
        except ImportError:
            serializer = BlogPostSerializer(blog, context={'request': request})
        
        return Response({
            'preview': True,
            'is_internal_preview': True,
            'is_published': blog.is_published,
            'status': blog.status,
            'blog': serializer.data
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], url_path='blog-by-slug/(?P<slug>[^/.]+)')
    def preview_blog_by_slug(self, request, slug=None):
        """
        Preview a blog post by slug as it will appear publicly.
        Accessible to authenticated users (admins, content creators).
        """
        website_id = request.query_params.get('website_id')
        
        queryset = BlogPost.objects.filter(
            slug=slug,
            is_deleted=False
        )
        
        if website_id:
            queryset = queryset.filter(website_id=website_id)
        
        try:
            blog = queryset.first()
        except BlogPost.DoesNotExist:
            return Response(
                {'error': 'Blog post not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if not blog:
            return Response(
                {'error': 'Blog post not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check permissions
        user = request.user
        if user.role not in ['superadmin', 'admin']:
            user_website = getattr(user, 'website', None)
            if user_website and blog.website != user_website:
                return Response(
                    {'error': 'You do not have permission to preview this blog post'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Use enhanced serializer
        try:
            from ..serializers.enhanced_serializers import EnhancedBlogPostSerializer
            serializer = EnhancedBlogPostSerializer(
                blog,
                context={'request': request}
            )
        except ImportError:
            serializer = BlogPostSerializer(blog, context={'request': request})
        
        return Response({
            'preview': True,
            'is_internal_preview': True,
            'is_published': blog.is_published,
            'status': blog.status,
            'blog': serializer.data
        }, status=status.HTTP_200_OK)
