"""
API views for website-level content metrics and SEO health.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone

from ..models.analytics_models import (
    WebsiteContentMetrics,
    WebsitePublishingTarget,
    CategoryPublishingTarget,
    ContentFreshnessReminder,
)
from ..serializers.metrics_serializers import (
    WebsiteContentMetricsSerializer,
    WebsitePublishingTargetSerializer,
    CategoryPublishingTargetSerializer,
    ContentFreshnessReminderSerializer,
)
from websites.models import Website


class WebsiteContentMetricsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Exposes aggregated content metrics per website, broken down by category/tag,
    plus basic SEO health checks (meta title/description length & presence).

    Endpoints:
    - GET /content/website-metrics/?website_id=...  → list snapshots for a website
    - GET /content/website-metrics/latest/?website_id=...  → latest snapshot only
    - POST /content/website-metrics/recalculate/ { website_id } → force recalculation
    """

    queryset = WebsiteContentMetrics.objects.all().select_related("website")
    serializer_class = WebsiteContentMetricsSerializer
    permission_classes = [IsAuthenticated]  # Changed from IsAdminUser to allow editors/admins

    def get_queryset(self):
        qs = super().get_queryset()
        website_id = self.request.query_params.get("website_id")
        if website_id:
            qs = qs.filter(website_id=website_id)
        return qs

    @action(detail=False, methods=["get"])
    def latest(self, request):
        """
        Return the latest metrics snapshot for a given website.
        """
        website_id = request.query_params.get("website_id")
        if not website_id:
            return Response(
                {"detail": "website_id query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            website = Website.objects.get(id=website_id)
        except Website.DoesNotExist:
            return Response(
                {"detail": "Website not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        snapshot = (
            WebsiteContentMetrics.objects.filter(website=website)
            .order_by("-calculated_at")
            .first()
        )
        if not snapshot:
            # Try to calculate metrics if none exist
            try:
                from ..models.analytics_models import WebsiteContentMetrics as MetricsModel
                snapshot = MetricsModel.calculate_for_website(website)
            except Exception as e:
                return Response(
                    {"detail": f"No metrics snapshot found for this website and calculation failed: {str(e)}"},
                    status=status.HTTP_404_NOT_FOUND,
                )

        serializer = self.get_serializer(
            snapshot, context={"seo_health_limit": request.query_params.get("seo_health_limit", 50)}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"])
    def recalculate(self, request):
        """
        Force recalculation of metrics for a website and return the new snapshot.
        """
        website_id = request.data.get("website_id")
        if not website_id:
            return Response(
                {"detail": "website_id is required in request body."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            website = Website.objects.get(id=website_id)
        except Website.DoesNotExist:
            return Response(
                {"detail": "Website not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        from ..models.analytics_models import WebsiteContentMetrics as MetricsModel

        snapshot = MetricsModel.calculate_for_website(website)

        serializer = self.get_serializer(
            snapshot, context={"seo_health_limit": request.data.get("seo_health_limit", 50)}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=["get"])
    def by_category(self, request):
        """
        Get metrics filtered by a specific category.
        Returns metrics for posts in that category.
        """
        website_id = request.query_params.get("website_id")
        category_name = request.query_params.get("category")
        
        if not website_id:
            return Response(
                {"detail": "website_id query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        if not category_name:
            return Response(
                {"detail": "category query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        try:
            website = Website.objects.get(id=website_id)
        except Website.DoesNotExist:
            return Response(
                {"detail": "Website not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        
        snapshot = (
            WebsiteContentMetrics.objects.filter(website=website)
            .order_by("-calculated_at")
            .first()
        )
        
        if not snapshot:
            return Response(
                {"detail": "No metrics snapshot found for this website."},
                status=status.HTTP_404_NOT_FOUND,
            )
        
        # Get category metrics
        category_data = snapshot.category_metrics.get(category_name)
        if not category_data:
            return Response(
                {
                    "category": category_name,
                    "message": "No metrics found for this category.",
                    "metrics": {}
                },
                status=status.HTTP_200_OK,
            )
        
        return Response({
            "category": category_name,
            "website_id": website.id,
            "website_name": website.name,
            "calculated_at": snapshot.calculated_at,
            "metrics": category_data
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=["get"])
    def by_tag(self, request):
        """
        Get metrics filtered by a specific tag.
        Returns metrics for posts with that tag.
        """
        website_id = request.query_params.get("website_id")
        tag_name = request.query_params.get("tag")
        
        if not website_id:
            return Response(
                {"detail": "website_id query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        if not tag_name:
            return Response(
                {"detail": "tag query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        try:
            website = Website.objects.get(id=website_id)
        except Website.DoesNotExist:
            return Response(
                {"detail": "Website not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        
        snapshot = (
            WebsiteContentMetrics.objects.filter(website=website)
            .order_by("-calculated_at")
            .first()
        )
        
        if not snapshot:
            return Response(
                {"detail": "No metrics snapshot found for this website."},
                status=status.HTTP_404_NOT_FOUND,
            )
        
        # Get tag metrics (try both slug and name)
        tag_data = snapshot.tag_metrics.get(tag_name) or snapshot.tag_metrics.get(tag_name.lower())
        if not tag_data:
            return Response(
                {
                    "tag": tag_name,
                    "message": "No metrics found for this tag.",
                    "metrics": {}
                },
                status=status.HTTP_200_OK,
            )
        
        return Response({
            "tag": tag_name,
            "website_id": website.id,
            "website_name": website.name,
            "calculated_at": snapshot.calculated_at,
            "metrics": tag_data
        }, status=status.HTTP_200_OK)


class WebsitePublishingTargetViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing monthly publishing targets per website.
    """
    queryset = WebsitePublishingTarget.objects.all()
    serializer_class = WebsitePublishingTargetSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['website']
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related('website', 'updated_by')
        website_id = self.request.query_params.get('website_id')
        if website_id:
            queryset = queryset.filter(website_id=website_id)
        return queryset
    
    @action(detail=False, methods=['get'])
    def get_or_create(self, request):
        """Get or create publishing target for a website."""
        website_id = request.query_params.get('website_id')
        if not website_id:
            return Response(
                {'error': 'website_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from websites.models import Website
            website = Website.objects.get(id=website_id)
        except Website.DoesNotExist:
            return Response(
                {'error': 'Website not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        target = WebsitePublishingTarget.get_or_create_for_website(website)
        serializer = self.get_serializer(target)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def monthly_stats(self, request):
        """Get monthly publishing stats for all websites."""
        from websites.models import Website
        
        websites = Website.objects.filter(is_active=True)
        stats = []
        
        for website in websites:
            target = WebsitePublishingTarget.get_or_create_for_website(website)
            month_stats = target.get_current_month_stats()
            stats.append({
                'website_id': website.id,
                'website_name': website.name,
                **month_stats
            })
        
        return Response(stats, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['patch'])
    def update_threshold(self, request, pk=None):
        """Update freshness threshold for a website."""
        target = self.get_object()
        threshold = request.data.get('freshness_threshold_months')
        
        if threshold is None:
            return Response(
                {'error': 'freshness_threshold_months is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not (1 <= threshold <= 12):
            return Response(
                {'error': 'Threshold must be between 1 and 12 months'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        target.freshness_threshold_months = threshold
        target.save()
        
        serializer = self.get_serializer(target)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def historical_trends(self, request):
        """
        Get historical publishing trends for a website.
        Returns monthly publishing data for the last 12 months.
        """
        website_id = request.query_params.get('website_id')
        months = int(request.query_params.get('months', 12))
        
        if not website_id:
            return Response(
                {'error': 'website_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            website = Website.objects.get(id=website_id)
        except Website.DoesNotExist:
            return Response(
                {'error': 'Website not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        from datetime import datetime, timedelta
        from collections import defaultdict
        
        target = WebsitePublishingTarget.get_or_create_for_website(website)
        target_value = target.monthly_target
        
        # Get historical data
        from ..models import BlogPost
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=months * 30)
        
        blog_posts = BlogPost.objects.filter(
            website=website,
            is_published=True,
            is_deleted=False,
            publish_date__date__gte=start_date
        ).values('publish_date')
        
        # Group by month
        monthly_data = defaultdict(lambda: {'published': 0, 'target': target_value})
        
        for post in blog_posts:
            if post['publish_date']:
                month_key = post['publish_date'].strftime('%Y-%m')
                monthly_data[month_key]['published'] += 1
        
        # Convert to list and sort
        result = [
            {
                'month': month,
                'published': data['published'],
                'target': data['target'],
                'percentage': (data['published'] / data['target'] * 100) if data['target'] > 0 else 0,
                'status': 'met' if data['published'] >= data['target'] else 'below'
            }
            for month, data in sorted(monthly_data.items())
        ]
        
        # Calculate averages
        if result:
            avg_published = sum(r['published'] for r in result) / len(result)
            months_met = sum(1 for r in result if r['status'] == 'met')
            success_rate = (months_met / len(result) * 100) if result else 0
        else:
            avg_published = 0
            months_met = 0
            success_rate = 0
        
        return Response({
            'website_id': website.id,
            'website_name': website.name,
            'target': target_value,
            'monthly_data': result,
            'summary': {
                'average_published': round(avg_published, 1),
                'months_met_target': months_met,
                'total_months': len(result),
                'success_rate': round(success_rate, 1)
            }
        }, status=status.HTTP_200_OK)


class CategoryPublishingTargetViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing per-category publishing targets.
    """
    queryset = CategoryPublishingTarget.objects.all()
    serializer_class = CategoryPublishingTargetSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['website', 'category', 'is_active']
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related('website', 'category')
        website_id = self.request.query_params.get('website_id')
        if website_id:
            queryset = queryset.filter(website_id=website_id)
        return queryset
    
    @action(detail=False, methods=['get'])
    def by_website(self, request):
        """Get all category targets for a website."""
        website_id = request.query_params.get('website_id')
        if not website_id:
            return Response(
                {'error': 'website_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        targets = CategoryPublishingTarget.objects.filter(
            website_id=website_id,
            is_active=True
        ).select_related('category')
        
        serializer = self.get_serializer(targets, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ContentFreshnessReminderViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for content freshness reminders.
    """
    queryset = ContentFreshnessReminder.objects.all()
    serializer_class = ContentFreshnessReminderSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_acknowledged', 'blog_post__website']
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related(
            'blog_post', 'blog_post__website', 'acknowledged_by'
        )
        website_id = self.request.query_params.get('website_id')
        if website_id:
            queryset = queryset.filter(blog_post__website_id=website_id)
        return queryset.order_by('-blog_post__updated_at')
    
    @action(detail=False, methods=['get'])
    def stale_content(self, request):
        """Get all stale content (not updated in 3+ months)."""
        months = int(request.query_params.get('months', 3))
        stale_posts = ContentFreshnessReminder.get_stale_content(months_threshold=months)
        
        from ..serializers import BlogPostSerializer
        serializer = BlogPostSerializer(stale_posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def acknowledge(self, request, pk=None):
        """Acknowledge a freshness reminder."""
        reminder = self.get_object()
        reminder.is_acknowledged = True
        reminder.acknowledged_at = timezone.now()
        reminder.acknowledged_by = request.user
        reminder.save()
        
        serializer = self.get_serializer(reminder)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'])
    def refresh_reminders(self, request):
        """Refresh/create freshness reminders for stale content."""
        months = int(request.data.get('months', 3))
        reminders = ContentFreshnessReminder.create_or_update_reminders(months_threshold=months)
        
        serializer = self.get_serializer(reminders, many=True)
        return Response({
            'count': len(reminders),
            'reminders': serializer.data
        }, status=status.HTTP_200_OK)


class ContentCalendarViewSet(viewsets.ViewSet):
    """
    API endpoint for content calendar showing blog posts and service pages by publish date.
    """
    permission_classes = [IsAdminUser]
    
    @action(detail=False, methods=['get'])
    def calendar_data(self, request):
        """
        Get content calendar data for a website.
        Returns blog posts and service pages grouped by publish date.
        """
        website_id = request.query_params.get('website_id')
        start_date = request.query_params.get('start_date')  # YYYY-MM-DD
        end_date = request.query_params.get('end_date')  # YYYY-MM-DD
        
        if not website_id:
            return Response(
                {'error': 'website_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            website = Website.objects.get(id=website_id)
        except Website.DoesNotExist:
            return Response(
                {'error': 'Website not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        from datetime import datetime, timedelta
        from django.utils.dateparse import parse_date
        
        # Parse dates or use defaults
        if start_date:
            start = parse_date(start_date)
        else:
            start = timezone.now().date() - timedelta(days=90)  # Last 3 months
        
        if end_date:
            end = parse_date(end_date)
        else:
            end = timezone.now().date() + timedelta(days=30)  # Next month
        
        # Get blog posts
        from ..models import BlogPost
        blog_posts = BlogPost.objects.filter(
            website=website,
            is_published=True,
            is_deleted=False,
            publish_date__date__gte=start,
            publish_date__date__lte=end
        ).select_related('category', 'website').prefetch_related('tags', 'authors').order_by('publish_date')
        
        # Get service pages
        from service_pages_management.models import ServicePage
        service_pages = ServicePage.objects.filter(
            website=website,
            is_published=True,
            is_deleted=False,
            publish_date__date__gte=start,
            publish_date__date__lte=end
        ).select_related('website').order_by('publish_date')
        
        # Group by date
        calendar_data = {}
        
        for post in blog_posts:
            date_key = post.publish_date.date().isoformat() if post.publish_date else None
            if not date_key:
                continue
            
            if date_key not in calendar_data:
                calendar_data[date_key] = {
                    'date': date_key,
                    'blog_posts': [],
                    'service_pages': [],
                    'total_count': 0
                }
            
            calendar_data[date_key]['blog_posts'].append({
                'id': post.id,
                'title': post.title,
                'slug': post.slug,
                'category': post.category.name if post.category else None,
                'authors': [{'id': a.id, 'name': a.name or a.username} for a in post.authors.all()],
                'publish_date': post.publish_date.isoformat() if post.publish_date else None,
                'url': f"/blog/{post.slug}/",
                'type': 'blog_post'
            })
            calendar_data[date_key]['total_count'] += 1
        
        for page in service_pages:
            date_key = page.publish_date.date().isoformat() if page.publish_date else None
            if not date_key:
                continue
            
            if date_key not in calendar_data:
                calendar_data[date_key] = {
                    'date': date_key,
                    'blog_posts': [],
                    'service_pages': [],
                    'total_count': 0
                }
            
            calendar_data[date_key]['service_pages'].append({
                'id': page.id,
                'title': page.title,
                'slug': page.slug,
                'header': page.header,
                'publish_date': page.publish_date.isoformat() if page.publish_date else None,
                'url': f"/page/{page.slug}/",
                'type': 'service_page'
            })
            calendar_data[date_key]['total_count'] += 1
        
        # Convert to list and sort by date
        result = sorted(calendar_data.values(), key=lambda x: x['date'])
        
        return Response({
            'website_id': website.id,
            'website_name': website.name,
            'start_date': start.isoformat(),
            'end_date': end.isoformat(),
            'calendar': result,
            'total_blog_posts': sum(len(day['blog_posts']) for day in result),
            'total_service_pages': sum(len(day['service_pages']) for day in result),
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def monthly_summary(self, request):
        """
        Get monthly summary of content published.
        Returns count of blog posts and service pages per month.
        """
        website_id = request.query_params.get('website_id')
        months = int(request.query_params.get('months', 12))  # Default to 12 months
        
        if not website_id:
            return Response(
                {'error': 'website_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            website = Website.objects.get(id=website_id)
        except Website.DoesNotExist:
            return Response(
                {'error': 'Website not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        from datetime import datetime, timedelta
        from collections import defaultdict
        
        start_date = timezone.now().date() - timedelta(days=months * 30)
        
        # Get blog posts
        from ..models import BlogPost
        blog_posts = BlogPost.objects.filter(
            website=website,
            is_published=True,
            is_deleted=False,
            publish_date__date__gte=start_date
        ).values_list('publish_date', flat=True)
        
        # Get service pages
        from service_pages_management.models import ServicePage
        service_pages = ServicePage.objects.filter(
            website=website,
            is_published=True,
            is_deleted=False,
            publish_date__date__gte=start_date
        ).values_list('publish_date', flat=True)
        
        # Group by month
        monthly_data = defaultdict(lambda: {'blog_posts': 0, 'service_pages': 0, 'total': 0})
        
        for publish_date in blog_posts:
            if publish_date:
                month_key = publish_date.strftime('%Y-%m')
                monthly_data[month_key]['blog_posts'] += 1
                monthly_data[month_key]['total'] += 1
        
        for publish_date in service_pages:
            if publish_date:
                month_key = publish_date.strftime('%Y-%m')
                monthly_data[month_key]['service_pages'] += 1
                monthly_data[month_key]['total'] += 1
        
        # Convert to list and sort
        result = [
            {
                'month': month,
                'blog_posts': data['blog_posts'],
                'service_pages': data['service_pages'],
                'total': data['total']
            }
            for month, data in sorted(monthly_data.items())
        ]
        
        return Response({
            'website_id': website.id,
            'website_name': website.name,
            'monthly_summary': result
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'])
    def bulk_reschedule(self, request):
        """
        Bulk reschedule content (blog posts or service pages).
        Expects: { content_items: [{id, type: 'blog_post'|'service_page', new_date: 'YYYY-MM-DD'}], ... }
        """
        content_items = request.data.get('content_items', [])
        
        if not content_items:
            return Response(
                {'error': 'content_items is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        results = {'success': [], 'failed': []}
        
        for item in content_items:
            try:
                content_id = item.get('id')
                content_type = item.get('type')
                new_date_str = item.get('new_date')
                
                if not all([content_id, content_type, new_date_str]):
                    results['failed'].append({
                        'id': content_id,
                        'error': 'Missing required fields'
                    })
                    continue
                
                from datetime import datetime
                new_date = datetime.strptime(new_date_str, '%Y-%m-%d').date()
                new_datetime = timezone.make_aware(
                    datetime.combine(new_date, datetime.min.time())
                )
                
                if content_type == 'blog_post':
                    from ..models import BlogPost
                    content = BlogPost.objects.get(id=content_id)
                    content.publish_date = new_datetime
                    content.save()
                elif content_type == 'service_page':
                    from service_pages_management.models import ServicePage
                    content = ServicePage.objects.get(id=content_id)
                    content.publish_date = new_datetime
                    content.save()
                else:
                    results['failed'].append({
                        'id': content_id,
                        'error': f'Invalid content type: {content_type}'
                    })
                    continue
                
                results['success'].append({
                    'id': content_id,
                    'type': content_type,
                    'new_date': new_date_str
                })
            except Exception as e:
                results['failed'].append({
                    'id': item.get('id'),
                    'error': str(e)
                })
        
        return Response(results, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def export_ical(self, request):
        """
        Export content calendar as iCal format.
        """
        website_id = request.query_params.get('website_id')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not website_id:
            return Response(
                {'error': 'website_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            website = Website.objects.get(id=website_id)
        except Website.DoesNotExist:
            return Response(
                {'error': 'Website not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        from datetime import datetime, timedelta
        from django.utils.dateparse import parse_date
        
        if start_date:
            start = parse_date(start_date)
        else:
            start = timezone.now().date() - timedelta(days=90)
        
        if end_date:
            end = parse_date(end_date)
        else:
            end = timezone.now().date() + timedelta(days=365)
        
        # Get blog posts
        from ..models import BlogPost
        blog_posts = BlogPost.objects.filter(
            website=website,
            is_published=True,
            is_deleted=False,
            publish_date__date__gte=start,
            publish_date__date__lte=end
        ).select_related('category').order_by('publish_date')
        
        # Get service pages
        from service_pages_management.models import ServicePage
        service_pages = ServicePage.objects.filter(
            website=website,
            is_published=True,
            is_deleted=False,
            publish_date__date__gte=start,
            publish_date__date__lte=end
        ).order_by('publish_date')
        
        # Generate iCal content
        ical_lines = [
            'BEGIN:VCALENDAR',
            'VERSION:2.0',
            'PRODID:-//Content Management System//Content Calendar//EN',
            'CALSCALE:GREGORIAN',
            'METHOD:PUBLISH',
        ]
        
        for post in blog_posts:
            if not post.publish_date:
                continue
            dt_start = post.publish_date.strftime('%Y%m%dT%H%M%S')
            dt_stamp = timezone.now().strftime('%Y%m%dT%H%M%S')
            summary = post.title.replace(',', '\\,').replace(';', '\\;')
            url = f"https://{website.domain}/blog/{post.slug}/" if website.domain else f"/blog/{post.slug}/"
            
            ical_lines.extend([
                'BEGIN:VEVENT',
                f'UID:blog-{post.id}@content-calendar',
                f'DTSTART:{dt_start}',
                f'DTSTAMP:{dt_stamp}',
                f'SUMMARY:{summary}',
                f'DESCRIPTION:Blog Post - {post.category.name if post.category else "Uncategorized"}',
                f'URL:{url}',
                'END:VEVENT',
            ])
        
        for page in service_pages:
            if not page.publish_date:
                continue
            dt_start = page.publish_date.strftime('%Y%m%dT%H%M%S')
            dt_stamp = timezone.now().strftime('%Y%m%dT%H%M%S')
            summary = page.title.replace(',', '\\,').replace(';', '\\;')
            url = f"https://{website.domain}/page/{page.slug}/" if website.domain else f"/page/{page.slug}/"
            
            ical_lines.extend([
                'BEGIN:VEVENT',
                f'UID:page-{page.id}@content-calendar',
                f'DTSTART:{dt_start}',
                f'DTSTAMP:{dt_stamp}',
                f'SUMMARY:{summary}',
                f'DESCRIPTION:Service Page',
                f'URL:{url}',
                'END:VEVENT',
            ])
        
        ical_lines.append('END:VCALENDAR')
        ical_content = '\r\n'.join(ical_lines)
        
        from django.http import HttpResponse
        response = HttpResponse(ical_content, content_type='text/calendar')
        response['Content-Disposition'] = f'attachment; filename="content-calendar-{website.slug}.ics"'
        return response


