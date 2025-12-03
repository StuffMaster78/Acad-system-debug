"""
Password History Service
Manages password history to prevent reuse of recent passwords.
"""
import logging
from typing import Optional
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ValidationError
from django.db import transaction
from authentication.models.password_security import PasswordHistory
from websites.utils import get_current_website

logger = logging.getLogger(__name__)


class PasswordHistoryService:
    """
    Service for managing password history and preventing password reuse.
    """
    
    DEFAULT_HISTORY_DEPTH = 5  # Keep last 5 passwords
    
    def __init__(self, user, website=None):
        self.user = user
        self.website = website or get_current_website()
        if not self.website:
            from websites.models import Website
            self.website = Website.objects.filter(is_active=True).first()
    
    def save_password_to_history(self, password: str, history_depth: int = None):
        """
        Save current password to history before changing.
        
        Args:
            password: Plain text password to save
            history_depth: Number of passwords to keep (default: 5)
        """
        if not self.website:
            logger.warning(f"No website context for password history for user {self.user.id}")
            return
        
        history_depth = history_depth or self.DEFAULT_HISTORY_DEPTH
        
        with transaction.atomic():
            # Get current password hash from user
            current_password_hash = self.user.password
            
            # Save to history
            PasswordHistory.objects.create(
                user=self.user,
                website=self.website,
                password_hash=current_password_hash
            )
            
            # Clean up old history entries (keep only last N)
            old_entries = PasswordHistory.objects.filter(
                user=self.user,
                website=self.website
            ).order_by('-created_at')[history_depth:]
            
            for entry in old_entries:
                entry.delete()
    
    def is_password_in_history(self, password: str, check_last_n: int = None) -> bool:
        """
        Check if password exists in recent history.
        
        Args:
            password: Plain text password to check
            check_last_n: Number of recent passwords to check (default: 5)
        
        Returns:
            True if password is in history, False otherwise
        """
        if not self.website:
            return False
        
        check_last_n = check_last_n or self.DEFAULT_HISTORY_DEPTH
        
        # Get recent password history
        recent_passwords = PasswordHistory.objects.filter(
            user=self.user,
            website=self.website
        ).order_by('-created_at')[:check_last_n]
        
        # Check against each password in history
        for password_history in recent_passwords:
            if check_password(password, password_history.password_hash):
                return True
        
        return False
    
    def validate_password_not_in_history(self, password: str, check_last_n: int = None):
        """
        Validate that password is not in recent history.
        Raises ValidationError if password is found in history.
        
        Args:
            password: Plain text password to validate
            check_last_n: Number of recent passwords to check
        
        Raises:
            ValidationError: If password is in history
        """
        if self.is_password_in_history(password, check_last_n):
            raise ValidationError(
                "This password was recently used. Please choose a different password."
            )
    
    def get_history_count(self) -> int:
        """Get number of passwords in history."""
        if not self.website:
            return 0
        return PasswordHistory.objects.filter(
            user=self.user,
            website=self.website
        ).count()
    
    def clear_history(self):
        """Clear all password history for user."""
        if not self.website:
            return
        PasswordHistory.objects.filter(
            user=self.user,
            website=self.website
        ).delete()

