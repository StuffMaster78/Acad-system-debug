"""
Files Management
==================
 
Centralized file storage. Every file uploaded anywhere in the system
flows through ManagedFile. Other apps never use FileField directly —
they FK to ManagedFile.
 
Extends the existing media_management app concept. In production,
this may be integrated into the existing app rather than standing alone.
 
Storage backend: DigitalOcean Spaces (S3-compatible).
Virus scanning: ClamAV via Celery task.
Deduplication: SHA-256 hash comparison.
FileBucket — logical grouping mapping to a DigitalOcean Spaces bucket + path prefix.

Each bucket defines storage behaviour: public/private, CDN, signed URL expiry,
file size limits. Buckets can be shared or tenant-scoped.
"""
 
from django.db import models
from files_management.enums import BucketType
 
class FileBucket(models.Model):
    """Logical grouping of files mapping to a Spaces bucket + path prefix.
 
    Examples:
    - prod-public-cms (CDN-enabled, public-read)
    - prod-private-files (signed URLs only)
    - prod-backups (different region, disaster recovery)
    """
 
    name = models.CharField(max_length=100, unique=True)
    bucket_type = models.CharField(
        max_length=50,
        choices=BucketType.choices,
        db_index=True,
    )
 
    # Tenant scope (null = shared across all tenants)
    site = models.ForeignKey(
        "wagtailcore.Site",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="file_buckets",
    )
 
    # DO Spaces configuration
    spaces_bucket_name = models.CharField(max_length=100)
    spaces_region = models.CharField(max_length=20, default="nyc3")
    spaces_path_prefix = models.CharField(
        max_length=255,
        blank=True,
        help_text="Path prefix within the bucket (e.g., 'nursemygrade/media')",
    )
 
    # CDN
    cdn_endpoint = models.URLField(blank=True)
    cdn_enabled = models.BooleanField(default=False)
 
    # Access control
    is_public = models.BooleanField(default=False)
    requires_signed_urls = models.BooleanField(default=True)
    signed_url_expiry_seconds = models.PositiveIntegerField(
        default=3600,
        help_text="Signed URL lifetime in seconds (default: 1 hour)",
    )
 
    # Quotas
    max_file_size_bytes = models.BigIntegerField(
        default=104857600,
        help_text="Maximum single file size in bytes (default: 100MB)",
    )
    allowed_extensions = models.JSONField(
        default=list,
        blank=True,
        help_text='Allowed file extensions (empty = all). e.g., ["pdf", "docx", "jpg"]',
    )
    blocked_extensions = models.JSONField(
        default=list,
        blank=True,
        help_text='Blocked extensions (overrides allowed). e.g., ["exe", "bat"]',
    )
 
    created_at = models.DateTimeField(auto_now_add=True)
 
    class Meta:
        ordering = ["name"]
 
    def __str__(self):
        return f"{self.name} ({self.get_bucket_type_display()})"
    
    @property
    def endpoint_url(self):
        """Full Spaces endpoint URL for boto3."""
        return f"https://{self.spaces_region}.digitaloceanspaces.com"