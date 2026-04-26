"""
Enumerations for the files_management app.

The values in this module are intentionally explicit because they are
stored in the database, exposed through APIs, and used by domain policy
classes.
"""

from django.db import models


class FileKind(models.TextChoices):
    """
    High level type of the managed file.

    The kind is used for validation, previews, processing jobs, and UI
    grouping. It should not be used as the only access control input.
    """

    IMAGE = "image", "Image"
    DOCUMENT = "document", "Document"
    VIDEO = "video", "Video"
    AUDIO = "audio", "Audio"
    ARCHIVE = "archive", "Archive"
    EXTERNAL = "external", "External"
    OTHER = "other", "Other"


class FileLifecycleStatus(models.TextChoices):
    """
    Lifecycle status of a managed file.

    Files are soft controlled through status transitions. Physical
    deletion should be delayed and handled by retention aware services.
    """

    ACTIVE = "active", "Active"
    PENDING_REVIEW = "pending_review", "Pending Review"
    QUARANTINED = "quarantined", "Quarantined"
    ARCHIVED = "archived", "Archived"
    DELETED = "deleted", "Deleted"


class FilePurpose(models.TextChoices):
    """
    Business purpose of a file attachment.

    Purpose explains why a file is attached to a domain object. It helps
    APIs, frontend clients, policies, and audit flows understand context.
    """

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

    ADMIN_INTERNAL = "admin_internal", "Admin Internal"
    LEGAL_DOCUMENT = "legal_document", "Legal Document"
    BULK_IMPORT = "bulk_import", "Bulk Import"
    EXPORT_FILE = "export_file", "Export File"


class FileVisibility(models.TextChoices):
    """
    Visibility level for a file attachment.

    Visibility is a broad access hint. Final access decisions should
    still be delegated to file access services and domain policies.
    """

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
    """
    Access action requested against a file.
    """

    VIEW = "view", "View"
    DOWNLOAD = "download", "Download"
    PREVIEW = "preview", "Preview"
    REPLACE = "replace", "Replace"
    DELETE = "delete", "Delete"
    ATTACH = "attach", "Attach"
    DETACH = "detach", "Detach"


class FileScanStatus(models.TextChoices):
    """
    Result status for antivirus, moderation, or processing scans.
    """

    NOT_SCANNED = "not_scanned", "Not Scanned"
    PENDING = "pending", "Pending"
    PASSED = "passed", "Passed"
    FAILED = "failed", "Failed"
    FLAGGED = "flagged", "Flagged"
    ERROR = "error", "Error"


class FileProcessingStatus(models.TextChoices):
    """
    Status for background processing jobs.
    """

    PENDING = "pending", "Pending"
    RUNNING = "running", "Running"
    SUCCEEDED = "succeeded", "Succeeded"
    FAILED = "failed", "Failed"
    CANCELLED = "cancelled", "Cancelled"


# class ExternalFileProvider(models.TextChoices):
#     """
#     Supported external file providers.

#     These values allow the system to manage files that are referenced
#     externally instead of uploaded into platform storage.
#     """

#     GOOGLE_DRIVE = "google_drive", "Google Drive"
#     DROPBOX = "dropbox", "Dropbox"
#     ONE_DRIVE = "one_drive", "OneDrive"
#     YOUTUBE = "youtube", "YouTube"
#     VIMEO = "vimeo", "Vimeo"
#     LOOM = "loom", "Loom"
#     OTHER = "other", "Other"


class DeletionRequestStatus(models.TextChoices):
    """
    Status of a file deletion request.
    """

    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"
    COMPLETED = "completed", "Completed"
    CANCELLED = "cancelled", "Cancelled"


class ExternalFileProvider(models.TextChoices):
    """
    Supported external file providers.
    """

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
    """
    Staff review status for external file links.
    """

    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"
    EXPIRED = "expired", "Expired"

class DeletionRequestScope(models.TextChoices):
    """
    Defines what an approved deletion request should remove.
    """

    DETACH_ONLY = "detach_only", "Detach Only"
    ARCHIVE_FILE = "archive_file", "Archive File"
    DELETE_FILE = "delete_file", "Delete File"