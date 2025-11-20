"""
Public preview view for blog posts using preview tokens.
"""
from django.shortcuts import get_object_or_404
from django.http import Http404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

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

