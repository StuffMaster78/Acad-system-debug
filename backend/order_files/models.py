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
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='order_file_category'
    )
    name = models.CharField(max_length=100, unique=True)
    allowed_extensions = models.JSONField(default=list)  # ["pdf", "docx", "xlsx"]
    is_final_draft = models.BooleanField(default=False)  # True if category is Final Draft
    is_extra_service = models.BooleanField(default=False)  # True if for extra services

    def __str__(self):
        return self.name


class OrderFile(models.Model):
    """
    Stores uploaded order files with admin & support-controlled download restrictions.
    """
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

    def check_download_access(self, user):
        """
        Ensures that Admins, Editors, and Support can access and download files.
        """
        # Admins, Editors, and Support can always download
        if user.is_staff or user.groups.filter(name__in=["Support", "Editor"]).exists():
            return True

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

    def __str__(self):
        category_name = self.category.name if self.category else "Uncategorized"
        return f"{category_name} - Order {self.order.id}"


class FileDownloadLog(models.Model):
    """
    Tracks file downloads for security and audit purposes.
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