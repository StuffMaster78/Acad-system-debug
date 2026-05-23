from __future__ import annotations

from rest_framework import serializers

from special_orders.models import (
    EstimatedSpecialOrderSettings,
    PredefinedSpecialOrderConfig,
    PredefinedSpecialOrderDuration,
    SpecialOrder,
    SpecialOrderFundingMilestone,
    SpecialOrderInquiryFile,
    WriterBonus,
)


class PredefinedSpecialOrderConfigSerializer(serializers.ModelSerializer):
    """
    Compatibility serializer for fixed special-order configurations.
    """

    class Meta:
        model = PredefinedSpecialOrderConfig
        fields = "__all__"


class PredefinedSpecialOrderDurationSerializer(serializers.ModelSerializer):
    """
    Compatibility serializer for fixed special-order duration prices.
    """

    class Meta:
        model = PredefinedSpecialOrderDuration
        fields = "__all__"


class FundingMilestoneSerializer(serializers.ModelSerializer):
    """Serialize special-order funding milestones."""

    balance_amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True,
    )
    net_funded_amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True,
    )

    class Meta:
        model = SpecialOrderFundingMilestone
        fields = [
            "id",
            "website",
            "funding_plan",
            "special_order",
            "sequence",
            "label",
            "milestone_type",
            "status",
            "amount_due",
            "funded_amount",
            "refunded_amount",
            "balance_amount",
            "net_funded_amount",
            "due_at",
            "required_before_staffing",
            "required_before_draft",
            "required_before_delivery",
            "required_before_completion",
            "metadata",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


# Backwards-compatible import name for old admin views during the transition.
InstallmentPaymentSerializer = FundingMilestoneSerializer


class SpecialOrderSerializer(serializers.ModelSerializer):
    """Serialize current special-order workflow state."""

    client_username = serializers.CharField(
        source="client.username",
        read_only=True,
    )
    writer_username = serializers.CharField(
        source="writer.username",
        read_only=True,
    )
    predefined_config_detail = PredefinedSpecialOrderConfigSerializer(
        source="predefined_config",
        read_only=True,
    )
    funding_total_amount = serializers.SerializerMethodField()
    funding_deposit_amount = serializers.SerializerMethodField()
    funding_funded_amount = serializers.SerializerMethodField()
    funding_refunded_amount = serializers.SerializerMethodField()
    funding_balance_amount = serializers.SerializerMethodField()
    funding_status = serializers.SerializerMethodField()
    funding_milestones = serializers.SerializerMethodField()

    class Meta:
        model = SpecialOrder
        fields = [
            "id",
            "website",
            "client",
            "client_username",
            "writer",
            "writer_username",
            "title",
            "pricing_mode",
            "status",
            "origin",
            "priority",
            "predefined_config",
            "predefined_config_detail",
            "predefined_duration",
            "inquiry_details",
            "admin_notes",
            "budget",
            "duration_days",
            "currency",
            "funding_total_amount",
            "funding_deposit_amount",
            "funding_funded_amount",
            "funding_refunded_amount",
            "funding_balance_amount",
            "funding_status",
            "funding_milestones",
            "accepted_quote",
            "converted_order",
            "assigned_at",
            "started_at",
            "completed_at",
            "cancelled_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def _get_funding_plan(self, obj: SpecialOrder):
        """Return the funding plan if it has been created."""
        return getattr(obj, "funding_plan", None)

    def get_funding_total_amount(self, obj: SpecialOrder):
        """Return the active funding total."""
        funding_plan = self._get_funding_plan(obj)
        return funding_plan.total_amount if funding_plan else None

    def get_funding_deposit_amount(self, obj: SpecialOrder):
        """Return the active deposit requirement."""
        funding_plan = self._get_funding_plan(obj)
        return funding_plan.deposit_amount if funding_plan else None

    def get_funding_funded_amount(self, obj: SpecialOrder):
        """Return the amount funded so far."""
        funding_plan = self._get_funding_plan(obj)
        return funding_plan.funded_amount if funding_plan else None

    def get_funding_refunded_amount(self, obj: SpecialOrder):
        """Return the amount refunded so far."""
        funding_plan = self._get_funding_plan(obj)
        return funding_plan.refunded_amount if funding_plan else None

    def get_funding_balance_amount(self, obj: SpecialOrder):
        """Return the remaining unpaid funding balance."""
        funding_plan = self._get_funding_plan(obj)
        return funding_plan.balance_amount if funding_plan else None

    def get_funding_status(self, obj: SpecialOrder):
        """Return the funding plan status."""
        funding_plan = self._get_funding_plan(obj)
        return funding_plan.status if funding_plan else None

    def get_funding_milestones(self, obj: SpecialOrder) -> list[dict]:
        """Return funding milestones for the order."""
        milestones = obj.funding_milestones.all()
        return FundingMilestoneSerializer(milestones, many=True).data


class WriterBonusSerializer(serializers.ModelSerializer):
    """
    Serializer for special-order writer bonuses.
    """

    writer_username = serializers.CharField(
        source="writer.username",
        read_only=True,
    )
    special_order_id = serializers.PrimaryKeyRelatedField(
        queryset=SpecialOrder.objects.all(),
        source="special_order",
        write_only=True,
    )

    class Meta:
        model = WriterBonus
        fields = [
            "id",
            "writer",
            "writer_username",
            "special_order_id",
            "website",
            "amount",
            "category",
            "is_paid",
            "granted_at",
        ]
        read_only_fields = ["granted_at"]


class SpecialOrderInquiryFileSerializer(serializers.ModelSerializer):
    """
    Compatibility serializer for special-order inquiry files.
    """

    uploaded_by_username = serializers.CharField(
        source="uploaded_by.username",
        read_only=True,
    )
    uploaded_by_email = serializers.CharField(
        source="uploaded_by.email",
        read_only=True,
    )
    file_url = serializers.SerializerMethodField()
    file_name = serializers.CharField(
        source="original_name",
        read_only=True,
    )
    file_size = serializers.IntegerField(source="size", read_only=True)
    file_size_mb = serializers.SerializerMethodField()

    class Meta:
        model = SpecialOrderInquiryFile
        fields = [
            "id",
            "website",
            "special_order",
            "uploaded_by",
            "uploaded_by_username",
            "uploaded_by_email",
            "file",
            "file_url",
            "file_name",
            "file_size",
            "file_size_mb",
            "content_type",
            "uploaded_at",
        ]
        read_only_fields = [
            "id",
            "uploaded_at",
            "uploaded_by",
            "file_name",
            "file_size",
            "content_type",
        ]

    def get_file_url(self, obj: SpecialOrderInquiryFile) -> str | None:
        """
        Return the uploaded inquiry file URL.
        """
        if not obj.file:
            return None

        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.file.url)

        return obj.file.url

    def get_file_size_mb(self, obj: SpecialOrderInquiryFile):
        """
        Return file size in megabytes.
        """
        if obj.size:
            return round(obj.size / (1024 * 1024), 2)

        return None

    def create(self, validated_data):
        """
        Create inquiry file metadata from the uploaded file.
        """
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            validated_data["uploaded_by"] = request.user

        uploaded_file = validated_data.get("file")
        if uploaded_file:
            validated_data["original_name"] = uploaded_file.name
            validated_data["size"] = uploaded_file.size
            validated_data["content_type"] = getattr(
                uploaded_file,
                "content_type",
                "",
            )

        return super().create(validated_data)


class EstimatedSpecialOrderSettingsSerializer(serializers.ModelSerializer):
    """
    Serializer for estimated special-order funding settings.
    """

    class Meta:
        model = EstimatedSpecialOrderSettings
        fields = "__all__"
