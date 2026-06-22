from rest_framework import serializers
from django.utils.timezone import now
from decimal import Decimal

from orders.models.orders import Order

from rest_framework.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from orders.registry.decorator import get_all_registered_actions
from django.utils import timezone


User = get_user_model()


STAFF_ROLES = {'admin', 'superadmin', 'support', 'editor'}
WRITER_HIDDEN_ORDER_FIELDS = {
    'client',
    'client_deadline',
    'client_email',
    'external_contact_email',
    'external_contact_name',
    'external_contact_phone',
    'payment_status',
    'total_price',
    'amount_paid',
    'remaining_balance',
}


def _apply_order_field_visibility(data, role):
    if role == 'writer':
        for field in WRITER_HIDDEN_ORDER_FIELDS:
            data.pop(field, None)
        return

    if role == 'client':
        data.pop('assigned_writer', None)
        data.pop('writer_compensation', None)


def _as_decimal(value) -> Decimal:
    try:
        return Decimal(str(value or "0"))
    except Exception:
        return Decimal("0")


def _collect_order_items(obj):
    try:
        return list(obj.items.all())
    except Exception:
        return []


def _payload_values(payload, *keys):
    if not isinstance(payload, dict):
        return []
    values = []
    for key in keys:
        value = payload.get(key)
        if isinstance(value, list):
            values.extend(value)
        elif value not in (None, ""):
            values.append(value)
    return values


class OrderBriefingFieldsMixin:
    """
    Computed order brief fields shared by list/detail serializers.

    These fields are intentionally safe for writers: they expose scope,
    deliverables, and writer-pay data, not client payment totals.
    """

    def _quantity_for(self, obj, *unit_types: str) -> int:
        total = 0
        for item in _collect_order_items(obj):
            if item.unit_type in unit_types:
                total += int(item.quantity or 0)
        if total:
            return total
        if getattr(obj, "unit_type", None) in unit_types:
            return int(getattr(obj, "base_quantity", 0) or 0)
        return 0

    def get_number_of_pages(self, obj) -> int:
        return self._quantity_for(obj, "page")

    def get_number_of_slides(self, obj) -> int:
        return self._quantity_for(obj, "slide")

    def get_number_of_designs(self, obj) -> int:
        return self._quantity_for(obj, "design_concept")

    def get_number_of_diagrams(self, obj) -> int:
        return self._quantity_for(obj, "diagram")

    def _current_snapshot(self, obj):
        try:
            # Use the prefetched attribute set by the base queryset Prefetch.
            # Fallback to a live filter when called outside a prefetched queryset
            # (e.g. detail views or nested serializers).
            prefetched = getattr(obj, '_current_pricing_snapshots', None)
            if prefetched is not None:
                return prefetched[0] if prefetched else None
            return obj.pricing_snapshots.filter(is_current=True).first()
        except Exception:
            return None

    def _pricing_payloads(self, obj) -> list[dict]:
        payloads = []
        current = self._current_snapshot(obj)
        if current and isinstance(current.pricing_payload, dict):
            payloads.append(current.pricing_payload)
        try:
            source_payload = getattr(obj.pricing_snapshot, "payload", None)
            if isinstance(source_payload, dict):
                payloads.append(source_payload)
        except Exception:
            pass
        for item in _collect_order_items(obj):
            if isinstance(item.metadata, dict):
                payloads.append(item.metadata)
        return payloads

    def get_selected_addon_codes(self, obj) -> list[str]:
        codes = []
        for payload in self._pricing_payloads(obj):
            codes.extend(
                _payload_values(
                    payload,
                    "selected_addon_codes",
                    "addon_codes",
                    "addons",
                )
            )
        normalized = []
        for code in codes:
            if isinstance(code, dict):
                code = code.get("code") or code.get("addon_code") or code.get("name")
            if code:
                normalized.append(str(code))
        return sorted(set(normalized))

    def get_addon_names(self, obj) -> list[str]:
        names = []
        for payload in self._pricing_payloads(obj):
            names.extend(_payload_values(payload, "addon_names", "addon_labels"))
            for addon in _payload_values(payload, "addons", "selected_addons"):
                if isinstance(addon, dict):
                    value = addon.get("name") or addon.get("label") or addon.get("code")
                    if value:
                        names.append(value)
                elif addon:
                    names.append(addon)
        if not names:
            names = self.get_selected_addon_codes(obj)
        return sorted(set(str(name).replace("_", " ") for name in names if name))

    def get_copies_of_sources_required(self, obj) -> bool:
        haystack = [
            *(getattr(obj, "flags", None) or []),
            *self.get_selected_addon_codes(obj),
            *self.get_addon_names(obj),
        ]
        for payload in self._pricing_payloads(obj):
            for key in ("copies_of_sources_required", "source_copies_required", "requires_source_copies"):
                if payload.get(key) is True:
                    return True
            haystack.extend(str(value) for value in payload.values() if isinstance(value, str))
        return any(
            any(token in str(item).lower() for token in ("copy", "copies", "source file", "sources"))
            for item in haystack
        )

    def get_order_items(self, obj) -> list[dict]:
        return [
            {
                "id": item.pk,
                "unit_type": item.unit_type,
                "item_kind": item.item_kind,
                "service_family": item.service_family,
                "service_code": item.service_code,
                "topic": item.topic,
                "quantity": item.quantity,
                "metadata": item.metadata,
            }
            for item in _collect_order_items(obj)
        ]

    def get_writer_pay_breakdown(self, obj) -> dict:
        current = self._current_snapshot(obj)
        total = (
            _as_decimal(current.writer_compensation_amount)
            if current
            else _as_decimal(getattr(obj, "writer_compensation", 0))
        )
        quantities = {
            "page": self.get_number_of_pages(obj),
            "slide": self.get_number_of_slides(obj),
            "design": self.get_number_of_designs(obj),
            "diagram": self.get_number_of_diagrams(obj),
        }
        rates = {
            key: str((total / Decimal(quantity)).quantize(Decimal("0.01")))
            for key, quantity in quantities.items()
            if quantity
        }
        return {
            "currency": getattr(obj, "currency", "USD") or "USD",
            "total": str(total.quantize(Decimal("0.01"))),
            "rates": rates,
            "source": "pricing_snapshot" if current else "order_summary",
        }


class OrderListSerializer(OrderBriefingFieldsMixin, serializers.ModelSerializer):
    """
    Lightweight serializer for order list views.
    Excludes large fields like order_instructions and style_reference_files.
    Strips cross-role identity fields: writers never see client_username and
    clients never see writer_username — enforced server-side here.
    """
    client_username = serializers.CharField(source='client.username', read_only=True, allow_null=True)
    writer_username = serializers.CharField(source='assigned_writer.username', read_only=True, allow_null=True)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            role = getattr(request.user, "role", None)
            if role == "writer":
                data.pop("client_username", None)
            elif role == "client":
                data.pop("writer_username", None)
            _apply_order_field_visibility(data, role)
        return data
    paper_type_name = serializers.CharField(source='paper_type.name', read_only=True, allow_null=True)
    academic_level_name = serializers.CharField(source='academic_level.name', read_only=True, allow_null=True)
    formatting_style_name = serializers.CharField(source='formatting_style.name', read_only=True, allow_null=True)
    type_of_work_name = serializers.CharField(source='type_of_work.name', read_only=True, allow_null=True)
    english_type_name = serializers.CharField(source='english_type.name', read_only=True, allow_null=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True, allow_null=True)
    number_of_pages = serializers.SerializerMethodField(read_only=True)
    number_of_slides = serializers.SerializerMethodField(read_only=True)
    number_of_designs = serializers.SerializerMethodField(read_only=True)
    number_of_diagrams = serializers.SerializerMethodField(read_only=True)
    addon_names = serializers.SerializerMethodField(read_only=True)
    selected_addon_codes = serializers.SerializerMethodField(read_only=True)
    copies_of_sources_required = serializers.SerializerMethodField(read_only=True)
    writer_pay_breakdown = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'public_order_number', 'reference', 'topic', 'paper_type', 'paper_type_name', 'academic_level', 'academic_level_name',
            'formatting_style', 'formatting_style_name', 'type_of_work', 'type_of_work_name',
            'english_type', 'english_type_name', 'client_deadline', 'writer_deadline',
            'client', 'client_username', 'writer_username',
            'preferred_writer', 'preferred_writer_status',
            'total_price', 'writer_compensation', 'subject', 'subject_name', 'status', 'payment_status', 'flags', 'created_at', 'updated_at',
            'is_follow_up', 'is_urgent', 'website',
            'service_family', 'service_code', 'is_composite',
            'number_of_pages', 'number_of_slides', 'number_of_designs', 'number_of_diagrams',
            'addon_names', 'selected_addon_codes', 'copies_of_sources_required',
            'writer_pay_breakdown',
        ]
        read_only_fields = [
            'id', 'public_order_number', 'reference', 'client_username', 'writer_username', 'total_price', 'writer_compensation',
            'payment_status', 'created_at', 'updated_at',
            'flags', 'writer_deadline'
        ]


class OrderSerializer(OrderBriefingFieldsMixin, serializers.ModelSerializer):
    client_username = serializers.CharField(source='client.username', read_only=True)
    writer_username = serializers.CharField(source='assigned_writer.username', read_only=True)
    paper_type_name = serializers.CharField(source='paper_type.name', read_only=True, allow_null=True)
    academic_level_name = serializers.CharField(source='academic_level.name', read_only=True, allow_null=True)
    formatting_style_name = serializers.CharField(source='formatting_style.name', read_only=True, allow_null=True)
    type_of_work_name = serializers.CharField(source='type_of_work.name', read_only=True, allow_null=True)
    english_type_name = serializers.CharField(source='english_type.name', read_only=True, allow_null=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True, allow_null=True)
    number_of_pages = serializers.SerializerMethodField(read_only=True)
    number_of_slides = serializers.SerializerMethodField(read_only=True)
    number_of_designs = serializers.SerializerMethodField(read_only=True)
    number_of_diagrams = serializers.SerializerMethodField(read_only=True)
    order_items = serializers.SerializerMethodField(read_only=True)
    addon_names = serializers.SerializerMethodField(read_only=True)
    selected_addon_codes = serializers.SerializerMethodField(read_only=True)
    copies_of_sources_required = serializers.SerializerMethodField(read_only=True)
    writer_pay_breakdown = serializers.SerializerMethodField(read_only=True)
    is_unattributed = serializers.SerializerMethodField(read_only=True)
    # Fake client ID for writers viewing unattributed orders
    fake_client_id = serializers.SerializerMethodField(read_only=True)
    # Expose external contact fields and unpaid override to admins only (gate in to_representation)
    external_contact_name = serializers.CharField(read_only=True)
    external_contact_email = serializers.EmailField(read_only=True)
    external_contact_phone = serializers.CharField(read_only=True)
    allow_unpaid_access = serializers.BooleanField(read_only=True)
    # Client information (role-based visibility in to_representation)
    client_email = serializers.SerializerMethodField(read_only=True)
    client_registration_id = serializers.SerializerMethodField(read_only=True)
    # Subject specialty information
    subject_is_technical = serializers.SerializerMethodField(read_only=True)
    # Revision eligibility info for clients
    revision_eligibility = serializers.SerializerMethodField(read_only=True)
    # Style reference files uploaded by client
    style_reference_files = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'public_order_number', 'reference', 'topic', 'order_instructions', 'paper_type', 'paper_type_name',
            'academic_level', 'academic_level_name',
            'formatting_style', 'formatting_style_name',
            'type_of_work', 'type_of_work_name',
            'english_type', 'english_type_name', 'base_quantity', 'unit_type',
            'client_deadline', 'writer_deadline',
            'client', 'client_username', 'client_email', 'client_registration_id', 'writer_username',
            'preferred_writer', 'total_price', 'writer_compensation',
            'subject', 'subject_name', 'subject_is_technical', 'status', 'payment_status', 'flags', 'created_at', 'updated_at',
            'created_by_admin', 'is_follow_up',
            'previous_order', 'requires_editing', 'editing_skip_reason', 'is_urgent',
            'is_unattributed', 'fake_client_id', 'external_contact_name', 'external_contact_email', 'external_contact_phone',
            'allow_unpaid_access', 'revision_eligibility', 'style_reference_files',
            'qa_review_note', 'qa_approved_at', 'qa_returned_at',
            'plagiarism_check_status', 'ai_detection_status', 'formatting_review_status', 'editor_notes',
            'service_family', 'service_code', 'is_composite',
            'number_of_pages', 'number_of_slides', 'number_of_designs', 'number_of_diagrams',
            'order_items', 'addon_names', 'selected_addon_codes',
            'copies_of_sources_required', 'writer_pay_breakdown',
        ]
        read_only_fields = [
            'id', 'public_order_number', 'reference', 'client_username', 'writer_username', 'total_price', 'writer_compensation',
            'payment_status', 'created_at', 'updated_at',
            'flags', 'writer_deadline', 'editing_skip_reason',
            'qa_review_note', 'qa_approved_at', 'qa_returned_at',
        ]

    def validate_academic_level(self, value):
        """
        Make sure the academic level belongs to the current website.
        """
        request = self.context['request']
        if value.website != request.website:
            raise serializers.ValidationError("Invalid academic level for this website.")
        return value

    def get_is_unattributed(self, obj):
        return obj.client_id is None and (
            bool(getattr(obj, 'external_contact_name', None)) or
            bool(getattr(obj, 'external_contact_email', None))
        )

    def get_fake_client_id(self, obj):
        """
        Returns a fake client ID for writers viewing unattributed orders.
        This ensures writers see a client ID even when the order is unattributed.
        """
        is_unattributed = obj.client_id is None and (
            bool(getattr(obj, 'external_contact_name', None)) or
            bool(getattr(obj, 'external_contact_email', None))
        )

        if is_unattributed:
            # Generate a consistent fake ID based on order ID
            # This ensures the same fake ID is shown for the same order
            return f"EXT-{obj.id:06d}"
        return None

    def get_client_email(self, obj):
        """Get client email (admin/superadmin only, filtered in to_representation)"""
        if obj.client:
            return obj.client.email
        return None

    def get_client_registration_id(self, obj):
        """Get client registration ID"""
        if obj.client and hasattr(obj.client, 'client_profile'):
            return obj.client.client_profile.registration_id
        return None

    def get_subject_is_technical(self, obj):
        """Get whether subject is technical"""
        if obj.subject:
            return getattr(obj.subject, 'is_technical', False)
        return None

    def get_revision_eligibility(self, obj):
        """
        Expose whether the order is still within the free revision window.
        Used by client dashboards to show 'Unlimited Revisions' vs
        'Past free revision period'.
        """
        # Only meaningful for completed orders
        status = (obj.status or '').lower()
        # Use submitted_at (writer finished) as primary completion timestamp,
        # falling back to updated_at if needed.
        completed_ts = getattr(obj, "submitted_at", None) or getattr(obj, "updated_at", None)
        if status != 'completed' or not completed_ts:
            return {
                "is_within_free_window": False,
                "free_revision_until": None,
                "days_left": 0,
            }

        try:
            from datetime import timedelta
            from order_configs.models import RevisionPolicyConfig

            # Cache per-website to avoid a DB hit for every order in a list.
            ctx = self.context if hasattr(self, 'context') else {}
            cache_key = f'_revision_policy_{getattr(obj.website, "pk", None)}'
            if cache_key not in ctx:
                ctx[cache_key] = RevisionPolicyConfig.objects.filter(
                    website=obj.website, active=True,
                ).first()
            policy = ctx.get(cache_key)
            deadline = timedelta(days=policy.free_revision_days if policy else 14)
        except Exception:
            return {
                "is_within_free_window": False,
                "free_revision_until": None,
                "days_left": 0,
            }

        free_until = completed_ts + deadline
        now_ts = timezone.now()
        if now_ts >= free_until:
            return {
                "is_within_free_window": False,
                "free_revision_until": free_until.isoformat(),
                "days_left": 0,
            }

        delta = free_until - now_ts
        days_left = max(0, delta.days)
        return {
            "is_within_free_window": True,
            "free_revision_until": free_until.isoformat(),
            "days_left": days_left,
        }

    def get_style_reference_files(self, obj):
        """Get style reference files for this order."""
        try:
            from files_management.api.serializers.response_serializers import (
                FileAttachmentDetailSerializer,
            )
            from files_management.enums import FilePurpose
            from files_management.selectors import FileAttachmentSelector

            style_refs = FileAttachmentSelector.for_object_and_purpose(
                website=obj.website,
                obj=obj,
                purpose=FilePurpose.STYLE_REFERENCE,  # type: ignore[arg-type]
            ).select_related("managed_file", "external_link")

            serializer = FileAttachmentDetailSerializer(
                style_refs,
                many=True,
                context=self.context
            )
            return serializer.data
        except Exception:
            return []

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Hide external contact details from non-admin roles
        request = self.context.get('request')
        role = getattr(getattr(request, 'user', None), 'role', None)
        user = getattr(request, 'user', None)

        is_unattributed = instance.client_id is None and (
            bool(getattr(instance, 'external_contact_name', None)) or
            bool(getattr(instance, 'external_contact_email', None))
        )

        # Role-based field visibility
        if role not in STAFF_ROLES:
            data.pop('external_contact_name', None)
            data.pop('external_contact_email', None)
            data.pop('external_contact_phone', None)
            # Hide client email and registration_id from non-admin roles
            data.pop('client_email', None)
            # Keep client_registration_id visible to writers (they need client ID)
            if role != 'writer':
                data.pop('client_registration_id', None)
            # keep allow_unpaid_access visible only if owner/admin
            if role not in ['admin', 'superadmin'] and user != instance.client:
                data.pop('allow_unpaid_access', None)

        # For writers viewing unattributed orders, show fake client ID instead of null
        if role == 'writer' and is_unattributed and not data.get('client'):
            # Keep fake_client_id visible to writers
            # Optionally, set client_username to the fake ID for display
            if data.get('fake_client_id'):
                data['client_username'] = data['fake_client_id']
                # Also set client_registration_id to fake_client_id for consistency
                data['client_registration_id'] = data['fake_client_id']
        elif role not in STAFF_ROLES:
            # Hide fake_client_id from non-admin roles (except writers who need it)
            if role != 'writer':
                data.pop('fake_client_id', None)

        _apply_order_field_visibility(data, role)

        return data

    def perform_create(self, serializer):
        is_follow_up = self.request.data.get('is_follow_up', False)
        previous_order_id = self.request.data.get('previous_order')

        if is_follow_up and not previous_order_id:
            raise serializers.ValidationError("Follow-up orders must reference a previous order.")

        previous_order = None
        if previous_order_id:
            previous_order = Order.objects.get(id=previous_order_id)
            if previous_order.client != self.request.user:
                raise PermissionDenied("You can only follow up on your own orders.")

        serializer.save(client=self.request.user, previous_order=previous_order)


class OrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            'topic', 'order_instructions', 'paper_type', 'academic_level',
            'formatting_style', 'type_of_work', 'english_type', 'client_deadline', 'client', 'preferred_writer'
        ]

    def validate_deadline(self, value):
        """Ensure the deadline is in the future."""
        if value <= now():
            raise serializers.ValidationError("The deadline must be in the future.")
        return value

    def validate_preferred_writer(self, value):
        """Ensure the preferred writer is available."""
        if value and not value.is_active:
            raise serializers.ValidationError("The preferred writer is not available.")
        return value


class OrderActionSerializer(serializers.Serializer):
    action = serializers.CharField(required=True)
    order_id = serializers.IntegerField(required=True)
    params = serializers.DictField(required=False, default=dict)

    # You can also add custom validation logic here if needed
    def validate_action(self, value):
        """
        Ensure the action is valid.
        """
        if value not in get_all_registered_actions():
            raise serializers.ValidationError(f"Action '{value}' is not registered.")
        return value

    def validate_order_id(self, value):
        """
        Ensure the order exists.
        """
        if not Order.objects.filter(id=value).exists():
            raise serializers.ValidationError(f"Order with id {value} does not exist.")
        return value
