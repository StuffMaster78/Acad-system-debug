from django.contrib import admin

from files_management.models import (
    ExternalFileLink,
    FileAccessGrant,
    FileAttachment,
    FileCategory,
    FileDeletionRequest,
    FileDownloadLog,
    FilePolicy,
    FileProcessingJob,
    FileScanResult,
    FileVersion,
    ManagedFile,
)


@admin.register(FileCategory)
class FileCategoryAdmin(admin.ModelAdmin):
    """
    Admin interface for tenant file categories.

    Categories help staff organize files by business meaning while still
    allowing services to enforce stricter purpose based rules.
    """

    list_display = (
        "name",
        "code",
        "website",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active", "website")
    search_fields = ("name", "code", "description")
    ordering = ("name",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(ManagedFile)
class ManagedFileAdmin(admin.ModelAdmin):
    """
    Admin interface for uploaded files.

    Staff should use this mainly for inspection and support workflows.
    Business actions such as deletion, replacement, or access grants
    should still go through services.
    """

    list_display = (
        "original_name",
        "website",
        "uploaded_by",
        "file_kind",
        "mime_type",
        "file_size",
        "lifecycle_status",
        "scan_status",
        "is_public",
        "created_at",
    )
    list_filter = (
        "website",
        "file_kind",
        "lifecycle_status",
        "scan_status",
        "is_public",
    )
    search_fields = (
        "original_name",
        "mime_type",
        "checksum",
        "storage_key",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    ordering = ("-created_at",)


@admin.register(FileAttachment)
class FileAttachmentAdmin(admin.ModelAdmin):
    """
    Admin interface for file attachments.

    Attachments are where files gain business meaning. A file can exist
    once and be attached to orders, messages, profiles, CMS entries, or
    any other supported domain object.
    """

    list_display = (
        "id",
        "website",
        "purpose",
        "visibility",
        "is_primary",
        "is_active",
        "attached_by",
        "attached_at",
    )
    list_filter = (
        "website",
        "purpose",
        "visibility",
        "is_primary",
        "is_active",
    )
    search_fields = (
        "display_name",
        "notes",
        "managed_file__original_name",
        "external_link__title",
        "external_link__url",
    )
    readonly_fields = (
        "attached_at",
        "updated_at",
    )
    ordering = ("-attached_at",)


@admin.register(FileVersion)
class FileVersionAdmin(admin.ModelAdmin):
    """
    Admin interface for file version history.
    """

    list_display = (
        "file",
        "version_number",
        "replaced_file",
        "created_by",
        "created_at",
    )
    list_filter = ("created_at",)
    search_fields = (
        "file__original_name",
        "replaced_file__original_name",
        "notes",
    )
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)


@admin.register(FileDownloadLog)
class FileDownloadLogAdmin(admin.ModelAdmin):
    """
    Admin interface for file download audit logs.

    Download logs are evidence. They should generally be read only from
    admin to preserve audit integrity.
    """

    list_display = (
        "file",
        "downloaded_by",
        "ip_address",
        "downloaded_at",
    )
    list_filter = ("downloaded_at",)
    search_fields = (
        "file__original_name",
        "downloaded_by__email",
        "ip_address",
        "user_agent",
    )
    readonly_fields = (
        "file",
        "downloaded_by",
        "ip_address",
        "user_agent",
        "downloaded_at",
    )
    ordering = ("-downloaded_at",)

    def has_add_permission(self, request) -> bool:
        return False


@admin.register(ExternalFileLink)
class ExternalFileLinkAdmin(admin.ModelAdmin):
    """
    Admin interface for externally hosted file links.

    Staff should review external links before normal users rely on them.
    This helps reduce phishing, broken links, unsafe sharing, and files
    that do not match the stated purpose.
    """

    list_display = (
        "title",
        "provider",
        "website",
        "submitted_by",
        "review_status",
        "reviewed_by",
        "is_active",
        "created_at",
    )
    list_filter = (
        "website",
        "provider",
        "review_status",
        "is_active",
    )
    search_fields = (
        "title",
        "url",
        "submitted_by__email",
        "review_note",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    ordering = ("-created_at",)


@admin.register(FileDeletionRequest)
class FileDeletionRequestAdmin(admin.ModelAdmin):
    """
    Admin interface for governed file deletion requests.

    Clients and writers should request deletion instead of deleting files
    directly. Staff review protects evidence, audit trails, and business
    workflows.
    """

    list_display = (
        "managed_file",
        "attachment",
        "website",
        "requested_by",
        "scope",
        "status",
        "reviewed_by",
        "created_at",
    )
    list_filter = (
        "website",
        "scope",
        "status",
        "created_at",
    )
    search_fields = (
        "managed_file__original_name",
        "requested_by__email",
        "reason",
        "admin_comment",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
        "completed_at",
    )
    ordering = ("-created_at",)


@admin.register(FileAccessGrant)
class FileAccessGrantAdmin(admin.ModelAdmin):
    """
    Admin interface for explicit file access grants.

    Grants should be used sparingly. Normal access should come from
    domain policies such as order, message, profile, CMS, or support
    policies.
    """

    list_display = (
        "managed_file",
        "grantee",
        "action",
        "website",
        "granted_by",
        "expires_at",
        "revoked_at",
        "created_at",
    )
    list_filter = (
        "website",
        "action",
        "expires_at",
        "revoked_at",
    )
    search_fields = (
        "managed_file__original_name",
        "grantee__email",
        "granted_by__email",
        "reason",
    )
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)


@admin.register(FilePolicy)
class FilePolicyAdmin(admin.ModelAdmin):
    """
    Admin interface for tenant file policies.

    These policies allow each website to safely configure accepted file
    extensions, MIME types, size limits, external link rules, and review
    requirements per file purpose.
    """

    list_display = (
        "name",
        "website",
        "purpose",
        "max_file_size_bytes",
        "allow_external_links",
        "external_links_require_review",
        "is_active",
    )
    list_filter = (
        "website",
        "purpose",
        "allow_external_links",
        "external_links_require_review",
        "is_active",
    )
    search_fields = ("name", "purpose")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("website", "purpose")


@admin.register(FileScanResult)
class FileScanResultAdmin(admin.ModelAdmin):
    """
    Admin interface for file scan results.
    """

    list_display = (
        "managed_file",
        "scan_type",
        "status",
        "provider",
        "scanned_at",
        "created_at",
    )
    list_filter = (
        "scan_type",
        "status",
        "provider",
        "scanned_at",
    )
    search_fields = (
        "managed_file__original_name",
        "scan_type",
        "provider",
        "summary",
    )
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)


@admin.register(FileProcessingJob)
class FileProcessingJobAdmin(admin.ModelAdmin):
    """
    Admin interface for background file processing jobs.
    """

    list_display = (
        "managed_file",
        "job_type",
        "status",
        "attempts",
        "scheduled_at",
        "started_at",
        "completed_at",
    )
    list_filter = (
        "job_type",
        "status",
        "scheduled_at",
        "completed_at",
    )
    search_fields = (
        "managed_file__original_name",
        "job_type",
        "last_error",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    ordering = ("-created_at",)