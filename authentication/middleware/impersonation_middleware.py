"""
Middleware to inject impersonation context into request for JWT authentication.
Allows impersonation info to be accessible even with stateless JWT tokens.
"""
import logging
from typing import Optional
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class ImpersonationMiddleware(MiddlewareMixin):
    """
    Middleware to extract impersonation information from JWT tokens
    and make it available in request object.
    """
    
    def process_request(self, request):
        """
        Extract impersonation info from JWT token claims if present.
        """
        # Check if request has authenticated user with JWT token
        if hasattr(request, 'auth') and request.auth:
            try:
                # Extract impersonation claims from JWT
                if isinstance(request.auth, dict):
                    if request.auth.get('is_impersonation'):
                        # Set impersonation context in request
                        request._impersonation_context = {
                            'is_impersonating': True,
                            'impersonated_by': request.auth.get('impersonated_by'),
                            'original_user_id': request.auth.get('impersonated_by'),
                        }
                        return None
            except (AttributeError, TypeError, KeyError):
                pass
        
        # Check session as fallback
        if hasattr(request, 'session') and request.session.get('_impersonator_id'):
            request._impersonation_context = {
                'is_impersonating': True,
                'impersonated_by': request.session.get('_impersonator_id'),
                'original_user_id': request.session.get('_impersonator_id'),
            }
        else:
            request._impersonation_context = {
                'is_impersonating': False,
            }
        
        return None

