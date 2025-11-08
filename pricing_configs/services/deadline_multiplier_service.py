"""
Service for managing deadline multiplier logic and calculations.
"""
from decimal import Decimal
from typing import Optional, List, Dict
from django.utils import timezone
from django.core.exceptions import ValidationError
from pricing_configs.models import DeadlineMultiplier
from websites.models import Website


class DeadlineMultiplierService:
    """
    Service class for deadline multiplier operations.
    Provides methods to get multipliers, validate deadlines, and manage deadline configurations.
    """

    @staticmethod
    def get_multiplier_for_hours(website: Website, hours: float) -> Decimal:
        """
        Get the appropriate multiplier for a given number of hours.
        
        Args:
            website: The website to get multipliers for
            hours: Number of hours until deadline (can be negative for past deadlines)
            
        Returns:
            Decimal: The multiplier to apply (defaults to 1.0 if no match found)
        """
        if hours < 0:
            # Past deadline - return maximum multiplier or a penalty multiplier
            # Get the smallest hours multiplier (most urgent) as penalty
            penalty_multiplier = DeadlineMultiplier.objects.filter(
                website=website
            ).order_by('hours').first()
            if penalty_multiplier:
                # Apply extra penalty for past deadline (e.g., 1.5x the most urgent multiplier)
                return Decimal(str(penalty_multiplier.multiplier)) * Decimal('1.5')
            return Decimal('2.0')  # Default penalty multiplier
        
        # Find the largest deadline multiplier that is <= hours_left
        # This means if you have 25 hours, and there are multipliers for 24h and 48h,
        # you get the 24h multiplier (more urgent)
        match = DeadlineMultiplier.objects.filter(
            website=website,
            hours__lte=hours
        ).order_by('-hours').first()
        
        return match.multiplier if match else Decimal('1.0')

    @staticmethod
    def get_multiplier_for_deadline(website: Website, deadline) -> Decimal:
        """
        Get the multiplier for a specific deadline datetime.
        
        Args:
            website: The website to get multipliers for
            deadline: The deadline datetime
            
        Returns:
            Decimal: The multiplier to apply
        """
        if not deadline:
            return Decimal('1.0')
        
        now = timezone.now()
        if deadline < now:
            # Past deadline
            hours = (now - deadline).total_seconds() / 3600
            return DeadlineMultiplierService.get_multiplier_for_hours(website, -hours)
        
        hours_left = (deadline - now).total_seconds() / 3600
        return DeadlineMultiplierService.get_multiplier_for_hours(website, hours_left)

    @staticmethod
    def get_available_options(website: Website) -> List[Dict]:
        """
        Get all available deadline multiplier options for a website.
        Useful for frontend display of deadline options.
        
        Args:
            website: The website to get options for
            
        Returns:
            List of dicts with label, hours, and multiplier
        """
        multipliers = DeadlineMultiplier.objects.filter(
            website=website
        ).order_by('hours')
        
        return [
            {
                'id': dm.id,
                'label': dm.label,
                'hours': dm.hours,
                'multiplier': float(dm.multiplier),
                'formatted_multiplier': f"{dm.multiplier}x"
            }
            for dm in multipliers
        ]

    @staticmethod
    def get_multiplier_info(website: Website, hours: float) -> Dict:
        """
        Get detailed information about the multiplier that would apply.
        
        Args:
            website: The website to get multipliers for
            hours: Number of hours until deadline
            
        Returns:
            Dict with multiplier, label, and hours info
        """
        multiplier = DeadlineMultiplierService.get_multiplier_for_hours(website, hours)
        
        if hours < 0:
            return {
                'multiplier': float(multiplier),
                'label': 'Past Deadline',
                'hours': hours,
                'is_past_deadline': True,
                'warning': 'Deadline has passed'
            }
        
        # Find the matching deadline multiplier
        match = DeadlineMultiplier.objects.filter(
            website=website,
            hours__lte=hours
        ).order_by('-hours').first()
        
        if match:
            return {
                'multiplier': float(multiplier),
                'label': match.label,
                'hours': match.hours,
                'hours_remaining': hours,
                'is_past_deadline': False
            }
        
        return {
            'multiplier': float(multiplier),
            'label': 'Standard',
            'hours': None,
            'hours_remaining': hours,
            'is_past_deadline': False
        }

    @staticmethod
    def validate_multiplier_config(website: Website, hours: int, multiplier: Decimal, exclude_id: Optional[int] = None) -> List[str]:
        """
        Validate a deadline multiplier configuration.
        
        Args:
            website: The website
            hours: Hours for the deadline
            multiplier: The multiplier value
            exclude_id: ID to exclude from duplicate check (for updates)
            
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        if hours <= 0:
            errors.append("Hours must be greater than 0")
        
        if multiplier < Decimal('0.1') or multiplier > Decimal('10.0'):
            errors.append("Multiplier must be between 0.1 and 10.0")
        
        # Check for duplicate hours
        existing = DeadlineMultiplier.objects.filter(
            website=website,
            hours=hours
        )
        if exclude_id:
            existing = existing.exclude(id=exclude_id)
        if existing.exists():
            errors.append(f"A deadline multiplier for {hours} hours already exists for this website")
        
        return errors

    @staticmethod
    def get_recommended_multipliers() -> List[Dict]:
        """
        Get recommended default deadline multiplier configurations.
        Useful for initial setup or suggestions.
        
        Returns:
            List of recommended configurations
        """
        return [
            {'label': '1 Hour', 'hours': 1, 'multiplier': Decimal('2.5')},
            {'label': '3 Hours', 'hours': 3, 'multiplier': Decimal('2.0')},
            {'label': '6 Hours', 'hours': 6, 'multiplier': Decimal('1.75')},
            {'label': '12 Hours', 'hours': 12, 'multiplier': Decimal('1.5')},
            {'label': '24 Hours', 'hours': 24, 'multiplier': Decimal('1.3')},
            {'label': '48 Hours', 'hours': 48, 'multiplier': Decimal('1.15')},
            {'label': '72 Hours', 'hours': 72, 'multiplier': Decimal('1.05')},
        ]

