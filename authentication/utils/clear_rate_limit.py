"""
Utility to clear rate limit cache for magic links (useful for testing/admin purposes).
"""
from django.core.cache import cache
from django.core.management.base import BaseCommand


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


class Command(BaseCommand):
    help = 'Clear magic link rate limit for a specific email'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='Email address to clear rate limit for')

    def handle(self, *args, **options):
        email = options['email']
        result = clear_magic_link_rate_limit(email)
        self.stdout.write(self.style.SUCCESS(result))

