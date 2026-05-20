"""
Serializers for the Mass Email System.

Supports campaign creation, scheduling, attachments,
recipient tracking, and reusable templates.
"""

from rest_framework import serializers

from mass_emails.services.attachment_service import CampaignAttachmentService

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
    uploaded_file = serializers.FileField(
        write_only=True,
        required=False,
    )
    campaign = serializers.PrimaryKeyRelatedField(
        queryset=EmailCampaign.objects.all(),
        write_only=True,
    )
    attachment_id = serializers.IntegerField(
        source="attachment.id",
        read_only=True,
    )
    file_name = serializers.CharField(
        source="attachment.managed_file.original_name",
        read_only=True,
    )
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = CampaignAttachment
        fields = [
            "id",
            "campaign",
            "name",
            "attachment_id",
            "file_name",
            "file_url",
            "uploaded_file",
            "created_by",
            "created_at",
        ]
        read_only_fields = [
            "attachment_id",
            "file_name",
            "file_url",
            "created_by",
            "created_at",
        ]

    def get_file_url(self, obj):
        managed_file = getattr(obj.attachment, "managed_file", None)
        if not managed_file or not managed_file.file:
            return None
        try:
            return managed_file.file.url
        except ValueError:
            return None

    def create(self, validated_data):
        uploaded_file = validated_data.pop("uploaded_file", None)
        campaign = validated_data.pop("campaign")
        if uploaded_file is None:
            raise serializers.ValidationError(
                {"uploaded_file": "This field is required."}
            )

        request = self.context.get("request")
        uploaded_by = getattr(request, "user", None)
        return CampaignAttachmentService.upload_attachment(
            campaign=campaign,
            uploaded_by=uploaded_by,
            uploaded_file=uploaded_file,
            name=validated_data.get("name", ""),
        )


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
    template_id = serializers.IntegerField(
        required=False,
        write_only=True,
        help_text="Optional. Populate subject/body from this template.",
    )

    class Meta:
        model = EmailCampaign
        fields = [
            'title', 'subject', 'body',
            'website', 'email_type',
            'target_roles', 'scheduled_time',
            'template_id',
        ]

    def validate_target_roles(self, value):
        allowed = {"client", "writer"}
        roles = value or []
        invalid = sorted(set(roles) - allowed)
        if invalid:
            invalid_roles = ", ".join(invalid)
            raise serializers.ValidationError(
                "Mass emails can only target clients or writers. "
                f"Invalid: {invalid_roles}"
            )
        if not roles:
            raise serializers.ValidationError(
                "At least one target role is required."
            )
        return sorted(set(roles))

    def validate(self, attrs):
        template_id = attrs.pop("template_id", None)
        if template_id:
            try:
                template = EmailTemplate.objects.get(id=template_id)
            except EmailTemplate.DoesNotExist as exc:
                raise serializers.ValidationError(
                    "Template not found."
                ) from exc
            attrs.setdefault("subject", template.subject)
            attrs.setdefault("body", template.body)
        return attrs

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
