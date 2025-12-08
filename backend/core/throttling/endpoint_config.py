"""
Endpoint-specific rate limit configuration.
Allows fine-grained control over rate limits for different endpoints.
"""

# Rate limit configurations for specific endpoints
# Format: 'endpoint_path': {'scope': 'scope_name', 'rate': 'rate_string'}
# If rate is not specified, uses the scope's default rate from settings

ENDPOINT_RATE_LIMITS = {
    # Authentication endpoints - stricter limits
    '/api/v1/auth/auth/login/': {
        'scope': 'login',
        'rate': '10/minute',
    },
    '/api/v1/auth/auth/password-reset/': {
        'scope': 'password_reset',
        'rate': '10/hour',
    },
    '/api/v1/auth/auth/magic-link/': {
        'scope': 'magic_link',
        'rate': '5/minute',
    },
    '/api/v1/auth/auth/mfa-challenge/': {
        'scope': 'mfa_challenge',
        'rate': '20/hour',
    },
    
    # Order endpoints - moderate limits
    '/api/v1/orders/orders/': {
        'scope': 'write',
        'rate': '50/hour',  # Creating orders
    },
    '/api/v1/orders/orders/(?P<pk>[^/.]+)/': {
        'scope': 'write',
        'rate': '100/hour',  # Updating orders
    },
    
    # Payment endpoints - stricter limits
    '/api/v1/order-payments/payments/': {
        'scope': 'write',
        'rate': '30/hour',  # Payment processing
    },
    '/api/v1/order-payments/payments/(?P<pk>[^/.]+)/': {
        'scope': 'write',
        'rate': '30/hour',
    },
    
    # Guest checkout - moderate limits
    '/api/v1/orders/guest-orders/start/': {
        'scope': 'public',
        'rate': '20/hour',  # Guest order creation
    },
    '/api/v1/orders/guest-orders/verify-email/': {
        'scope': 'public',
        'rate': '10/hour',  # Email verification
    },
    
    # Dashboard endpoints - higher limits (read-heavy)
    '/api/v1/admin/dashboard/': {
        'scope': 'read',
        'rate': '200/hour',  # Dashboard data
    },
    
    # Media upload - moderate limits
    '/api/v1/media/media-assets/': {
        'scope': 'write',
        'rate': '30/hour',  # Media uploads
    },
    
    # Communication endpoints - use existing scopes
    '/api/v1/communications/messages/': {
        'scope': 'communication_message',
        'rate': '60/minute',
    },
    '/api/v1/communications/threads/': {
        'scope': 'communication_thread',
        'rate': '60/minute',
    },
    
    # Notification endpoints
    '/api/v1/notifications/notifications/': {
        'scope': 'notifications_write_burst',
        'rate': '100/minute',
    },
    
    # Search endpoints - moderate limits
    '/api/v1/orders/orders/search/': {
        'scope': 'read',
        'rate': '100/hour',
    },
}

def get_endpoint_rate_limit(endpoint_path):
    """
    Get rate limit configuration for an endpoint.
    
    Args:
        endpoint_path: The endpoint path (e.g., '/api/v1/orders/orders/')
    
    Returns:
        dict with 'scope' and optionally 'rate', or None if not configured
    """
    # Try exact match first
    if endpoint_path in ENDPOINT_RATE_LIMITS:
        return ENDPOINT_RATE_LIMITS[endpoint_path]
    
    # Try pattern matching (simplified - for production, use regex)
    for pattern, config in ENDPOINT_RATE_LIMITS.items():
        if pattern.replace('(?P<pk>[^/.]+)', '') in endpoint_path:
            return config
    
    return None

