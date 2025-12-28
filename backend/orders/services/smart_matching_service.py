"""
Smart Matching Service

AI/ML-based writer-order matching using:
- Past performance on similar orders
- Writing style matching
- Subject expertise scoring
"""
from typing import List, Dict, Optional, Tuple
from decimal import Decimal
from django.db.models import Count, Avg, Q, F, FloatField
from django.db.models.functions import Coalesce
from django.core.exceptions import ValidationError
from django.utils import timezone

from orders.models import Order, OrderStatus
from writer_management.models.profile import WriterProfile
from writer_management.models.levels import WriterLevel


class SmartMatchingService:
    """
    Service for intelligent writer-order matching.
    """
    
    @staticmethod
    def find_best_matches(
        order: Order,
        max_results: int = 10,
        min_rating: float = 4.0,
    ) -> List[Dict]:
        """
        Find best matching writers for an order using multiple factors.
        
        Args:
            order: Order to match
            max_results: Maximum number of matches to return
            min_rating: Minimum writer rating
            
        Returns:
            List of matched writers with scores and reasons
        """
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Get base writer queryset
        # Filter writers with profiles that are available
        # Note: We'll calculate avg_rating in Python to avoid Django ORM field lookup issues
        writers = User.objects.filter(
            role='writer',
            is_active=True,
        ).filter(
            writer_profile__is_available_for_auto_assignments=True,
            writer_profile__is_deleted=False,
        ).annotate(
            active_orders=Count(
                'orders_as_writer',
                filter=Q(
                    orders_as_writer__status__in=[
                        OrderStatus.IN_PROGRESS.value,
                        OrderStatus.ON_HOLD.value,
                        OrderStatus.REVISION_REQUESTED.value,
                    ],
                    orders_as_writer__is_deleted=False,
                )
            ),
        ).select_related('writer_profile', 'writer_profile__writer_level')
        
        # Calculate average rating for each writer in Python
        # Ratings are stored in WriterRating model, not directly on Order
        writer_ids = list(writers.values_list('id', flat=True))
        if writer_ids:
            from django.db.models import Avg
            from writer_management.models.ratings import WriterRating
            
            # Get writer profiles for these users
            writer_profiles = WriterProfile.objects.filter(user_id__in=writer_ids).select_related('user')
            writer_profile_dict = {profile.user_id: profile.id for profile in writer_profiles}
            writer_profile_ids = list(writer_profile_dict.values())
            
            if writer_profile_ids:
                # Get average ratings from WriterRating model
                # Group by writer profile, then map back to user_id
                rating_data = WriterRating.objects.filter(
                    writer_id__in=writer_profile_ids
                ).values('writer_id').annotate(
                    avg_rating=Avg('rating')
                )
                
                # Create reverse mapping: profile_id -> user_id
                profile_to_user = {v: k for k, v in writer_profile_dict.items()}
                rating_dict = {
                    profile_to_user[item['writer_id']]: float(item['avg_rating'])
                    for item in rating_data
                    if item['writer_id'] in profile_to_user
                }
            else:
                rating_dict = {}
        else:
            rating_dict = {}
        
        # Add avg_rating as an attribute to each writer object
        for writer in writers:
            writer.avg_rating = rating_dict.get(writer.id, 0.0)
        
        # Filter by rating if specified
        if min_rating > 0:
            writers = [w for w in writers if w.avg_rating >= min_rating]
        
        # If no writers match rating filter, try without rating filter (but still prefer rated writers)
        if not writers and min_rating > 0:
            # Re-fetch without rating filter
            writers = User.objects.filter(
                role='writer',
                is_active=True,
            ).filter(
                writer_profile__is_available_for_auto_assignments=True,
                writer_profile__is_deleted=False,
            ).annotate(
                active_orders=Count(
                    'orders_as_writer',
                    filter=Q(
                        orders_as_writer__status__in=[
                            OrderStatus.IN_PROGRESS.value,
                            OrderStatus.ON_HOLD.value,
                            OrderStatus.REVISION_REQUESTED.value,
                        ],
                        orders_as_writer__is_deleted=False,
                    )
                ),
            ).select_related('writer_profile', 'writer_profile__writer_level')
            
            # Recalculate ratings
            writer_ids = list(writers.values_list('id', flat=True))
            if writer_ids:
                from django.db.models import Avg
                from writer_management.models.ratings import WriterRating
                
                # Get writer profiles for these users
                writer_profiles = WriterProfile.objects.filter(user_id__in=writer_ids).select_related('user')
                writer_profile_dict = {profile.user_id: profile.id for profile in writer_profiles}
                writer_profile_ids = list(writer_profile_dict.values())
                
                if writer_profile_ids:
                    # Get average ratings from WriterRating model
                    rating_data = WriterRating.objects.filter(
                        writer_id__in=writer_profile_ids
                    ).values('writer_id').annotate(
                        avg_rating=Avg('rating')
                    )
                    
                    # Create reverse mapping: profile_id -> user_id
                    profile_to_user = {v: k for k, v in writer_profile_dict.items()}
                    rating_dict = {
                        profile_to_user[item['writer_id']]: float(item['avg_rating'])
                        for item in rating_data
                        if item['writer_id'] in profile_to_user
                    }
                else:
                    rating_dict = {}
            else:
                rating_dict = {}
            
            for writer in writers:
                writer.avg_rating = rating_dict.get(writer.id, 0.0)
        
        # Convert to list if it's a queryset
        if hasattr(writers, '__iter__') and not isinstance(writers, (list, tuple)):
            writers = list(writers)
        
        # Score each writer
        matches = []
        for writer in writers[:50]:  # Limit initial candidates
            try:
                score, reasons = SmartMatchingService._calculate_match_score(order, writer)
                
                matches.append({
                    'writer': writer,
                    'writer_id': writer.id,
                    'writer_username': writer.username,
                    'score': score,
                    'reasons': reasons,
                    'rating': float(getattr(writer, 'avg_rating', 0) or 0),
                    'active_orders': getattr(writer, 'active_orders', 0) or 0,
                })
            except Exception as e:
                # Skip writers that cause errors during scoring
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Error scoring writer {writer.id} for order {order.id}: {str(e)}")
                continue
        
        # Sort by score (descending)
        matches.sort(key=lambda x: x['score'], reverse=True)
        
        return matches[:max_results]
    
    @staticmethod
    def _calculate_match_score(order: Order, writer) -> Tuple[float, Dict]:
        """
        Calculate match score for a writer-order pair.
        
        Returns:
            Tuple of (score, reasons_dict)
        """
        score = 0.0
        reasons = {}
        
        # 1. Subject Expertise (30% weight)
        subject_score = SmartMatchingService._calculate_subject_expertise(order, writer)
        score += subject_score * 0.30
        reasons['subject_expertise'] = round(subject_score, 2)
        
        # 2. Past Performance on Similar Orders (25% weight)
        performance_score = SmartMatchingService._calculate_past_performance(order, writer)
        score += performance_score * 0.25
        reasons['past_performance'] = round(performance_score, 2)
        
        # 3. Paper Type Experience (15% weight)
        paper_type_score = SmartMatchingService._calculate_paper_type_experience(order, writer)
        score += paper_type_score * 0.15
        reasons['paper_type_experience'] = round(paper_type_score, 2)
        
        # 4. Academic Level Match (10% weight)
        academic_score = SmartMatchingService._calculate_academic_level_match(order, writer)
        score += academic_score * 0.10
        reasons['academic_level'] = round(academic_score, 2)
        
        # 5. Rating (10% weight)
        rating = float(writer.avg_rating or 0)
        rating_score = min(rating / 5.0, 1.0)
        score += rating_score * 0.10
        reasons['rating'] = round(rating_score, 2)
        
        # 6. Workload Balance (10% weight)
        workload_score = SmartMatchingService._calculate_workload_balance(writer)
        score += workload_score * 0.10
        reasons['workload_balance'] = round(workload_score, 2)
        
        return score, reasons
    
    @staticmethod
    def _calculate_subject_expertise(order: Order, writer) -> float:
        """
        Calculate subject expertise score (0-1).
        
        Factors:
        - Number of completed orders in same subject
        - Success rate on subject orders
        - Portfolio specialties
        """
        if not order.subject:
            return 0.5  # Neutral if no subject
        
        # Count completed orders in same subject
        completed_in_subject = Order.objects.filter(
            assigned_writer=writer,
            subject=order.subject,
            status=OrderStatus.COMPLETED.value,
            is_deleted=False,
        ).count()
        
        # Count total completed orders
        total_completed = Order.objects.filter(
            assigned_writer=writer,
            status=OrderStatus.COMPLETED.value,
            is_deleted=False,
        ).count()
        
        # Calculate subject ratio
        if total_completed > 0:
            subject_ratio = completed_in_subject / total_completed
        else:
            subject_ratio = 0.0
        
        # Check portfolio specialties
        portfolio_match = False
        try:
            from writer_management.models.portfolio import WriterPortfolio
            if order.subject:
                portfolio_match = WriterPortfolio.objects.filter(
                    writer=writer,
                    is_enabled=True,
                    specialties=order.subject,
                ).exists()
        except (ImportError, AttributeError, Exception):
            # Portfolio model might not exist or have different structure
            pass
        
        # Score: subject ratio (70%) + portfolio match (30%)
        score = (subject_ratio * 0.7) + (1.0 if portfolio_match else 0.0) * 0.3
        
        # Normalize: 0 orders = 0.0, 5+ orders = 1.0
        if completed_in_subject > 0:
            experience_bonus = min(1.0, completed_in_subject / 5.0) * 0.2
            score = min(1.0, score + experience_bonus)
        
        return min(1.0, score)
    
    @staticmethod
    def _calculate_past_performance(order: Order, writer) -> float:
        """
        Calculate past performance score on similar orders (0-1).
        
        Similar orders = same subject + similar paper type + similar academic level
        """
        # Find similar orders
        similar_orders = Order.objects.filter(
            assigned_writer=writer,
            status=OrderStatus.COMPLETED.value,
            is_deleted=False,
        )
        
        # Filter by subject if available
        if order.subject:
            similar_orders = similar_orders.filter(subject=order.subject)
        
        # Filter by paper type if available
        if order.paper_type:
            similar_orders = similar_orders.filter(paper_type=order.paper_type)
        
        # Filter by academic level if available
        if order.academic_level:
            similar_orders = similar_orders.filter(academic_level=order.academic_level)
        
        similar_count = similar_orders.count()
        
        if similar_count == 0:
            return 0.3  # Low score if no similar orders
        
        # Calculate average rating on similar orders
        # Ratings are stored in WriterRating model, not on Order
        from writer_management.models.ratings import WriterRating
        
        similar_order_ids = list(similar_orders.values_list('id', flat=True))
        if similar_order_ids:
            avg_rating_result = WriterRating.objects.filter(
                order_id__in=similar_order_ids
            ).aggregate(avg=Avg('rating'))
            avg_rating = float(avg_rating_result['avg'] or 0.0)
        else:
            avg_rating = 0.0
        
        # Calculate on-time delivery rate
        # Check if orders were submitted on time (use submitted_at if available, otherwise check status transitions)
        from orders.models import OrderTransitionLog
        from django.utils import timezone
        
        on_time_count = 0
        for similar_order in similar_orders:
            # Check if order was submitted/completed before deadline
            if similar_order.submitted_at and similar_order.client_deadline:
                if similar_order.submitted_at <= similar_order.client_deadline:
                    on_time_count += 1
            elif similar_order.client_deadline:
                # Check latest status transition to completed/approved
                latest_transition = OrderTransitionLog.objects.filter(
                    order=similar_order,
                    new_status__in=[OrderStatus.COMPLETED.value, OrderStatus.APPROVED.value]
                ).order_by('-timestamp').first()
                
                if latest_transition and latest_transition.timestamp <= similar_order.client_deadline:
                    on_time_count += 1
        
        on_time_rate = on_time_count / similar_count if similar_count > 0 else 0.0
        
        # Score: rating (60%) + on-time rate (40%)
        rating_score = min(avg_rating / 5.0, 1.0)
        score = (rating_score * 0.6) + (on_time_rate * 0.4)
        
        # Bonus for more similar orders
        if similar_count >= 10:
            score = min(1.0, score + 0.1)
        elif similar_count >= 5:
            score = min(1.0, score + 0.05)
        
        return min(1.0, score)
    
    @staticmethod
    def _calculate_paper_type_experience(order: Order, writer) -> float:
        """Calculate paper type experience score (0-1)."""
        if not order.paper_type:
            return 0.5  # Neutral
        
        completed_count = Order.objects.filter(
            assigned_writer=writer,
            paper_type=order.paper_type,
            status=OrderStatus.COMPLETED.value,
            is_deleted=False,
        ).count()
        
        # Normalize: 0 orders = 0.0, 10+ orders = 1.0
        return min(1.0, completed_count / 10.0)
    
    @staticmethod
    def _calculate_academic_level_match(order: Order, writer) -> float:
        """Calculate academic level match score (0-1)."""
        if not order.academic_level:
            return 0.5  # Neutral
        
        completed_count = Order.objects.filter(
            assigned_writer=writer,
            academic_level=order.academic_level,
            status=OrderStatus.COMPLETED.value,
            is_deleted=False,
        ).count()
        
        # Normalize: 0 orders = 0.0, 5+ orders = 1.0
        return min(1.0, completed_count / 5.0)
    
    @staticmethod
    def _calculate_workload_balance(writer) -> float:
        """Calculate workload balance score (0-1)."""
        max_orders = 5  # Default
        try:
            if hasattr(writer, 'writer_profile') and writer.writer_profile:
                if hasattr(writer.writer_profile, 'writer_level') and writer.writer_profile.writer_level:
                    max_orders = getattr(writer.writer_profile.writer_level, 'max_orders', 5) or 5
        except (AttributeError, Exception):
            pass  # Use default if profile doesn't exist
        
        active = getattr(writer, 'active_orders', 0) or 0
        
        if max_orders > 0:
            ratio = 1.0 - (active / max_orders)
            return max(0.0, ratio)
        
        return 0.5  # Neutral if unknown
    
    @staticmethod
    def get_match_explanation(order: Order, writer) -> str:
        """
        Get human-readable explanation of why a writer matches an order.
        """
        score, reasons = SmartMatchingService._calculate_match_score(order, writer)
        
        explanations = []
        
        if reasons.get('subject_expertise', 0) > 0.7:
            explanations.append("Strong subject expertise")
        elif reasons.get('subject_expertise', 0) > 0.4:
            explanations.append("Moderate subject experience")
        
        if reasons.get('past_performance', 0) > 0.8:
            explanations.append("Excellent past performance on similar orders")
        elif reasons.get('past_performance', 0) > 0.6:
            explanations.append("Good track record with similar orders")
        
        if reasons.get('paper_type_experience', 0) > 0.7:
            explanations.append("Extensive experience with this paper type")
        
        if reasons.get('rating', 0) > 0.8:
            explanations.append("High writer rating")
        
        if reasons.get('workload_balance', 0) > 0.7:
            explanations.append("Good workload capacity")
        
        if not explanations:
            return "General match based on availability and rating"
        
        return "; ".join(explanations)

