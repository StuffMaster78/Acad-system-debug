from django.db import models
class ActiveManager(models.Manager):
    """
    Custom manager to exclude soft-deleted records by default and add utilities.
    """
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)

    def deleted(self):
        """Return only soft-deleted records."""
        return super().get_queryset().filter(deleted_at__isnull=False)

    def all_with_deleted(self):
        """Return all records, including soft-deleted ones."""
        return super().get_queryset()
    
    def active_count(self):
        """Count active (non-soft-deleted) records."""
        return self.get_queryset().count()

    def deleted_count(self):
        """Count soft-deleted records."""
        return super().get_queryset().filter(deleted_at__isnull=False).count()