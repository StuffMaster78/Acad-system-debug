from django.db import models
from django.conf import settings
from orders.models import Order
from websites.models import Website

User = settings.AUTH_USER_MODEL 


class OrderFilesConfig(models.Model):
    """
    Admin-controlled configurations for managing file uploads, downloads, and extra service files.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='order_files'
    )
    allowed_extensions = models.JSONField(default=list)  # Example: ["pdf", "docx", "xlsx"]
    enable_external_links = models.BooleanField(default=True)  # Can be disabled by admin
    max_upload_size = models.IntegerField(default=100)  # Max file size in MB
    final_draft_required = models.BooleanField(default=True)  # Writers must upload Final Draft
    extra_service_file_rules = models.JSONField(default=dict)  # {"Plagiarism Report": ["pdf"], "Smart Paper": ["docx"]}

    def __str__(self):
        return "Order Files Configuration"

    @classmethod
    def get_config(cls, website=None):
        """
        Get or create OrderFilesConfig for a website.
        If website is None, tries to get from current context or uses first active website.
        """
        if website is None:
            # Try to get website from thread-local context if available
            try:
                from core.tenant_context import get_current_website
                website = get_current_website()
            except (ImportError, AttributeError):
                pass
            
            # Fallback: get first active website
            if not website:
                website = Website.objects.filter(is_active=True).first()
                if not website:
                    # Create a default config if no website exists (shouldn't happen in production)
                    website, _ = Website.objects.get_or_create(
                        name="Default",
                        defaults={'domain': 'default.local', 'is_active': True}
                    )
        
        config, created = cls.objects.get_or_create(website=website)
        return config


class OrderFileCategory(models.Model):
    """
    Admin-defined file categories such as "Final Draft", "Order Instructions", "Plagiarism Report".
    
    - If website is None: Universal category (available to all websites)
    - If website is set: Website-specific category (only for that website)
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='order_file_category',
        null=True,
        blank=True,
        help_text="Leave blank for universal categories (available to all websites), or select a website for website-specific categories"
    )
    name = models.CharField(max_length=100)
    allowed_extensions = models.JSONField(default=list)  # ["pdf", "docx", "xlsx"]
    is_final_draft = models.BooleanField(default=False)  # True if category is Final Draft
    is_extra_service = models.BooleanField(default=False)  # True if for extra services

    class Meta:
        # Ensure name is unique per website (or globally if website is null)
        unique_together = [['name', 'website']]
        verbose_name_plural = "Order File Categories"

    def __str__(self):
        scope = "Universal" if self.website is None else f"{self.website.name}"
        return f"{self.name} ({scope})"


class OrderFile(models.Model):
    """
    Stores uploaded order files with admin & support-controlled download restrictions.
    Enhanced with versioning and Final Paper marking.
    """
    FILE_STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('revision', 'Revision'),
        ('final', 'Final Paper'),
        ('archived', 'Archived'),
    ]
    
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='order_file'
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="files"
    )
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )
    category = models.ForeignKey(
        OrderFileCategory,
        on_delete=models.SET_NULL,
        null=True
    )
    file = models.FileField(upload_to="order_files/")
    created_at = models.DateTimeField(auto_now_add=True)
    is_downloadable = models.BooleanField(default=True)  # Admin can disable downloads per file
    
    # Versioning and status
    version = models.PositiveIntegerField(default=1, help_text="File version number")
    status = models.CharField(
        max_length=20,
        choices=FILE_STATUS_CHOICES,
        default='draft',
        help_text="File status (draft, revision, final, archived)"
    )
    is_final_paper = models.BooleanField(
        default=False,
        help_text="Mark this file as the final paper for submission"
    )
    description = models.TextField(
        blank=True,
        help_text="Optional description or notes about this file version"
    )
    previous_version = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='next_versions',
        help_text="Previous version of this file (for versioning chain)"
    )

    def check_download_access(self, user):
        """
        Ensures that Admins, Editors, and Support can access and download files.
        Also allows writers to access files for orders they're assigned to or have requested.
        """
        # Admins, Editors, and Support can always download
        if user.is_staff or user.groups.filter(name__in=["Support", "Editor"]).exists():
            return True

        # Writers can access files for orders they're assigned to or have requested
        if hasattr(user, 'role') and user.role == 'writer':
            # Check if writer is assigned to the order
            if self.order.assigned_writer == user:
                return self.is_downloadable
            
            # Check if writer has requested this order
            from writer_management.models.requests import WriterOrderRequest
            try:
                writer_profile = user.writer_profile
                has_requested = WriterOrderRequest.objects.filter(
                    writer=writer_profile,
                    order=self.order
                ).exists()
                if has_requested:
                    return self.is_downloadable
            except Exception:
                pass

        # Clients can't download Final Drafts until payment is complete
        if self.category and self.category.is_final_draft:
            # Check payment status via OrderPayment or is_paid field
            from order_payments_management.models import OrderPayment
            has_completed_payment = OrderPayment.objects.filter(
                order=self.order,
                status__in=['completed', 'succeeded']
            ).exists()
            if not has_completed_payment and not self.order.is_paid:
                return False  # Lock Final Drafts for unpaid orders

        return self.is_downloadable  # Admin-controlled per file

    class Meta:
        ordering = ['-created_at', '-version']
        indexes = [
            models.Index(fields=['order', 'is_final_paper']),
            models.Index(fields=['order', 'status']),
            models.Index(fields=['order', 'version']),
        ]
    
    def __str__(self):
        category_name = self.category.name if self.category else "Uncategorized"
        status_label = " (Final)" if self.is_final_paper else f" (v{self.version})"
        return f"{category_name} - Order {self.order.id}{status_label}"
    
    def save(self, *args, **kwargs):
        """Auto-increment version and handle Final Paper marking."""
        if self.pk is None:  # New file
            # Get the highest version for this order
            max_version = OrderFile.objects.filter(
                order=self.order
            ).aggregate(models.Max('version'))['version__max'] or 0
            self.version = max_version + 1
        
        # If marking as final, unmark other final papers for this order
        if self.is_final_paper:
            OrderFile.objects.filter(
                order=self.order,
                is_final_paper=True
            ).exclude(pk=self.pk).update(is_final_paper=False)
        
        super().save(*args, **kwargs)
    
    def mark_as_final(self):
        """Mark this file as the final paper."""
        self.is_final_paper = True
        self.status = 'final'
        # Unmark other final papers
        OrderFile.objects.filter(
            order=self.order,
            is_final_paper=True
        ).exclude(pk=self.pk).update(is_final_paper=False)
        self.save(update_fields=['is_final_paper', 'status'])
    
    @property
    def is_latest_version(self):
        """Check if this is the latest version for the order."""
        latest = OrderFile.objects.filter(order=self.order).order_by('-version').first()
        return latest and latest.id == self.id


class FileDownloadLog(models.Model):
    """
    Tracks file downloads for security and audit purposes.
    Enhanced to track who downloaded what and when.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='file_download_log'
    )
    file = models.ForeignKey(
        OrderFile,
        on_delete=models.CASCADE,
        related_name="downloads"
    )
    downloaded_by = models.ForeignKey(
        'users.User', on_delete=models.CASCADE,
        related_name="file_downloads",
        help_text="User who downloaded the file"
    )
    downloaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Download Log - {self.file} by {self.downloaded_by}"


class FileDeletionRequest(models.Model):
    """
    Handles file deletion requests from writers or clients, requiring admin approval.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='file_deletion_request'
    )
    file = models.ForeignKey(OrderFile, on_delete=models.CASCADE)
    requested_by = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name="file_deletion_requests",
        help_text="User who requested the file deletion"
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("approved", "Approved"),
            ("rejected", "Rejected")
        ],
        default="pending"
    )
    requested_at = models.DateTimeField(auto_now_add=True)
    reviewed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        blank=True, related_name="file_deletion_reviews"
    )

    def __str__(self):
        return f"Deletion Request - {self.file} by {self.requested_by}"


class ExternalFileLink(models.Model):
    """
    Stores links for externally uploaded files (Google Drive, Dropbox, etc.) that require admin approval.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='order_external_file_link'
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="external_links"
    )
    uploaded_by = models.ForeignKey(
        'users.User', on_delete=models.CASCADE,
        related_name="external_file_links",
        help_text="User who uploaded the external file link"
    )
    link = models.URLField()
    description = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("approved", "Approved"),
            ("rejected", "Rejected")
        ],
        default="pending"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        blank=True, related_name="external_link_reviews"
    )

    def __str__(self):
        return f"External Link - Order {self.order.id}"


class ExtraServiceFile(models.Model):
    """
    Handles extra service files such as Plagiarism Reports, Smart Papers, etc.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='extra_service_file'
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="extra_service_files"
    )
    category = models.ForeignKey(
        OrderFileCategory,
        on_delete=models.CASCADE,
        related_name="extra_service_files",
        help_text="Category for the extra service file (e.g., Plagiarism Report, Smart Paper)"
    )
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )
    file = models.FileField(upload_to="extra_service_files/")
    created_at = models.DateTimeField(auto_now_add=True)
    is_downloadable = models.BooleanField(default=False)  # Locked until payment is confirmed

    def check_extra_service_download(self):
        """
        Checks if an extra service file is downloadable based on payment status.
        """
        return self.is_downloadable  # Controlled by admin

    def __str__(self):
        category_name = self.category.name if self.category else "Unknown"
        return f"Extra Service File - {category_name} (Order {self.order.id})"


class StyleReferenceFile(models.Model):
    """
    Stores style reference files uploaded by clients to help writers match their writing style.
    These are optional files that clients can upload with previous papers or instructor feedback.
    """
    REFERENCE_TYPE_CHOICES = [
        ('previous_paper', 'Previous Paper'),
        ('instructor_feedback', 'Instructor Feedback'),
        ('style_guide', 'Style Guide'),
        ('sample_work', 'Sample Work'),
    ]
    
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='style_reference_files'
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="style_reference_files",
        help_text="The order this style reference is associated with"
    )
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="uploaded_style_references",
        help_text="Client who uploaded this style reference"
    )
    file = models.FileField(
        upload_to="style_references/",
        help_text="The style reference file (PDF, DOCX, etc.)"
    )
    reference_type = models.CharField(
        max_length=50,
        choices=REFERENCE_TYPE_CHOICES,
        default='previous_paper',
        help_text="Type of style reference (previous paper, instructor feedback, etc.)"
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Optional description or notes about this style reference"
    )
    file_name = models.CharField(
        max_length=255,
        help_text="Original filename"
    )
    file_size = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="File size in bytes"
    )
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the style reference was uploaded"
    )
    is_visible_to_writer = models.BooleanField(
        default=True,
        help_text="Whether the writer can view this style reference"
    )
    
    class Meta:
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['order', 'uploaded_at']),
            models.Index(fields=['order', 'reference_type']),
        ]
        verbose_name = "Style Reference File"
        verbose_name_plural = "Style Reference Files"
    
    def __str__(self):
        return f"Style Reference - {self.get_reference_type_display()} (Order {self.order.id})"
    
    def save(self, *args, **kwargs):
        """Auto-set file_name and file_size if not provided."""
        if self.file and not self.file_name:
            self.file_name = self.file.name.split('/')[-1] if '/' in self.file.name else self.file.name
        if self.file and not self.file_size:
            try:
                self.file_size = self.file.size
            except (AttributeError, FileNotFoundError):
                pass
        
        # Auto-set website from order if not set
        if not self.website and self.order:
            self.website = self.order.website
        
        super().save(*args, **kwargs)
    
    def can_access(self, user):
        """
        Check if a user can access this style reference file.
        - Clients who uploaded it can always access
        - Writers assigned to the order can access if is_visible_to_writer is True
        - Admins, editors, and support can always access
        """
        # Admins, editors, and support can always access
        if user.is_staff or user.groups.filter(name__in=["Support", "Editor"]).exists():
            return True
        
        # Client who uploaded can access
        if self.uploaded_by == user:
            return True
        
        # Writer assigned to the order can access if visible
        if hasattr(user, 'role') and user.role == 'writer':
            if self.order.assigned_writer == user and self.is_visible_to_writer:
                return True
        
        return False