from __future__ import annotations

from typing import Any, Optional, cast

from rest_framework import serializers

from discounts.models import Discount
from order_configs.models import AcademicLevel
from order_configs.models import EnglishType
from order_configs.models import FormattingandCitationStyle
from order_configs.models import PaperType
from order_configs.models import Subject
from order_configs.models import TypeOfWork
from order_pricing_core.models.pricing_dimensions import WriterLevelRate
from order_pricing_core.models.pricing_snapshots import PricingSnapshot
from orders.models import Order
from orders.selectors.order_creation_selectors import (
    OrderCreationContext,
    OrderCreationSelector,
)
from orders.validators.order_creation_validators import (
    OrderCreationValidator,
)


class CreateOrderSerializer(serializers.Serializer):
    """
    Validate order creation input before orchestration.

    This serializer validates transport-level input and delegates:
        1. object resolution to OrderCreationSelector
        2. business rule validation to OrderCreationValidator

    Actual order creation should be delegated to OrderCreationService.
    """

    topic = serializers.CharField(
        max_length=255,
        trim_whitespace=True,
    )
    paper_type_id = serializers.IntegerField()
    academic_level_id = serializers.IntegerField(
        required=False,
        allow_null=True,
    )
    formatting_style_id = serializers.IntegerField(
        required=False,
        allow_null=True,
    )
    subject_id = serializers.IntegerField(
        required=False,
        allow_null=True,
    )
    type_of_work_id = serializers.IntegerField(
        required=False,
        allow_null=True,
    )
    english_type_id = serializers.IntegerField(
        required=False,
        allow_null=True,
    )
    writer_level_id = serializers.IntegerField(
        required=False,
        allow_null=True,
    )
    discount_id = serializers.IntegerField(
        required=False,
        allow_null=True,
    )
    discount_code_used = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=100,
    )
    is_follow_up = serializers.BooleanField(
        required=False,
        default=False,
    )
    previous_order_id = serializers.IntegerField(
        required=False,
        allow_null=True,
    )
    preferred_writer_id = serializers.IntegerField(
        required=False,
        allow_null=True,
    )
    flags = serializers.ListField(
        child=serializers.CharField(max_length=64),
        required=False,
        default=list,
    )
    client_id = serializers.IntegerField(
        required=False,
        allow_null=True,
    )
    client_deadline = serializers.DateTimeField()
    writer_deadline = serializers.DateTimeField(
        required=False,
        allow_null=True,
    )
    is_urgent = serializers.BooleanField(
        required=False,
        default=False,
    )
    requires_editing = serializers.BooleanField(
        required=False,
        allow_null=True,
    )
    editing_skip_reason = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=255,
    )
    order_instructions = serializers.CharField()
    external_contact_name = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=255,
    )
    external_contact_email = serializers.EmailField(
        required=False,
        allow_blank=True,
    )
    external_contact_phone = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=20,
    )
    allow_unpaid_access = serializers.BooleanField(
        required=False,
        default=False,
    )
    pricing_snapshot_id = serializers.IntegerField()

    def validate_paper_type_id(self, value: int) -> int:
        """
        Ensure paper type exists.
        """
        if not PaperType.objects.filter(pk=value).exists():
            raise serializers.ValidationError("Invalid paper_type_id.")
        return value

    def validate_academic_level_id(
        self,
        value: Optional[int],
    ) -> Optional[int]:
        """
        Ensure academic level exists when provided.
        """
        if value is None:
            return value
        if not AcademicLevel.objects.filter(pk=value).exists():
            raise serializers.ValidationError(
                "Invalid academic_level_id."
            )
        return value

    def validate_formatting_style_id(
        self,
        value: Optional[int],
    ) -> Optional[int]:
        """
        Ensure formatting style exists when provided.
        """
        if value is None:
            return value
        if not FormattingandCitationStyle.objects.filter(
            pk=value
        ).exists():
            raise serializers.ValidationError(
                "Invalid formatting_style_id."
            )
        return value

    def validate_subject_id(
        self,
        value: Optional[int],
    ) -> Optional[int]:
        """
        Ensure subject exists when provided.
        """
        if value is None:
            return value
        if not Subject.objects.filter(pk=value).exists():
            raise serializers.ValidationError("Invalid subject_id.")
        return value

    def validate_type_of_work_id(
        self,
        value: Optional[int],
    ) -> Optional[int]:
        """
        Ensure type of work exists when provided.
        """
        if value is None:
            return value
        if not TypeOfWork.objects.filter(pk=value).exists():
            raise serializers.ValidationError(
                "Invalid type_of_work_id."
            )
        return value

    def validate_english_type_id(
        self,
        value: Optional[int],
    ) -> Optional[int]:
        """
        Ensure English type exists when provided.
        """
        if value is None:
            return value
        if not EnglishType.objects.filter(pk=value).exists():
            raise serializers.ValidationError(
                "Invalid english_type_id."
            )
        return value

    def validate_writer_level_id(
        self,
        value: Optional[int],
    ) -> Optional[int]:
        """
        Ensure writer level exists when provided.
        """
        if value is None:
            return value
        if not WriterLevelRate.objects.filter(pk=value).exists():
            raise serializers.ValidationError(
                "Invalid writer_level_id."
            )
        return value

    def validate_discount_id(
        self,
        value: Optional[int],
    ) -> Optional[int]:
        """
        Ensure discount exists when provided.
        """
        if value is None:
            return value
        if not Discount.objects.filter(pk=value).exists():
            raise serializers.ValidationError("Invalid discount_id.")
        return value

    def validate_previous_order_id(
        self,
        value: Optional[int],
    ) -> Optional[int]:
        """
        Ensure previous order exists when provided.
        """
        if value is None:
            return value
        if not Order.all_objects.filter(pk=value).exists():
            raise serializers.ValidationError(
                "Invalid previous_order_id."
            )
        return value

    def validate_client_id(
        self,
        value: Optional[int],
    ) -> Optional[int]:
        """
        Ensure client exists when provided.

        Notes:
            Only staff-assisted creation should use this field.
            Tenant consistency is enforced in the view.
        """
        if value is None:
            return value

        user_model = self._get_user_model()
        if not user_model.objects.filter(pk=value).exists():
            raise serializers.ValidationError("Invalid client_id.")
        return value
    
    def validate_preferred_writer_id(
        self,
        value: Optional[int],
    ) -> Optional[int]:
        """
        Ensure preferred writer exists when provided.
        """
        if value is None:
            return value

        user_model = self._get_user_model()
        if not user_model.objects.filter(pk=value).exists():
            raise serializers.ValidationError(
                "Invalid preferred_writer_id."
            )
        return value

    def validate_pricing_snapshot_id(self, value: int) -> int:
        """
        Ensure pricing snapshot exists.
        """
        if not PricingSnapshot.objects.filter(pk=value).exists():
            raise serializers.ValidationError(
                "Invalid pricing_snapshot_id."
            )
        return value

    def validate_flags(self, value: list[str]) -> list[str]:
        """
        Normalize and deduplicate submitted flags.
        """
        normalized: list[str] = []
        seen: set[str] = set()

        for item in value:
            flag = item.strip().lower()
            if not flag:
                continue
            if flag in seen:
                continue
            seen.add(flag)
            normalized.append(flag)

        return normalized

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """
        Validate cross-field rules and resolve creation context.
        """
        request = self.context.get("request")
        request_user = getattr(request, "user", None)

        creation_context = OrderCreationSelector.build_context(
            paper_type_id=attrs["paper_type_id"],
            pricing_snapshot_id=attrs["pricing_snapshot_id"],
            academic_level_id=attrs.get("academic_level_id"),
            formatting_style_id=attrs.get("formatting_style_id"),
            subject_id=attrs.get("subject_id"),
            type_of_work_id=attrs.get("type_of_work_id"),
            english_type_id=attrs.get("english_type_id"),
            writer_level_id=attrs.get("writer_level_id"),
            discount_id=attrs.get("discount_id"),
            previous_order_id=attrs.get("previous_order_id"),
            preferred_writer_id=attrs.get("preferred_writer_id"),
        )

        attrs["request_user"] = request_user

        OrderCreationValidator.validate(
            attrs=attrs,
            context=creation_context,
            request_user=request_user,
        )

        attrs["pricing_snapshot"] = creation_context.pricing_snapshot
        attrs["paper_type"] = creation_context.paper_type
        attrs["academic_level"] = creation_context.academic_level
        attrs["formatting_style"] = creation_context.formatting_style
        attrs["subject"] = creation_context.subject
        attrs["type_of_work"] = creation_context.type_of_work
        attrs["english_type"] = creation_context.english_type
        attrs["writer_level"] = creation_context.writer_level
        attrs["discount"] = creation_context.discount
        attrs["previous_order"] = creation_context.previous_order
        attrs["preferred_writer"] = creation_context.preferred_writer

        attrs.pop("request_user", None)

        return attrs

    def to_order_payload(self) -> dict[str, Any]:
        """
        Convert validated_data into OrderCreationService payload.
        """
        if not hasattr(self, "validated_data"):
            raise serializers.ValidationError(
                "Serializer must be validated before building payload."
            )

        data = cast(dict[str, Any], self.validated_data)

        return {
            "topic": data["topic"],
            "paper_type": data["paper_type"],
            "academic_level": data.get("academic_level"),
            "formatting_style": data.get("formatting_style"),
            "subject": data.get("subject"),
            "type_of_work": data.get("type_of_work"),
            "english_type": data.get("english_type"),
            "writer_level": data.get("writer_level"),
            "discount": data.get("discount"),
            "discount_code_used": data.get("discount_code_used", ""),
            "is_follow_up": data.get("is_follow_up", False),
            "previous_order": data.get("previous_order"),
            "preferred_writer": data.get("preferred_writer"),
            "flags": data.get("flags", []),
            "client_deadline": data["client_deadline"],
            "writer_deadline": data.get("writer_deadline"),
            "is_urgent": data.get("is_urgent", False),
            "requires_editing": data.get("requires_editing"),
            "editing_skip_reason": data.get(
                "editing_skip_reason",
                "",
            ),
            "created_by_admin": self._request_user_is_staff(),
            "order_instructions": data["order_instructions"],
            "external_contact_name": data.get(
                "external_contact_name",
                "",
            ),
            "external_contact_email": data.get(
                "external_contact_email",
                "",
            ),
            "external_contact_phone": data.get(
                "external_contact_phone",
                "",
            ),
            "allow_unpaid_access": data.get(
                "allow_unpaid_access",
                False,
            ),
            "service_family": getattr(
                data["pricing_snapshot"],
                "service_family",
                "",
            ),
            "service_code": getattr(
                data["pricing_snapshot"],
                "service_code",
                "",
            ),
        }

    @staticmethod
    def _get_user_model():
        """
        Return Django user model class.
        """
        from django.contrib.auth import get_user_model

        return get_user_model()

    def _request_user_is_staff(self) -> bool:
        """
        Return whether current request user is staff.
        """
        request = self.context.get("request")
        if request is None:
            return False

        user = getattr(request, "user", None)
        return bool(getattr(user, "is_staff", False))