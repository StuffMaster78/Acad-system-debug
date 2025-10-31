from django.db import models
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from django.utils import timezone
from django.conf import settings
# from django.contrib.auth import get_user_model

User = settings.AUTH_USER_MODEL
# ActualUser = get_user_model()
class PromotionalCampaign(models.Model):
    """
    Represents a Promotional Campaign that discounts can be associated with.
    Examples: Summer, Black Friday, CyberMonday etc.
    """

    CAMPAIGN_STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('pending', 'Pending'),
        ('cancelled', 'Cancelled'),
        ('deleted', 'Deleted'),
        ('completed', 'Completed'),
        ('archived', 'Archived'),
    ]

    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name='promotional_campaigns',
        help_text="Website this campaign is associated with"
    )
    campaign_name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Event name (e.g., Black Friday, Christmas Sale)"
    )
    description = models.TextField(
        null=True,
        blank=True,
        help_text="Optional description of the promotional campaign"
    )
    slug = models.SlugField(
        unique=True,
        null=True,
        blank=True,
        help_text="Slug for URL or admin filtering"
    )
    # Status of the campaign
    status = models.CharField(
        max_length=20,
        choices=CAMPAIGN_STATUS_CHOICES,
        default='draft'
    )
     # Active window
    start_date = models.DateTimeField(help_text="When the  promotional campaign starts")
    end_date = models.DateTimeField(help_text="When the promotional campaign ends")
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this promotional campaign is currently active"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_campaigns'
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='updated_campaigns'
    )

    is_deleted = models.BooleanField(
        default=False,
        help_text="Indicates if the campaign is soft-deleted"
    )
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when the campaign was soft-deleted"
    )
    deleted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='deleted_campaigns'
    )
    restored_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='restored_campaigns'
    )
    # Optional campaign type
    campaign_type = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Optional type (e.g. 'email-blast', 'referral', 'flash-sale')"
    )

    class Meta:
        unique_together = ('website', 'slug')
        ordering = ['-is_active', '-start_date']
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['status']),
        ]

    def clean(self):
        if self.start_date > self.end_date:
            raise ValidationError("End date must be after start date.")

    @property
    def name(self):
        return self.campaign_name

    def save(self, *args, **kwargs):
        if self.end_date < timezone.now():
            self.is_active = False
        if not self.slug:
            self.slug = slugify(f"{self.campaign_name}-{self.website_id}")
        super().save(*args, **kwargs)

    def activate(self):
        self.is_active = True
        self.save(update_fields=['is_active'])

    def deactivate(self):
        self.is_active = False
        self.save(update_fields=['is_active'])
    def archive(self):
        """
        Archive the campaign, setting its status to 'archived'.
        """
        self.status = 'archived'
        self.save(update_fields=['status'])
    def unarchive(self):
        """
        Unarchive the campaign, setting its status to 'active'.
        """
        self.status = 'active'
        self.save(update_fields=['status'])
    def soft_delete(self, deleted_by=None):
        """
        Soft-delete the campaign by setting is_active to False and is_deleted to True.
        Optionally set the user who deleted it.
        """
        if deleted_by and not isinstance(deleted_by, User):
            raise ValidationError("deleted_by must be a valid User instance")

        if self.is_deleted:
            raise ValidationError("This campaign is already soft-deleted.")

        self.status = 'deleted'
        self.slug = slugify(f"{self.campaign_name}-{self.website_id}-deleted")
        self.is_active = False
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.updated_at = timezone.now()
        self.updated_by = deleted_by
        self.deleted_by = deleted_by

        self.save(update_fields=[
            'status', 'slug', 'is_active', 'is_deleted',
            'deleted_at', 'updated_at', 'updated_by', 'deleted_by'
        ])
    def restore(self, restored_by=None):
        """
        Restore a soft-deleted campaign by setting is_active to True.
        """
        if not self.is_deleted:
            raise ValidationError("This campaign is not deleted.")

        if restored_by and not isinstance(restored_by, User):
            raise ValidationError("restored_by must be a valid User instance")

        self.is_active = True
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by = None

        # Regenerate slug cleanly, removing any trailing '-deleted'
        base_slug = slugify(f"{self.campaign_name}-{self.website_id}")
        self.slug = self.generate_unique_slug(
            base_slug,
            self.website_id,
            self.__class__
        )

        self.status = 'active'
        self.updated_at = timezone.now()
        self.updated_by = restored_by

        self.save(update_fields=[
            'is_active', 'is_deleted', 'deleted_at', 'deleted_by',
            'slug', 'status', 'updated_at', 'updated_by'
        ])

    def clean_fields(self, exclude=None):
        """
        Validate fields before saving."""
        super().clean_fields(exclude)
        if self.is_deleted and self.status not in ['deleted', 'archived']:
            raise ValidationError(
                "Deleted campaigns must have status 'deleted' or 'archived"
            )
        
    def generate_unique_slug(self, base, website_id, model_class):
        '''
        Generate a unique slug for the campaign based on its name and website ID.
        If a slug already exists, append a counter to make it unique.
        '''
        slug = slugify(f"{base}-{website_id}")
        counter = 1
        orig_slug = slug
        while model_class.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            slug = f"{orig_slug}-{counter}"
            counter += 1
        return slug

    def get_status_display_badge(self):
        """
        Returns a status color code for UI badge rendering.
        """
        return {
            'draft': 'secondary',      # Gray
            'active': 'success',       # Green
            'paused': 'warning',       # Yellow
            'pending': 'info',         # Blue
            'cancelled': 'danger',     # Red
            'deleted': 'dark',         # Black/Grey
            'completed': 'primary',    # Blue/Purple
            'archived': 'muted',       # Faded
        }.get(self.status, 'light')   # Default fallback


    @property
    def is_live(self):
        now = timezone.now()
        return self.is_active and self.start_date <= now <= self.end_date
    @property
    def has_started(self):
        return timezone.now() >= self.start_date

    @property
    def has_ended(self):
        return timezone.now() > self.end_date

    def __str__(self):
        return f"{self.campaign_name} ({self.start_date.date()} - {self.end_date.date()})"