from django.contrib.auth import authenticate
from authentication.models.mfa_settings import MFASettings
from django.core.exceptions import ValidationError

class LoginService:
    def __init__(self, website):
        self.website = website

    def login(self, username, password):
        user = authenticate(username=username, password=password)
        if user is None:
            raise ValidationError("Invalid credentials")

        # Multitenancy check here if needed

        mfa_settings = MFASettings.objects.filter(user=user).first()
        if mfa_settings and mfa_settings.is_mfa_enabled:
            return {"2fa_required": True, "user_id": user.id}

        # Login success: issue token/session
        token = self.issue_token(user)
        return {"token": token}

    def issue_token(self, user):
        # JWT or session logic here
        pass
