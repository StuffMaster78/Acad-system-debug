from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

class OTP(models.Model):
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE
    )
    otp_code = models.CharField(max_length=6)
    expiration_time = models.DateTimeField()

    def is_expired(self):
        return timezone.now() > self.expiration_time

    def __str__(self):
        return f"OTP for {self.user} - Expires at {self.expiration_time}"