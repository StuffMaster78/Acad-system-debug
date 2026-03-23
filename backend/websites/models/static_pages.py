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

class WebsiteStaticPage(models.Model):
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="static_pages"
    )
    title = models.CharField(max_length=255)
    language = models.CharField(
        max_length=10,
        choices=[("en", "English"), ("fr", "French"), ("es", "Spanish")],
        default="en"
    )
    slug = models.SlugField(unique=True)
    content = models.TextField()
    # Simple version number for legal/audit purposes (e.g. terms v1, v2, ...)
    version = models.PositiveIntegerField(
        default=1,
        help_text="Version number for this page (useful for Terms & Conditions)."
    )
    meta_title = models.CharField(
        max_length=255,
        blank=True
    )
    meta_description = models.TextField(blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    scheduled_publish_date = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Schedule content update"
    )
    views = models.PositiveIntegerField(default=0)  # Count page views
    previous_versions = models.JSONField(
        default=list,
        blank=True,
        help_text="Stores older versions"
    )

    class Meta:
        unique_together = ("website", "slug")

    def is_scheduled(self):
        return self.scheduled_publish_date and self.scheduled_publish_date > timezone.now()

    def increment_views(self):
        self.views += 1
        self.save(update_fields=["views"])

    def save(self, *args, **kwargs):
        if self.pk:
            old_instance = WebsiteStaticPage.objects.get(pk=self.pk)
            if old_instance.content != self.content:
                self.previous_versions.append(
                    {
                        "content": old_instance.content,
                        "last_updated": old_instance.last_updated.isoformat(),
                        "version": old_instance.version,
                    }
                )
                # Bump version when content changes
                self.version = old_instance.version + 1

        is_new = self.pk is None
        super().save(*args, **kwargs)

        if not is_new:  # Notify only for updates, not new pages
            send_mail(
                subject="Static Page Updated",
                message=f"The static page '{self.title}' was updated.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[admin.email for admin in User.objects.filter(is_superuser=True)],  # 🔥 Send to all superadmins
            )

    def __str__(self):
        return f"{self.website.name} - {self.title}"

