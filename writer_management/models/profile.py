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
        db_index=True,
        help_text="Unique writer registration ID (e.g., Writer #12345)."
    )
    timezone = models.CharField(
        max_length=50,
        default="UTC",
        help_text="Writer's timezone."
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
        db_index=True,
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
    introduction = models.TextField(
        blank=True,
        null=True,
        help_text="Brief introduction or bio of the writer."
    )
    active_orders = models.PositiveIntegerField(
        default=0,
        help_text="Number of ongoing orders assigned to the writer."
    )
    joined_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="Date and time when the writer joined the platform."
    )
    last_active = models.DateTimeField(null=True, blank=True)
    last_logged_in = models.DateTimeField(null=True, blank=True)
    location_verified = models.BooleanField(
        default=False,
        help_text="Indicates whether the writer's location has been verified."
    )
    location = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Writer's location."
    )
    wallet = models.OneToOneField(
        Wallet,
        on_delete=models.CASCADE,
        related_name="writer_profile",
        help_text="The wallet associated with the writer."
    )
    average_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.00,
        help_text="Average rating received by the writer."
    )
    reviews_count = models.PositiveIntegerField(
        default=0,
        help_text="Total number of reviews received by the writer."
    )
    allow_public_view = models.BooleanField(
        default=False,
        help_text="Allow public viewing of the writer's profile."
    )
    slug = models.SlugField(unique=True, blank=True)
    is_draft = models.BooleanField(default=True)

    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)





    def __str__(self):
        username = self.user.username if self.user else "Unknown"
        return f"Writer Profile: {username} ({self.registration_id})"

    class Meta:
        verbose_name = "Writer Profile"
        verbose_name_plural = "Writer Profiles"
        ordering = ['-joined_at']
        unique_together = ("website", "registration_id")

    def clean(self):
        """
        Custom validation to ensure registration ID is unique and valid.
        """
        if not self.registration_id:
            raise ValidationError("Registration ID cannot be empty.")
        
        if len(self.registration_id) < 5:
            raise ValidationError("Registration ID must be at least 5 characters long.")
        
        if not self.registration_id.startswith("Writer #"):
            raise ValidationError("Registration ID must start with 'Writer #'.")
        
        if self.website.writer_profile.filter(registration_id=self.registration_id).exists():
            raise ValidationError("This registration ID already exists for another writer.")    
    
    def save(self, *args, **kwargs):
        """
        Override save method to perform custom validation.
        """
        self.clean()
        super().save(*args, **kwargs)

    def get_summary(self):
        """
        Returns a brief summary of the writer's profile.
        """
        return {
            "username": self.user.username,
            "registration_id": self.registration_id,
            "writer_level": self.writer_level.name if self.writer_level else "N/A",
            "skills": [
                s.strip() for s in self.skills.split(",")
            ] if self.skills else [],
            "subject_preferences": [
                s.strip() for s in self.subject_preferences.split(",")
            ] if self.subject_preferences else [],
            "total_completed_orders": self.completed_orders,
            "total_active_orders": self.active_orders,
            "total_takes": self.number_of_takes,
            "total_earnings": str(self.total_earnings),
            "verification_status": self.verification_status,
            "verification_documents": self.verification_documents,
            "active_orders": self.active_orders,
            "joined_at": self.joined_at.strftime("%Y-%m-%d %H:%M:%S"),
        }

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
    course = models.CharField(
        max_length=255,
        help_text="Degree or certification obtained."
    )
    start_year = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Year when the course started."
    )
    end_year = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Year when the course ended."
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
    degree = models.CharField(
        max_length=255,
        help_text="Degree or qualification obtained."
    )
    academic_level = models.CharField(
        max_length=100,
        help_text="Level of education (e.g., Bachelor's, Master's, PhD)."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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

class WriterSubjectPreference(models.Model):
    """
    Represents a writer's subject preferences for assignments.
    Allows writers to specify subjects they are comfortable with.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="writer_subject_preferences"
    )
    writer = models.ForeignKey(
        WriterProfile,
        on_delete=models.CASCADE,
        related_name="subject_preferences_for_specific_writer",
        help_text="The writer whose subject preferences are being set."
    )
    subjects = ArrayField(
        models.CharField(max_length=100),
        blank=True,
        default=list,
        help_text="List of subjects the writer prefers to work on."
    )

    def __str__(self):
        return f"Subject Preferences for {self.writer.user.username}"
    
    class Meta:
        verbose_name = "Writer Subject Preference"
        verbose_name_plural = "Writer Subject Preferences"
        unique_together = ("website", "writer")

class WriterProfileWebhookSetting(models.Model):
    """
    Webhook settings for writer profile updates.
    Allows integration with external systems for real-time updates.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="webhook_settings_for_writer_profile",
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
        related_name="webhook_for_specific_events",
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