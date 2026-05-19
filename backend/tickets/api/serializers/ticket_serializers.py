from __future__ import annotations

from django.contrib.auth import get_user_model
from rest_framework import serializers

from tickets.models import Ticket, TicketLog
from tickets.services import TicketService
from websites.models.websites import Website


class TicketLogSerializer(serializers.ModelSerializer):
    performed_by_name = serializers.CharField(
        source="performed_by.username",
        read_only=True,
    )

    class Meta:
        model = TicketLog
        fields = [
            "id",
            "ticket",
            "website",
            "action",
            "performed_by",
            "performed_by_name",
            "timestamp",
        ]
        read_only_fields = fields


class TicketListSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(
        source="created_by.username",
        read_only=True,
    )
    assigned_to_name = serializers.CharField(
        source="assigned_to.username",
        read_only=True,
    )

    class Meta:
        model = Ticket
        fields = [
            "id",
            "title",
            "description",
            "created_by",
            "created_by_name",
            "assigned_to",
            "assigned_to_name",
            "website",
            "status",
            "priority",
            "category",
            "is_escalated",
            "has_sla",
            "resolution_time",
            "content_type",
            "object_id",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class TicketDetailSerializer(TicketListSerializer):
    logs = TicketLogSerializer(many=True, read_only=True)

    class Meta(TicketListSerializer.Meta):
        fields = TicketListSerializer.Meta.fields + ["logs"]


class TicketCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    description = serializers.CharField()
    website = serializers.PrimaryKeyRelatedField(
        queryset=Website.objects.all(),
        required=False,
        allow_null=True,
    )
    priority = serializers.ChoiceField(
        choices=Ticket.PRIORITY_CHOICES,
        default="medium",
    )
    category = serializers.ChoiceField(
        choices=Ticket.CATEGORY_CHOICES,
        default="general",
    )
    created_by = serializers.PrimaryKeyRelatedField(
        queryset=get_user_model().objects.all(),
        required=False,
        allow_null=True,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and getattr(request.user, "role", None) not in {
            "admin",
            "superadmin",
            "support",
            "editor",
        }:
            self.fields["created_by"].read_only = True

    def create(self, validated_data):
        request = self.context["request"]
        return TicketService.create_ticket(
            actor=request.user,
            **validated_data,
        )


class TicketUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = [
            "status",
            "priority",
            "website",
            "assigned_to",
            "is_escalated",
            "category",
        ]


class TicketAssignSerializer(serializers.Serializer):
    assigned_to = serializers.PrimaryKeyRelatedField(
        queryset=get_user_model().objects.all(),
    )


class TicketCloseSerializer(serializers.Serializer):
    reason = serializers.CharField(required=False, allow_blank=True)


class TicketReopenSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=(("open", "Open"), ("in_progress", "In Progress")),
        default="open",
    )
    reason = serializers.CharField(required=False, allow_blank=True)
