"""
Content audit views - identify content that needs attention.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta

from ..models import BlogPost
from ..models.analytics_models import WebsiteContentMetrics
from service_pages_management.models import ServicePage


class ContentAuditViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for content audit - identifies posts/pages that need attention.
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def blog_issues(self, request):
        """
        Get blog posts with SEO/content issues.
        
        Query params:
        - website_id: Filter by website
        - only_issues: If true, only return posts with issues
        - order_by: freshness_score, view_count, conversion_count (default: freshness_score)
        - freshness_threshold: Minimum freshness score (default: 40)
        - min_word_count: Minimum word count (default: 300)
        """
        website_id = request.query_params.get('website_id')
        only_issues = request.query_params.get('only_issues', 'false').lower() == 'true'
        order_by = request.query_params.get('order_by', 'freshness_score')
        freshness_threshold = int(request.query_params.get('freshness_threshold', 40))
        min_word_count = int(request.query_params.get('min_word_count', 300))
        
        queryset = BlogPost.objects.filter(
            is_deleted=False
        ).select_related('category', 'website')
        
        if website_id:
            queryset = queryset.filter(website_id=website_id)
        
        # Filter by website if not superadmin or admin
        if request.user.role not in ['superadmin', 'admin']:
            website = getattr(request.user, 'website', None)
            if website:
                queryset = queryset.filter(website=website)
        
        issues = []
        for blog in queryset:
            blog_issues = []
            
            # SEO issues
            if not blog.meta_title:
                blog_issues.append('missing_meta_title')
            elif len(blog.meta_title) > 60:
                blog_issues.append('meta_title_too_long')
            
            if not blog.meta_description:
                blog_issues.append('missing_meta_description')
            elif len(blog.meta_description) > 160:
                blog_issues.append('meta_description_too_long')
            
            # Content quality issues
            word_count = len(blog.content.split())
            if word_count < min_word_count:
                blog_issues.append('low_word_count')
            
            # Freshness issues
            freshness_score = getattr(blog, 'freshness_score', 100)  # Default to 100 if not set
            if freshness_score < freshness_threshold:
                blog_issues.append('stale_content')
            
            # Engagement issues (optional flags)
            if blog.view_count == 0 and blog.is_published:
                blog_issues.append('no_views')
            
            if blog.conversion_count == 0 and blog.view_count > 100:
                blog_issues.append('low_conversion_rate')
            
            if only_issues and not blog_issues:
                continue
            
            issues.append({
                'id': blog.id,
                'title': blog.title,
                'slug': blog.slug,
                'website_id': blog.website_id,
                'status': blog.status,
                'is_published': blog.is_published,
                'publish_date': blog.publish_date.isoformat() if blog.publish_date else None,
                'freshness_score': getattr(blog, 'freshness_score', 100),
                'view_count': blog.view_count,
                'conversion_count': blog.conversion_count,
                'word_count': word_count,
                'meta_title_length': len(blog.meta_title) if blog.meta_title else 0,
                'meta_description_length': len(blog.meta_description) if blog.meta_description else 0,
                'issues': blog_issues,
                'issue_count': len(blog_issues)
            })
        
        # Sort
        reverse = order_by in ['freshness_score', 'view_count', 'conversion_count']
        issues.sort(key=lambda x: x.get(order_by, 0), reverse=reverse)
        
        return Response({
            'total': len(issues),
            'with_issues': sum(1 for i in issues if i['issue_count'] > 0),
            'issues': issues
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def service_page_issues(self, request):
        """
        Get service pages with SEO/content issues.
        """
        website_id = request.query_params.get('website_id')
        only_issues = request.query_params.get('only_issues', 'false').lower() == 'true'
        min_word_count = int(request.query_params.get('min_word_count', 300))
        
        queryset = ServicePage.objects.filter(
            is_deleted=False
        ).select_related('website')
        
        if website_id:
            queryset = queryset.filter(website_id=website_id)
        
        if request.user.role not in ['superadmin', 'admin']:
            website = getattr(request.user, 'website', None)
            if website:
                queryset = queryset.filter(website=website)
        
        issues = []
        for page in queryset:
            page_issues = []
            
            # SEO issues
            if not page.meta_title:
                page_issues.append('missing_meta_title')
            elif len(page.meta_title) > 60:
                page_issues.append('meta_title_too_long')
            
            if not page.meta_description:
                page_issues.append('missing_meta_description')
            elif len(page.meta_description) > 160:
                page_issues.append('meta_description_too_long')
            
            # Content quality
            word_count = len(page.content.split())
            if word_count < min_word_count:
                page_issues.append('low_word_count')
            
            # Engagement
            from service_pages_management.models import ServicePageClick, ServicePageConversion
            click_count = ServicePageClick.objects.filter(service_page=page).count()
            conversion_count = ServicePageConversion.objects.filter(service_page=page).count()
            
            if click_count == 0 and page.is_published:
                page_issues.append('no_clicks')
            
            if only_issues and not page_issues:
                continue
            
            issues.append({
                'id': page.id,
                'title': page.title,
                'slug': page.slug,
                'website_id': page.website_id,
                'is_published': page.is_published,
                'publish_date': page.publish_date.isoformat() if page.publish_date else None,
                'click_count': click_count,
                'conversion_count': conversion_count,
                'word_count': word_count,
                'meta_title_length': len(page.meta_title) if page.meta_title else 0,
                'meta_description_length': len(page.meta_description) if page.meta_description else 0,
                'issues': page_issues,
                'issue_count': len(page_issues)
            })
        
        issues.sort(key=lambda x: x['issue_count'], reverse=True)
        
        return Response({
            'total': len(issues),
            'with_issues': sum(1 for i in issues if i['issue_count'] > 0),
            'issues': issues
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get summary of content health across all content."""
        try:
            website_id = request.query_params.get('website_id')
            
            blog_issues_response = self.blog_issues(request)
            service_issues_response = self.service_page_issues(request)
            
            blog_data = blog_issues_response.data if hasattr(blog_issues_response, 'data') else blog_issues_response
            service_data = service_issues_response.data if hasattr(service_issues_response, 'data') else service_issues_response
            
            return Response({
                'blog_audit': blog_data.get('issues', []),
                'service_page_audit': service_data.get('issues', []),
                'blogs': {
                    'total': blog_data.get('total', 0),
                    'with_issues': blog_data.get('with_issues', 0),
                    'issue_breakdown': {
                        'missing_meta_title': sum(1 for b in blog_data.get('issues', []) if 'missing_meta_title' in b.get('issues', [])),
                        'meta_title_too_long': sum(1 for b in blog_data.get('issues', []) if 'meta_title_too_long' in b.get('issues', [])),
                        'missing_meta_description': sum(1 for b in blog_data.get('issues', []) if 'missing_meta_description' in b.get('issues', [])),
                        'meta_description_too_long': sum(1 for b in blog_data.get('issues', []) if 'meta_description_too_long' in b.get('issues', [])),
                        'low_word_count': sum(1 for b in blog_data.get('issues', []) if 'low_word_count' in b.get('issues', [])),
                        'stale_content': sum(1 for b in blog_data.get('issues', []) if 'stale_content' in b.get('issues', [])),
                    }
                },
                'service_pages': {
                    'total': service_data.get('total', 0),
                    'with_issues': service_data.get('with_issues', 0),
                    'issue_breakdown': {
                        'missing_meta_title': sum(1 for s in service_data.get('issues', []) if 'missing_meta_title' in s.get('issues', [])),
                        'meta_title_too_long': sum(1 for s in service_data.get('issues', []) if 'meta_title_too_long' in s.get('issues', [])),
                        'missing_meta_description': sum(1 for s in service_data.get('issues', []) if 'missing_meta_description' in s.get('issues', [])),
                        'meta_description_too_long': sum(1 for s in service_data.get('issues', []) if 'meta_description_too_long' in s.get('issues', [])),
                        'low_word_count': sum(1 for s in service_data.get('issues', []) if 'low_word_count' in s.get('issues', [])),
                    }
                }
            }, status=status.HTTP_200_OK)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response(
                {'error': f'Error generating audit summary: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def audit_overview(self, request):
        """
        Get audit overview - alias for summary endpoint.
        Returns summary of content health across all content.
        """
        return self.summary(request)

