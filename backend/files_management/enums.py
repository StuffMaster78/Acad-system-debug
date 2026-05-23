"""
Enumerations for the files_management app.

These values are stored in the database, exposed through APIs, and used
by domain policy classes. Rename values carefully because migrations and
existing rows may depend on them.
"""

from django.db import models


class FileKind(models.TextChoices):
    """High-level category of a managed file."""

    IMAGE = "image", "Image"
    DOCUMENT = "document", "Document"
    VIDEO = "video", "Video"
    AUDIO = "audio", "Audio"
    ARCHIVE = "archive", "Archive"
    EXTERNAL = "external", "External"

    CMS_IMAGE = "cms_image", "CMS Image"
    CMS_ATTACHMENT = "cms_attachment", "CMS Attachment"
    CMS_MEDIA = "cms_media", "CMS Media"

    USER_AVATAR = "user_avatar", "User Avatar"
    AUTHOR_PHOTO = "author_photo", "Author Profile Photo"

    ORDER_FILE = "order_file", "Order File"
    ORDER_ATTACHMENT = "order_attachment", "Order Attachment"
    WRITER_DELIVERABLE = "writer_deliverable", "Writer Deliverable"
    REVISION_FILE = "revision_file", "Revision File"

    MESSAGE_ATTACHMENT = "message_attachment", "Message Attachment"
    TICKET_ATTACHMENT = "ticket_attachment", "Ticket Attachment"

    CLASS_MATERIAL = "class_material", "Class Material"
    SPECIAL_ORDER_FILE = "special_order_file", "Special Order File"

    NEWSLETTER_IMAGE = "newsletter_image", "Newsletter Image"

    SYSTEM_BACKUP = "system_backup", "System Backup"
    SYSTEM_EXPORT = "system_export", "System Export"

    OTHER = "other", "Other"


class FileLifecycleStatus(models.TextChoices):
    """Lifecycle state of a managed file."""

    UPLOADING = "uploading", "Uploading"
    PROCESSING = "processing", "Processing"
    ACTIVE = "active", "Active"
    PENDING_REVIEW = "pending_review", "Pending Review"
    QUARANTINED = "quarantined", "Quarantined"
    ARCHIVED = "archived", "Archived"
    PENDING_DELETION = "pending_deletion", "Pending Deletion"
    DELETED = "deleted", "Deleted"


class FileScanStatus(models.TextChoices):
    """Virus, malware, moderation, or safety scan state."""

    NOT_SCANNED = "not_scanned", "Not Scanned"
    QUEUED = "queued", "Queued for Scan"
    SCANNING = "scanning", "Scanning"
    CLEAN = "clean", "Clean"
    INFECTED = "infected", "Infected"
    FAILED = "failed", "Failed"
    FLAGGED = "flagged", "Flagged"
    ERROR = "error", "Error"
    SKIPPED = "skipped", "Skipped"
    PASSED = "passed", "Passed"


class FileProcessingStatus(models.TextChoices):
    """Background processing job state."""

    PENDING = "pending", "Pending"
    RUNNING = "running", "Running"
    SUCCEEDED = "succeeded", "Succeeded"
    FAILED = "failed", "Failed"
    CANCELLED = "cancelled", "Cancelled"


class FilePurpose(models.TextChoices):
    """Business reason a file is attached to a domain object."""

    ORDER_INSTRUCTION = "order_instruction", "Order Instruction"
    ORDER_REFERENCE = "order_reference", "Order Reference"
    ORDER_DRAFT = "order_draft", "Order Draft"
    ORDER_FINAL = "order_final", "Order Final"
    ORDER_REVISION = "order_revision", "Order Revision"
    STYLE_REFERENCE = "style_reference", "Style Reference"
    EXTRA_SERVICE_FILE = "extra_service_file", "Extra Service File"

    MESSAGE_ATTACHMENT = "message_attachment", "Message Attachment"
    SUPPORT_ATTACHMENT = "support_attachment", "Support Attachment"
    DISPUTE_EVIDENCE = "dispute_evidence", "Dispute Evidence"

    PROFILE_AVATAR = "profile_avatar", "Profile Avatar"
    PROFILE_PHOTO = "profile_photo", "Profile Photo"
    WRITER_SAMPLE = "writer_sample", "Writer Sample"
    VERIFICATION_DOCUMENT = "verification_document", "Verification Document"

    CMS_FEATURED_IMAGE = "cms_featured_image", "CMS Featured Image"
    CMS_INLINE_IMAGE = "cms_inline_image", "CMS Inline Image"
    CMS_VIDEO = "cms_video", "CMS Video"
    CMS_DOWNLOAD = "cms_download", "CMS Download"
    CMS_SAMPLE_WORK = "cms_sample_work", "CMS Sample Work"

    CLASS_RESOURCE = "class_resource", "Class Resource"
    CLASS_ASSIGNMENT = "class_assignment", "Class Assignment"
    CLASS_SUBMISSION = "class_submission", "Class Submission"

    PAYMENT_PROOF = "payment_proof", "Payment Proof"
    INVOICE = "invoice", "Invoice"
    REFUND_EVIDENCE = "refund_evidence", "Refund Evidence"
    PAYOUT_EVIDENCE = "payout_evidence", "Payout Evidence"

    MASS_EMAIL_ATTACHMENT = "mass_email_attachment", "Mass Email Attachment"

    ADMIN_INTERNAL = "admin_internal", "Admin Internal"
    LEGAL_DOCUMENT = "legal_document", "Legal Document"
    BULK_IMPORT = "bulk_import", "Bulk Import"
    EXPORT_FILE = "export_file", "Export File"


class FileVisibility(models.TextChoices):
    """Visibility hint used by file access policies."""

    PRIVATE = "private", "Private"
    PUBLIC = "public", "Public"
    STAFF_ONLY = "staff_only", "Staff Only"
    OWNER_ONLY = "owner_only", "Owner Only"
    TENANT_STAFF = "tenant_staff", "Tenant Staff"
    INTERNAL_ONLY = "internal_only", "Internal Only"

    ORDER_PARTICIPANTS = "order_participants", "Order Participants"
    CONVERSATION_PARTICIPANTS = (
        "conversation_participants",
        "Conversation Participants",
    )
    WRITER_AND_STAFF = "writer_and_staff", "Writer And Staff"
    CLIENT_AND_STAFF = "client_and_staff", "Client And Staff"
    CLIENT_WRITER_STAFF = "client_writer_staff", "Client Writer Staff"
    CMS_PUBLIC = "cms_public", "CMS Public"


class FileAccessAction(models.TextChoices):
    """Action requested against a file."""

    VIEW = "view", "View"
    DOWNLOAD = "download", "Download"
    PREVIEW = "preview", "Preview"
    REPLACE = "replace", "Replace"
    DELETE = "delete", "Delete"
    ATTACH = "attach", "Attach"
    DETACH = "detach", "Detach"


class FileAccessType(models.TextChoices):
    """Recorded access event type for audit logs."""

    VIEW = "view", "Viewed"
    DOWNLOAD = "download", "Downloaded"
    PREVIEW = "preview", "Preview Generated"
    UPLOAD = "upload", "Uploaded"
    UPDATE = "update", "Updated"
    DELETE = "delete", "Deleted"
    SCAN = "scan", "Virus Scanned"
    DERIVE = "derive", "Derivative Generated"


class BucketType(models.TextChoices):
    """Logical bucket categories."""

    TENANT_PUBLIC = "tenant_public", "Tenant Public Files"
    TENANT_PRIVATE = "tenant_private", "Tenant Private Files"
    ORDER_FILES = "order_files", "Order Files"
    WRITER_DELIVERABLES = "writer_deliverables", "Writer Deliverables"
    CMS_ATTACHMENTS = "cms_attachments", "CMS Attachments"
    CMS_MEDIA = "cms_media", "CMS Media"
    USER_AVATARS = "user_avatars", "User Avatars"
    SYSTEM = "system", "System Files"


class RetentionPolicy(models.TextChoices):
    """How long a file is kept before deletion eligibility."""

    FOREVER = "forever", "Keep Forever"
    DAYS_30 = "30_days", "Delete After 30 Days"
    DAYS_90 = "90_days", "Delete After 90 Days"
    YEAR_1 = "1_year", "Delete After 1 Year"
    ORDER_COMPLETE_30 = "order_complete_30", "30 Days After Order Completion"
    ORDER_COMPLETE_90 = "order_complete_90", "90 Days After Order Completion"


class DerivativeType(models.TextChoices):
    """Generated derivative type for transformed files."""

    ORIGINAL = "", "Original"
    THUMBNAIL_SM = "thumbnail_sm", "Small Thumbnail"
    THUMBNAIL_MD = "thumbnail_md", "Medium Thumbnail"
    THUMBNAIL_LG = "thumbnail_lg", "Large Thumbnail"
    PREVIEW_PDF = "preview_pdf", "PDF Preview"
    OPTIMIZED = "optimized", "Optimized Version"
    WEBP = "webp", "WebP Version"


class ExternalFileProvider(models.TextChoices):
    """Supported external file providers."""

    GOOGLE_DRIVE = "google_drive", "Google Drive"
    GOOGLE_DOCS = "google_docs", "Google Docs"
    GOOGLE_SHEETS = "google_sheets", "Google Sheets"
    GOOGLE_SLIDES = "google_slides", "Google Slides"
    DROPBOX = "dropbox", "Dropbox"
    ONE_DRIVE = "one_drive", "OneDrive"
    YOUTUBE = "youtube", "YouTube"
    VIMEO = "vimeo", "Vimeo"
    LOOM = "loom", "Loom"
    OTHER = "other", "Other"


class ExternalFileReviewStatus(models.TextChoices):
    """Staff review status for external file links."""

    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"
    EXPIRED = "expired", "Expired"


class DeletionRequestStatus(models.TextChoices):
    """Status of a file deletion request."""

    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"
    COMPLETED = "completed", "Completed"
    CANCELLED = "cancelled", "Cancelled"


class DeletionRequestScope(models.TextChoices):
    """Defines what an approved deletion request should remove."""

    DETACH_ONLY = "detach_only", "Detach Only"
    ARCHIVE_FILE = "archive_file", "Archive File"
    DELETE_FILE = "delete_file", "Delete File"