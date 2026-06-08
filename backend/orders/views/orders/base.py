from datetime import datetime, time
from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.db import models, transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.dateparse import parse_date, parse_datetime
from django.utils.functional import cached_property
from django.core.cache import cache
from rest_framework import decorators, mixins, status, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.core.exceptions import ValidationError
from orders.models.orders import Order
from orders.order_enums import OrderFlags, OrderStatus
from orders.permissions import IsAdminOrSuperAdmin, IsOrderOwnerOrSupport
from orders.serializers.orders import OrderSerializer
from payments_processor.models import PaymentIntent
from orders.exceptions import InvalidTransitionError
from orders.services.old_services.order_deletion_service import (
    ALLOWED_STAFF_ROLES,
    OrderDeletionService,
)
from wallets.exceptions import InsufficientWalletBalanceError


class LimitedPagination(PageNumberPagination):
    """Custom pagination class with safety limits to prevent performance issues."""
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 500 # Safety limit to prevent excessive data transfer

    def get_paginated_response(self, data):
        """Return paginated response with metadata."""
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data,
            'current_page': self.page.number,
            'total_pages': self.page.paginator.num_pages,
        })


STATUS_GROUPS = {
    "initial": [
        OrderStatus.CREATED.value,
        OrderStatus.PENDING.value,
        OrderStatus.UNPAID.value,
    ],
    "payment": [
        OrderStatus.AVAILABLE.value,
        OrderStatus.PENDING.value,
    ],
    "assignment": [
        OrderStatus.PENDING_WRITER_ASSIGNMENT.value,
        OrderStatus.PENDING_PREFERRED.value,
        OrderStatus.AVAILABLE.value,
    ],
    "active": [
        OrderStatus.CREATED.value,
        OrderStatus.PENDING.value,
        OrderStatus.UNPAID.value,
        OrderStatus.AVAILABLE.value,
        OrderStatus.ASSIGNED.value,
        OrderStatus.IN_PROGRESS.value,
        OrderStatus.UNDER_EDITING.value,
        OrderStatus.ON_HOLD.value,
        OrderStatus.REASSIGNED.value,
        OrderStatus.SUBMITTED.value,
    ],
    "pending": [
        OrderStatus.PENDING.value,
        OrderStatus.UNPAID.value,
        OrderStatus.PENDING_PREFERRED.value,
        OrderStatus.PENDING_WRITER_ASSIGNMENT.value,
        OrderStatus.AVAILABLE.value,
    ],
    "submission": [
        OrderStatus.SUBMITTED.value,
        OrderStatus.REVIEWED.value,
        OrderStatus.RATED.value,
    ],
    "revision": [
        OrderStatus.REVISION_REQUESTED.value,
        OrderStatus.ON_REVISION.value,
        OrderStatus.REVISED.value,
    ],
    "editing": [
        OrderStatus.UNDER_EDITING.value,
    ],
    "needs_attention": [
        OrderStatus.REVISION_REQUESTED.value,
        OrderStatus.ON_REVISION.value,
        OrderStatus.REVISED.value,
        OrderStatus.DISPUTED.value,
        OrderStatus.LATE.value,
        OrderStatus.CRITICAL.value,
        OrderStatus.ON_HOLD.value,
    ],
    "completed": [
        OrderStatus.COMPLETED.value,
        OrderStatus.APPROVED.value,
        OrderStatus.RATED.value,
        OrderStatus.REVIEWED.value,
        OrderStatus.CLOSED.value,
    ],
    "cancelled": [
        OrderStatus.CANCELLED.value,
        OrderStatus.REFUNDED.value,
    ],
    "archived": [
        OrderStatus.ARCHIVED.value,
        OrderStatus.REFUNDED.value,
        OrderStatus.CANCELLED.value,
        OrderStatus.EXPIRED.value,
    ],
    "final": [
        OrderStatus.CLOSED.value,
        OrderStatus.ARCHIVED.value,
    ],
}


class OrderBaseViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """
    Base viewset for orders. Supports list, retrieve, and update operations.

    Attributes:
        queryset: QuerySet of Order objects.
        serializer_class: Serializer used for order objects.
        permission_classes: List of permission classes.
    """

    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsOrderOwnerOrSupport]
    pagination_class = LimitedPagination # Paginated with safety limits


    def get_serializer_class(self):
        """
        Use lightweight serializer for list views to reduce data transfer.
        """
        if self.action == 'list':
            from orders.serializers_legacy import OrderListSerializer
            return OrderListSerializer
        return OrderSerializer

    def update(self, request, *args, **kwargs):
        """
        Update order fields.

        Admin and superadmin can edit order metadata directly. Workflow
        transitions should still prefer the action system, but this endpoint
        supports controlled staff corrections for order detail fields.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        role = getattr(request.user, "role", None)
        is_full_order_editor = (
            request.user.is_superuser or role in {"admin", "superadmin"}
        )

        if is_full_order_editor:
            editable_fields = {
                "topic",
                "order_instructions",
                "paper_type",
                "academic_level",
                "formatting_style",
                "subject",
                "type_of_work",
                "english_type",
                "client_deadline",
                "writer_deadline",
                "base_quantity",
                "unit_type",
                "status",
                "visibility_mode",
                "preferred_writer_status",
                "total_price",
                "amount_paid",
                "currency",
                "payment_status",
                "writer_compensation",
                "service_family",
                "service_code",
                "is_urgent",
                "requires_editing",
                "editing_skip_reason",
                "discount_code_used",
                "flags",
                "completion_notes",
                "qa_review_note",
            }
            fk_fields = {
                "paper_type",
                "academic_level",
                "formatting_style",
                "subject",
                "type_of_work",
                "english_type",
            }
            decimal_fields = {
                "total_price",
                "amount_paid",
                "writer_compensation",
            }
            datetime_fields = {"client_deadline", "writer_deadline"}
            boolean_fields = {"is_urgent", "requires_editing"}
            integer_fields = {"base_quantity"}

            provided = {
                key: value
                for key, value in request.data.items()
                if key in editable_fields
            }
            if not provided:
                return Response(
                    {
                        "detail": "No editable order fields provided.",
                        "allowed_fields": sorted(editable_fields),
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            update_fields = []
            errors = {}

            for field, value in provided.items():
                if field in fk_fields:
                    if value in ("", None):
                        if field == "paper_type":
                            errors[field] = "Paper type is required."
                            continue
                        setattr(instance, f"{field}_id", None)
                        update_fields.append(field)
                        continue
                    try:
                        pk = int(value)
                    except (TypeError, ValueError):
                        errors[field] = "Expected a numeric config id."
                        continue

                    model_field = instance._meta.get_field(field)
                    related_model = model_field.remote_field.model
                    related_obj = related_model.objects.filter(pk=pk).first()
                    if related_obj is None:
                        errors[field] = "Config option does not exist."
                        continue
                    related_website_id = getattr(related_obj, "website_id", None)
                    if (
                        related_website_id is not None
                        and related_website_id != instance.website_id
                    ):
                        errors[field] = "Config option belongs to a different website."
                        continue
                    setattr(instance, f"{field}_id", pk)
                    update_fields.append(field)
                    continue

                if field in decimal_fields:
                    if value in ("", None):
                        value = Decimal("0")
                    try:
                        value = Decimal(str(value))
                    except (InvalidOperation, ValueError):
                        errors[field] = "Expected a valid decimal amount."
                        continue

                if field in datetime_fields:
                    if value in ("", None):
                        if field == "client_deadline":
                            errors[field] = "Client deadline is required."
                            continue
                        value = None
                    else:
                        parsed = parse_datetime(str(value))
                        if parsed is None:
                            errors[field] = "Expected an ISO datetime."
                            continue
                        if timezone.is_naive(parsed):
                            parsed = timezone.make_aware(
                                parsed,
                                timezone.get_current_timezone(),
                            )
                        value = parsed

                if field in boolean_fields:
                    if value in ("", None) and field == "requires_editing":
                        value = None
                    elif isinstance(value, bool):
                        pass
                    else:
                        value = str(value).strip().lower() in {
                            "1",
                            "true",
                            "yes",
                            "on",
                        }

                if field in integer_fields:
                    try:
                        value = int(value)
                    except (TypeError, ValueError):
                        errors[field] = "Expected a whole number."
                        continue
                    if value < 0:
                        errors[field] = "Must be zero or greater."
                        continue

                if field == "flags" and not isinstance(value, list):
                    errors[field] = "Expected a list of flags."
                    continue

                setattr(instance, field, value)
                update_fields.append(field)

            if errors:
                return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)

            if "updated_at" not in update_fields:
                update_fields.append("updated_at")
            instance.save(update_fields=sorted(set(update_fields)))
            instance.refresh_from_db()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)

        # Define allowed fields that can be updated directly
        # These fields are updated directly on the model, bypassing serializer validation
        allowed_direct_fields = {
            'completion_notes', # For revision notes and completion notes
        }

        # Fields that go through serializer validation
        allowed_serializer_fields = {
            'order_instructions', # For updating instructions
        }

        # Separate direct updates from serializer updates
        direct_updates = {}
        serializer_updates = {}

        for key, value in request.data.items():
            if key in allowed_direct_fields:
                direct_updates[key] = value
            elif key in allowed_serializer_fields:
                serializer_updates[key] = value

        if not direct_updates and not serializer_updates:
            return Response(
                {
                    "detail": "No allowed fields provided for update. Allowed fields: " +
                    ", ".join(allowed_direct_fields | allowed_serializer_fields)
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update direct fields on the model (bypass serializer since completion_notes is not in serializer fields)
        update_fields = []
        for field, value in direct_updates.items():
            # Validate field exists on model
            if hasattr(instance, field):
                setattr(instance, field, value)
                update_fields.append(field)
            else:
                return Response(
                    {"detail": f"Field '{field}' does not exist on Order model"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Update serializer fields if any
        if serializer_updates:
            try:
                serializer = self.get_serializer(instance, data=serializer_updates, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                # Add serializer fields to update_fields
                update_fields.extend(serializer_updates.keys())
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error updating order serializer fields: {str(e)}", exc_info=True)
                return Response(
                    {"detail": f"Error updating order: {str(e)}", "errors": getattr(serializer, 'errors', {})},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Save direct updates
        if direct_updates:
            # Always include updated_at in update_fields
            if 'updated_at' not in update_fields:
                update_fields.append('updated_at')
            instance.save(update_fields=update_fields)

        # Return updated order
        instance.refresh_from_db()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def get_queryset(self):
        """
        Returns the filtered queryset for the current user.

        Returns:
            QuerySet: A queryset filtered based on user role.
        """
        user = self.request.user

        # Check if user is authenticated
        if not user or not user.is_authenticated:
            return Order.objects.none()

        # Check if this is a simple count/check query (page_size=1, minimal params)
        # Store this as an attribute so list() method can access it
        params = self.request.query_params
        self._is_simple_query = (
            self.action == 'list' and
            params.get('page_size', '10') in ['1', '0'] and
            len([k for k in params.keys() if k not in ['page', 'page_size', 'ordering']]) <= 2
        )

        # Select-related for valid FK fields only (writer assignment is via OrderAssignment model)
        qs = Order.objects.all().select_related(
            'client',
            'website',
            'preferred_writer',
            'paper_type',
            'academic_level',
            'formatting_style',
            'type_of_work',
            'english_type',
            'subject',
            'previous_order',
            'discount',
        )

        # Role-based scoping
        # Both superadmin and admin should see all orders (no website filtering)
        user_role = getattr(user, 'role', None)
        if user.is_superuser or user_role == 'superadmin':
            base_qs = qs
        elif user_role == 'client':
            # For clients, use indexed client_id filter for better performance
            # Add explicit ordering to use created_at index
            base_qs = qs.filter(client_id=user.id).order_by('-created_at')
        elif user_role == 'writer':
            from orders.selectors.order_visibility_selector import (
                OrderVisibilitySelector,
            )

            visible_ids = OrderVisibilitySelector.visible_to_writer(
                writer=user,
            ).values_list("id", flat=True)
            base_qs = qs.filter(id__in=visible_ids)
        elif user_role in ['admin', 'support', 'editor']:
            # Admins, support, and editors see all orders (no website filtering)
            base_qs = qs
        else:
            base_qs = qs.none()

        # Query param filters
        params = self.request.query_params

        def parse_bool(value):
            if value is None:
                return None
            if isinstance(value, bool):
                return value
            return str(value).strip().lower() in {"1", "true", "yes", "on"}

        def parse_decimal_param(value):
            if value in (None, ""):
                return None
            try:
                return Decimal(str(value))
            except (InvalidOperation, ValueError):
                return None

        def parse_datetime_param(value, *, end_of_day=False):
            if not value:
                return None
            dt = parse_datetime(value)
            if dt is None:
                date_value = parse_date(value)
                if date_value is None:
                    return None
                dt = datetime.combine(
                    date_value,
                    time.max if end_of_day else time.min,
                )
                if settings.USE_TZ:
                    dt = timezone.make_aware(dt, timezone.get_current_timezone())
            elif settings.USE_TZ and timezone.is_naive(dt):
                dt = timezone.make_aware(dt, timezone.get_current_timezone())
            return dt

        def parse_csv(value):
            if not value:
                return []
            if isinstance(value, (list, tuple)):
                return [str(item).strip() for item in value if str(item).strip()]
            return [item.strip() for item in str(value).split(",") if item.strip()]

        unattributed = params.get('unattributed')
        if unattributed is not None:
            val = unattributed.lower() in ['1', 'true', 'yes']
            if val:
                base_qs = base_qs.filter(client__isnull=True).filter(
                    models.Q(external_contact_name__isnull=False) | models.Q(external_contact_email__isnull=False)
                )
            else:
                base_qs = base_qs.exclude(client__isnull=True)

        contact_search = params.get('contact')
        if contact_search:
            base_qs = base_qs.filter(
                models.Q(external_contact_name__icontains=contact_search) |
                models.Q(external_contact_email__icontains=contact_search) |
                models.Q(external_contact_phone__icontains=contact_search)
            )

        # is_paid is a property (amount_paid >= total_price), not a DB field.
        # Filter by payment_status instead.
        paid = parse_bool(params.get('is_paid'))
        if paid is not None:
            if paid:
                base_qs = base_qs.filter(payment_status='paid')
            else:
                base_qs = base_qs.exclude(payment_status='paid')

        # is_special_order is not a DB field on Order; skip this filter.
        # Special orders live in a separate model/app.

        # Apply status filtering early for optimal query performance
        # This uses the status index and reduces the dataset early
        statuses = parse_csv(params.get('status'))
        status_groups = parse_csv(params.get('status_group'))

        # Combine status and status_group filters
        if statuses or status_groups:
            resolved_statuses = set()

            # Add explicit statuses
            if statuses:
                resolved_statuses.update(statuses)

            # Add status group statuses
            if status_groups:
                for group in status_groups:
                    resolved_statuses.update(STATUS_GROUPS.get(group, []))

            # Apply single filter with all statuses (uses index efficiently)
            if resolved_statuses:
                base_qs = base_qs.filter(status__in=list(resolved_statuses))

        # Filter by "can transition to" - orders that can transition to a specific status
        can_transition_to = params.get('can_transition_to')
        if can_transition_to:
            from orders.services.status_transition_service import VALID_TRANSITIONS
            can_transition_statuses = [
                from_status for from_status, allowed_transitions in VALID_TRANSITIONS.items()
                if can_transition_to in allowed_transitions
            ]
            if can_transition_statuses:
                base_qs = base_qs.filter(status__in=can_transition_statuses)

        # Filter by "needs attention" - overdue, stuck, unassigned, etc.
        needs_attention = params.get('needs_attention')
        if needs_attention:
            from django.utils import timezone
            from datetime import timedelta

            if needs_attention == 'overdue':
                now = timezone.now()
                base_qs = base_qs.filter(
                    client_deadline__lt=now,
                    status__in=[
                        OrderStatus.IN_PROGRESS.value,
                        OrderStatus.ON_HOLD.value,
                        OrderStatus.SUBMITTED.value,
                        OrderStatus.PENDING.value,
                        OrderStatus.AVAILABLE.value,
                    ]
                )
            elif needs_attention == 'stuck':
                cutoff = timezone.now() - timedelta(days=7)
                base_qs = base_qs.filter(
                    updated_at__lt=cutoff,
                    status__in=[
                        OrderStatus.IN_PROGRESS.value,
                        OrderStatus.ON_HOLD.value,
                        OrderStatus.AVAILABLE.value,
                        OrderStatus.PENDING_WRITER_ASSIGNMENT.value,
                    ]
                )
            elif needs_attention == 'unassigned':
                base_qs = base_qs.filter(
                    status__in=[
                        OrderStatus.AVAILABLE.value,
                        OrderStatus.PENDING_WRITER_ASSIGNMENT.value,
                        OrderStatus.PENDING_PREFERRED.value,
                    ]
                )
            elif needs_attention == 'unpaid':
                base_qs = base_qs.filter(
                    payment_status__in=['unpaid', 'partial'],
                    status__in=[
                        OrderStatus.UNPAID.value,
                        OrderStatus.PENDING.value,
                    ]
                )

        # Filter by recently transitioned
        recently_transitioned = params.get('recently_transitioned')
        if recently_transitioned:
            from django.utils import timezone
            from datetime import timedelta
            from orders.models.orders import OrderTransitionLog

            period_map = {
                '1h': timedelta(hours=1),
                '6h': timedelta(hours=6),
                '24h': timedelta(hours=24),
                '7d': timedelta(days=7),
            }

            cutoff = timezone.now() - period_map.get(recently_transitioned, timedelta(hours=24))
            recent_order_ids = OrderTransitionLog.objects.filter(
                timestamp__gte=cutoff
            ).values_list('order_id', flat=True).distinct()
            base_qs = base_qs.filter(id__in=recent_order_ids)

        # Text search
        search_term = params.get('q') or params.get('search')
        if search_term:
            search_term = search_term.strip()
            search_filter = (
                Q(topic__icontains=search_term)
                | Q(order_instructions__icontains=search_term)
                | Q(client__username__icontains=search_term)
                | Q(client__email__icontains=search_term)
                | Q(subject__name__icontains=search_term)
            )
            if search_term.isdigit():
                search_filter |= Q(id=int(search_term))
            base_qs = base_qs.filter(search_filter)

        # ID filter
        ids_param = parse_csv(params.get('ids'))
        if ids_param:
            id_list = []
            for value in ids_param:
                if value.isdigit():
                    id_list.append(int(value))
            if id_list:
                base_qs = base_qs.filter(id__in=id_list)

        # Numeric and select filters
        mapping_fields = {
            'subject_id': 'subject_id',
            'paper_type_id': 'paper_type_id',
            'academic_level_id': 'academic_level_id',
            'type_of_work_id': 'type_of_work_id',
            'english_type_id': 'english_type_id',
            'formatting_style_id': 'formatting_style_id',
            'writer_id': 'preferred_writer_id',
            'preferred_writer_id': 'preferred_writer_id',
            'client_id': 'client_id',
        }
        for param_name, field_name in mapping_fields.items():
            value = params.get(param_name)
            if value and str(value).isdigit():
                base_qs = base_qs.filter(**{field_name: int(value)})

        # Writer/client query strings
        writer_query = params.get('writer_query')
        if writer_query:
            base_qs = base_qs.filter(
                Q(preferred_writer__username__icontains=writer_query)
                | Q(preferred_writer__email__icontains=writer_query)
            )

        client_query = params.get('client_query')
        if client_query:
            base_qs = base_qs.filter(
                Q(client__username__icontains=client_query)
                | Q(client__email__icontains=client_query)
            )

        # Pages filter
        pages_min = params.get('pages_min')
        if pages_min and pages_min.isdigit():
            base_qs = base_qs.filter(number_of_pages__gte=int(pages_min))
        pages_max = params.get('pages_max')
        if pages_max and pages_max.isdigit():
            base_qs = base_qs.filter(number_of_pages__lte=int(pages_max))

        # Flags filter
        flag_values = parse_csv(params.get('flags'))
        if flag_values:
            for flag in flag_values:
                base_qs = base_qs.filter(flags__contains=[flag])

        # Price filters
        price_min = parse_decimal_param(params.get('price_min'))
        if price_min is not None:
            base_qs = base_qs.filter(total_price__gte=price_min)
        price_max = parse_decimal_param(params.get('price_max'))
        if price_max is not None:
            base_qs = base_qs.filter(total_price__lte=price_max)

        # Deadline range
        deadline_from = parse_datetime_param(params.get('deadline_from'))
        deadline_to = parse_datetime_param(params.get('deadline_to'), end_of_day=True)
        if deadline_from:
            base_qs = base_qs.filter(client_deadline__gte=deadline_from)
        if deadline_to:
            base_qs = base_qs.filter(client_deadline__lte=deadline_to)

        # Created range
        created_from = parse_datetime_param(params.get('created_from') or params.get('date_from'))
        created_to = parse_datetime_param(params.get('created_to') or params.get('date_to'), end_of_day=True)
        if created_from:
            base_qs = base_qs.filter(created_at__gte=created_from)
        if created_to:
            base_qs = base_qs.filter(created_at__lte=created_to)

        # Updated range
        updated_from = parse_datetime_param(params.get('updated_from'))
        updated_to = parse_datetime_param(params.get('updated_to'), end_of_day=True)
        if updated_from:
            base_qs = base_qs.filter(updated_at__gte=updated_from)
        if updated_to:
            base_qs = base_qs.filter(updated_at__lte=updated_to)

        include_archived = parse_bool(params.get('include_archived'))
        only_archived = parse_bool(params.get('only_archived'))

        # Admin and superadmin should see all orders including archived by default
        # unless explicitly excluded
        is_admin_or_superadmin = (
            user.is_superuser or
            user_role in ['admin', 'superadmin', 'support']
        )

        if only_archived:
            archived_statuses = STATUS_GROUPS["archived"]
            base_qs = base_qs.filter(status__in=archived_statuses)
        elif not include_archived and not status_groups and not statuses:
            # For admin/superadmin: include archived by default
            # For others: exclude archived unless explicitly requested
            if not is_admin_or_superadmin:
                base_qs = base_qs.exclude(status=OrderStatus.ARCHIVED.value)
            # Admin/superadmin see all orders including archived (no exclusion)

        # Sorting
        sort_field = params.get('sort_by')
        allowed_sorts = {
            'created_at',
            'updated_at',
            'client_deadline',
            'total_price',
            'status',
        }
        sort_direction = params.get('sort_dir', 'desc')
        if sort_field in allowed_sorts:
            direction = '-' if sort_direction != 'asc' else ''
            base_qs = base_qs.order_by(f"{direction}{sort_field}", '-id')
        else:
            base_qs = base_qs.order_by('-created_at', '-id')

        # Apply ordering - use created_at index for better performance
        # The Order model has ordering = ['-created_at'] in Meta, but we ensure it here
        # for list views, use the index efficiently
        if self.action == 'list':
            # For list views, ensure we're using the created_at index
            base_qs = base_qs.order_by('-created_at')

        return base_qs

    def list(self, request, *args, **kwargs):
        """
        Override list to ensure queryset is not filtered by object permissions.
        DRF doesn't filter list results by object permissions by default,
        but we want to make sure our queryset filtering works correctly.
        Also includes phone reminder info for clients.
        Adds caching for simple queries to improve performance.
        """
        from django.core.cache import cache
        import hashlib
        import json

        # Only cache simple, frequently-used queries (status, is_paid filters)
        params = request.query_params
        has_simple_filters = (
            len(params) <= 3 and # Only 1-3 query params
            all(key in ['status', 'is_paid', 'page', 'page_size', 'ordering'] for key in params.keys())
        )

        # For very simple queries (page_size=1), use longer cache
        is_simple_count_query = (
            params.get('page_size', '10') in ['1', '0'] and
            len([k for k in params.keys() if k not in ['page', 'page_size', 'ordering']]) <= 2
        )
        cache_ttl = 120 if is_simple_count_query else 30 # 2 minutes for count queries, 30s for others

        cache_key: str | None = None
        if has_simple_filters and request.user.is_authenticated:
            # Build cache key
            cache_key_parts = [
                'orders_list',
                str(request.user.id),
                str(request.user.role),
                json.dumps(dict(sorted(params.items())), sort_keys=True)
            ]
            cache_key_data = ':'.join(cache_key_parts)
            cache_key = f"orders_list:{hashlib.md5(cache_key_data.encode()).hexdigest()}"

            # Try cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return Response(cached_result)

        try:
            queryset = self.filter_queryset(self.get_queryset())

            # Ensure distinct() is applied for complex OR queries
            if hasattr(queryset.query, 'where') and queryset.query.where:
                queryset = queryset.distinct()

            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                response = self.get_paginated_response(serializer.data)
            else:
                serializer = self.get_serializer(queryset, many=True)
                response = Response(serializer.data)

            # Cache simple queries
            if has_simple_filters and request.user.is_authenticated:
                if hasattr(response, 'data'):
                    cache.set(cache_key, response.data, cache_ttl)

            # Add phone reminder info for clients (skip for simple count queries)
            is_simple = getattr(self, '_is_simple_query', False)
            if (request.user.role in ['client', 'customer'] and not is_simple):
                from users.services.phone_reminder_service import PhoneReminderService
                phone_service = PhoneReminderService(request.user)

                # Check if reminder should be shown (user has active orders)
                active_orders = queryset.filter(
                    status__in=['pending', 'in_progress', 'submitted', 'reviewed',
                               'rated', 'revision_requested', 'on_revision', 'revised']
                ).exists()

                if active_orders and phone_service.should_show_reminder_in_order_context():
                    reminder_info = phone_service.get_reminder_info()
                    if isinstance(response.data, dict):
                        response.data['phone_reminder'] = reminder_info

            return response
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in OrderBaseViewSet.list: {str(e)}", exc_info=True)
            # Return empty result instead of 500 error
            return Response({
                'count': 0,
                'next': None,
                'previous': None,
                'results': [],
                'total_pages': 0,
            })

    def get_object(self):
        """
        Override get_object to check permissions first, then fetch the order.
        This ensures that even if the queryset filters out an order (e.g., unpaid orders for writers),
        we can still check object-level permissions and provide better error messages.
        """
        from rest_framework.exceptions import NotFound, PermissionDenied

        # Get the order ID from the URL kwargs
        # DRF uses 'pk' as the default lookup_field
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        order_id = self.kwargs[lookup_url_kwarg]

        # Fetch the order directly from the database (bypass queryset filtering)
        # This allows us to check permissions even if the queryset would exclude it
        try:
            order = Order.objects.select_related(
                'client', 'website', 'preferred_writer'
            ).get(id=order_id)
        except Order.DoesNotExist:
            raise NotFound("No Order matches the given query.")

        # Check object-level permissions
        # This will check if the user has permission to view this specific order
        permission_classes = self.get_permissions()
        for permission in permission_classes:
            if hasattr(permission, 'has_object_permission'):
                if not permission.has_object_permission(self.request, self, order):
                    # Provide a more helpful error message
                    if self.request.user.role == 'writer' and not order.is_fully_paid:
                        raise PermissionDenied(
                            "You cannot view this order because it has not been paid yet. "
                            "Only paid orders are visible to writers."
                        )
                    raise PermissionDenied(
                        "You do not have permission to view this order."
                    )

        return order

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a single order with phone reminder info for clients.
        """
        response = super().retrieve(request, *args, **kwargs)

        # Add phone reminder info for clients viewing orders
        if request.user.role in ['client', 'customer']:
            from users.services.phone_reminder_service import PhoneReminderService
            phone_service = PhoneReminderService(request.user)

            order = self.get_object()
            if phone_service.should_show_reminder_in_order_context(order):
                reminder_info = phone_service.get_reminder_info()
                if isinstance(response.data, dict):
                    response.data['phone_reminder'] = reminder_info

        return response

    @decorators.action(detail=False, methods=["get"], url_path="filter-options", permission_classes=[IsAuthenticated])
    def filter_options(self, request):
        status_list = [
            {"value": status.value, "label": status.name.replace("_", " ").title()}
            for status in OrderStatus
        ]
        status_groups = [
            {
                "key": key,
                "label": key.replace("_", " ").title(),
                "statuses": values,
            }
            for key, values in STATUS_GROUPS.items()
        ]
        flag_options = [
            {"value": flag.value, "label": flag.name.replace("_", " ").title()}
            for flag in OrderFlags
        ]
        return Response(
            {
                "statuses": status_list,
                "status_groups": status_groups,
                "flags": flag_options,
            }
        )

    @decorators.action(detail=False, methods=["get"], url_path="summary", permission_classes=[IsAuthenticated])
    def summary(self, request):
        """
        Return role-scoped order counts with status and group breakdowns.
        Respects the same filters as the list endpoint.
        """
        cache_key = f"orders:summary:{request.user.id}:{request.get_full_path()}"
        cached_payload = cache.get(cache_key)
        if cached_payload is not None:
            return Response(cached_payload)

        queryset = self.filter_queryset(self.get_queryset())
        status_counts = queryset.values("status").annotate(count=models.Count("id"))
        status_breakdown = {
            item["status"]: item["count"] for item in status_counts
        }

        total_count = sum(status_breakdown.values())
        group_breakdown = {}
        for key, statuses in STATUS_GROUPS.items():
            group_breakdown[key] = sum(
                status_breakdown.get(status, 0) for status in statuses
            )

        payload = {
            "total": total_count,
            "status_breakdown": status_breakdown,
            "status_group_breakdown": group_breakdown,
        }
        cache.set(cache_key, payload, timeout=30)
        return Response(payload)

    @decorators.action(
        detail=True,
        methods=["get"],
        url_path="payment-summary",
        permission_classes=[IsAuthenticated, IsAdminOrSuperAdmin],
    )
    def payment_summary(self, request, pk=None):
        """
        Provide payment and installment summary for the order owner or staff.
        """
        from django.contrib.contenttypes.models import ContentType
        order = self.get_object()
        order_ct = ContentType.objects.get_for_model(Order)
        payments_qs = PaymentIntent.objects.filter(
            payable_content_type=order_ct,
            payable_object_id=order.pk,
        ).order_by("-created_at")

        def _sum_amount(queryset):
            total = queryset.aggregate(total=models.Sum("amount")).get("total")
            return total or Decimal("0.00")

        completed_statuses = ["succeeded"]
        pending_statuses = ["pending", "processing", "requires_action", "created"]
        refunded_statuses = ["refunded", "partially_refunded"]

        amount_paid = _sum_amount(payments_qs.filter(status__in=completed_statuses))
        pending_amount = _sum_amount(payments_qs.filter(status__in=pending_statuses))
        refunded_amount = _sum_amount(payments_qs.filter(status__in=refunded_statuses))

        total_price = order.total_price or Decimal("0.00")
        balance_due = total_price - amount_paid
        if balance_due < Decimal("0.00"):
            balance_due = Decimal("0.00")

        def _format_decimal(value):
            return f"{(value or Decimal('0.00')).quantize(Decimal('0.01'))}"

        payments_payload = [
            {
                "id": payment.id,
                "amount": _format_decimal(payment.amount),
                "status": payment.status,
                "payment_method": payment.provider,
                "payment_type": payment.purpose,
                "reference_id": payment.reference,
                "transaction_id": payment.provider_transaction_id,
                "created_at": payment.created_at,
                "confirmed_at": payment.paid_at,
            }
            for payment in payments_qs
        ]

        summary = {
            "order_id": order.id,
            "currency": "USD",
            "order_total": _format_decimal(total_price),
            "amount_paid": _format_decimal(amount_paid),
            "pending_amount": _format_decimal(pending_amount),
            "refunded_amount": _format_decimal(refunded_amount),
            "balance_due": _format_decimal(balance_due),
            "is_fully_paid": balance_due == Decimal("0.00"),
            "last_payment_at": payments_qs.filter(status__in=completed_statuses).values_list("paid_at", flat=True).first(),
            "payments": payments_payload,
            "installments": [],
            "upcoming_installment": None,
        }

        return Response(summary, status=status.HTTP_200_OK)



    @decorators.action(detail=False, methods=["post"], url_path="create")
    def create_order(self, request):
        """
        Client creates a new order. Supports paper, design, diagram, and combo orders.

        Required (all families): topic, client_deadline, order_instructions
        Paper orders also require: paper_type_id, pages (or number_of_pages)
        Design orders require: service_code (presentation_design / infographic_design / poster_flyer_design)
                               slides (for presentations) or quantity
        Diagram orders require: service_code (flowchart_diagram / erd_diagram / uml_diagram / system_diagram)
                                quantity, diagram_complexity
        Combo orders send the paper fields plus design/diagram fields; service_family="combo_order"
        """
        user = request.user
        if user.role != 'client' and not user.is_superuser:
            return Response({"detail": "Only clients can create orders."}, status=status.HTTP_403_FORBIDDEN)

        data = request.data if isinstance(request.data, dict) else {}

        service_family = str(data.get("service_family") or "paper_order")
        service_code = str(data.get("service_code") or "academic_writing")

        # Accept pages or number_of_pages for paper-based orders
        pages_raw = data.get("pages") or data.get("number_of_pages")

        # Validate required fields based on service family
        required_check: dict = {
            "topic": data.get("topic"),
            "client_deadline": data.get("client_deadline"),
            "order_instructions": data.get("order_instructions"),
        }
        if service_family in ("paper_order", "combo_order"):
            required_check["paper_type_id"] = data.get("paper_type_id")
            required_check["pages"] = pages_raw
        if service_family == "design_order":
            required_check["quantity"] = data.get("slides") or data.get("quantity")
        if service_family == "diagram_order":
            required_check["quantity"] = data.get("quantity")

        missing = [k for k, v in required_check.items() if not v]
        if missing:
            return Response({"detail": f"Missing fields: {', '.join(missing)}"}, status=status.HTTP_400_BAD_REQUEST)

        # Determine unit_type from service family
        unit_type_map = {
            "paper_order": "page",
            "design_order": "slide" if "presentation" in service_code else "design_concept",
            "diagram_order": "diagram",
            "combo_order": "page",
        }
        unit_type = unit_type_map.get(service_family, "page")

        # Quantity: pages for paper/combo, slides/qty for design/diagram
        if service_family == "design_order":
            quantity = int(data.get("slides") or data.get("quantity") or 1)
        elif service_family == "diagram_order":
            quantity = int(data.get("quantity") or 1)
        else:
            quantity = int(pages_raw or 1)

        try:
            create_kwargs: dict = dict(
                website=getattr(user, 'website', None),
                client=user,
                topic=data["topic"],
                base_quantity=quantity,
                unit_type=unit_type,
                client_deadline=data["client_deadline"],
                order_instructions=data["order_instructions"],
                created_by_admin=False,
                payment_status='unpaid',
                is_urgent=bool(data.get("is_urgent", False)),
                service_family=service_family,
                service_code=service_code,
            )
            if service_family in ("paper_order", "combo_order") and data.get("paper_type_id"):
                create_kwargs["paper_type_id"] = int(data["paper_type_id"])

            order = Order.objects.create(**create_kwargs)

            # Optional FK fields
            for field in ("academic_level_id", "formatting_style_id", "subject_id",
                          "type_of_work_id", "english_type_id", "writer_level_id"):
                val = data.get(field)
                if val:
                    setattr(order, field, int(val))

            if data.get("pricing_snapshot_id"):
                snapshot_id = int(data["pricing_snapshot_id"])
                order.pricing_snapshot_id = snapshot_id
                try:
                    from order_pricing_core.models import PricingSnapshot
                    snap = PricingSnapshot.objects.get(pk=snapshot_id)
                    order.total_price = snap.final_price
                    if snap.currency:
                        order.currency = snap.currency
                except Exception:
                    pass

            # For combo orders the frontend passes the combined total directly
            if data.get("total_price_override"):
                from decimal import Decimal, InvalidOperation
                try:
                    order.total_price = Decimal(str(data["total_price_override"]))
                except InvalidOperation:
                    pass

            order.save()

            # Extra services many-to-many
            extra_services = data.get("extra_services") or []
            if isinstance(extra_services, list) and extra_services:
                order.extra_services.set(extra_services)

            return Response(
                {
                    "order": OrderSerializer(order, context={"request": request}).data,
                    "checkout_started": False,
                    "payment_intent": None,
                },
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @decorators.action(detail=False, methods=["post"], url_path="quote")
    def quote(self, request):
        """
        Calculate price quote for a prospective order without saving it.
        Required fields mirror create_order. Returns detailed breakdown.
        """
        data = request.data if isinstance(request.data, dict) else {}
        try:
            from django.utils import timezone
            from datetime import datetime

            # Parse deadline
            deadline = data.get("client_deadline")
            if deadline:
                if isinstance(deadline, str):
                    deadline = datetime.fromisoformat(deadline.replace('Z', '+00:00'))

            temp = Order(
                website=getattr(request.user, 'website', None),
                client=request.user if getattr(request.user, 'role', None) == 'client' else None,
                topic=data.get("topic", ""),
                paper_type_id=data.get("paper_type_id"),
                number_of_pages=int(data.get("number_of_pages", 1)),
                number_of_slides=int(data.get("number_of_slides", 0)),
                client_deadline=deadline,
                order_instructions=data.get("order_instructions", ""),
                created_at=timezone.now(),
            )
            # Optional fields
            if data.get("academic_level_id"):
                temp.academic_level_id = int(data["academic_level_id"])
            if data.get("formatting_style_id"):
                temp.formatting_style_id = int(data["formatting_style_id"])
            if data.get("subject_id"):
                temp.subject_id = int(data["subject_id"])
            if data.get("type_of_work_id"):
                temp.type_of_work_id = int(data["type_of_work_id"])
            if data.get("english_type_id"):
                temp.english_type_id = int(data["english_type_id"])
            if data.get("preferred_writer_id"):
                temp.preferred_writer_id = int(data["preferred_writer_id"])
            if data.get("writer_level_id"):
                from order_pricing_core.models import WriterLevelOptionConfig
                try:
                    temp.writer_level = WriterLevelOptionConfig.objects.get(id=int(data["writer_level_id"]))
                except WriterLevelOptionConfig.DoesNotExist:
                    pass

            # Handle extra services - calculate price manually since we can't save M2M on unsaved order
            extra_services_price = Decimal("0.00")
            if data.get("extra_services"):
                from order_pricing_core.models import AdditionalService
                service_ids = data["extra_services"]
                if isinstance(service_ids, list):
                    services = AdditionalService.objects.filter(id__in=service_ids, is_active=True)
                    extra_services_price = sum(Decimal(str(s.service_cost or 0)) for s in services)

            # Handle discount code
            if data.get("discount_code"):
                from discounts.models import Discount
                try:
                    discount = Discount.objects.get(
                        code=data["discount_code"],
                        website=temp.website,
                        is_active=True
                    )
                    temp.discount = discount
                except Discount.DoesNotExist:
                    pass

            # Use pricing calculator service
            from orders.services.pricing_calculator import PricingCalculatorService
            calculator = PricingCalculatorService(temp)
            breakdown = calculator.calculate_breakdown()
            total = calculator.calculate_total_price()

            # Get deadline multiplier for display
            deadline_multiplier = calculator.get_deadline_multiplier()

            # Calculate hours until deadline
            hours_until_deadline = None
            if deadline:
                hours_until_deadline = (deadline - timezone.now()).total_seconds() / 3600

            # Manually add extra services to total if they weren't included
            final_total = float(total)
            if extra_services_price > 0:
                final_total += float(extra_services_price)

            return Response({
                "total_price": final_total,
                "base_price": breakdown.get("base_price", 0),
                "slides_price": float(temp.number_of_slides * calculator.config.base_price_per_slide) if temp.number_of_slides > 0 else 0,
                "extra_services": float(extra_services_price),
                "writer_level": breakdown.get("writer_level", 0),
                "preferred_writer": breakdown.get("preferred_writer", 0),
                "discount_amount": breakdown.get("discount", 0),
                "deadline_multiplier": float(deadline_multiplier),
                "hours_until_deadline": hours_until_deadline,
                "breakdown": breakdown
            }, status=status.HTTP_200_OK)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @decorators.action(detail=False, methods=["get"], url_path="preferred-writers")
    def get_preferred_writers(self, request):
        """
        Get list of writers the client has worked with before (for preferred writer selection).
        """
        from orders.services.preferred_writer_service import PreferredWriterService
        from users.serializers import UserSerializer

        if request.user.role != 'client':
            return Response(
                {"detail": "This endpoint is only available for clients."},
                status=status.HTTP_403_FORBIDDEN
            )

        writer_ids = PreferredWriterService.get_last_five_writers_for_client(request.user)
        from django.contrib.auth import get_user_model
        User = get_user_model()
        writers = User.objects.filter(id__in=writer_ids).select_related('writer_profile')

        # Get preferred writer costs
        from order_pricing_core.models import PreferredWriterConfig
        website = getattr(request.user, 'website', None)
        writer_data = []
        for writer in writers:
            cost = Decimal("0.00")
            if website:
                try:
                    config = PreferredWriterConfig.objects.get(website=website)
                    if config.is_active:
                        cost = config.preferred_writer_cost
                except PreferredWriterConfig.DoesNotExist:
                    pass

            writer_data.append({
                'id': writer.id,
                'username': writer.username,
                'email': writer.email,
                'first_name': writer.first_name,
                'last_name': writer.last_name,
                'preferred_writer_cost': float(cost)
            })

        return Response(writer_data, status=status.HTTP_200_OK)

    @decorators.action(detail=True, methods=["post"], url_path="pay/wallet")
    def pay_with_wallet(self, request, pk=None):
        """
        Process order payment using client's wallet balance.

        Requires the requesting user to be the order's client or a staff member.
        """
        from wallets.services.client_wallet_service import ClientWalletService

        order = get_object_or_404(Order, pk=pk)
        user = request.user

        user_role = getattr(user, "role", None)
        if not (user.is_superuser or user_role in ["admin", "support"] or order.client_id == user.id):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

        if order.is_fully_paid:
            return Response({"detail": "Order already paid."}, status=status.HTTP_400_BAD_REQUEST)

        if not order.client:
            return Response(
                {"detail": "Order does not have an associated client."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        client = order.client
        order_total = order.total_price

        try:
            with transaction.atomic():
                wallet = ClientWalletService.get_wallet(website=order.website, client=client)

                if wallet.available_balance < order_total:
                    return Response(
                        {
                            "detail": "Insufficient wallet balance.",
                            "required": float(order_total),
                            "available": float(wallet.available_balance),
                            "shortfall": float(order_total - wallet.available_balance),
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                ClientWalletService.debit_for_order(
                    website=order.website,
                    client=client,
                    amount=order_total,
                    created_by=user,
                    reference=f"order-{order.id}",
                    reference_id=str(order.id),
                    description=f"Wallet payment for order #{order.id}",
                )

                # Mark paid by recording the amount and updating payment status.
                order.amount_paid = order.amount_paid + order_total
                order.payment_status = "paid"
                order.save(update_fields=["amount_paid", "payment_status", "updated_at"])

                wallet.refresh_from_db()

                try:
                    from notifications_system.services.notification_service import NotificationService
                    NotificationService.notify(
                        event_key="order_paid",
                        recipient=order.client,
                        website=order.website,
                        context={"order": order, "amount": order_total, "payment_method": "wallet"},
                        channels=["email", "in_app"],
                        is_critical=True,
                        priority="high",
                    )
                except Exception:
                    pass

                return Response(
                    {
                        "detail": "Order paid successfully using wallet.",
                        "payment": {
                            "amount": float(order_total),
                            "status": "succeeded",
                            "method": "wallet",
                        },
                        "wallet_balance": float(wallet.available_balance),
                    },
                    status=status.HTTP_200_OK,
                )

        except InsufficientWalletBalanceError as e:
            return Response(
                {"detail": "Insufficient wallet balance.", "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            return Response(
                {"detail": f"Payment validation error: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            import logging
            import traceback
            logger = logging.getLogger(__name__)
            logger.error(f"Error processing wallet payment for order {order.id}: {e}")
            logger.error(traceback.format_exc())
            return Response(
                {"detail": "An error occurred while processing the payment. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @decorators.action(detail=True, methods=["post"], url_path="add-pages-slides")
    def add_pages_slides(self, request, pk=None):
        """
        Allow clients to directly add pages or slides to their order.
        This creates a payment requirement that must be fulfilled.

        Expected payload:
        {
            "additional_pages": int (optional),
            "additional_slides": int (optional),
            "payment_method": "wallet" | "stripe" | "smart" (optional, defaults to redirect to payment)
        }
        """
        order = get_object_or_404(Order, pk=pk)
        user = request.user

        # Authorization check
        if not (user.is_superuser or user.role in ["admin", "support"] or order.client_id == user.id):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

        additional_pages = request.data.get("additional_pages", 0) or 0
        additional_slides = request.data.get("additional_slides", 0) or 0

        if additional_pages <= 0 and additional_slides <= 0:
            return Response(
                {"detail": "At least one of additional_pages or additional_slides must be greater than 0."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            with transaction.atomic():
                # Calculate the cost for additional pages/slides
                from orders.services.pricing_calculator import PricingCalculatorService
                calculator = PricingCalculatorService(order)

                # Get pricing config
                config = calculator.get_pricing_config_for_website(order.website.id)

                # Calculate additional cost
                pages_cost = Decimal(str(additional_pages)) * config.base_price_per_page if additional_pages > 0 else Decimal('0.00')
                slides_cost = Decimal(str(additional_slides)) * config.base_price_per_slide if additional_slides > 0 else Decimal('0.00')
                additional_cost = pages_cost + slides_cost

                # Apply discount if order has one
                if order.discount:
                    from discounts.services.discount_engine import DiscountEngine
                    discount_engine = DiscountEngine(
                        discount_codes=[order.discount.code],
                        user=order.client,
                        order=order,
                        website=order.website,
                        custom_cost_context={
                            "additional_pages": additional_pages,
                            "additional_slides": additional_slides,
                        },
                    )
                    discount_engine.apply_discounts()
                    additional_cost = discount_engine.discounted_total

                # Update order immediately (pages/slides added)
                order.number_of_pages += additional_pages
                order.number_of_slides += additional_slides

                # Recalculate total order price
                order.total_price = calculator.calculate_total_price()
                order.save(update_fields=["number_of_pages", "number_of_slides", "total_price", "updated_at"])

                # If payment method is provided and it's wallet, process immediately
                payment_method = request.data.get("payment_method")
                if payment_method == "wallet" and additional_cost > 0:
                    from wallets.models import Wallet
                    from wallets.services.client_wallet_service import ClientWalletService

                    wallet = ClientWalletService.get_wallet(
                        website=order.website,
                        client=order.client,
                    )
                    wallet = Wallet.objects.select_for_update().get(id=wallet.id)

                    if wallet.available_balance < additional_cost:
                        # Rollback order changes
                        order.number_of_pages -= additional_pages
                        order.number_of_slides -= additional_slides
                        order.total_price = calculator.calculate_total_price()
                        order.save(update_fields=["number_of_pages", "number_of_slides", "total_price", "updated_at"])

                        return Response(
                            {
                                "detail": "Insufficient wallet balance.",
                                "required": float(additional_cost),
                                "available": float(wallet.available_balance),
                                "shortfall": float(additional_cost - wallet.available_balance)
                            },
                            status=status.HTTP_400_BAD_REQUEST
                        )

                    ClientWalletService.debit_for_order(
                        website=order.website,
                        client=order.client,
                        amount=additional_cost,
                        created_by=request.user,
                        reference=f"order-{order.id}-pages",
                        reference_id=str(order.id),
                        description=f"Wallet payment for extra pages/slides on order #{order.id}",
                    )

                    return Response({
                        "detail": "Pages/slides added and paid successfully.",
                        "order": OrderSerializer(order, context={"request": request}).data,
                        "payment": {
                            "amount": float(additional_cost),
                            "status": "succeeded",
                            "method": "wallet",
                        },
                        "additional_pages": additional_pages,
                        "additional_slides": additional_slides,
                        "cost": float(additional_cost)
                    }, status=status.HTTP_200_OK)
                else:
                    # Return payment info for client to complete payment
                    return Response({
                        "detail": "Pages/slides added. Payment required.",
                        "order": OrderSerializer(order, context={"request": request}).data,
                        "requires_payment": True,
                        "amount": float(additional_cost),
                        "additional_pages": additional_pages,
                        "additional_slides": additional_slides,
                        "payment_url": f"/orders/{order.id}/pay"
                    }, status=status.HTTP_200_OK)

        except Exception as e:
            import logging
            import traceback
            logger = logging.getLogger(__name__)
            logger.error(f"Error adding pages/slides to order {order.id}: {e}")
            logger.error(traceback.format_exc())
            return Response(
                {"detail": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @decorators.action(detail=True, methods=["post"], url_path="add-extra-services")
    def add_extra_services(self, request, pk=None):
        """
        Allow clients to add additional services to their order.
        This creates a payment requirement that must be fulfilled.

        Expected payload:
        {
            "service_ids": [int, int, ...],
            "payment_method": "wallet" | "stripe" | "smart" (optional, defaults to redirect to payment)
        }
        """
        order = get_object_or_404(Order, pk=pk)
        user = request.user

        # Authorization check
        if not (user.is_superuser or user.role in ["admin", "support"] or order.client_id == user.id):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

        service_ids = request.data.get("service_ids", [])

        if not service_ids or not isinstance(service_ids, list):
            return Response(
                {"detail": "service_ids must be a non-empty list of service IDs."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            with transaction.atomic():
                from order_pricing_core.models import AdditionalService
                from orders.services.pricing_calculator import PricingCalculatorService

                # Get the services
                services = AdditionalService.objects.filter(
                    id__in=service_ids,
                    is_active=True,
                    website=order.website
                )

                if services.count() != len(service_ids):
                    return Response(
                        {"detail": "One or more services not found or inactive."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Check if services are already added
                existing_service_ids = set(order.extra_services.values_list('id', flat=True))
                new_service_ids = set(service_ids)
                already_added = existing_service_ids.intersection(new_service_ids)

                if already_added:
                    return Response(
                        {"detail": f"Services with IDs {list(already_added)} are already added to this order."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Calculate additional cost
                additional_cost = sum(Decimal(str(service.cost)) for service in services)

                # Apply discount if order has one
                if order.discount and additional_cost > 0:
                    from discounts.services.discount_engine import DiscountEngine
                    discount_engine = DiscountEngine(
                        discount_codes=[order.discount.code],
                        user=order.client,
                        order=order,
                        website=order.website,
                        custom_cost_context={
                            "extra_services": list(service_ids),
                        },
                    )
                    discount_engine.apply_discounts()
                    additional_cost = discount_engine.discounted_total

                # Add services to order
                order.extra_services.add(*services)

                # Recalculate total order price
                calculator = PricingCalculatorService(order)
                order.total_price = calculator.calculate_total_price()
                order.save(update_fields=["total_price", "updated_at"])

                # If payment method is provided and it's wallet, process immediately
                payment_method = request.data.get("payment_method")
                if payment_method == "wallet" and additional_cost > 0:
                    from wallets.models import Wallet
                    from wallets.services.client_wallet_service import ClientWalletService

                    wallet = ClientWalletService.get_wallet(
                        website=order.website,
                        client=order.client,
                    )
                    wallet = Wallet.objects.select_for_update().get(id=wallet.id)

                    if wallet.available_balance < additional_cost:
                        # Rollback service addition
                        order.extra_services.remove(*services)
                        order.total_price = calculator.calculate_total_price()
                        order.save(update_fields=["total_price", "updated_at"])

                        return Response(
                            {
                                "detail": "Insufficient wallet balance.",
                                "required": float(additional_cost),
                                "available": float(wallet.available_balance),
                                "shortfall": float(additional_cost - wallet.available_balance)
                            },
                            status=status.HTTP_400_BAD_REQUEST
                        )

                    ClientWalletService.debit_for_order(
                        website=order.website,
                        client=order.client,
                        amount=additional_cost,
                        created_by=request.user,
                        reference=f"order-{order.id}-services",
                        reference_id=str(order.id),
                        description=f"Wallet payment for extra services on order #{order.id}",
                    )

                    return Response({
                        "detail": "Services added and paid successfully.",
                        "order": OrderSerializer(order, context={"request": request}).data,
                        "payment": {
                            "amount": float(additional_cost),
                            "status": "succeeded",
                            "method": "wallet",
                        },
                        "services_added": [{"id": s.id, "name": s.service_name, "cost": float(s.cost)} for s in services],
                        "total_cost": float(additional_cost)
                    }, status=status.HTTP_200_OK)
                else:
                    # Return payment info for client to complete payment
                    return Response({
                        "detail": "Services added. Payment required.",
                        "order": OrderSerializer(order, context={"request": request}).data,
                        "requires_payment": True,
                        "amount": float(additional_cost),
                        "services_added": [{"id": s.id, "name": s.service_name, "cost": float(s.cost)} for s in services],
                        "payment_url": f"/orders/{order.id}/pay"
                    }, status=status.HTTP_200_OK)

        except Exception as e:
            import logging
            import traceback
            logger = logging.getLogger(__name__)
            logger.error(f"Error adding extra services to order {order.id}: {e}")
            logger.error(traceback.format_exc())
            return Response(
                {"detail": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # ---------- soft delete (clients: only UNPAID; staff: any) ----------

    def destroy(self, request, pk=None):
        """
        Soft delete an order.
        - Clients: only their own UNPAID orders.
        - Staff (admin/support/superadmin): any order.
        Returns 204 if a transition happened, 200 if it was already deleted.
        """
        order = get_object_or_404(self.get_queryset().model,
                                  pk=pk, website_id=self.website.id)
        # use the raw manager to bypass deleted filter when needed
        # but we already got it via model; refetch guarded by tenant:
        order = get_object_or_404(Order, pk=pk, website_id=self.website.id)

        reason = request.data.get("reason", "") if isinstance(
            request.data, dict
        ) else ""

        result = self._svc().soft_delete(user=request.user,
                                         order=order,
                                         reason=reason)
        code = status.HTTP_204_NO_CONTENT if result.was_deleted \
            else status.HTTP_200_OK
        return Response(status=code)

    # ---------- restore (client: own; staff: any) ----------

    @decorators.action(detail=True, methods=["post"], url_path="restore")
    def restore(self, request, pk=None):
        """
        Restore a soft-deleted order.
        - Clients: only their own.
        - Staff: any.
        Returns 200 on success.
        """
        # need to access even if currently deleted, so use all_objects
        order = get_object_or_404(Order.all_objects, pk=pk, website_id=self.website.id)
        self._svc().restore(user=request.user, order=order)
        return Response(status=status.HTTP_200_OK)

    # ---------- hard delete (irreversible; staff-only) ----------

    @decorators.action(detail=True, methods=["delete"], url_path="hard")
    def hard_delete(self, request, pk=None):
        """
        Irreversible delete (row removal).
        - Staff only: admin/support/superadmin (or superuser).
        Returns 204 if deleted, 200 if it was already gone.
        """
        if not self._is_staff_role(request.user):
            return Response({"detail": "Forbidden."},
                            status=status.HTTP_403_FORBIDDEN)

        result = self._svc().hard_delete_by_id(user=request.user,
                                               order_id=int(pk or 0))
        code = status.HTTP_204_NO_CONTENT if result.was_deleted \
            else status.HTTP_200_OK
        return Response(status=code)

    @decorators.action(detail=True, methods=["get", "post"], url_path="transition")
    def transition_status(self, request, pk=None):
        """
        GET: Get available transitions for an order.
        POST: Transition order to a new status.

        POST Body:
        {
            "target_status": "in_progress",
            "reason": "Optional reason for transition",
            "skip_payment_check": false,
            "metadata": {}
        }
        """
        order = get_object_or_404(Order, pk=pk)

        if request.method == "GET":
            # Return available transitions
            from orders.services.transition_helper import OrderTransitionHelper
            available_transitions = OrderTransitionHelper.get_available_transitions(order)

            return Response(
                {
                    "order_id": order.id,
                    "current_status": order.status,
                    "available_transitions": available_transitions,
                    "can_transition": {
                        status: OrderTransitionHelper.can_transition(order, status)
                        for status in available_transitions
                    }
                },
                status=status.HTTP_200_OK
            )

        # POST: Perform transition
        target_status = request.data.get("target_status")
        reason = request.data.get("reason", "")
        skip_payment_check = request.data.get("skip_payment_check", False)
        metadata = request.data.get("metadata", {})
        action = request.data.get("action", "status_transition")
        is_automatic = request.data.get("is_automatic", False)

        if not target_status:
            return Response(
                {"detail": "target_status is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if user has permission (admin/superadmin/support can skip checks)
        user_role = getattr(request.user, 'role', None)
        if user_role not in ['admin', 'superadmin', 'support']:
            skip_payment_check = False

        try:
            from orders.services.transition_helper import OrderTransitionHelper

            old_status = order.status
            updated_order = OrderTransitionHelper.transition_order(
                order=order,
                target_status=target_status,
                user=request.user,
                reason=reason,
                action=action,
                is_automatic=is_automatic,
                skip_payment_check=skip_payment_check,
                metadata=metadata
            )

            # Refresh order from DB to get latest state
            updated_order.refresh_from_db()

            return Response(
                {
                    "message": f"Order transitioned from '{old_status}' to '{target_status}'",
                    "old_status": old_status,
                    "new_status": updated_order.status,
                    "order": OrderSerializer(updated_order, context={"request": request}).data
                },
                status=status.HTTP_200_OK
            )
        except InvalidTransitionError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except ValidationError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"detail": f"Transition failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @decorators.action(detail=True, methods=["get"], url_path="available-transitions")
    def get_available_transitions(self, request, pk=None):
        """
        Get list of available status transitions for an order.
        """
        order = get_object_or_404(Order, pk=pk)

        from orders.services.transition_helper import OrderTransitionHelper
        available = OrderTransitionHelper.get_available_transitions(order)

        return Response(
            {
                "current_status": order.status,
                "available_transitions": available,
                "order_id": order.id
            },
            status=status.HTTP_200_OK
        )

    @decorators.action(detail=True, methods=["post"], url_path="auto-assign")
    def auto_assign(self, request, pk=None):
        """
        Automatically assign a writer to an order.

        Body (optional):
        {
            "min_rating": 4.0,
            "max_candidates": 10,
            "require_subject_match": true
        }
        """
        order = get_object_or_404(Order, pk=pk, website_id=self.website.id)

        # Check permissions (admin/support only)
        if not (request.user.is_staff or getattr(request.user, 'role', None) in ['admin', 'superadmin', 'support']):
            return Response(
                {"detail": "Only administrators can use auto-assignment."},
                status=status.HTTP_403_FORBIDDEN
            )

        min_rating = request.data.get('min_rating', 4.0)
        max_candidates = request.data.get('max_candidates', 10)

        try:
            from orders.services.auto_assignment_service import AutoAssignmentService

            service = AutoAssignmentService(order, actor=request.user)
            updated_order, writer, assignment_info = service.auto_assign(
                reason=f"Auto-assigned by {request.user.username}",
                require_acceptance=True,
                max_candidates=max_candidates,
                min_rating=min_rating,
            )

            return Response(
                {
                    "message": f"Order #{order.id} auto-assigned to {writer.username}",
                    "order": OrderSerializer(updated_order, context={"request": request}).data,
                    "writer": {
                        "id": writer.id,
                        "username": writer.username,
                        "email": writer.email,
                    },
                    "assignment_info": assignment_info,
                },
                status=status.HTTP_200_OK
            )
        except ValidationError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"detail": f"Auto-assignment failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @decorators.action(detail=False, methods=["post"], url_path="bulk-auto-assign")
    def bulk_auto_assign(self, request):
        """
        Automatically assign multiple available orders.

        Body (optional):
        {
            "max_assignments": 10,
            "min_rating": 4.0,
            "website_id": 1
        }
        """
        # Check permissions (admin/support only)
        if not (request.user.is_staff or getattr(request.user, 'role', None) in ['admin', 'superadmin', 'support']):
            return Response(
                {"detail": "Only administrators can use bulk auto-assignment."},
                status=status.HTTP_403_FORBIDDEN
            )

        max_assignments = request.data.get('max_assignments', 10)
        min_rating = request.data.get('min_rating', 4.0)
        website_id = request.data.get('website_id', self.website.id)

        try:
            from orders.services.auto_assignment_service import AutoAssignmentService
            from websites.models.websites import Website

            website = Website.objects.get(id=website_id) if website_id else self.website

            results = AutoAssignmentService.auto_assign_available_orders(
                website=website,
                max_assignments=max_assignments,
                min_rating=min_rating,
                actor=request.user,
            )

            return Response(
                {
                    "message": f"Bulk auto-assignment completed: {results['successful']} successful, {results['failed']} failed",
                    "results": results,
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"detail": f"Bulk auto-assignment failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @decorators.action(detail=False, methods=["post"], url_path="bulk-assign")
    def bulk_assign(self, request):
        """
        Bulk assign multiple orders to writers.

        Body:
        {
            "assignments": [
                {"order_id": 1, "writer_id": 5, "reason": "..."},
                {"order_id": 2, "writer_id": 6, "reason": "..."}
            ],
            "strategy": "balanced" // or "round_robin", "best_match"
        }
        """
        # Check permissions (admin/support only)
        if not (request.user.is_staff or getattr(request.user, 'role', None) in ['admin', 'superadmin', 'support']):
            return Response(
                {"detail": "Only administrators can use bulk assignment."},
                status=status.HTTP_403_FORBIDDEN
            )

        assignments = request.data.get('assignments', [])
        strategy = request.data.get('strategy', 'balanced')

        if not assignments:
            return Response(
                {"detail": "No assignments provided"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            from orders.services.bulk_assignment_service import BulkAssignmentService

            # If assignments is a list of order IDs, use automatic distribution
            if isinstance(assignments[0], int):
                # List of order IDs - use automatic distribution
                order_ids = assignments
                orders = Order.objects.filter(
                    id__in=order_ids,
                    website_id=self.website.id,
                )

                results = BulkAssignmentService.distribute_orders_automatically(
                    orders=list(orders),
                    actor=request.user,
                    strategy=strategy,
                )
            else:
                # List of assignment dicts - use manual assignment
                results = BulkAssignmentService.assign_orders_to_writers(
                    assignments=assignments,
                    actor=request.user,
                )

            return Response(
                {
                    "message": f"Bulk assignment completed: {results['successful']} successful, {results['failed']} failed",
                    "results": results,
                },
                status=status.HTTP_200_OK
            )
        except ValidationError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"detail": f"Bulk assignment failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @decorators.action(detail=True, methods=["get"], url_path="smart-match")
    def smart_match(self, request, pk=None):
        """
        Get smart matching recommendations for an order.

        Query params:
        - max_results: Maximum matches to return (default: 10)
        - min_rating: Minimum writer rating (default: 4.0)
        """
        # Get order - use get_queryset() to respect permissions and filtering
        order = get_object_or_404(self.get_queryset(), pk=pk)

        max_results = int(request.query_params.get('max_results', 10))
        min_rating = float(request.query_params.get('min_rating', 4.0))

        try:
            from orders.services.smart_matching_service import SmartMatchingService

            matches = SmartMatchingService.find_best_matches(
                order=order,
                max_results=max_results,
                min_rating=min_rating,
            )

            # Format response
            results = []
            for match in matches:
                explanation = SmartMatchingService.get_match_explanation(order, match['writer'])
                results.append({
                    'writer_id': match['writer_id'],
                    'writer_username': match['writer_username'],
                    'score': round(match['score'], 3),
                    'rating': match['rating'],
                    'active_orders': match['active_orders'],
                    'reasons': match['reasons'],
                    'explanation': explanation,
                })

            return Response(
                {
                    "order_id": order.id,
                    "matches": results,
                    "total_matches": len(results),
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Smart matching failed for order {pk}: {str(e)}", exc_info=True)
            return Response(
                {"detail": f"Smart matching failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
