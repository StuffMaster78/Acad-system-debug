# File: myapp/middleware.py
from django.shortcuts import redirect
from django.contrib.auth import logout
from .models import Blacklist

class BlacklistMiddleware:
    """Middleware to prevent blacklisted users from accessing the system."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            user_blacklisted = Blacklist.objects.filter(user=request.user, is_active=True).exists()
            ip_blacklisted = Blacklist.objects.filter(ip_address=request.META.get('REMOTE_ADDR'), is_active=True).exists()

            if user_blacklisted or ip_blacklisted:
                logout(request)
                return redirect("blacklist_notice")  # Redirect to a "You're Blacklisted" page.

        return self.get_response(request)