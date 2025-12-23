"""
Middleware to capture the current user for config versioning.
"""
import threading

# Thread-local storage for the current user
_thread_locals = threading.local()


def get_current_user():
    """Get the current user from thread-local storage."""
    return getattr(_thread_locals, 'user', None)


def set_current_user(user):
    """Set the current user in thread-local storage."""
    _thread_locals.user = user


class ConfigVersioningMiddleware:
    """
    Middleware to capture the current user for config versioning.
    This allows signals to know which user made the change.
    """
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Set the current user in thread-local storage
        if hasattr(request, 'user') and request.user.is_authenticated:
            set_current_user(request.user)
        else:
            set_current_user(None)
        
        try:
            response = self.get_response(request)
        finally:
            # Clean up thread-local storage
            if hasattr(_thread_locals, 'user'):
                delattr(_thread_locals, 'user')
        
        return response

