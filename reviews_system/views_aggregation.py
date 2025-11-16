from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Avg, Q

from reviews_system.models import WebsiteReview, WriterReview, OrderReview


class ReviewAggregationViewSet(viewsets.ViewSet):
    """API for review aggregation, display rules, and moderation queue."""
    permission_classes = [IsAdminUser]

    @action(detail=False, methods=['get'], url_path='stats')
    def get_stats(self, request):
        """Get aggregated review statistics."""
        review_type = request.query_params.get('type', 'all')
        
        stats = {}
        
        if review_type in ['all', 'website']:
            website_stats = WebsiteReview.objects.aggregate(
                total=Count('id'),
                approved=Count('id', filter=Q(is_approved=True)),
                pending=Count('id', filter=Q(is_approved=False, is_shadowed=False)),
                flagged=Count('id', filter=Q(is_flagged=True)),
                shadowed=Count('id', filter=Q(is_shadowed=True)),
                avg_rating=Avg('rating', filter=Q(is_approved=True)),
            )
            stats['website'] = website_stats
        
        if review_type in ['all', 'writer']:
            writer_stats = WriterReview.objects.aggregate(
                total=Count('id'),
                approved=Count('id', filter=Q(is_approved=True)),
                pending=Count('id', filter=Q(is_approved=False, is_shadowed=False)),
                flagged=Count('id', filter=Q(is_flagged=True)),
                shadowed=Count('id', filter=Q(is_shadowed=True)),
                avg_rating=Avg('rating', filter=Q(is_approved=True)),
            )
            stats['writer'] = writer_stats
        
        if review_type in ['all', 'order']:
            order_stats = OrderReview.objects.aggregate(
                total=Count('id'),
                approved=Count('id', filter=Q(is_approved=True)),
                pending=Count('id', filter=Q(is_approved=False, is_shadowed=False)),
                flagged=Count('id', filter=Q(is_flagged=True)),
                shadowed=Count('id', filter=Q(is_shadowed=True)),
                avg_rating=Avg('rating', filter=Q(is_approved=True)),
            )
            stats['order'] = order_stats
        
        return Response(stats)
    
    @action(detail=False, methods=['get'], url_path='queue')
    def get_queue(self, request):
        """Get review moderation queue."""
        status_filter = request.query_params.get('status', 'pending')
        review_type = request.query_params.get('type', 'all')
        
        queue = []
        
        if review_type in ['all', 'website']:
            website_qs = WebsiteReview.objects.all()
            if status_filter == 'pending':
                website_qs = website_qs.filter(is_approved=False, is_shadowed=False)
            elif status_filter == 'flagged':
                website_qs = website_qs.filter(is_flagged=True)
            elif status_filter == 'shadowed':
                website_qs = website_qs.filter(is_shadowed=True)
            
            for review in website_qs[:50]:
                queue.append({
                    'id': review.id,
                    'type': 'website',
                    'reviewer': review.reviewer.username,
                    'rating': review.rating,
                    'comment': review.comment[:100] if review.comment else '',
                    'status': 'approved' if review.is_approved else ('shadowed' if review.is_shadowed else ('flagged' if review.is_flagged else 'pending')),
                    'submitted_at': review.submitted_at.isoformat() if review.submitted_at else None,
                })
        
        if review_type in ['all', 'writer']:
            writer_qs = WriterReview.objects.all()
            if status_filter == 'pending':
                writer_qs = writer_qs.filter(is_approved=False, is_shadowed=False)
            elif status_filter == 'flagged':
                writer_qs = writer_qs.filter(is_flagged=True)
            elif status_filter == 'shadowed':
                writer_qs = writer_qs.filter(is_shadowed=True)
            
            for review in writer_qs[:50]:
                queue.append({
                    'id': review.id,
                    'type': 'writer',
                    'reviewer': review.reviewer.username,
                    'rating': review.rating,
                    'comment': review.comment[:100] if review.comment else '',
                    'status': 'approved' if review.is_approved else ('shadowed' if review.is_shadowed else ('flagged' if review.is_flagged else 'pending')),
                    'submitted_at': review.submitted_at.isoformat() if review.submitted_at else None,
                })
        
        if review_type in ['all', 'order']:
            order_qs = OrderReview.objects.all()
            if status_filter == 'pending':
                order_qs = order_qs.filter(is_approved=False, is_shadowed=False)
            elif status_filter == 'flagged':
                order_qs = order_qs.filter(is_flagged=True)
            elif status_filter == 'shadowed':
                order_qs = order_qs.filter(is_shadowed=True)
            
            for review in order_qs[:50]:
                queue.append({
                    'id': review.id,
                    'type': 'order',
                    'reviewer': review.reviewer.username,
                    'rating': review.rating,
                    'comment': review.comment[:100] if review.comment else '',
                    'status': 'approved' if review.is_approved else ('shadowed' if review.is_shadowed else ('flagged' if review.is_flagged else 'pending')),
                    'submitted_at': review.submitted_at.isoformat() if review.submitted_at else None,
                })
        
        # Sort by submitted_at descending
        queue.sort(key=lambda x: x['submitted_at'] or '', reverse=True)
        
        return Response(queue[:100])  # Return top 100

