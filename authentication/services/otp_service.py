import random
from datetime import timedelta
from django.utils import timezone
from authentication.models.otp import OTP

class OTPService:
    """
    Handles generation and validation of one-time passcodes.
    """

    @staticmethod
    def generate_otp(user, website, length=6, valid_minutes=5):
        """
        Generates and stores an OTP for the user.
        """
        otp_code = "".join([str(random.randint(0, 9)) for _ in range(length)])
        expiration = timezone.now() + timedelta(minutes=valid_minutes)

        otp = OTP.objects.create(
            user=user,
            website=website,
            otp_code=otp_code,
            expiration_time=expiration
        )
        return otp

    @staticmethod
    def validate_otp(user, website, otp_code):
        """
        Validates the submitted OTP.
        """
        try:
            otp = OTP.objects.get(
                user=user,
                website=website,
                otp_code=otp_code
            )
            if otp.is_expired():
                otp.delete()
                return False
            otp.delete()  # Burn it
            return True
        except OTP.DoesNotExist:
            return False