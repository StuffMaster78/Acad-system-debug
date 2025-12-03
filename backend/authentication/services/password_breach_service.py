"""
Password Breach Detection Service
Checks passwords against Have I Been Pwned database.
"""
import hashlib
import logging
import requests
from typing import Dict, Any, Optional
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils import timezone
from authentication.models.password_security import PasswordBreachCheck
from websites.utils import get_current_website

logger = logging.getLogger(__name__)


class PasswordBreachService:
    """
    Service for checking passwords against breach databases.
    Uses Have I Been Pwned API (k-anonymity model for privacy).
    """
    
    HIBP_API_URL = "https://api.pwnedpasswords.com/range/"
    TIMEOUT = 5  # seconds
    
    def __init__(self, user, website=None):
        self.user = user
        self.website = website or get_current_website()
        if not self.website:
            from websites.models import Website
            self.website = Website.objects.filter(is_active=True).first()
    
    def check_password_breach(self, password: str, force_check: bool = False) -> Dict[str, Any]:
        """
        Check if password has been found in data breaches.
        Uses k-anonymity model (only sends first 5 chars of hash).
        
        Args:
            password: Plain text password to check
            force_check: Force check even if recently checked
        
        Returns:
            Dict with breach information
        """
        if not self.website:
            logger.warning(f"No website context for breach check for user {self.user.id}")
            return {'is_breached': False, 'breach_count': 0, 'error': 'No website context'}
        
        # Hash password with SHA-1
        sha1_hash = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
        prefix = sha1_hash[:5]
        suffix = sha1_hash[5:]
        
        try:
            # Check if we recently checked this password
            if not force_check:
                recent_check = PasswordBreachCheck.objects.filter(
                    user=self.user,
                    website=self.website,
                    password_hash_prefix=prefix
                ).order_by('-checked_at').first()
                
                if recent_check and (timezone.now() - recent_check.checked_at).total_seconds() < 3600:
                    # Use cached result if checked within last hour
                    return {
                        'is_breached': recent_check.is_breached,
                        'breach_count': recent_check.breach_count,
                        'cached': True,
                    }
            
            # Query HIBP API (k-anonymity)
            response = requests.get(
                f"{self.HIBP_API_URL}{prefix}",
                timeout=self.TIMEOUT,
                headers={'User-Agent': 'WritingSystem-PasswordChecker'}
            )
            
            if response.status_code != 200:
                logger.warning(f"HIBP API returned status {response.status_code}")
                return {'is_breached': False, 'breach_count': 0, 'error': 'API error'}
            
            # Parse response (format: SUFFIX:COUNT)
            breach_count = 0
            is_breached = False
            
            for line in response.text.splitlines():
                if ':' in line:
                    hash_suffix, count = line.split(':')
                    if hash_suffix == suffix:
                        breach_count = int(count)
                        is_breached = True
                        break
            
            # Save check result
            check = PasswordBreachCheck.objects.create(
                user=self.user,
                website=self.website,
                password_hash_prefix=prefix,
                is_breached=is_breached,
                breach_count=breach_count,
            )
            
            return {
                'is_breached': is_breached,
                'breach_count': breach_count,
                'checked_at': check.checked_at.isoformat(),
            }
            
        except requests.RequestException as e:
            logger.error(f"Error checking password breach: {e}")
            return {'is_breached': False, 'breach_count': 0, 'error': str(e)}
        except Exception as e:
            logger.error(f"Unexpected error in breach check: {e}")
            return {'is_breached': False, 'breach_count': 0, 'error': str(e)}
    
    def validate_password_not_breached(self, password: str, raise_on_breach: bool = True):
        """
        Validate that password is not in breach database.
        
        Args:
            password: Plain text password to validate
            raise_on_breach: Whether to raise ValidationError if breached
        
        Raises:
            ValidationError: If password is breached and raise_on_breach is True
        """
        result = self.check_password_breach(password)
        
        if result.get('is_breached', False):
            breach_count = result.get('breach_count', 0)
            if raise_on_breach:
                raise ValidationError(
                    f"This password has been found in {breach_count} data breach(es). "
                    "Please choose a different password for your security."
                )
            return False
        
        return True
    
    def get_breach_history(self, limit: int = 10):
        """Get recent breach check history for user."""
        if not self.website:
            return []
        
        return PasswordBreachCheck.objects.filter(
            user=self.user,
            website=self.website
        ).order_by('-checked_at')[:limit]

