"""
Utility to clear rate limit cache for magic links and impersonation (useful for testing/admin purposes).
"""
from django.core.cache import cache
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


def clear_magic_link_rate_limit(email=None):
    """
    Clear rate limit cache for magic link requests.
    
    Args:
        email: If provided, clears rate limit for that specific email.
              If None, clears all magic link rate limits (use with caution).
    """
    if email:
        cache_key = f'throttle_magic-link-{email}'
        cache.delete(cache_key)
        return f"Cleared rate limit for {email}"
    else:
        # Clear all magic link throttles (this is more aggressive)
        # Note: This requires knowing the cache key pattern
        # DRF uses: throttle_<scope>_<ident>
        # We'd need to iterate through cache keys, which is not always possible
        # For now, we'll just clear if we know the email
        return "Please provide an email address to clear rate limit"


def clear_impersonation_rate_limit(user_id=None):
    """
    Clear rate limit cache for impersonation token creation.
    
    Args:
        user_id: If provided, clears rate limit for that specific user.
                If None, clears all impersonation rate limits (use with caution).
    """
    if user_id:
        # DRF UserRateThrottle cache key format: throttle_<scope>_<ident>
        cache_key = f'throttle_impersonation_token_{user_id}'
        cache.delete(cache_key)
        return f"Cleared impersonation rate limit for user {user_id}"
    else:
        # Try to clear all impersonation throttle keys
        # This is approximate - would need to know all user IDs
        # For now, return a message
        return "Please provide a user_id to clear rate limit, or restart Redis to clear all"


class Command(BaseCommand):
    help = 'Clear rate limits for magic links or impersonation'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            type=str,
            choices=['magic_link', 'impersonation'],
            help='Type of rate limit to clear'
        )
        parser.add_argument(
            '--email',
            type=str,
            help='Email address (for magic_link)'
        )
        parser.add_argument(
            '--user-id',
            type=int,
            help='User ID (for impersonation)'
        )
    
    def handle(self, *args, **options):
        limit_type = options.get('type')
        
        if limit_type == 'magic_link':
            email = options.get('email')
            if not email:
                self.stdout.write(self.style.ERROR('Please provide --email for magic_link'))
                return
            result = clear_magic_link_rate_limit(email)
            self.stdout.write(self.style.SUCCESS(result))
        elif limit_type == 'impersonation':
            user_id = options.get('user_id')
            if not user_id:
                self.stdout.write(self.style.ERROR('Please provide --user-id for impersonation'))
                return
            result = clear_impersonation_rate_limit(user_id)
            self.stdout.write(self.style.SUCCESS(result))
        else:
            self.stdout.write(self.style.ERROR('Please specify --type (magic_link or impersonation)'))

