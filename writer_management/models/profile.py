from django.db import models
from django.utils.timezone import now
from django.conf import settings
from websites.models import Website
from orders.models import Order
from wallet.models import Wallet
from django.core.exceptions import ValidationError
from django.contrib.postgres.fields import ArrayField

User = settings.AUTH_USER_MODEL 


class WriterProfile(models.Model):
    """
    Represents the profile of a writer.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="writer_profile"
    )
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="writer_profile",
        limit_choices_to={"role": "writer"},
        help_text="The user associated with this writer profile."
    )
    registration_id = models.CharField(
        max_length=50,
        unique=True,
        help_text="Unique writer registration ID (e.g., Writer #12345)."
    )
    email = models.EmailField(
        unique=True,
        help_text="Writer's email address."
    )
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        help_text="Writer's phone number."
    )
    country = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Writer's country."
    )
    timezone = models.CharField(
        max_length=50,
        default="UTC",
        help_text="Writer's timezone."
    )
    ip_address = models.GenericIPAddressField(
        blank=True,
        null=True,
        help_text="Last known IP address of the writer."
    )
    location_verified = models.BooleanField(
        default=False,
        help_text="Whether the writer's location has been verified."
    )
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="writers",
        help_text="Website the writer is associated with."
    )
    joined = models.DateTimeField(
        default=now,
        help_text="Date when the writer joined."
    )
    last_logged_in = models.DateTimeField(
        blank=True,
        null=True,
        help_text="The last time the writer logged in."
    )
    writer_level = models.ForeignKey(
        "WriterLevel",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="writers",
        help_text="The level of the writer."
    )
    completed_orders = models.PositiveIntegerField(
        default=0,
        help_text="Total completed orders by the writer."
    )
    number_of_takes = models.PositiveIntegerField(
        default=0,
        help_text="Total orders the writer has accepted."
    )
    total_earnings = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        help_text="Total earnings by the writer."
    )
    verification_status = models.BooleanField(
        default=False,
        help_text="Indicates whether the writer has been verified."
    )
    verification_documents = models.JSONField(
        default=dict,
        blank=True,
        help_text="Uploaded documents for verification (e.g., ID, certificates)."
    )
    skills = models.TextField(
        blank=True,
        null=True, help_text="Skills and specialties of the writer."
    )
    subject_preferences = models.TextField(
        blank=True,
        null=True,
        help_text="Subjects or topics the writer prefers to handle."
    )
    education = models.JSONField(
        default=list,
        blank=True,
        help_text="List of schools attended and uploaded certificates."
    )
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.00,
        help_text="Average rating of the writer."
    )
    active_orders = models.PositiveIntegerField(
        default=0,
        help_text="Number of ongoing orders assigned to the writer."
    )

    def __str__(self):
        return f"Writer Profile: {self.user.username} ({self.registration_id})"

    @property
    def average_rating(self):
        """
        Calculate the average rating for the writer based on WriterRating objects.
        """
        avg_rating = self.ratings.aggregate(models.Avg("rating"))["rating__avg"]
        return round(avg_rating, 2) if avg_rating is not None else 0.0


    @property
    def total_ratings(self):
        """
        Count the total number of ratings the writer has received.
        """
        return self.ratings.count()

    @property
    def recent_feedback(self):
        """
        Retrieve the most recent feedback provided for the writer.
        """
        return self.ratings.order_by("-created_at").values("feedback", "rating", "created_at")[:5]

    @property
    def leave_status(self):
        """
        Check if the writer is currently on leave.
        """
        current_leaves = self.leaves.filter(
            start_date__lte=now(),
            end_date__gte=now(),
            approved=True
        )
        return current_leaves.exists()

    @property
    def wallet_balance(self):
        """
        Retrieve the writer's wallet balance.
        """
        wallet = Wallet.objects.filter(user=self.user).first()
        return wallet.balance if wallet else 0.00
    
class WriterEducation(models.Model):
    """
    Tracks education history and uploaded certificates for verification.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="writer_education_level"
    )
    writer = models.ForeignKey(
        WriterProfile,
        on_delete=models.CASCADE,
        related_name="education_details",
        help_text="The writer whose education details are being tracked."
    )
    institution_name = models.CharField(
        max_length=255,
        help_text="Name of the educational institution."
    )
    degree = models.CharField(
        max_length=255,
        help_text="Degree or certification obtained."
    )
    graduation_year = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Year of graduation."
    )
    document = models.FileField(
        upload_to="education_certificates/",
        help_text="Upload proof of education (e.g., certificate)."
    )
    is_verified = models.BooleanField(
        default=False,
        help_text="Indicates whether this education has been verified by the admin."
    )

    def __str__(self):
        return f"{self.degree} from {self.institution_name} ({self.writer.user.username})"
    
    class Meta:
        verbose_name = "Writer Education"
        verbose_name_plural = "Writer Education"
        ordering = ['-graduation_year']

    def clean(self):
        """
        Custom validation to ensure graduation year is not in the future.
        """
        if self.graduation_year and self.graduation_year > now().year:
            raise ValidationError("Graduation year cannot be in the future.")
        
        if not self.document:
            raise ValidationError("Document is required for education verification.")
        
    def save(self, *args, **kwargs):
        """
        Override save method to perform custom validation.
        """
        self.clean()
        super().save(*args, **kwargs)


class WriterProfileAdmin(models.Model):
    """
    Admin interface for managing writer profiles.
    Allows admins to create, update, and delete writer profiles.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="writer_profile_admin"
    )
    writer = models.ForeignKey(
        WriterProfile,
        on_delete=models.CASCADE,
        related_name="admin_profiles",
        help_text="The writer whose profile is being managed."
    )
    admin_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="managed_writer_profiles",
        help_text="The admin user managing this writer profile."
    )
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Admin Profile Management: {self.writer.user.username} by {self.admin_user.username}"

    class Meta:
        verbose_name = "Writer Profile Admin Management"
        verbose_name_plural = "Writer Profile Admin Management"
        ordering = ['-updated_at']


class WriterProfileSettings(models.Model):
    """
    Settings for writer profiles, allowing customization of profile visibility and features.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="writer_profile_settings"
    )
    writer = models.ForeignKey(
        WriterProfile,
        on_delete=models.CASCADE,
        related_name="settings",
        help_text="The writer whose settings are being configured."
    )
    allow_public_view = models.BooleanField(
        default=True,
        help_text="Allow public viewing of the writer's profile."
    )
    enable_notifications = models.BooleanField(
        default=True,
        help_text="Enable notifications for the writer."
    )
    custom_fields = models.JSONField(
        default=dict,
        blank=True,
        help_text="Custom fields for additional profile information."
    )
    
    def __str__(self):
        return f"Settings for {self.writer.user.username} on {self.website.name}"
    
    class Meta:
        verbose_name = "Writer Profile Settings"
        verbose_name_plural = "Writer Profile Settings"
        unique_together = ("website", "writer")


    def clean(self):
        """
        Custom validation to ensure settings are valid.
        """
        if not isinstance(self.custom_fields, dict):
            raise ValidationError("Custom fields must be a dictionary.")
        
        if not self.custom_fields:
            raise ValidationError("Custom fields cannot be empty.")
        

    def save(self, *args, **kwargs):
        """
        Override save method to perform custom validation.
        """
        self.clean()
        super().save(*args, **kwargs)

class WriterProfileNotification(models.Model):
    """
    Notifications for writers about profile updates or important events.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="writer_profile_notifications"
    )
    writer = models.ForeignKey(
        WriterProfile,
        on_delete=models.CASCADE,
        related_name="notifications",
        help_text="The writer receiving the notification."
    )
    message = models.TextField(
        help_text="Notification message content."
    )
    sent_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification: {self.writer.user.username} - {self.sent_at} (Read: {self.read})"
    
    class Meta:
        verbose_name = "Writer Profile Notification"
        verbose_name_plural = "Writer Profile Notifications"
        ordering = ['-sent_at']


class WriterProfileWebhookSetting(models.Model):
    """
    Webhook settings for writer profile updates.
    Allows integration with external systems for real-time updates.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="writer_webhook_settings",
        help_text="The user associated with the webhook settings."
    )
    platform = models.CharField(
        max_length=50,
        help_text="Platform for the webhook (e.g., Slack, Discord)."
    )
    url = models.URLField(
        help_text="Webhook URL to send notifications to."
    )
    events = ArrayField(
        models.CharField(max_length=50),
        blank=True,
        default=list,
        help_text="List of events that trigger the webhook."
    )
    
    def __str__(self):
        return f"{self.user.username} – {self.platform} webhook"
    
    class Meta:
        unique_together = ("user", "platform")
        verbose_name = "Writer Profile Webhook Setting"
        verbose_name_plural = "Writer Profile Webhook Settings"


    def clean(self):
        """
        Custom validation to ensure the URL is valid and events are provided.
        """
        if not self.url.startswith("http"):
            raise ValidationError("Webhook URL must start with 'http' or 'https'.")
        
        if not self.events:
            raise ValidationError("At least one event must be specified for the webhook.")
        
        if len(self.events) > 10:
            raise ValidationError("A maximum of 10 events can be subscribed to a webhook.")

    def save(self, *args, **kwargs):
        """
        Override save method to perform custom validation.
        """
        self.clean()
        super().save(*args, **kwargs)

class WriterProfileHistory(models.Model):
    """
    History of changes made to a writer's profile.
    """
    writer = models.ForeignKey(
        WriterProfile,
        on_delete=models.CASCADE,
        related_name="profile_history"
    )
    change_type = models.CharField(
        max_length=50,
        choices=[
            ("update", "Profile Update"),
            ("deletion", "Profile Deletion"),
        ],
        help_text="Type of change made to the profile."
    )
    change_details = models.JSONField(
        help_text="Details of the changes made."
    )
    changed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.writer.user.username} - {self.change_type} at {self.changed_at}"

    class Meta:
        verbose_name = "Writer Profile History"
        verbose_name_plural = "Writer Profile Histories"
        ordering = ['-changed_at']

    def clean(self):
        """
        Custom validation to ensure change details are provided.
        """
        if not self.change_details:
            raise ValidationError("Change details cannot be empty.")
        
        if not isinstance(self.change_details, dict):
            raise ValidationError("Change details must be a dictionary.")   
        
    def save(self, *args, **kwargs):
        """
        Override save method to perform custom validation.
        """
        self.clean()
        super().save(*args, **kwargs)


class WriterProfileWebhookEvent(models.Model):
    """
    Represents a webhook event for writer profile updates.
    This model is used to log events that trigger webhooks.
    """
    webhook_setting = models.ForeignKey(
        WriterProfileWebhookSetting,
        on_delete=models.CASCADE,
        related_name="events",
        help_text="The webhook setting that triggered this event."
    )
    event_type = models.CharField(
        max_length=50,
        help_text="Type of the event (e.g., 'profile_updated')."
    )
    payload = models.JSONField(
        help_text="Data sent with the webhook event."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Webhook Event: {self.event_type} for {self.webhook_setting.user.username}"
    
    class Meta:
        verbose_name = "Writer Profile Webhook Event"
        verbose_name_plural = "Writer Profile Webhook Events"
        ordering = ['-created_at']

    def clean(self):
        """
        Custom validation to ensure event type and payload are valid.
        """
        if not self.event_type:
            raise ValidationError("Event type cannot be empty.")
        
        if not isinstance(self.payload, dict):
            raise ValidationError("Payload must be a dictionary.")
        
        if len(self.payload) > 1000:
            raise ValidationError("Payload size exceeds the maximum limit of 1000 characters.")     
        
    def save(self, *args, **kwargs):
        """
        Override save method to perform custom validation.
        """
        self.clean()
        super().save(*args, **kwargs)