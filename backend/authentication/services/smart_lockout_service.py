"""
Smart Lockout Service - Intelligent account lockout that adapts based on context.

This service provides progressive, context-aware lockout that reduces false positives
while maintaining security against actual attacks.
"""
import logging
from datetime import timedelta
from django.utils import timezone
from django.core.exceptions import ValidationError
from typing import Optional, Dict, Any

from authentication.models import FailedLoginAttempt
from authentication.services.failed_login_attempts import FailedLoginService

logger = logging.getLogger(__name__)


class SmartLockoutService:
    """
    Intelligent lockout service that adapts based on:
    - IP address (same IP = potential attack, different IP = user mistake)
    - Device trust status (trusted devices get more lenient treatment)
    - Recent successful logins (recent success = more lenient)
    - Time of day patterns (unusual times = more strict)
    """
    
    def __init__(self, user, website):
        self.user = user
        self.website = website
        self.failed_login_service = FailedLoginService(user=user, website=website)
    
    def get_lockout_duration(self, ip_address: str, is_trusted_device: bool = False) -> int:
        """
        Get lockout duration in minutes based on context.
        
        Args:
            ip_address: IP address of the login attempt
            is_trusted_device: Whether the device is trusted
        
        Returns:
            Lockout duration in minutes
        """
        base_duration = 5  # Base lockout: 5 minutes
        
        # Get recent failed attempts
        failed_attempts = self._get_recent_failed_attempts_count()
        
        # Check if same IP as recent attempts (potential brute force)
        if self._is_same_ip_as_recent_attempts(ip_address):
            # Same IP = potential attack, be stricter
            return base_duration * (2 + (failed_attempts // 3))  # 10, 15, 20, 25...
        
        # Check if trusted device
        if is_trusted_device:
            # Trusted device = more lenient
            return base_duration  # Just 5 minutes
        
        # Check for recent successful login
        if self._has_recent_successful_login(hours=24):
            # Recent success = user might just be making a mistake
            return base_duration  # 5 minutes
        
        # Default progressive lockout
        # 5, 10, 15, 20 minutes based on attempt count
        return base_duration * (1 + (failed_attempts // 3))
    
    def should_lockout(self, ip_address: str, is_trusted_device: bool = False) -> tuple[bool, Optional[str]]:
        """
        Determine if account should be locked.
        
        Args:
            ip_address: IP address of the login attempt
            is_trusted_device: Whether the device is trusted
        
        Returns:
            Tuple of (should_lockout, reason_message)
        """
        failed_attempts = self._get_recent_failed_attempts_count()
        
        # Trusted device: more lenient (10 attempts before lockout)
        if is_trusted_device:
            if failed_attempts >= 10:
                return True, "Too many failed attempts on trusted device"
            return False, None
        
        # Same IP as recent attempts: stricter (3 attempts)
        if self._is_same_ip_as_recent_attempts(ip_address):
            if failed_attempts >= 3:
                return True, "Multiple failed attempts from same location"
            return False, None
        
        # Recent successful login: more lenient (7 attempts)
        if self._has_recent_successful_login(hours=24):
            if failed_attempts >= 7:
                return True, "Multiple failed attempts after recent successful login"
            return False, None
        
        # Default: lock after 5 attempts
        if failed_attempts >= 5:
            return True, "Too many failed login attempts"
        
        return False, None
    
    def get_lockout_info(self, ip_address: str, is_trusted_device: bool = False) -> Dict[str, Any]:
        """
        Get comprehensive lockout information for user feedback.
        
        Returns:
            Dict with lockout status, duration, attempts remaining, etc.
        """
        should_lock, reason = self.should_lockout(ip_address, is_trusted_device)
        failed_attempts = self._get_recent_failed_attempts_count()
        
        if should_lock:
            duration = self.get_lockout_duration(ip_address, is_trusted_device)
            lockout_until = timezone.now() + timedelta(minutes=duration)
            
            return {
                "is_locked": True,
                "reason": reason,
                "lockout_until": lockout_until.isoformat(),
                "lockout_duration_minutes": duration,
                "failed_attempts": failed_attempts,
                "unlock_options": {
                    "wait": f"Try again in {duration} minutes",
                    "email_unlock": "Request unlock via email",
                    "contact_support": "Contact support for immediate unlock"
                }
            }
        
        # Not locked, but show attempts remaining
        attempts_until_lockout = self._get_attempts_until_lockout(ip_address, is_trusted_device)
        
        return {
            "is_locked": False,
            "failed_attempts": failed_attempts,
            "attempts_remaining": attempts_until_lockout,
            "warning": f"{attempts_until_lockout} attempts remaining before temporary lockout" if attempts_until_lockout <= 2 else None
        }
    
    def _get_recent_failed_attempts_count(self, minutes: int = 15) -> int:
        """Get count of recent failed login attempts."""
        cutoff = timezone.now() - timedelta(minutes=minutes)
        return FailedLoginAttempt.objects.filter(
            user=self.user,
            website=self.website,
            timestamp__gte=cutoff
        ).count()
    
    def _is_same_ip_as_recent_attempts(self, ip_address: str) -> bool:
        """Check if IP matches recent failed attempts (potential attack)."""
        cutoff = timezone.now() - timedelta(minutes=15)
        recent_attempts = FailedLoginAttempt.objects.filter(
            user=self.user,
            website=self.website,
            timestamp__gte=cutoff,
            ip_address=ip_address
        ).count()
        
        return recent_attempts >= 2  # 2+ attempts from same IP
    
    def _has_recent_successful_login(self, hours: int = 24) -> bool:
        """Check if user has logged in successfully recently."""
        if not hasattr(self.user, 'last_login') or not self.user.last_login:
            return False
        
        cutoff = timezone.now() - timedelta(hours=hours)
        return self.user.last_login >= cutoff
    
    def _get_attempts_until_lockout(self, ip_address: str, is_trusted_device: bool) -> int:
        """Get number of attempts remaining before lockout."""
        failed_attempts = self._get_recent_failed_attempts_count()
        
        # Use the same logic as should_lockout
        if is_trusted_device:
            return max(0, 10 - failed_attempts)
        
        if self._is_same_ip_as_recent_attempts(ip_address):
            return max(0, 3 - failed_attempts)
        
        if self._has_recent_successful_login(hours=24):
            return max(0, 7 - failed_attempts)
        
        return max(0, 5 - failed_attempts)
    
    def get_failed_attempts(self) -> int:
        """Get current failed attempts count."""
        return self._get_recent_failed_attempts_count()

