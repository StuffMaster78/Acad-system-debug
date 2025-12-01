from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from fines.models import (
    Fine,
    FineAppeal,
    FineStatus,
    FineAppealEvent,
    FineAppealEvidence,
)
from orders.models import Order

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user-related fields in fine objects."""

    class Meta:
        model = User
        fields = ["id", "username", "email"]


class FineAppealEvidenceSerializer(serializers.ModelSerializer):
    """Serializer for evidence attachments tied to an appeal."""

    uploaded_by = UserSerializer(read_only=True)
    file_url = serializers.SerializerMethodField()
    file_name = serializers.SerializerMethodField()

    class Meta:
        model = FineAppealEvidence
        fields = [
            "id",
            "description",
            "file",
            "file_url",
            "file_name",
            "uploaded_at",
            "uploaded_by",
            "event_id",
        ]
        read_only_fields = [
            "id",
            "file_url",
            "file_name",
            "uploaded_at",
            "uploaded_by",
            "event_id",
        ]
        extra_kwargs = {
            "file": {"write_only": True},
        }

    def get_file_url(self, obj):
        if not obj.file:
            return None
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.file.url)
        return obj.file.url

    def get_file_name(self, obj):
        if not obj.file:
            return None
        return obj.file.name.split("/")[-1]


class FineAppealEventSerializer(serializers.ModelSerializer):
    """Serializer for appeal timeline entries."""

    actor = UserSerializer(read_only=True)
    attachments = FineAppealEvidenceSerializer(
        many=True, read_only=True, source="attachments"
    )

    class Meta:
        model = FineAppealEvent
        fields = [
            "id",
            "event_type",
            "message",
            "metadata",
            "created_at",
            "actor",
            "actor_role",
            "attachments",
        ]
        read_only_fields = fields


class FineSerializer(serializers.ModelSerializer):
    """
    Serializer for Fine model with support for read/write operations.

    Includes validation for fine amounts and ensures status integrity.
    """

    issued_by = UserSerializer(read_only=True)
    waived_by = UserSerializer(read_only=True)
    order_id = serializers.IntegerField(write_only=True, required=False)
    order = serializers.IntegerField(source="order.id", read_only=True)
    order_topic = serializers.CharField(source="order.topic", read_only=True)
    writer_username = serializers.CharField(source="order.assigned_writer.username", read_only=True, allow_null=True)
    fine_type_name = serializers.CharField(source="fine_type_config.name", read_only=True, allow_null=True)
    fine_type_code = serializers.CharField(source="fine_type_config.code", read_only=True, allow_null=True)
    has_appeal = serializers.SerializerMethodField()
    can_dispute = serializers.SerializerMethodField()
    appeal = serializers.SerializerMethodField()

    class Meta:
        model = Fine
        fields = [
            "id",
            "order_id",
            "order",
            "order_topic",
            "writer_username",
            "fine_type",
            "fine_type_config",
            "fine_type_name",
            "fine_type_code",
            "amount",
            "reason",
            "status",
            "imposed_at",
            "waived_by",
            "waived_at",
            "waiver_reason",
            "resolved",
            "resolved_at",
            "resolved_reason",
            "has_appeal",
            "can_dispute",
            "appeal",
        ]
        read_only_fields = [
            "status",
            "imposed_at",
            "waived_by",
            "waived_at",
            "waiver_reason",
            "resolved",
            "resolved_at",
            "resolved_reason",
            "has_appeal",
            "can_dispute",
            "appeal",
        ]
    
    def get_has_appeal(self, obj):
        """Check if fine has an appeal/dispute."""
        return hasattr(obj, 'appeal')
    
    def get_can_dispute(self, obj):
        """Check if fine can be disputed."""
        return obj.status == FineStatus.ISSUED

    def validate_amount(self, value):
        """Ensure the fine amount is positive."""
        if value <= 0:
            raise serializers.ValidationError(
                "Fine amount must be greater than zero."
            )
        return value

    def create(self, validated_data):
        """
        Create and return a new Fine instance.

        Adds current user as `issued_by` and sets status to 'issued'.
        """
        request = self.context.get("request")
        if request:
            validated_data["issued_by"] = request.user
        validated_data["status"] = FineStatus.ISSUED
        return Fine.objects.create(**validated_data)

    def get_appeal(self, obj):
        appeal = getattr(obj, "appeal", None)
        if not appeal:
            return None
        context = dict(self.context) if self.context else {}
        context["include_timeline"] = False
        return FineAppealSerializer(appeal, context=context).data


class FineAppealSerializer(serializers.ModelSerializer):
    """
    Serializer for FineAppeal model with support for read/write ops.

    Validates appeal ownership and ensures only one appeal per fine.
    """

    appealed_by = UserSerializer(read_only=True)
    reviewed_by = UserSerializer(read_only=True)
    escalated_to_username = serializers.CharField(source="escalated_to.username", read_only=True)
    fine_id = serializers.IntegerField(write_only=True, required=False)
    fine = serializers.IntegerField(source="fine.id", read_only=True)
    fine_amount = serializers.DecimalField(source="fine.amount", read_only=True, max_digits=10, decimal_places=2)
    fine_status = serializers.CharField(source="fine.status", read_only=True)
    order_id = serializers.IntegerField(source="fine.order.id", read_only=True)
    order_topic = serializers.CharField(source="fine.order.topic", read_only=True)
    events = serializers.SerializerMethodField()
    evidence_files = serializers.SerializerMethodField()

    class Meta:
        model = FineAppeal
        fields = [
            "id",
            "fine_id",
            "fine",
            "fine_amount",
            "fine_status",
            "order_id",
            "order_topic",
            "reason",
            "appealed_by",
            "created_at",
            "reviewed_by",
            "reviewed_at",
            "accepted",
            "escalated",
            "escalated_at",
            "escalated_to_username",
            "resolution_notes",
            "events",
            "evidence_files",
        ]
        read_only_fields = [
            "created_at",
            "reviewed_by",
            "reviewed_at",
            "accepted",
            "escalated",
            "escalated_at",
            "resolution_notes",
            "events",
            "evidence_files",
        ]

    def validate_fine_id(self, fine_id):
        """Ensure the fine exists and has not already been appealed."""
        if not Fine.objects.filter(id=fine_id).exists():
            raise serializers.ValidationError("Fine does not exist.")
        if FineAppeal.objects.filter(fine_id=fine_id).exists():
            raise serializers.ValidationError("This fine is already appealed.")
        return fine_id

    def create(self, validated_data):
        """
        Create and return a new FineAppeal instance.

        Adds current user as `appealed_by`.
        """
        request = self.context.get("request")
        if request:
            validated_data["appealed_by"] = request.user
        
        fine_id = validated_data.pop('fine_id', None)
        if fine_id:
            fine = get_object_or_404(Fine, id=fine_id)
            validated_data['fine'] = fine
        
        return FineAppeal.objects.create(**validated_data)

    def _include_timeline(self):
        return self.context.get("include_timeline", True)

    def get_events(self, obj):
        if not self._include_timeline():
            return []
        events = obj.events.all()
        return FineAppealEventSerializer(
            events, many=True, context=self.context
        ).data

    def get_evidence_files(self, obj):
        if not self._include_timeline():
            return []
        evidence = obj.evidence_files.all()
        return FineAppealEvidenceSerializer(
            evidence, many=True, context=self.context
        ).data