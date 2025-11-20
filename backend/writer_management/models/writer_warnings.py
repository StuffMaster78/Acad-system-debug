from django.db import models
from django.utils.timezone import now
from websites.models import Website
from writer_management.models.profile import WriterProfile
from django.conf import settings

class WriterWarning(models.Model):
    website = models.ForeignKey(
        Website, on_delete=models.CASCADE,
        related_name="writer_warnings"
    )
    writer = models.ForeignKey(
        WriterProfile, on_delete=models.CASCADE,
        related_name="warnings"
    )
    reason = models.TextField()
    issued_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="issued_warnings"
    )
    warning_type = models.CharField(
        max_length=50,
        choices=[
            ('minor', 'Minor'),
            ('major', 'Major'),
            ('critical', 'Critical')
        ],
        default='minor'
    )
    issued_at = models.DateTimeField(default=now)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Warning for {self.writer.user.username} on {self.issued_at.date()}"