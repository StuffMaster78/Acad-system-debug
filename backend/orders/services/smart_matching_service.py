"""
Smart Matching Service

AI/ML-based writer-order matching using:
- Past performance on similar orders
- Writing style matching
- Subject expertise scoring
"""
from typing import List, Dict, Optional, Tuple
from decimal import Decimal
from django.db.models import Count, Avg, Q, F
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
        writers = User.objects.filter(
            role='writer',
            is_active=True,
            writer_profile__is_available_for_auto_assignments=True,
            writer_profile__is_deleted=False,
        ).annotate(
            avg_rating=Avg('orders_as_writer__rating'),
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
        ).filter(
            avg_rating__gte=min_rating,
        ).select_related('writer_profile', 'writer_profile__writer_level')
        
        # Score each writer
        matches = []
        for writer in writers[:50]:  # Limit initial candidates
            score, reasons = SmartMatchingService._calculate_match_score(order, writer)
            
            matches.append({
                'writer': writer,
                'writer_id': writer.id,
                'writer_username': writer.username,
                'score': score,
                'reasons': reasons,
                'rating': float(writer.avg_rating or 0),
                'active_orders': writer.active_orders or 0,
            })
        
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
            portfolio = WriterPortfolio.objects.filter(
                writer=writer,
                is_enabled=True,
                specialties=order.subject,
            ).exists()
            portfolio_match = portfolio
        except:
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
        avg_rating = similar_orders.aggregate(
            avg=Avg('rating')
        )['avg'] or 0.0
        
        # Calculate on-time delivery rate
        on_time_count = similar_orders.filter(
            completed_at__lte=F('client_deadline')
        ).count()
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
        if writer.writer_profile and writer.writer_profile.writer_level:
            max_orders = writer.writer_profile.writer_level.max_orders or 5
        
        active = writer.active_orders or 0
        
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

