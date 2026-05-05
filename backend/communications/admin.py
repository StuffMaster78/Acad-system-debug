from __future__ import annotations

from django.contrib import admin

from communications.models.audit import CommunicationAuditLog
from communications.models.attachment import CommunicationAttachment
from communications.models.escalation import CommunicationEscalation
from communications.models.edit import CommunicationMessageEdit
from communications.models.moderation import CommunicationModerationFlag
from communications.models.participant import CommunicationParticipant
from communications.models.saved_reply import CommunicationSavedReply
from communications.models.assignment import CommunicationThreadAssignment
from communications.models.policy import CommunicationThreadPolicy
from communications.models.sla import CommunicationThreadSLA
from communications.models.tag import CommunicationThreadTag
from communications.models.tag import CommunicationThreadTagAssignment
from communications.models.link_review import CommunicationLinkReview
from communications.models.screening_rule import CommunicationScreeningRule

@admin.register(CommunicationParticipant)
class CommunicationParticipantAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "website",
        "thread",
        "user",
        "role",
        "can_view",
        "can_send",
        "can_upload",
        "is_observer",
        "joined_at",
        "removed_at",
    )
    list_filter = (
        "role",
        "can_view",
        "can_send",
        "can_upload",
        "is_observer",
        "website",
    )
    search_fields = (
        "user__email",
        "user__username",
        "thread__id",
    )
    readonly_fields = ("joined_at",)


@admin.register(CommunicationAttachment)
class CommunicationAttachmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "website",
        "thread",
        "message",
        "file",
        "uploaded_by",
        "is_visible",
        "requires_moderation",
        "created_at",
    )
    list_filter = (
        "is_visible",
        "requires_moderation",
        "website",
    )
    search_fields = (
        "thread__id",
        "message__id",
        "uploaded_by__email",
        "uploaded_by__username",
    )
    readonly_fields = ("created_at",)


@admin.register(CommunicationThreadPolicy)
class CommunicationThreadPolicyAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "website",
        "thread_kind",
        "allow_client_messages",
        "allow_writer_messages",
        "allow_staff_messages",
        "allow_attachments",
        "require_attachment_moderation",
        "require_message_moderation",
        "is_active",
    )
    list_filter = (
        "website",
        "thread_kind",
        "is_active",
        "allow_attachments",
        "require_attachment_moderation",
        "require_message_moderation",
    )
    search_fields = (
        "thread_kind",
        "website__name",
    )


@admin.register(CommunicationThreadAssignment)
class CommunicationThreadAssignmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "website",
        "thread",
        "assigned_to",
        "assigned_by",
        "is_active",
        "assigned_at",
        "unassigned_at",
    )
    list_filter = (
        "website",
        "is_active",
    )
    search_fields = (
        "thread__id",
        "assigned_to__email",
        "assigned_to__username",
        "assigned_by__email",
        "assigned_by__username",
    )
    readonly_fields = ("assigned_at",)


@admin.register(CommunicationMessageEdit)
class CommunicationMessageEditAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "website",
        "thread",
        "message",
        "edited_by",
        "edited_at",
    )
    list_filter = (
        "website",
        "edited_at",
    )
    search_fields = (
        "thread__id",
        "message__id",
        "edited_by__email",
        "edited_by__username",
    )
    readonly_fields = (
        "previous_body",
        "new_body",
        "edited_at",
    )


@admin.register(CommunicationThreadSLA)
class CommunicationThreadSLAAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "website",
        "thread",
        "first_response_due_at",
        "next_response_due_at",
        "is_breached",
        "breached_at",
    )
    list_filter = (
        "website",
        "is_breached",
    )
    search_fields = ("thread__id",)


@admin.register(CommunicationThreadTag)
class CommunicationThreadTagAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "website",
        "name",
        "color",
        "is_active",
        "created_at",
    )
    list_filter = (
        "website",
        "is_active",
    )
    search_fields = (
        "name",
        "website__name",
    )


@admin.register(CommunicationThreadTagAssignment)
class CommunicationThreadTagAssignmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "website",
        "thread",
        "tag",
        "created_at",
    )
    list_filter = (
        "website",
        "tag",
    )
    search_fields = (
        "thread__id",
        "tag__name",
    )


@admin.register(CommunicationSavedReply)
class CommunicationSavedReplyAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "website",
        "title",
        "category",
        "is_active",
        "created_by",
        "created_at",
    )
    list_filter = (
        "website",
        "category",
        "is_active",
    )
    search_fields = (
        "title",
        "body",
        "category",
        "created_by__email",
        "created_by__username",
    )


@admin.register(CommunicationEscalation)
class CommunicationEscalationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "website",
        "thread",
        "status",
        "escalated_by",
        "resolved_by",
        "escalated_at",
        "resolved_at",
    )
    list_filter = (
        "website",
        "status",
    )
    search_fields = (
        "thread__id",
        "reason",
        "escalated_by__email",
        "escalated_by__username",
    )


@admin.register(CommunicationAuditLog)
class CommunicationAuditLogAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "website",
        "thread",
        "message",
        "actor",
        "action",
        "created_at",
    )
    list_filter = (
        "website",
        "action",
        "created_at",
    )
    search_fields = (
        "thread__id",
        "message__id",
        "actor__email",
        "actor__username",
    )
    readonly_fields = (
        "website",
        "thread",
        "message",
        "actor",
        "action",
        "details",
        "ip_address",
        "user_agent",
        "created_at",
    )


@admin.register(CommunicationModerationFlag)
class CommunicationModerationFlagAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "website",
        "thread",
        "message",
        "status",
        "severity",
        "reason",
        "created_by",
        "resolved_by",
        "created_at",
        "resolved_at",
    )
    list_filter = (
        "website",
        "status",
        "severity",
    )
    search_fields = (
        "thread__id",
        "message__id",
        "reason",
        "details",
        "created_by__email",
        "created_by__username",
    )

@admin.register(CommunicationScreeningRule)
class CommunicationScreeningRuleAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "website",
        "name",
        "pattern",
        "match_type",
        "action",
        "severity",
        "is_active",
        "is_platform_rule",
        "created_by",
        "updated_by",
        "created_at",
    )
    list_filter = (
        "website",
        "match_type",
        "action",
        "severity",
        "is_active",
        "is_platform_rule",
    )
    search_fields = (
        "name",
        "pattern",
        "reason",
        "created_by__email",
        "created_by__username",
        "updated_by__email",
        "updated_by__username",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )


@admin.register(CommunicationLinkReview)
class CommunicationLinkReviewAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "website",
        "thread",
        "message",
        "domain",
        "status",
        "submitted_by",
        "reviewed_by",
        "created_at",
        "reviewed_at",
    )
    list_filter = (
        "website",
        "status",
        "domain",
        "created_at",
        "reviewed_at",
    )
    search_fields = (
        "url",
        "domain",
        "thread__id",
        "message__id",
        "submitted_by__email",
        "submitted_by__username",
        "reviewed_by__email",
        "reviewed_by__username",
    )
    readonly_fields = (
        "website",
        "thread",
        "message",
        "url",
        "domain",
        "submitted_by",
        "created_at",
        "updated_at",
    )