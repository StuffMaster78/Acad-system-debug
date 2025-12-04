from django.db import models
from django.conf import settings
from django.core.validators import MaxLengthValidator
from websites.models import Website

User = settings.AUTH_USER_MODEL 


class ServicePage(models.Model):
    """
    Represents a unique service page associated with a client website.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='service_pages'
    )
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    header = models.CharField(
        max_length=255,
        help_text="Header text displayed on the frontend."
    )
    content = models.TextField(
        help_text="Main content. Supports HTML or rich text."
    )
    image = models.ImageField(
        upload_to='service_pages/images/',
        null=True,
        blank=True
    )

    # SEO fields
    meta_title = models.CharField(
        max_length=255,
        blank=True,
        help_text="SEO title (recommended max 60 characters)",
        validators=[MaxLengthValidator(60)],
    )
    meta_description = models.TextField(
        blank=True,
        help_text="SEO description (recommended max 160 characters)",
        validators=[MaxLengthValidator(160)],
    )
    og_image = models.ImageField(
        upload_to='service_pages/og_images/',
        null=True,
        blank=True
    )

    # Publication tracking
    is_published = models.BooleanField(default=False)
    publish_date = models.DateTimeField(null=True, blank=True)

    # Audit fields
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_service_pages'
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='updated_service_pages'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Soft Delete
    is_deleted = models.BooleanField(default=False)

    class Meta:
        unique_together = ['website', 'slug']
        ordering = ['-publish_date']

    def __str__(self):
        return f"{self.website} | {self.title}"

    def delete(self, *args, **kwargs):
        """
        Soft delete: mark the page as deleted instead
        of removing it.
        """
        self.is_deleted = True
        self.save()
    
    def save(self, *args, **kwargs):
        """Track content changes for edit history."""
        # Track changes for edit history
        fields_changed = []
        previous_content = None
        if self.pk:
            try:
                old_instance = ServicePage.objects.get(pk=self.pk)
                previous_content = old_instance.content
                # Track changed fields
                for field in ['title', 'content', 'meta_title', 'meta_description', 'header']:
                    if getattr(old_instance, field) != getattr(self, field):
                        fields_changed.append(field)
            except ServicePage.DoesNotExist:
                pass
        
        super().save(*args, **kwargs)
        
        # Track media usage for image
        self._track_image_usage()
        
        # Create edit history entry if content changed
        if previous_content and previous_content != self.content and fields_changed:
            try:
                from .models.enhanced_models import ServicePageEditHistory
                ServicePageEditHistory.objects.create(
                    service_page=self,
                    edited_by=self.updated_by,
                    previous_content=previous_content,
                    current_content=self.content,
                    fields_changed=fields_changed,
                    changes_summary=f"Updated: {', '.join(fields_changed)}"
                )
            except Exception:
                # Silently fail if edit history model doesn't exist yet (migration pending)
                pass
    
    def _track_image_usage(self):
        """Track usage of image in this service page."""
        try:
            from media_management.models import MediaUsage
            
            # Remove old usage if image changed
            if self.pk:
                try:
                    old_instance = ServicePage.objects.get(pk=self.pk)
                    if old_instance.image and old_instance.image != self.image:
                        # Try to track old image removal
                        try:
                            if hasattr(old_instance.image, 'id'):
                                MediaUsage.remove_usage(
                                    old_instance.image,
                                    self,
                                    'page_image'
                                )
                        except Exception:
                            pass
                except ServicePage.DoesNotExist:
                    pass
            
            # Track new image
            if self.image:
                try:
                    # Check if it's a file field (ImageField)
                    if hasattr(self.image, 'name'):
                        # For ImageField, we'd need to track via MediaAsset or BlogMediaFile
                        # For now, we'll track if it's a MediaAsset
                        from media_management.models import MediaAsset
                        # This is a simplified version - you may need to adjust based on your setup
                        pass
                except Exception:
                    pass
        except ImportError:
            # media_management app not installed
            pass


class ServicePageClick(models.Model):
    """
    Logs clicks/views on a service page.
    """
    service_page = models.ForeignKey(ServicePage, on_delete=models.CASCADE)
    website = models.ForeignKey(Website, on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    session_id = models.CharField(max_length=255, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)


class ServicePageConversion(models.Model):
    """
    Logs conversion actions tied to a service page.
    """
    service_page = models.ForeignKey(ServicePage, on_delete=models.CASCADE)
    website = models.ForeignKey(Website, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    referral_url = models.URLField(blank=True)
    conversion_type = models.CharField(
        max_length=50, default='order',
        help_text="e.g., order, contact, subscribe"
    )