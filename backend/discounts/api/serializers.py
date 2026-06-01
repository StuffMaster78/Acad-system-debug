from __future__ import annotations

from decimal import Decimal
from typing import Any

from rest_framework import serializers
from django.utils import timezone

from discounts.constants import (
    DiscountOrigin,
    DiscountType,
    PayableType,
)
from discounts.models import Discount
from discounts.models import DiscountSettings
from discounts.models import FirstOrderDiscountConfig
from discounts.models import PromotionalCampaign


class PromotionalCampaignSerializer(serializers.ModelSerializer):
    """
    Serializer for promotional campaign records.
    """

    class Meta:
        model = PromotionalCampaign
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "starts_at",
            "ends_at",
            "is_active",
            "is_archived",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]


class DiscountSerializer(serializers.ModelSerializer):
    """
    Serializer for admin discount reads.
    """

    campaign = PromotionalCampaignSerializer(read_only=True)
    campaign_id = serializers.IntegerField(read_only=True)
    usage_count = serializers.IntegerField(read_only=True)
    distinct_clients = serializers.IntegerField(read_only=True)
    total_discount_given = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True,
    )

    class Meta:
        model = Discount
        fields = [
            "id",
            "campaign",
            "campaign_id",
            "is_campaign_managed",
            "discount_code",
            "name",
            "description",
            "discount_type",
            "discount_value",
            "max_discount_amount",
            "min_payable_amount",
            "starts_at",
            "ends_at",
            "usage_limit",
            "per_client_usage_limit",
            "first_order_only",
            "origin",
            "is_active",
            "is_archived",
            "is_deleted",
            "usage_count",
            "distinct_clients",
            "total_discount_given",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "campaign",
            "campaign_id",
            "is_deleted",
            "usage_count",
            "distinct_clients",
            "total_discount_given",
            "created_at",
            "updated_at",
        ]


class DiscountCreateSerializer(serializers.Serializer):
    """
    Serializer for creating discounts through the admin API.
    """

    name = serializers.CharField(max_length=120)

    discount_code = serializers.CharField(
        max_length=64,
        required=False,
        allow_blank=True,
    )
    generate_code = serializers.BooleanField(
        required=False,
        default=False,
    )
    code_prefix = serializers.CharField(
        max_length=32,
        required=False,
        allow_blank=True,
    )

    campaign_id = serializers.IntegerField(
        required=False,
        allow_null=True,
    )
    is_campaign_managed = serializers.BooleanField(
        required=False,
        default=True,
    )
    description = serializers.CharField(
        required=False,
        allow_blank=True,
    )

    discount_type = serializers.ChoiceField(
        choices=[choice[0] for choice in DiscountType.CHOICES],
    )
    discount_value = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal("0.01"),
    )

    max_discount_amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        allow_null=True,
        min_value=Decimal("0.01"),
    )
    min_payable_amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        default=Decimal("0.00"),
        min_value=Decimal("0.00"),
    )

    starts_at = serializers.DateTimeField(
        required=False,
        allow_null=True,
    )
    ends_at = serializers.DateTimeField(
        required=False,
        allow_null=True,
    )

    usage_limit = serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=1,
    )
    per_client_usage_limit = serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=1,
    )

    first_order_only = serializers.BooleanField(
        required=False,
        default=False,
    )
    origin = serializers.ChoiceField(
        choices=[choice[0] for choice in DiscountOrigin.CHOICES],
        required=False,
        default=DiscountOrigin.MANUAL,
    )
    is_active = serializers.BooleanField(
        required=False,
        default=True,
    )

    eligible_client_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        required=False,
        allow_empty=True,
    )

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """
        Validate discount creation rules.
        """
        self._validate_date_window(attrs=attrs)
        self._validate_code_rules(attrs=attrs)
        self._validate_percentage(attrs=attrs)
        self._validate_usage_limits(attrs=attrs)

        return attrs

    @staticmethod
    def _validate_date_window(*, attrs: dict[str, Any]) -> None:
        """
        Validate date ordering.
        """
        starts_at = attrs.get("starts_at")
        ends_at = attrs.get("ends_at")

        if starts_at and ends_at and starts_at >= ends_at:
            raise serializers.ValidationError(
                "starts_at must be earlier than ends_at."
            )

    @staticmethod
    def _validate_code_rules(*, attrs: dict[str, Any]) -> None:
        """
        Validate manual versus generated discount code rules.
        """
        generate_code = attrs.get("generate_code", False)
        code = attrs.get("discount_code")

        if generate_code and code:
            raise serializers.ValidationError(
                "Provide either discount_code or generate_code, not both."
            )

        if not generate_code and not code:
            raise serializers.ValidationError(
                "discount_code is required when generate_code is False."
            )

        if code:
            attrs["discount_code"] = code.strip().upper()

    @staticmethod
    def _validate_percentage(*, attrs: dict[str, Any]) -> None:
        """
        Validate percentage discount bounds.
        """
        discount_type = attrs.get("discount_type")
        discount_value = attrs.get("discount_value")

        if (
            discount_type == DiscountType.PERCENTAGE
            and discount_value is not None
            and discount_value > Decimal("100.00")
        ):
            raise serializers.ValidationError(
                "Percentage discount cannot exceed 100."
            )

    @staticmethod
    def _validate_usage_limits(*, attrs: dict[str, Any]) -> None:
        """
        Validate usage limit relationship.
        """
        usage_limit = attrs.get("usage_limit")
        per_client_limit = attrs.get("per_client_usage_limit")

        if (
            usage_limit is not None
            and per_client_limit is not None
            and per_client_limit > usage_limit
        ):
            raise serializers.ValidationError(
                "per_client_usage_limit cannot exceed usage_limit."
            )


class DiscountUpdateSerializer(DiscountCreateSerializer):
    """
    Serializer for partial discount updates.
    """

    name = serializers.CharField(max_length=120, required=False)
    discount_code = serializers.CharField(
        max_length=64,
        required=False,
        allow_blank=True,
    )
    discount_type = serializers.ChoiceField(
        choices=[choice[0] for choice in DiscountType.CHOICES],
        required=False,
    )
    discount_value = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal("0.01"),
        required=False,
    )
    is_campaign_managed = serializers.BooleanField(
        required=False,
    )

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """
        Validate discount update rules.
        """
        self._validate_date_window(attrs=attrs)
        self._validate_update_code_rules(attrs=attrs)
        self._validate_percentage(attrs=attrs)
        self._validate_usage_limits(attrs=attrs)

        return attrs

    @staticmethod
    def _validate_update_code_rules(
        *,
        attrs: dict[str, Any],
    ) -> None:
        """
        Normalize discount code when provided during updates.
        """
        code = attrs.get("discount_code")

        if code:
            attrs["discount_code"] = code.strip().upper()

class AvailableDiscountSerializer(serializers.Serializer):
    """
    Client-facing available discount option.
    """

    discount_id = serializers.IntegerField()
    discount_code = serializers.CharField()
    name = serializers.CharField()
    description = serializers.CharField()
    origin = serializers.CharField()
    discount_type = serializers.CharField()
    discount_value = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
    )
    discount_amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    final_amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    usage_remaining = serializers.IntegerField(allow_null=True)
    client_usage_remaining = serializers.IntegerField(allow_null=True)
    expires_at = serializers.DateTimeField(allow_null=True)
    reason = serializers.CharField()
    explanation = serializers.CharField()
    frontend_label = serializers.CharField()
    frontend_badge = serializers.CharField()
    cta_label = serializers.CharField()

class DiscountPreviewRequestSerializer(serializers.Serializer):
    """
    Client request serializer for discount preview.
    """

    subtotal = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal("0.00"),
    )
    payable_type = serializers.ChoiceField(
        choices=[choice[0] for choice in PayableType.CHOICES],
    )
    lifetime_spend = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=False,
        allow_null=True,
        min_value=Decimal("0.00"),
    )
    entered_code = serializers.CharField(
        max_length=64,
        required=False,
        allow_blank=True,
        allow_null=True,
    )
    has_prior_paid_purchase = serializers.BooleanField()

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """
        Normalize entered discount code.
        """
        code = attrs.get("entered_code")

        if code:
            attrs["entered_code"] = code.strip().upper()

        return attrs


class DiscountApplyRequestSerializer(DiscountPreviewRequestSerializer):
    """
    Client request serializer for applying a discount.
    """

    payable_id = serializers.CharField(max_length=64)
    metadata = serializers.DictField(required=False)


class ResolvedDiscountSerializer(serializers.Serializer):
    """
    Serializer for resolved discount results.
    """

    discount_code = serializers.CharField()
    discount_type = serializers.CharField()
    discount_value = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
    )
    discount_amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    final_amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    origin = serializers.CharField()
    source = serializers.CharField()


class DiscountSettingsSerializer(serializers.ModelSerializer):
    """
    Serializer for tenant discount settings.
    """

    class Meta:
        model = DiscountSettings
        fields = [
            "id",
            "allow_manual_codes",
            "auto_apply_first_order_discount",
            "allow_code_to_replace_first_order",
            "auto_apply_best_discount",
            "allow_discounts_on_orders",
            "allow_discounts_on_special_orders",
            "allow_discounts_on_class_bundles",
            "require_admin_approval_for_campaigns",
            "notify_admins_on_large_discount",
            "large_discount_threshold",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]


class FirstOrderDiscountConfigSerializer(serializers.ModelSerializer):
    """
    Serializer for first order discount settings.
    """

    class Meta:
        model = FirstOrderDiscountConfig
        fields = [
            "id",
            "is_enabled",
            "discount_type",
            "discount_value",
            "max_discount_amount",
            "min_payable_amount",
            "applies_to_orders",
            "applies_to_special_orders",
            "applies_to_class_bundles",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

class CampaignDiscountPreviewSerializer(serializers.Serializer):
    """
    Small discount card for campaign calendar displays.
    """

    code = serializers.CharField(source="discount_code")
    name = serializers.CharField()
    discount_type = serializers.CharField()
    discount_value = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
    )
    cta_label = serializers.SerializerMethodField()

    def get_cta_label(self, obj) -> str:
        """
        Return frontend CTA label.
        """
        return f"Use {obj.discount_code}"


class ClientCampaignCalendarSerializer(serializers.ModelSerializer):
    """
    Client-facing campaign calendar serializer.
    """

    title = serializers.CharField(source="name")
    badge = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    discounts = CampaignDiscountPreviewSerializer(many=True)

    class Meta:
        model = PromotionalCampaign
        fields = [
            "id",
            "title",
            "description",
            "starts_at",
            "ends_at",
            "status",
            "badge",
            "discounts",
        ]

    def get_status(self, obj) -> str:
        """
        Return calendar-friendly campaign status.
        """
        now = timezone.now()

        if obj.is_archived:
            return "archived"

        if obj.starts_at and obj.starts_at > now:
            return "scheduled"

        if obj.ends_at and obj.ends_at < now:
            return "expired"

        if obj.is_active:
            return "active"

        return "inactive"

    def get_badge(self, obj) -> str:
        """
        Return frontend badge.
        """
        status_value = self.get_status(obj)

        if status_value == "scheduled":
            return "Coming soon"

        if status_value == "active":
            return "Live now"

        if status_value == "expired":
            return "Expired"

        return "Unavailable"


class AdminCampaignSerializer(serializers.ModelSerializer):
    """
    Admin campaign serializer.
    """

    discount_count = serializers.IntegerField(read_only=True)
    usage_count = serializers.IntegerField(read_only=True)
    distinct_clients = serializers.IntegerField(read_only=True)
    total_discount_given = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True,
    )

    class Meta:
        model = PromotionalCampaign
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "starts_at",
            "ends_at",
            "is_active",
            "is_archived",
            "discount_count",
            "usage_count",
            "distinct_clients",
            "total_discount_given",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "discount_count",
            "usage_count",
            "distinct_clients",
            "total_discount_given",
            "created_at",
            "updated_at",
        ]


class CampaignCreateUpdateSerializer(serializers.Serializer):
    """
    Admin serializer for creating and updating campaigns.
    """

    name = serializers.CharField(max_length=120, required=False)
    slug = serializers.SlugField(
        max_length=140,
        required=False,
        allow_blank=True,
    )
    description = serializers.CharField(
        required=False,
        allow_blank=True,
    )
    starts_at = serializers.DateTimeField(required=False, allow_null=True)
    ends_at = serializers.DateTimeField(required=False, allow_null=True)
    is_active = serializers.BooleanField(required=False, default=False)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """
        Validate campaign date window.
        """
        starts_at = attrs.get("starts_at")
        ends_at = attrs.get("ends_at")

        if starts_at and ends_at and starts_at >= ends_at:
            raise serializers.ValidationError(
                "starts_at must be earlier than ends_at."
            )

        return attrs

class DiscountSpendTierSerializer(serializers.Serializer):
    """
    Read serializer for spend tier discounts.
    """

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    minimum_lifetime_spend = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    is_active = serializers.BooleanField()
    discount = DiscountSerializer(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class DiscountSpendTierCreateSerializer(serializers.Serializer):
    """
    Create serializer for spend tier discounts.
    """

    website_id = serializers.IntegerField(required=False)
    name = serializers.CharField(max_length=120)
    discount_code = serializers.CharField(max_length=64)
    description = serializers.CharField(
        required=False,
        allow_blank=True,
    )
    minimum_lifetime_spend = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal("0.00"),
    )
    discount_type = serializers.ChoiceField(
        choices=[choice[0] for choice in DiscountType.CHOICES],
    )
    discount_value = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal("0.00"),
    )
    max_discount_amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        allow_null=True,
        min_value=Decimal("0.00"),
    )
    usage_limit = serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=1,
    )
    per_client_usage_limit = serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=1,
    )
    is_active = serializers.BooleanField(required=False, default=True)

    def validate(self, attrs):
        """
        Validate tier discount values.
        """
        discount_type = attrs.get("discount_type")
        discount_value = attrs.get("discount_value")

        if (
            discount_type == DiscountType.PERCENTAGE
            and discount_value > Decimal("100.00")
        ):
            raise serializers.ValidationError(
                "Percentage discount cannot exceed 100."
            )

        return attrs


class DiscountCloneSerializer(serializers.Serializer):
    """
    Request serializer for cloning one discount.
    """

    source_discount_id = serializers.IntegerField(min_value=1)
    target_website_id = serializers.IntegerField(min_value=1)
    new_code = serializers.CharField(
        max_length=64,
        required=False,
        allow_blank=True,
        allow_null=True,
    )
    target_campaign_id = serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=1,
    )

    def validate(self, attrs):
        """
        Validate cloning rules.
        """
        source_discount_id = attrs.get("source_discount_id")
        target_website_id = attrs.get("target_website_id")

        if source_discount_id == target_website_id:
            # Not strictly invalid, but likely a mistake
            raise serializers.ValidationError(
                "Source discount ID and target website ID "
                "should not match."
            )

        return attrs


class CampaignCloneSerializer(serializers.Serializer):
    """
    Request serializer for cloning a campaign.
    """

    source_campaign_id = serializers.IntegerField(min_value=1)
    target_website_id = serializers.IntegerField(min_value=1)
    new_name = serializers.CharField(
        max_length=120,
        required=False,
        allow_blank=True,
        allow_null=True,
    )
    new_slug = serializers.SlugField(
        max_length=140,
        required=False,
        allow_blank=True,
        allow_null=True,
    )

    def validate(self, attrs):
        """
        Validate campaign cloning input.
        """
        new_name = attrs.get("new_name")
        new_slug = attrs.get("new_slug")

        if new_slug and not new_name:
            raise serializers.ValidationError(
                "new_name is required when providing new_slug."
            )

        return attrs