from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class FailedLoginAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=timezone.now)
    
    def is_locked_out(self):
        recent_attempts = self.__class__.objects.filter(
            user=self.user,
            timestamp__gt=timezone.now() - timezone.timedelta(minutes=15)
        )
        return len(recent_attempts) >= 5  # Lock out if 5 or more failed attempts in 15 minutes