from datetime import datetime, time
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.dateparse import parse_date, parse_datetime
from django.utils.functional import cached_property
from rest_framework import decorators, mixins, status, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.core.exceptions import ValidationError
from orders.models import Order
from orders.order_enums import OrderFlags, OrderStatus
from orders.permissions import IsOrderOwnerOrSupport
from orders.serializers import OrderSerializer
from order_payments_management.models import OrderPayment
from orders.exceptions import InvalidTransitionError
from orders.services.order_deletion_service import (
    ALLOWED_STAFF_ROLES,
    OrderDeletionService,
)


class LimitedPagination(PageNumberPagination):
    """Custom pagination class with safety limits to prevent performance issues."""
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 500  # Safety limit to prevent excessive data transfer
    
    def get_paginated_response(self, data):
        """Return paginated response with metadata."""
        from rest_framework.response import Response
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
    pagination_class = LimitedPagination  # Paginated with safety limits
    
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
        Update order fields. Only allows updating specific safe fields.
        Status changes should go through the action system.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # Define allowed fields that can be updated directly
        # These fields are updated directly on the model, bypassing serializer validation
        allowed_direct_fields = {
            'completion_notes',  # For revision notes and completion notes
        }
        
        # Fields that go through serializer validation
        allowed_serializer_fields = {
            'order_instructions',  # For updating instructions
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

        # Optimize queryset with select_related and prefetch_related to prevent N+1 queries
        # For list views, use minimal select_related to speed up queries significantly
        if self.action == 'list':
            # Minimal fields for list view - only what's needed for OrderListSerializer
            # This dramatically reduces data transfer and query time
            qs = Order.objects.all().select_related(
                'client',           # For client_username
                'website',          # For website filtering
                'assigned_writer',  # For writer_username
                'paper_type',       # For paper_type_name
                'academic_level',   # For academic_level_name
                'subject',          # For subject_name
            ).only(
                # Only fetch fields used in OrderListSerializer - reduces data transfer by ~70%
                'id', 'topic', 'status', 'is_paid', 'total_price', 'writer_compensation',
                'client_deadline', 'writer_deadline', 'created_at', 'updated_at',
                'number_of_pages', 'number_of_slides', 'number_of_refereces',
                'spacing', 'discount_code_used', 'is_special_order', 'is_follow_up',
                'is_urgent', 'flags',
                # Foreign key IDs (needed for select_related to work)
                'client_id', 'assigned_writer_id', 'preferred_writer_id',
                'paper_type_id', 'academic_level_id', 'formatting_style_id',
                'type_of_work_id', 'english_type_id', 'subject_id', 'website_id',
            )
        else:
            # Full select_related for detail views
            qs = Order.objects.all().select_related(
                'client',           # Used in serializer
                'website',          # Used in serializer
                'assigned_writer',  # Used in serializer (writer_username)
                'preferred_writer', # Used in serializer
                'paper_type',       # Used in serializer
                'academic_level',   # Used in serializer
                'formatting_style', # Used in serializer
                'type_of_work',     # Used in serializer
                'english_type',     # Used in serializer
                'subject',          # Used in serializer
                'previous_order',   # Used in serializer
                'discount',         # Used in serializer
            ).prefetch_related(
                'extra_services',   # ManyToMany field used in serializer
            )

        # Role-based scoping
        # Both superadmin and admin should see all orders (no website filtering)
        user_role = getattr(user, 'role', None)
        if user.is_superuser or user_role == 'superadmin':
            base_qs = qs
        elif user_role == 'client':
            base_qs = qs.filter(client=user)
        elif user_role == 'writer':
            # Writers see:
            # 1. Orders assigned to them (always visible, regardless of payment status)
            # 2. Paid orders that are available and not assigned to other writers
            # 3. Paid orders that are preferred for them (unless they declined)
            from writer_management.models.profile import WriterProfile
            from orders.models import PreferredWriterResponse
            
            # Get writer's website from their profile - use select_related to avoid N+1
            writer_website = None
            try:
                # Use get() instead of hasattr to ensure we get the profile
                writer_profile = WriterProfile.objects.select_related('website').get(user=user)
                writer_website = writer_profile.website
            except WriterProfile.DoesNotExist:
                pass
            except Exception as e:
                # Log error but continue with fallback
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Error getting writer profile for user {user.id}: {str(e)}")
            
            if writer_website:
                # Get orders where writer has declined (to exclude them)
                declined_order_ids = list(PreferredWriterResponse.objects.filter(
                    writer=user,
                    response='declined'
                ).values_list('order_id', flat=True))
                
                # Get orders that the writer has requested (allows viewing requested orders)
                from writer_management.models.requests import WriterOrderRequest
                requested_order_ids = list(WriterOrderRequest.objects.filter(
                    writer=writer_profile
                ).values_list('order_id', flat=True))
                
                # Filter by website for available orders
                # Writers see:
                # 1. Orders assigned to them (always visible)
                # 2. Orders they have requested (allows viewing requested orders)
                # 3. Available paid orders that are:
                #    - Not assigned to anyone
                #    - In common pool (preferred_writer is None) OR preferred for this writer
                #    - Not declined by this writer
                base_qs = qs.filter(
                    models.Q(assigned_writer=user) |  # Orders assigned to them (always visible)
                    models.Q(id__in=requested_order_ids) |  # Orders they have requested
                    models.Q(
                        # Available paid orders not assigned to anyone
                        status=OrderStatus.AVAILABLE.value,
                        assigned_writer__isnull=True,
                        is_paid=True,  # Only paid orders
                        website=writer_website,
                    ) & (
                        # Either in common pool or preferred for this writer
                        models.Q(preferred_writer__isnull=True) | models.Q(preferred_writer=user)
                    )
                )
                
                # Only exclude declined orders if there are any
                if declined_order_ids:
                    base_qs = base_qs.exclude(id__in=declined_order_ids)
            else:
                # Fallback: only show assigned orders if no website
                base_qs = qs.filter(assigned_writer=user)
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
            except (Decimal.InvalidOperation, ValueError):
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

        paid = parse_bool(params.get('is_paid'))
        if paid is not None:
            base_qs = base_qs.filter(is_paid=paid)
        
        # Filter by special order flag
        is_special_order = parse_bool(params.get('is_special_order'))
        if is_special_order is not None:
            base_qs = base_qs.filter(is_special_order=is_special_order)

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
                    assigned_writer__isnull=True,
                    status__in=[
                        OrderStatus.AVAILABLE.value,
                        OrderStatus.PENDING_WRITER_ASSIGNMENT.value,
                        OrderStatus.PENDING_PREFERRED.value,
                    ]
                )
            elif needs_attention == 'unpaid':
                base_qs = base_qs.filter(
                    is_paid=False,
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
            from orders.models import OrderTransitionLog
            
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
                | Q(assigned_writer__username__icontains=search_term)
                | Q(assigned_writer__email__icontains=search_term)
                | Q(external_contact_name__icontains=search_term)
                | Q(external_contact_email__icontains=search_term)
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
            'writer_id': 'assigned_writer_id',
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
                Q(assigned_writer__username__icontains=writer_query)
                | Q(assigned_writer__email__icontains=writer_query)
                | Q(preferred_writer__username__icontains=writer_query)
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
        
        return base_qs
    
    def list(self, request, *args, **kwargs):
        """
        Override list to ensure queryset is not filtered by object permissions.
        DRF doesn't filter list results by object permissions by default,
        but we want to make sure our queryset filtering works correctly.
        Also includes phone reminder info for clients.
        """
        try:
            queryset = self.filter_queryset(self.get_queryset())
            
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                response = self.get_paginated_response(serializer.data)
            else:
                serializer = self.get_serializer(queryset, many=True)
                response = Response(serializer.data)
            
            # Add phone reminder info for clients
            if request.user.role in ['client', 'customer']:
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
        """
        Override list to ensure queryset is not filtered by object permissions.
        DRF doesn't filter list results by object permissions by default,
        but we want to make sure our queryset filtering works correctly.
        """
        try:
            queryset = self.filter_queryset(self.get_queryset())
            
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
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

    @decorators.action(detail=True, methods=["get"], url_path="payment-summary")
    def payment_summary(self, request, pk=None):
        """
        Provide payment and installment summary for the order owner or staff.
        """
        order = self.get_object()
        payments_qs = OrderPayment.objects.filter(order=order).order_by("-created_at")

        def _sum_amount(queryset):
            total = queryset.aggregate(total=models.Sum("amount")).get("total")
            return total or Decimal("0.00")

        completed_statuses = ["completed", "succeeded"]
        pending_statuses = ["pending", "processing", "under_review", "unpaid"]
        refunded_statuses = ["refunded", "partially_refunded", "fully_refunded"]

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
                "payment_method": payment.payment_method or "manual",
                "payment_type": payment.payment_type,
                "reference_id": payment.reference_id,
                "transaction_id": payment.transaction_id,
                "created_at": payment.created_at,
                "confirmed_at": payment.confirmed_at,
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
            "last_payment_at": payments_qs.filter(status__in=completed_statuses).values_list("confirmed_at", flat=True).first(),
            "payments": payments_payload,
            "installments": [],
            "upcoming_installment": None,
        }

        return Response(summary, status=status.HTTP_200_OK)



    @decorators.action(detail=False, methods=["post"], url_path="create")
    def create_order(self, request):
        """
        Client creates a new order. Minimal required fields:
        - topic (str)
        - paper_type_id (int)
        - number_of_pages (int >=1)
        - client_deadline (datetime ISO)
        - order_instructions (str)
        Optional:
        - academic_level_id, formatting_style_id, subject_id, extra_services (list[int])
        """
        user = request.user
        if user.role != 'client' and not user.is_superuser:
            return Response({"detail": "Only clients can create orders."}, status=status.HTTP_403_FORBIDDEN)

        data = request.data if isinstance(request.data, dict) else {}

        required = ["topic", "paper_type_id", "number_of_pages", "client_deadline", "order_instructions"]
        missing = [f for f in required if not data.get(f)]
        if missing:
            return Response({"detail": f"Missing fields: {', '.join(missing)}"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            order = Order.objects.create(
                website=getattr(user, 'website', None),
                client=user,
                topic=data["topic"],
                paper_type_id=int(data["paper_type_id"]),
                number_of_pages=int(data["number_of_pages"]),
                client_deadline=data["client_deadline"],
                order_instructions=data["order_instructions"],
                created_by_admin=False,
                is_paid=False,
            )

            # Optional fields
            if data.get("academic_level_id"):
                order.academic_level_id = int(data["academic_level_id"])
            if data.get("formatting_style_id"):
                order.formatting_style_id = int(data["formatting_style_id"])
            if data.get("subject_id"):
                order.subject_id = int(data["subject_id"])
            order.save()

            # Extra services many-to-many
            extra_services = data.get("extra_services") or []
            if isinstance(extra_services, list) and extra_services:
                order.extra_services.set(extra_services)

            return Response(OrderSerializer(order, context={"request": request}).data, status=status.HTTP_201_CREATED)
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
                from pricing_configs.models import WriterLevelOptionConfig
                try:
                    temp.writer_level = WriterLevelOptionConfig.objects.get(id=int(data["writer_level_id"]))
                except WriterLevelOptionConfig.DoesNotExist:
                    pass
            
            # Handle extra services - calculate price manually since we can't save M2M on unsaved order
            extra_services_price = Decimal("0.00")
            if data.get("extra_services"):
                from pricing_configs.models import AdditionalService
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
        from pricing_configs.models import PreferredWriterConfig
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
        
        This endpoint:
        1. Calculates the order total (including discounts)
        2. Creates an OrderPayment record
        3. Deducts the amount from the client's wallet
        4. Marks the order as paid
        
        Requires client to own the order or staff privileges.
        """
        from django.db import transaction
        from order_payments_management.services.payment_service import OrderPaymentService
        from orders.services.pricing_calculator import PricingCalculatorService
        from wallet.models import Wallet
        from wallet.exceptions import InsufficientWalletBalance
        
        order = get_object_or_404(Order, pk=pk)
        user = request.user
        
        # Authorization check
        if not (user.is_superuser or user.role in ["admin", "support"] or order.client_id == user.id):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

        # Check if order is already paid
        if order.is_paid:
            return Response(
                {"detail": "Order already paid."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if order has a client
        if not order.client:
            return Response(
                {"detail": "Order does not have an associated client."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get the client making the payment (use order.client or request.user if staff)
        client = order.client
        if user.role in ["admin", "support", "superadmin"]:
            # Staff can pay on behalf of client, but use order's client for wallet
            client = order.client
        
        try:
            with transaction.atomic():
                # Calculate order total using pricing calculator
                calculator = PricingCalculatorService(order)
                order_total = calculator.calculate_total_price()
                
                # Ensure order.total_price is up to date
                if order.total_price != order_total:
                    order.total_price = order_total
                    order.save(update_fields=["total_price"])
                
                # Ensure wallet exists (website-specific) and lock it for atomic operation
                from wallet.services.wallet_transaction_service import WalletTransactionService
                wallet = WalletTransactionService.get_wallet(client, order.website)
                wallet = Wallet.objects.select_for_update().get(id=wallet.id)
                
                # Create payment record first to get the actual discounted amount
                payment = OrderPaymentService.create_payment(
                    order=order,
                    client=client,
                    payment_method='wallet',
                    amount=order_total,
                    discount_code=order.discount.code if order.discount else None,
                    original_amount=order_total
                )
                
                # Check wallet balance against the actual discounted amount
                payment_amount = payment.discounted_amount or payment.amount
                if wallet.balance < payment_amount:
                    return Response(
                        {
                            "detail": "Insufficient wallet balance.",
                            "required": float(payment_amount),
                            "available": float(wallet.balance),
                            "shortfall": float(payment_amount - wallet.balance)
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Process wallet payment (deducts from wallet and marks payment as completed)
                payment = OrderPaymentService.process_wallet_payment(payment)
                
                # Mark order as paid
                order.is_paid = True
                order.save(update_fields=["is_paid", "updated_at"])
                
                # Send payment notification
                try:
                    from notifications_system.services.notification_helper import NotificationHelper
                    NotificationHelper.notify_order_paid(
                        order=order,
                        amount=payment.discounted_amount or payment.amount,
                        payment_method='wallet'
                    )
                except Exception as e:
                    # Log error but don't fail the payment
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Failed to send payment notification for order {order.id}: {e}")
                
                return Response({
                    "detail": "Order paid successfully using wallet.",
                    "order": OrderSerializer(order, context={"request": request}).data,
                    "payment": {
                        "id": payment.id,
                        "amount": float(payment.discounted_amount or payment.amount),
                        "status": payment.status,
                        "method": payment.payment_method
                    },
                    "wallet_balance": float(wallet.balance)
                }, status=status.HTTP_200_OK)
                
        except ValueError as e:
            # Handle insufficient funds or other validation errors
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except InsufficientWalletBalance as e:
            return Response(
                {
                    "detail": "Insufficient wallet balance.",
                    "message": str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )
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
                                               order_id=int(pk))
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
            from websites.models import Website
            
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
            "strategy": "balanced"  // or "round_robin", "best_match"
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