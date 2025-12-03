"""
IP Whitelist Service
Manages user-controlled IP whitelisting.
"""
import logging
from typing import List, Optional
from django.core.exceptions import ValidationError
from authentication.models.account_security import IPWhitelist, UserIPWhitelistSettings
from websites.utils import get_current_website

logger = logging.getLogger(__name__)


class IPWhitelistService:
    """
    Service for managing IP whitelist for users.
    """
    
    def __init__(self, user, website=None):
        self.user = user
        self.website = website or get_current_website()
        if not self.website:
            from websites.models import Website
            self.website = Website.objects.filter(is_active=True).first()
    
    def get_or_create_settings(self) -> UserIPWhitelistSettings:
        """Get or create IP whitelist settings for user."""
        if not self.website:
            raise ValueError("Website context required for IP whitelist")
        
        settings, created = UserIPWhitelistSettings.objects.get_or_create(
            user=self.user,
            website=self.website,
            defaults={
                'is_enabled': False,
                'allow_emergency_bypass': True,
            }
        )
        return settings
    
    def is_enabled(self) -> bool:
        """Check if IP whitelist is enabled for user."""
        settings = self.get_or_create_settings()
        return settings.is_enabled
    
    def is_ip_whitelisted(self, ip_address: str) -> bool:
        """
        Check if IP address is whitelisted.
        
        Args:
            ip_address: IP address to check
        
        Returns:
            True if whitelisted or whitelist not enabled, False otherwise
        """
        if not self.is_enabled():
            return True  # Whitelist not enabled, allow all
        
        if not self.website:
            return True
        
        return IPWhitelist.objects.filter(
            user=self.user,
            website=self.website,
            ip_address=ip_address,
            is_active=True
        ).exists()
    
    def add_ip(self, ip_address: str, label: str = "") -> IPWhitelist:
        """
        Add IP address to whitelist.
        
        Args:
            ip_address: IP address to whitelist
            label: Optional label for the IP
        
        Returns:
            Created IPWhitelist instance
        """
        if not self.website:
            raise ValueError("Website context required")
        
        whitelist_entry, created = IPWhitelist.objects.get_or_create(
            user=self.user,
            website=self.website,
            ip_address=ip_address,
            defaults={
                'label': label,
                'is_active': True,
            }
        )
        
        if not created:
            # Reactivate if it was deactivated
            whitelist_entry.is_active = True
            whitelist_entry.label = label or whitelist_entry.label
            whitelist_entry.save()
        
        return whitelist_entry
    
    def remove_ip(self, ip_address: str):
        """Remove IP address from whitelist."""
        if not self.website:
            return
        
        IPWhitelist.objects.filter(
            user=self.user,
            website=self.website,
            ip_address=ip_address
        ).update(is_active=False)
    
    def get_whitelisted_ips(self) -> List[IPWhitelist]:
        """Get all whitelisted IPs for user."""
        if not self.website:
            return []
        
        return list(IPWhitelist.objects.filter(
            user=self.user,
            website=self.website,
            is_active=True
        ).order_by('-created_at'))
    
    def enable_whitelist(self):
        """Enable IP whitelist for user."""
        settings = self.get_or_create_settings()
        settings.is_enabled = True
        settings.save(update_fields=['is_enabled'])
    
    def disable_whitelist(self):
        """Disable IP whitelist for user."""
        settings = self.get_or_create_settings()
        settings.is_enabled = False
        settings.save(update_fields=['is_enabled'])
    
    def update_last_used(self, ip_address: str):
        """Update last used timestamp for IP."""
        if not self.website:
            return
        
        from django.utils import timezone
        IPWhitelist.objects.filter(
            user=self.user,
            website=self.website,
            ip_address=ip_address
        ).update(last_used=timezone.now())
    
    def check_login_allowed(self, ip_address: str) -> dict:
        """
        Check if login is allowed from IP address.
        
        Args:
            ip_address: IP address attempting login
        
        Returns:
            Dict with allowed status and reason
        """
        if not self.is_enabled():
            return {'allowed': True, 'reason': 'whitelist_disabled'}
        
        if self.is_ip_whitelisted(ip_address):
            self.update_last_used(ip_address)
            return {'allowed': True, 'reason': 'ip_whitelisted'}
        
        # Check emergency bypass
        settings = self.get_or_create_settings()
        if settings.allow_emergency_bypass:
            return {
                'allowed': False,
                'reason': 'ip_not_whitelisted',
                'emergency_bypass_available': True,
                'message': 'Login from this IP is not allowed. Use emergency bypass via email verification.'
            }
        
        return {
            'allowed': False,
            'reason': 'ip_not_whitelisted',
            'emergency_bypass_available': False,
            'message': 'Login from this IP is not allowed. Please contact support.'
        }

