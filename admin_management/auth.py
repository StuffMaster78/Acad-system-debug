from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from .models import BlacklistedUser

User = get_user_model()

class BlacklistAuthenticationBackend(BaseBackend):
    """
    Prevents blacklisted users from logging in.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        user = User.objects.filter(username=username).first()

        if user and BlacklistedUser.objects.filter(email=user.email).exists():
            return None  # Deny authentication for blacklisted users

        return user