"""
Serializers for the Mass Email System.

Supports campaign creation, scheduling, attachments,
recipient tracking, and reusable templates.
"""

from rest_framework import serializers
from .models import (
    EmailCampaign,
    EmailRecipient,
    CampaignAttachment,
    EmailTemplate,
    EmailServiceIntegration,
)


class CampaignAttachmentSerializer(serializers.ModelSerializer):
    """
    Serializer for campaign attachments.
    """
    class Meta:
        model = CampaignAttachment
        fields = ['id', 'name', 'file']


class EmailRecipientSerializer(serializers.ModelSerializer):
    """
    Read-only serializer for recipients of a campaign.
    """
    campaign = serializers.SerializerMethodField()
    class Meta:
        model = EmailRecipient
        fields = [
            'id', 'email', 'status', 'campaign',
            'sent_at', 'opened_at', 'error_message'
        ]
        read_only_fields = fields

    def get_campaign(self, obj):
        c = getattr(obj, 'campaign', None)
        if not c:
            return None
        return {
            'id': c.id,
            'title': c.title,
            'subject': c.subject,
            'status': c.status,
            'email_type': c.email_type,
            'sent_time': c.sent_time.isoformat() if c.sent_time else None,
        }


class EmailCampaignListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing campaigns.
    """
    website = serializers.StringRelatedField()
    created_by = serializers.StringRelatedField()
    template_id = serializers.IntegerField(
        required=False, write_only=True,
        help_text="Optional. Populate subject/body from this template."
    )

    def validate(self, attrs):
        template_id = attrs.get("template_id")
        if template_id:
            try:
                template = EmailTemplate.objects.get(id=template_id)
                attrs['subject'] = template.subject
                attrs['body'] = template.body
            except EmailTemplate.DoesNotExist:
                raise serializers.ValidationError("Template not found.")
        return attrs

    class Meta:
        model = EmailCampaign
        fields = [
            'id', 'title', 'subject', 'status',
            'email_type', 'scheduled_time', 'sent_time',
            'website', 'created_by', 'created_at'
        ]


class EmailCampaignDetailSerializer(serializers.ModelSerializer):
    """
    Full detail serializer for campaign view.
    """
    attachments = CampaignAttachmentSerializer(many=True, read_only=True)
    recipients = EmailRecipientSerializer(many=True, read_only=True)
    website = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = EmailCampaign
        fields = [
            'id', 'title', 'subject', 'body',
            'email_type', 'target_roles', 'status',
            'scheduled_time', 'sent_time',
            'website', 'email_provider', 'failure_report',
            'attachments', 'recipients',
            'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'status', 'created_by',
            'created_at', 'updated_at',
            'sent_time', 'failure_report'
        ]


class EmailCampaignCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating/updating campaigns.
    """
    class Meta:
        model = EmailCampaign
        fields = [
            'title', 'subject', 'body',
            'website', 'email_type',
            'target_roles', 'scheduled_time'
        ]

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class EmailTemplateSerializer(serializers.ModelSerializer):
    """
    Serializer for reusable templates.
    """
    class Meta:
        model = EmailTemplate
        fields = [
            'id', 'name', 'subject', 'body',
            'is_global', 'created_by', 'created_at'
        ]
        read_only_fields = ['created_by', 'created_at']


class EmailServiceIntegrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailServiceIntegration
        fields = [
            'id', 'website', 'provider_name',
            'api_key', 'sender_email',
            'sender_name', 'is_active', 'created_at'
        ]
        read_only_fields = ['created_at']