from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone 
from django.core.mail import send_mail
from django.utils.text import slugify
import re  # Fix missing import
from django.utils.timezone import now  # Fix missing import
from django.contrib.postgres.fields import JSONField  # PostgreSQL JSON support
from django.conf import settings
from websites.models.websites import Website

User = settings.AUTH_USER_MODEL 


class WebsiteActionLog(models.Model):
    """Logs admin actions for website updates (SEO settings, deletions, etc.)."""
    ACTION_CHOICES = [
        ("SEO_UPDATED", "SEO Settings Updated"),
        ("SOFT_DELETED", "Website Soft Deleted"),
        ("RESTORED", "Website Restored"),
    ]

    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="action_logs"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES
    )
    details = models.TextField(
        blank=True,
        null=True,
        help_text="Extra details about the action"
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} {self.action} on {self.website.name} at {self.timestamp}"