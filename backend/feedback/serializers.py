from __future__ import annotations

from rest_framework import serializers

from .models import FeedbackRequest, FeedbackStatusEvent, FeedbackVote


# ── Category sets per portal surface ─────────────────────────────────────────
SURFACE_CATEGORIES: dict[str, list[str]] = {
    "client": [
        "orders", "payments", "client_experience",
        "file_delivery", "communication", "classes",
        "special_orders", "bug_report", "other",
    ],
    "writer": [
        "writer_workflow", "payout_earnings", "bidding",
        "workload", "file_delivery", "communication",
        "classes", "special_orders", "bug_report", "other",
    ],
    "staff": [
        "orders", "payments", "writer_workflow", "client_experience",
        "cms", "analytics", "support_tools", "admin_tools",
        "automation", "permissions", "classes", "special_orders",
        "bug_report", "other",
    ],
}


class FeedbackStatusEventSerializer(serializers.ModelSerializer):
    changed_by_name = serializers.SerializerMethodField()

    class Meta:
        model = FeedbackStatusEvent
        fields = [
            "id", "from_status", "to_status",
            "changed_by_name", "note", "created_at",
        ]
        read_only_fields = fields

    def get_changed_by_name(self, obj) -> str | None:
        if obj.changed_by:
            return obj.changed_by.get_full_name() or obj.changed_by.username
        return None


class FeedbackRequestListSerializer(serializers.ModelSerializer):
    """Lightweight listing — no internal notes, no vote list."""

    has_voted = serializers.SerializerMethodField()
    requester_display = serializers.SerializerMethodField()
    staff_owner_name = serializers.SerializerMethodField()
    duplicate_of_title = serializers.SerializerMethodField()

    class Meta:
        model = FeedbackRequest
        fields = [
            "id", "title", "request_type", "category", "priority", "status",
            "portal_surface", "requester_display", "requester_role",
            "upvote_count", "has_voted",
            "staff_owner_name", "public_response",
            "duplicate_of", "duplicate_of_title",
            "created_at", "updated_at",
        ]
        read_only_fields = fields

    def get_has_voted(self, obj) -> bool:
        request = self.context.get("request")
        if not request or not request.user or not request.user.is_authenticated:
            return False
        return FeedbackVote.objects.filter(request=obj, voter=request.user).exists()

    def get_requester_display(self, obj) -> str:
        u = obj.requester
        return u.get_full_name() or u.username

    def get_staff_owner_name(self, obj) -> str | None:
        if obj.staff_owner:
            return obj.staff_owner.get_full_name() or obj.staff_owner.username
        return None

    def get_duplicate_of_title(self, obj) -> str | None:
        if obj.duplicate_of_id:
            return obj.duplicate_of.title if obj.duplicate_of else None
        return None


class FeedbackRequestDetailSerializer(FeedbackRequestListSerializer):
    """Full detail — adds status_history. internal_notes only for staff."""

    status_history = FeedbackStatusEventSerializer(many=True, read_only=True)
    internal_notes = serializers.SerializerMethodField()
    responded_by_name = serializers.SerializerMethodField()

    class Meta(FeedbackRequestListSerializer.Meta):
        fields = FeedbackRequestListSerializer.Meta.fields + [
            "description", "internal_notes",
            "linked_order_id", "linked_ticket_id",
            "public_response_at", "responded_by_name",
            "status_history",
        ]
        read_only_fields = fields

    def get_internal_notes(self, obj) -> str:
        request = self.context.get("request")
        if not request:
            return ""
        role = getattr(request.user, "role", "")
        if role in {"admin", "superadmin", "support", "editor"} or request.user.is_staff:
            return obj.internal_notes
        return ""

    def get_responded_by_name(self, obj) -> str | None:
        if obj.responded_by:
            return obj.responded_by.get_full_name() or obj.responded_by.username
        return None


class FeedbackRequestCreateSerializer(serializers.ModelSerializer):
    """Used by clients and writers to submit new requests."""

    class Meta:
        model = FeedbackRequest
        fields = [
            "title", "description", "request_type",
            "category", "priority",
            "linked_order_id", "linked_ticket_id",
        ]

    def validate_category(self, value: str) -> str:
        surface = self.context.get("portal_surface", "")
        allowed = SURFACE_CATEGORIES.get(surface, [c[0] for c in FeedbackRequest.CATEGORY_CHOICES])
        if value not in allowed:
            raise serializers.ValidationError(
                f"Category '{value}' is not available for the {surface} portal."
            )
        return value

    def create(self, validated_data):
        request = self.context["request"]
        surface = self.context.get("portal_surface", "client")
        user = request.user
        website = getattr(user, "website", None)
        if website is None:
            from websites.models.websites import Website
            website = Website.objects.filter(is_active=True).first()

        return FeedbackRequest.objects.create(
            **validated_data,
            requester=user,
            requester_role=getattr(user, "role", ""),
            portal_surface=surface,
            website=website,
        )


class FeedbackTriageUpdateSerializer(serializers.ModelSerializer):
    """Staff-only update: status, owner, notes, duplicate linking."""

    note = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = FeedbackRequest
        fields = [
            "status", "staff_owner", "internal_notes",
            "public_response", "note",
        ]

    def update(self, instance, validated_data):
        note = validated_data.pop("note", "")
        new_status = validated_data.get("status")
        old_status = instance.status

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if new_status and new_status != old_status:
            FeedbackStatusEvent.objects.create(
                request=instance,
                from_status=old_status,
                to_status=new_status,
                changed_by=self.context["request"].user,
                note=note,
            )

        return instance


class FeedbackRequesterUpdateSerializer(serializers.ModelSerializer):
    """Requester-only update: title, description, priority."""

    class Meta:
        model = FeedbackRequest
        fields = ["title", "description", "priority"]
