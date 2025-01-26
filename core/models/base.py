from django.db import models
from django.utils.timezone import now

class ActiveManager(models.Manager):
    """Custom manager to exclude soft-deleted records by default."""
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)

class BaseModel(models.Model):
    """
    Abstract base model for common fields and functionality.
    """
    created_at = models.DateTimeField(default=now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True, help_text="Soft delete timestamp")
    created_by = models.ForeignKey(
        'users.User',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_%(class)s_set",
        help_text="User who created the record"
    )
    updated_by = models.ForeignKey(
        'users.User',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="updated_%(class)s_set",
        help_text="User who last updated the record"
    )

    # Managers
    objects = ActiveManager()  # Default: exclude soft-deleted records
    all_objects = models.Manager()  # Include all records

    class Meta:
        abstract = True  # Ensure no database table is created for this model

    def soft_delete(self):
        """Soft delete the record."""
        self.deleted_at = now()
        self.save()

    def restore(self):
        """Restore a soft-deleted record."""
        self.deleted_at = None
        self.save()

    def is_deleted(self):
        """Check if the record is soft-deleted."""
        return self.deleted_at is not None

class WebsiteSpecificBaseModel(BaseModel):
    """
    Abstract base model for models tied to specific websites.
    """
    website = models.ForeignKey(
        'websites.Website',  # Reference to the Website model
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="%(class)s_set",
        help_text="Website this record is associated with"
    )

    class Meta:
        abstract = True
