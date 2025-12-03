"""
Privacy Service
Manages privacy settings for writers and clients.
"""
import logging
from typing import Optional, Dict, Any
from users.models.privacy_settings import (
    WriterPrivacySettings, ClientPrivacySettings, PenName
)
from websites.utils import get_current_website

logger = logging.getLogger(__name__)


class PrivacyService:
    """
    Service for managing privacy settings.
    """
    
    def __init__(self, user, website=None):
        self.user = user
        self.website = website or get_current_website()
        if not self.website:
            from websites.models import Website
            self.website = Website.objects.filter(is_active=True).first()
    
    def get_writer_privacy_settings(self) -> WriterPrivacySettings:
        """Get or create writer privacy settings."""
        if not self.website:
            raise ValueError("Website context required")
        
        settings, created = WriterPrivacySettings.objects.get_or_create(
            user=self.user,
            website=self.website,
            defaults={
                'show_writer_id': True,
                'show_pen_name': True,
                'show_completed_orders_count': True,
                'show_rating': True,
                'show_workload': True,
                'show_bio': False,  # Default: hidden until approved
                'show_avatar': True,
            }
        )
        return settings
    
    def get_client_privacy_settings(self) -> ClientPrivacySettings:
        """Get or create client privacy settings."""
        if not self.website:
            raise ValueError("Website context required")
        
        settings, created = ClientPrivacySettings.objects.get_or_create(
            user=self.user,
            website=self.website,
            defaults={
                'show_client_id': True,
                'show_pen_name': True,
                'show_real_name': False,
                'show_email': False,
                'show_avatar': True,
            }
        )
        return settings
    
    def get_writer_display_info(self, writer_user, viewer_user) -> Dict[str, Any]:
        """
        Get what a viewer (client) can see about a writer.
        
        Args:
            writer_user: Writer user object
            viewer_user: User viewing (client)
        
        Returns:
            Dict with displayable information
        """
        if not self.website:
            return {}
        
        privacy = self.get_writer_privacy_settings()
        
        info = {}
        
        # Writer ID
        if privacy.show_writer_id:
            info['writer_id'] = writer_user.id
        
        # Pen name
        if privacy.show_pen_name:
            pen_name = PenName.objects.filter(
                user=writer_user,
                website=self.website,
                is_active=True
            ).first()
            if pen_name:
                info['pen_name'] = pen_name.pen_name
        
        # Completed orders count
        if privacy.show_completed_orders_count:
            from orders.models import Order
            info['completed_orders_count'] = Order.objects.filter(
                assigned_writer=writer_user,
                status='completed',
                website=self.website
            ).count()
        
        # Rating
        if privacy.show_rating:
            # Calculate rating from reviews/feedback
            # Placeholder - implement based on your rating system
            info['rating'] = getattr(writer_user, 'rating', 0.0)
        
        # Workload
        if privacy.show_workload:
            from orders.models import Order
            info['current_workload'] = Order.objects.filter(
                assigned_writer=writer_user,
                status__in=['in_progress', 'pending'],
                website=self.website
            ).count()
        
        # Bio (only if approved)
        if privacy.show_bio and privacy.bio_approved:
            profile = getattr(writer_user, 'user_main_profile', None)
            if profile:
                info['bio'] = profile.bio
        
        # Avatar (only if approved)
        if privacy.show_avatar:
            profile = getattr(writer_user, 'user_main_profile', None)
            if profile and profile.profile_picture:
                info['avatar'] = profile.profile_picture.url
        
        return info
    
    def get_client_display_info(self, client_user, viewer_user) -> Dict[str, Any]:
        """
        Get what a viewer (writer) can see about a client.
        
        Args:
            client_user: Client user object
            viewer_user: User viewing (writer)
        
        Returns:
            Dict with displayable information
        """
        if not self.website:
            return {}
        
        privacy = self.get_client_privacy_settings()
        
        info = {}
        
        # Client ID
        if privacy.show_client_id:
            info['client_id'] = client_user.id
        
        # Pen name
        if privacy.show_pen_name:
            pen_name = PenName.objects.filter(
                user=client_user,
                website=self.website,
                is_active=True
            ).first()
            if pen_name:
                info['pen_name'] = pen_name.pen_name
        
        # Real name (admin-controlled)
        if privacy.show_real_name:
            info['real_name'] = client_user.get_full_name()
        
        # Email (admin-controlled)
        if privacy.show_email:
            info['email'] = client_user.email
        
        # Avatar
        if privacy.show_avatar:
            profile = getattr(client_user, 'user_main_profile', None)
            if profile and profile.profile_picture:
                info['avatar'] = profile.profile_picture.url
        
        return info
    
    def set_pen_name(self, pen_name: str, requires_approval: bool = True) -> PenName:
        """
        Set pen name for user.
        
        Args:
            pen_name: Pen name to set
            requires_approval: Whether approval is needed (for writers)
        
        Returns:
            Created PenName instance
        """
        if not self.website:
            raise ValueError("Website context required")
        
        # Deactivate old pen name
        PenName.objects.filter(
            user=self.user,
            website=self.website,
            is_active=True
        ).update(is_active=False)
        
        # Create new pen name
        pen_name_obj, created = PenName.objects.get_or_create(
            user=self.user,
            website=self.website,
            pen_name=pen_name,
            defaults={
                'is_active': True,
                'is_approved': not requires_approval or self.user.role != 'writer'
            }
        )
        
        if not created:
            pen_name_obj.is_active = True
            pen_name_obj.is_approved = not requires_approval or self.user.role != 'writer'
            pen_name_obj.save()
        
        return pen_name_obj

