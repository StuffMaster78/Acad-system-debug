from __future__ import annotations

from rest_framework import serializers

from special_orders.models import SpecialOrder
from special_orders.services.new_services.special_order_available_actions_service import (
    SpecialOrderAvailableActionsService,
)


def _username(user):
    if user is None:
        return None
    return getattr(user, "username", None) or getattr(user, "email", None)


def serialize_special_order_milestone(*, order, milestone, deliverable=None, include_money: bool = True):
    amount_due = str(getattr(milestone, "amount_due", 0) or 0)
    due_at = getattr(milestone, "due_at", None)
    return {
        "id": milestone.id,
        "special_order_id": order.id,
        "sequence": getattr(milestone, "sequence", 0),
        "label": getattr(milestone, "label", f"Milestone {milestone.id}"),
        "description": getattr(milestone, "description", "") or "",
        "milestone_type": getattr(milestone, "milestone_type", ""),
        "status": getattr(milestone, "status", "pending"),
        "funding_status": getattr(milestone, "status", "pending"),
        "price": amount_due if include_money else None,
        "amount_due": amount_due if include_money else None,
        "funded_amount": str(getattr(milestone, "funded_amount", 0) or 0) if include_money else None,
        "balance_amount": str(getattr(milestone, "balance_amount", 0) or 0) if include_money else None,
        "currency": getattr(order, "currency", "USD"),
        "due_date": due_at.isoformat() if due_at else None,
        "due_at": due_at.isoformat() if due_at else None,
        "required_before_staffing": getattr(milestone, "required_before_staffing", False),
        "required_before_delivery": getattr(milestone, "required_before_delivery", False),
        "required_before_completion": getattr(milestone, "required_before_completion", False),
        "writer_id": getattr(order, "writer_id", None),
        "writer_username": _username(getattr(order, "writer", None)),
        "deliverable_id": getattr(deliverable, "id", None) if deliverable else None,
        "deliverable_status": getattr(deliverable, "status", None) if deliverable else None,
        "delivery_file_url": getattr(deliverable, "file_reference", None) if deliverable else None,
        "delivery_notes": getattr(deliverable, "description", None) if deliverable else None,
        "revision_notes": getattr(deliverable, "review_notes", None) if deliverable else None,
        "delivered_at": deliverable.uploaded_at.isoformat() if deliverable and deliverable.uploaded_at else None,
        "approved_at": deliverable.reviewed_at.isoformat() if deliverable and deliverable.reviewed_at else None,
    }


class SpecialOrderActionContractMixin(serializers.Serializer):
    available_actions = serializers.SerializerMethodField()
    blocked_actions = serializers.SerializerMethodField()

    def _actions(self, obj):
        request = self.context.get("request")
        if request is None:
            return {"available_actions": [], "blocked_actions": []}
        return SpecialOrderAvailableActionsService.for_order(
            special_order=obj,
            user=request.user,
        )

    def get_available_actions(self, obj):
        return self._actions(obj)["available_actions"]

    def get_blocked_actions(self, obj):
        return self._actions(obj)["blocked_actions"]


class CreateQuotedSpecialOrderSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    inquiry_details = serializers.CharField(
        required=False,
        allow_blank=True,
    )
    budget = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=False,
        allow_null=True,
    )
    duration_days = serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=1,
    )
    currency = serializers.CharField(
        required=False,
        default="USD",
        max_length=10,
    )


class CreateFixedSpecialOrderSerializer(serializers.Serializer):
    predefined_config_id = serializers.IntegerField()
    predefined_duration_id = serializers.IntegerField()

    title = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
    )
    inquiry_details = serializers.CharField(
        required=False,
        allow_blank=True,
    )
    currency = serializers.CharField(
        required=False,
        default="USD",
        max_length=10,
    )

    platform = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=80,
    )
    writer_level = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=50,
    )
    coupon_code = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=100,
    )


class SpecialOrderListSerializer(SpecialOrderActionContractMixin, serializers.ModelSerializer):
    reference = serializers.ReadOnlyField()
    client_name = serializers.CharField(
        source="client.get_full_name",
        read_only=True,
    )
    writer_name = serializers.CharField(
        source="writer.get_full_name",
        read_only=True,
    )
    predefined_config_name = serializers.CharField(
        source="predefined_config.name",
        read_only=True,
    )

    class Meta:
        model = SpecialOrder
        fields = [
            "id",
            "public_order_number",
            "reference",
            "title",
            "pricing_mode",
            "status",
            "origin",
            "priority",
            "currency",
            "duration_days",
            "client",
            "client_name",
            "writer",
            "writer_name",
            "predefined_config",
            "predefined_config_name",
            "available_actions",
            "blocked_actions",
            "created_at",
            "updated_at",
        ]


class SpecialOrderClientListSerializer(SpecialOrderActionContractMixin, serializers.ModelSerializer):
    writer_name = serializers.CharField(source="writer.get_full_name", read_only=True)
    predefined_config_name = serializers.CharField(source="predefined_config.name", read_only=True)
    quoted_price = serializers.SerializerMethodField()
    reference = serializers.SerializerMethodField()

    class Meta:
        model = SpecialOrder
        fields = [
            "id",
            "public_order_number",
            "reference",
            "title",
            "pricing_mode",
            "status",
            "priority",
            "currency",
            "duration_days",
            "writer",
            "writer_name",
            "predefined_config",
            "predefined_config_name",
            "quoted_price",
            "available_actions",
            "blocked_actions",
            "created_at",
            "updated_at",
        ]

    def get_reference(self, obj):
        return obj.reference

    def get_quoted_price(self, obj):
        return _latest_quote_amount(obj)


class SpecialOrderWriterListSerializer(SpecialOrderActionContractMixin, serializers.ModelSerializer):
    reference = serializers.SerializerMethodField()
    writer_compensation = serializers.SerializerMethodField()

    class Meta:
        model = SpecialOrder
        fields = [
            "id",
            "public_order_number",
            "reference",
            "title",
            "inquiry_details",
            "pricing_mode",
            "status",
            "priority",
            "duration_days",
            "currency",
            "writer_compensation",
            "available_actions",
            "blocked_actions",
            "assigned_at",
            "started_at",
            "created_at",
            "updated_at",
        ]

    def get_reference(self, obj):
        return obj.reference

    def get_writer_compensation(self, obj):
        rule = getattr(obj, "writer_pay_rule", None)
        if not rule:
            return None
        if getattr(rule, "fixed_amount", None) is not None:
            return {
                "type": "fixed_amount",
                "amount": str(rule.fixed_amount),
                "currency": getattr(obj, "currency", "USD"),
            }
        if getattr(rule, "percentage", None) is not None:
            return {"type": "percentage", "percentage": str(rule.percentage)}
        return None


def _latest_quote_amount(obj):
    try:
        from special_orders.models.quotes import SpecialOrderQuote

        q = SpecialOrderQuote.objects.filter(
            special_order=obj,
            status__in=["accepted", "sent", "pending"],
        ).order_by("-created_at").first()
        return str(q.total_amount) if q and q.total_amount else None
    except Exception:
        return None


class SpecialOrderDetailSerializer(SpecialOrderActionContractMixin, serializers.ModelSerializer):
    client_username = serializers.SerializerMethodField()
    client_email = serializers.SerializerMethodField()
    writer_username = serializers.SerializerMethodField()
    website_name = serializers.SerializerMethodField()
    milestones = serializers.SerializerMethodField()
    quotes = serializers.SerializerMethodField()
    total_milestones = serializers.SerializerMethodField()
    completed_milestones = serializers.SerializerMethodField()
    attachments_count = serializers.SerializerMethodField()
    quoted_price = serializers.SerializerMethodField()
    reference = serializers.SerializerMethodField()
    available_actions = serializers.SerializerMethodField()
    blocked_actions = serializers.SerializerMethodField()

    class Meta:
        model = SpecialOrder
        fields = [
            "id",
            "public_order_number",
            "reference",
            "title",
            "inquiry_details",
            "admin_notes",
            "budget",
            "duration_days",
            "currency",
            "pricing_mode",
            "status",
            "origin",
            "priority",
            "client",
            "client_username",
            "client_email",
            "writer",
            "writer_username",
            "website_name",
            "predefined_config",
            "predefined_duration",
            "writer_pay_rule",
            "accepted_quote",
            "converted_order",
            "milestones",
            "quotes",
            "total_milestones",
            "completed_milestones",
            "attachments_count",
            "quoted_price",
            "available_actions",
            "blocked_actions",
            "assigned_at",
            "started_at",
            "completed_at",
            "cancelled_at",
            "created_at",
            "updated_at",
        ]

    def get_client_username(self, obj):
        return getattr(getattr(obj, "client", None), "username", None)

    def get_client_email(self, obj):
        return getattr(getattr(obj, "client", None), "email", None)

    def get_writer_username(self, obj):
        return _username(getattr(obj, "writer", None))

    def get_website_name(self, obj):
        w = getattr(obj, "website", None)
        return getattr(w, "name", None) or getattr(w, "domain", None)

    def get_reference(self, obj):
        return obj.reference

    def get_milestones(self, obj):
        try:
            from special_orders.models.delivery import SpecialOrderDeliverable

            milestones = obj.funding_milestones.all().order_by("sequence")
            deliverables = {
                d.metadata.get("milestone_id"): d
                for d in SpecialOrderDeliverable.objects.filter(
                    special_order=obj,
                ).order_by("-created_at")
                if d.metadata.get("milestone_id")
            }
            return [
                serialize_special_order_milestone(
                    order=obj,
                    milestone=m,
                    deliverable=deliverables.get(m.id),
                    include_money=True,
                )
                for m in milestones
            ]
        except Exception:
            return []

    def get_quotes(self, obj):
        try:
            from special_orders.models.quotes import SpecialOrderQuote
            quotes = SpecialOrderQuote.objects.filter(special_order=obj).order_by("-created_at")
            return [
                {
                    "id": q.id,
                    "special_order_id": obj.id,
                    "status": q.status,
                    "price": str(q.total_amount or 0),
                    "total_amount": str(q.total_amount or 0),
                    "currency": q.currency,
                    "valid_until": q.expires_at.isoformat() if getattr(q, "expires_at", None) else None,
                    "notes": getattr(q, "notes", "") or "",
                    "milestones_preview": [],
                    "created_by": _username(getattr(q, "created_by", None)),
                    "created_at": q.created_at.isoformat() if q.created_at else None,
                    "responded_at": q.responded_at.isoformat() if getattr(q, "responded_at", None) else None,
                    "rejection_reason": getattr(q, "rejection_reason", None),
                }
                for q in quotes
            ]
        except Exception:
            return []

    def get_total_milestones(self, obj):
        try:
            return obj.funding_milestones.count()
        except Exception:
            return 0

    def get_completed_milestones(self, obj):
        try:
            return obj.funding_milestones.filter(status="paid").count()
        except Exception:
            return 0

    def get_attachments_count(self, obj):
        try:
            from files_management.models import FileAttachment
            return FileAttachment.objects.filter(
                content_type__model="specialorder",
                object_id=obj.id,
            ).count()
        except Exception:
            return 0

    def get_quoted_price(self, obj):
        return _latest_quote_amount(obj)


class SpecialOrderClientDetailSerializer(SpecialOrderDetailSerializer):
    class Meta(SpecialOrderDetailSerializer.Meta):
        fields = [
            field
            for field in SpecialOrderDetailSerializer.Meta.fields
            if field not in {"admin_notes", "client_email", "writer_pay_rule"}
        ]


class SpecialOrderWriterDetailSerializer(SpecialOrderActionContractMixin, serializers.ModelSerializer):
    writer_username = serializers.SerializerMethodField()
    website_name = serializers.SerializerMethodField()
    milestones = serializers.SerializerMethodField()
    total_milestones = serializers.SerializerMethodField()
    completed_milestones = serializers.SerializerMethodField()
    attachments_count = serializers.SerializerMethodField()
    reference = serializers.SerializerMethodField()
    writer_compensation = serializers.SerializerMethodField()

    class Meta:
        model = SpecialOrder
        fields = [
            "id",
            "public_order_number",
            "reference",
            "title",
            "inquiry_details",
            "duration_days",
            "currency",
            "pricing_mode",
            "status",
            "origin",
            "priority",
            "writer",
            "writer_username",
            "writer_compensation",
            "website_name",
            "predefined_config",
            "predefined_duration",
            "milestones",
            "total_milestones",
            "completed_milestones",
            "attachments_count",
            "available_actions",
            "blocked_actions",
            "assigned_at",
            "started_at",
            "completed_at",
            "created_at",
            "updated_at",
        ]

    def get_writer_username(self, obj):
        return _username(getattr(obj, "writer", None))

    def get_website_name(self, obj):
        w = getattr(obj, "website", None)
        return getattr(w, "name", None) or getattr(w, "domain", None)

    def get_reference(self, obj):
        return obj.reference

    def get_writer_compensation(self, obj):
        return SpecialOrderWriterListSerializer().get_writer_compensation(obj)

    def get_milestones(self, obj):
        try:
            from special_orders.models.delivery import SpecialOrderDeliverable

            deliverables = {
                d.metadata.get("milestone_id"): d
                for d in SpecialOrderDeliverable.objects.filter(
                    special_order=obj,
                ).order_by("-created_at")
                if d.metadata.get("milestone_id")
            }
            return [
                serialize_special_order_milestone(
                    order=obj,
                    milestone=m,
                    deliverable=deliverables.get(m.id),
                    include_money=False,
                )
                for m in obj.funding_milestones.all().order_by("sequence")
            ]
        except Exception:
            return []

    def get_total_milestones(self, obj):
        try:
            return obj.funding_milestones.count()
        except Exception:
            return 0

    def get_completed_milestones(self, obj):
        try:
            return obj.funding_milestones.filter(status="paid").count()
        except Exception:
            return 0

    def get_attachments_count(self, obj):
        try:
            from files_management.models import FileAttachment
            return FileAttachment.objects.filter(
                content_type__model="specialorder",
                object_id=obj.id,
            ).count()
        except Exception:
            return 0
