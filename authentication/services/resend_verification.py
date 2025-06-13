# services/ResendVerificationService.py

from authentication.services.otp_service import OTPService
from authentication.services.registration_token_service import RegistrationTokenService
from authentication.services.registration_token_emailer import RegistrationEmailService
from authentication.models.activation import EmailVerification
from django.utils import timezone
from django.core.exceptions import ValidationError

class ResendVerificationService:
    MAX_RESENDS = 3
    COOLDOWN_MINUTES = 1

    @staticmethod
    def resend(user):
        ev = EmailVerification.objects.filter(user=user).first()

        if ev and not ev.is_verified:
            time_since_last = timezone.now() - ev.created_at
            if time_since_last < timezone.timedelta(minutes=ResendVerificationService.COOLDOWN_MINUTES):
                raise ValidationError("Please wait before requesting again.")

            # Revoke old token, create new one
            ev.delete()

        # Generate new OTP and token
        otp = OTPService.generate_otp(user)
        token_obj = RegistrationTokenService.create_token(user)

        # Reuse existing send logic
        RegistrationEmailService.send_verification_email(user, otp.code, token_obj.token)
        return True