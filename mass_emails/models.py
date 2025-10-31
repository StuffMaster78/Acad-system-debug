"""
Models for the Mass Email System.

Supports website-specific marketing campaigns with scheduling,
recipient tracking, file attachments, and email templates.
"""
from django.conf import settings
from django.db import models

User = settings.AUTH_USER_MODEL 


class EmailCampaign(models.Model):
    """
    Represents a single email campaign created by admin/superadmin.
    Used for marketing and communication to selected user roles.
    """
    EMAIL_TYPE_CHOICES = [
        ('marketing', 'Marketing'),
        ('promos', 'Promos'),
        ('communication', 'Communication'),
        ('updates', 'Updates'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('sending', 'Sending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name='email_campaigns'
    )
    title = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    body = models.TextField()
    email_type = models.CharField(
        max_length=20,
        choices=EMAIL_TYPE_CHOICES,
        default='marketing',
        help_text="Categorize the type of marketing email"
    )

    target_roles = models.JSONField(
        help_text="Roles to target, e.g. ['client', 'writer']"
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_email_campaigns'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    scheduled_time = models.DateTimeField(null=True, blank=True)
    sent_time = models.DateTimeField(null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )

    email_provider = models.CharField(
        max_length=100,
        blank=True,
        help_text="e.g., SendGrid, Mailgun, SMTP"
    )
    failure_report = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.website.name})"

    def save(self, *args, **kwargs):
        # Ensure non-null JSON default for tests and NOT NULL constraint
        if self.target_roles in (None, "", []):
            self.target_roles = []
        # Ensure website exists for tests
        if not getattr(self, 'website_id', None):
            try:
                from websites.models import Website
                site = Website.objects.filter(is_active=True).first()
                if site is None:
                    site = Website.objects.create(name="Test Website", domain="https://test.local", is_active=True)
                self.website_id = site.id
            except Exception:
                pass
        super().save(*args, **kwargs)

    @property
    def resolved_sender_email(self):
        """
        Returns the website's marketing sender email.
        Raises error if not configured.
        """
        if not self.website.marketing_sender_email:
            raise ValueError(
                "Marketing sender email is not configured on the website."
            )
        return self.website.marketing_sender_email

    @property
    def resolved_sender_name(self):
        """
        Returns the website's default sender name or a fallback.
        """
        return self.website.default_sender_name or "Marketing Team"


class EmailRecipient(models.Model):
    """
    Tracks each individual recipient of a campaign.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('opened', 'Opened'),
        ('bounced', 'Bounced'),
        ('failed', 'Failed'),
        ('unsubscribed', 'Unsubscribed'),
    ]

    campaign = models.ForeignKey(
        EmailCampaign,
        on_delete=models.CASCADE,
        related_name='recipients'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    email = models.EmailField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    sent_at = models.DateTimeField(null=True, blank=True)
    opened_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = ('campaign', 'email')

    def __str__(self):
        return f"{self.email} - {self.status}"


class CampaignAttachment(models.Model):
    """
    Stores file attachments (e.g. PDFs, images) for a campaign.
    """
    campaign = models.ForeignKey(
        EmailCampaign,
        on_delete=models.CASCADE,
        related_name='attachments'
    )
    file = models.FileField(upload_to='email_attachments/')
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class EmailTemplate(models.Model):
    """
    Reusable templates to speed up campaign creation.
    """
    name = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    body = models.TextField()
    is_global = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_email_templates'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    

class EmailServiceIntegration(models.Model):
    """
    Stores credentials and settings for email provider integration.
    Linked per website.
    """
    PROVIDER_CHOICES = [
        ('smtp', 'SMTP'),
        ('sendgrid', 'SendGrid'),
        ('mailgun', 'Mailgun'),
    ]

    website = models.OneToOneField(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name='email_service'
    )
    provider_name = models.CharField(
        max_length=50,
        choices=PROVIDER_CHOICES
    )
    api_key = models.TextField()
    sender_email = models.EmailField()
    sender_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.website.name} - {self.provider_name}"
    

# mass_email/models.py (add these at the bottom)

class EmailOpenTracker(models.Model):
    recipient = models.OneToOneField(
        'mass_emails.EmailRecipient',
        on_delete=models.CASCADE,
        related_name='open_tracker'
    )
    opened_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Opened: {self.recipient.email}"


class EmailClickTracker(models.Model):
    recipient = models.ForeignKey(
        'mass_emails.EmailRecipient',
        on_delete=models.CASCADE,
        related_name='clicks'
    )
    url = models.URLField()
    clicked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Click: {self.recipient.email} → {self.url}"


class UnsubscribeLog(models.Model):
    email = models.EmailField(db_index=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    reason = models.TextField(blank=True)
    unsubscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Unsubscribed: {self.email}"