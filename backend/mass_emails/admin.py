"""
Django admin configuration for the Mass Email System.
"""

from django.contrib import admin
from .models import (
    EmailCampaign,
    EmailRecipient,
    CampaignAttachment,
    EmailTemplate,
    EmailServiceIntegration,
)
from rest_framework import filters, generics


class CampaignAttachmentInline(admin.TabularInline):
    """
    Inline attachment manager for EmailCampaign.
    """
    model = CampaignAttachment
    extra = 0


class EmailRecipientInline(admin.TabularInline):
    """
    Inline view for email recipients in a campaign.
    """
    model = EmailRecipient
    extra = 0
    can_delete = False
    readonly_fields = (
        'email', 'status', 'sent_at', 'opened_at', 'error_message'
    )
    show_change_link = True


@admin.register(EmailCampaign)
class EmailCampaignAdmin(admin.ModelAdmin):
    """
    Admin interface for managing marketing campaigns.
    """
    list_display = (
        'title', 'website', 'email_type', 'status',
        'scheduled_time', 'sent_time', 'created_by'
    )
    list_filter = ('status', 'email_type', 'website')
    search_fields = ('title', 'subject', 'body')
    autocomplete_fields = ('created_by', 'website')
    readonly_fields = ('created_at', 'updated_at', 'sent_time')
    inlines = [CampaignAttachmentInline, EmailRecipientInline]

    fieldsets = (
        (None, {
            'fields': (
                'title', 'subject', 'body',
                'website', 'email_type', 'target_roles'
            )
        }),
        ("Schedule & Status", {
            'fields': (
                'status', 'scheduled_time',
                'sent_time', 'email_provider', 'failure_report'
            )
        }),
        ("Metadata", {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
    )


@admin.register(EmailRecipient)
class EmailRecipientAdmin(admin.ModelAdmin):
    """
    Admin view for individual email recipients.
    """
    list_display = (
        'email', 'campaign', 'status', 'sent_at', 'opened_at'
    )
    list_filter = ('status', 'campaign__website')
    search_fields = ('email',)
    autocomplete_fields = ('user', 'campaign')


@admin.register(CampaignAttachment)
class CampaignAttachmentAdmin(admin.ModelAdmin):
    """
    Admin view for campaign file attachments.
    """
    list_display = ('name', 'campaign', 'file')
    autocomplete_fields = ('campaign',)


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    """
    Admin view for reusable email templates.
    """
    list_display = (
        'name', 'subject', 'is_global', 'created_by', 'created_at'
    )
    list_filter = ('is_global',)
    search_fields = ('name', 'subject', 'body')
    autocomplete_fields = ('created_by',)
    readonly_fields = ('created_at',)

@admin.register(EmailServiceIntegration)
class EmailServiceIntegrationAdmin(admin.ModelAdmin):
    list_display = (
        'website', 'provider_name', 'sender_email',
        'is_active', 'created_at'
    )
    list_filter = ('provider_name', 'is_active')
    search_fields = ('sender_email',)