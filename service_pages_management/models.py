from django.db import models
from django.contrib.auth import get_user_model
from websites.models import Website

User = get_user_model()

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
    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.TextField(blank=True)
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
