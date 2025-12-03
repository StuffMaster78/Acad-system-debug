"""
Phone Verification Service
Manages phone number verification via SMS.
"""
import logging
import random
from typing import Optional
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.mail import send_mail  # Fallback if SMS not available
from django.conf import settings
from authentication.models.account_security import PhoneVerification
from websites.utils import get_current_website

logger = logging.getLogger(__name__)


class PhoneVerificationService:
    """
    Service for managing phone number verification.
    """
    
    CODE_EXPIRY_MINUTES = 10
    CODE_LENGTH = 6
    
    def __init__(self, user, website=None):
        self.user = user
        self.website = website or get_current_website()
        if not self.website:
            from websites.models import Website
            self.website = Website.objects.filter(is_active=True).first()
    
    def generate_verification_code(self) -> str:
        """Generate 6-digit verification code."""
        return ''.join([str(random.randint(0, 9)) for _ in range(self.CODE_LENGTH)])
    
    def request_verification(self, phone_number: str) -> PhoneVerification:
        """
        Request phone verification code.
        
        Args:
            phone_number: Phone number to verify (E.164 format)
        
        Returns:
            Created PhoneVerification instance
        """
        if not self.website:
            raise ValueError("Website context required")
        
        # Cancel any existing pending verifications
        PhoneVerification.objects.filter(
            user=self.user,
            website=self.website,
            phone_number=phone_number,
            is_verified=False
        ).update(is_verified=True)  # Mark as cancelled
        
        # Generate code
        code = self.generate_verification_code()
        expires_at = timezone.now() + timezone.timedelta(minutes=self.CODE_EXPIRY_MINUTES)
        
        # Create verification record
        verification = PhoneVerification.objects.create(
            user=self.user,
            website=self.website,
            phone_number=phone_number,
            verification_code=code,
            expires_at=expires_at,
        )
        
        # Send SMS (or email fallback)
        self._send_verification_code(phone_number, code)
        
        return verification
    
    def verify_code(self, phone_number: str, code: str) -> bool:
        """
        Verify phone verification code.
        
        Args:
            phone_number: Phone number to verify
            code: Verification code
        
        Returns:
            True if verified successfully
        
        Raises:
            ValidationError: If code is invalid
        """
        if not self.website:
            raise ValueError("Website context required")
        
        try:
            verification = PhoneVerification.objects.get(
                user=self.user,
                website=self.website,
                phone_number=phone_number,
                is_verified=False
            )
        except PhoneVerification.DoesNotExist:
            raise ValidationError("No pending verification found for this phone number")
        
        # Check if expired
        if verification.is_expired:
            raise ValidationError("Verification code has expired. Please request a new one.")
        
        # Check if attempts exhausted
        if verification.is_exhausted:
            raise ValidationError("Maximum verification attempts exceeded. Please request a new code.")
        
        # Increment attempts
        verification.attempts += 1
        verification.save(update_fields=['attempts'])
        
        # Verify code
        if verification.verification_code != code:
            if verification.is_exhausted:
                raise ValidationError("Maximum verification attempts exceeded. Please request a new code.")
            raise ValidationError(f"Invalid verification code. {verification.max_attempts - verification.attempts} attempts remaining.")
        
        # Mark as verified
        verification.is_verified = True
        verification.verified_at = timezone.now()
        verification.save(update_fields=['is_verified', 'verified_at'])
        
        # Update user's phone number if needed
        if hasattr(self.user, 'phone_number'):
            self.user.phone_number = phone_number
            self.user.save(update_fields=['phone_number'])
        
        return True
    
    def _send_verification_code(self, phone_number: str, code: str):
        """
        Send verification code via SMS or email fallback.
        
        Args:
            phone_number: Phone number
            code: Verification code
        """
        # Try SMS first (if SMS service configured)
        sms_sent = False
        try:
            # Check if SMS service is configured
            if hasattr(settings, 'SMS_PROVIDER') and settings.SMS_PROVIDER:
                sms_sent = self._send_sms(phone_number, code)
        except Exception as e:
            logger.warning(f"SMS sending failed: {e}")
        
        # Fallback to email if SMS not available
        if not sms_sent:
            try:
                send_mail(
                    subject="Phone Verification Code",
                    message=f"Your phone verification code is: {code}\n\nThis code will expire in {self.CODE_EXPIRY_MINUTES} minutes.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[self.user.email],
                    fail_silently=False,
                )
            except Exception as e:
                logger.error(f"Failed to send verification code email: {e}")
                raise ValidationError("Failed to send verification code. Please try again.")
    
    def _send_sms(self, phone_number: str, code: str) -> bool:
        """
        Send SMS via configured provider.
        
        Args:
            phone_number: Phone number
            code: Verification code
        
        Returns:
            True if SMS sent successfully
        """
        # Placeholder for SMS integration (Twilio, AWS SNS, etc.)
        # Example with Twilio:
        # try:
        #     from twilio.rest import Client
        #     client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        #     message = client.messages.create(
        #         body=f"Your verification code is: {code}",
        #         from_=settings.TWILIO_PHONE_NUMBER,
        #         to=phone_number
        #     )
        #     return True
        # except Exception as e:
        #     logger.error(f"Twilio SMS error: {e}")
        #     return False
        
        # For now, return False to use email fallback
        return False
    
    def get_verified_phone(self) -> Optional[str]:
        """Get verified phone number for user."""
        if not self.website:
            return None
        
        verified = PhoneVerification.objects.filter(
            user=self.user,
            website=self.website,
            is_verified=True
        ).order_by('-verified_at').first()
        
        return verified.phone_number if verified else None

