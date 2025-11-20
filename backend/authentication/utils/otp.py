import random
import hashlib
import string
from datetime import timedelta
from django.utils import timezone
from authentication.models.otp import OTP

def generate_otp(user, expires_in=5):
    """
    Generate a 6-digit OTP and store it in the database.
    
    expires_in: Time in minutes until OTP expires (default is 5 minutes).
    """
    otp_code = ''.join(random.choices(string.digits, k=6))  # OTP is a 6-digit number
    expiration_time = timezone.now() + timedelta(minutes=expires_in)

    otp_hash = hashlib.sha256(otp_code.encode()).hexdigest()
    OTP.objects.create(
        user=user,
        otp_code_hash=otp_hash,
        expiration_time=expiration_time
    )
    
    return otp_code

def verify_otp(user, otp_code):
    """
    Verify an OTP against the stored value in the database.
    
    Returns True if OTP matches and hasn't expired, False otherwise.
    """
    otp = OTP.objects.filter(user=user).last()
    otp_hash = hashlib.sha256(otp_code.encode()).hexdigest()
    if otp and otp.otp_code_hash == otp_hash and otp.expiration_time > timezone.now():
        return True
    return False