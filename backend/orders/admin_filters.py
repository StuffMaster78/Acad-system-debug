"""
Custom admin filters for order status and transition states.
"""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from orders.order_enums import OrderStatus


class StatusGroupFilter(admin.SimpleListFilter):
    """
    Filter orders by status groups (Active, Completed, Cancelled, etc.)
    """
    title = _('Status Group')
    parameter_name = 'status_group'

    def lookups(self, request, model_admin):
        return (
            ('initial', _('Initial States (Created, Pending, Unpaid)')),
            ('payment', _('Payment States (Paid, Available)')),
            ('assignment', _('Assignment States (Pending Assignment, Available)')),
            ('active', _('Active Work (In Progress, On Hold, Reassigned)')),
            ('submission', _('Submission & Review (Submitted, Reviewed, Rated)')),
            ('revision', _('Revision States (Revision Requested, On Revision, Revised)')),
            ('editing', _('Editing States (Under Editing)')),
            ('completed', _('Completed States (Approved, Completed, Closed)')),
            ('disputed', _('Disputed')),
            ('cancelled', _('Cancelled States (Cancelled, Refunded)')),
            ('archived', _('Archived')),
            ('final', _('Final States (Closed, Archived, Deleted)')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'initial':
            return queryset.filter(status__in=[
                OrderStatus.CREATED.value,
                OrderStatus.PENDING.value,
                OrderStatus.UNPAID.value,
            ])
        elif self.value() == 'payment':
            return queryset.filter(status__in=[
                OrderStatus.PAID.value,
                OrderStatus.AVAILABLE.value,
            ])
        elif self.value() == 'assignment':
            return queryset.filter(status__in=[
                OrderStatus.PENDING_WRITER_ASSIGNMENT.value,
                OrderStatus.PENDING_PREFERRED.value,
                OrderStatus.AVAILABLE.value,
            ])
        elif self.value() == 'active':
            return queryset.filter(status__in=[
                OrderStatus.IN_PROGRESS.value,
                OrderStatus.ON_HOLD.value,
                OrderStatus.REASSIGNED.value,
            ])
        elif self.value() == 'submission':
            return queryset.filter(status__in=[
                OrderStatus.SUBMITTED.value,
                OrderStatus.REVIEWED.value,
                OrderStatus.RATED.value,
            ])
        elif self.value() == 'revision':
            return queryset.filter(status__in=[
                OrderStatus.REVISION_REQUESTED.value,
                OrderStatus.ON_REVISION.value,
                OrderStatus.REVISION_IN_PROGRESS.value,
                OrderStatus.REVISED.value,
            ])
        elif self.value() == 'editing':
            return queryset.filter(status__in=[
                OrderStatus.UNDER_EDITING.value,
            ])
        elif self.value() == 'completed':
            return queryset.filter(status__in=[
                OrderStatus.APPROVED.value,
                OrderStatus.COMPLETED.value,
                OrderStatus.CLOSED.value,
            ])
        elif self.value() == 'disputed':
            return queryset.filter(status__in=[
                OrderStatus.DISPUTED.value,
            ])
        elif self.value() == 'cancelled':
            return queryset.filter(status__in=[
                OrderStatus.CANCELLED.value,
                OrderStatus.REFUNDED.value,
            ])
        elif self.value() == 'archived':
            return queryset.filter(status__in=[
                OrderStatus.ARCHIVED.value,
            ])
        elif self.value() == 'final':
            final_statuses = [OrderStatus.CLOSED.value, OrderStatus.ARCHIVED.value]
            if hasattr(OrderStatus, 'DELETED'):
                final_statuses.append(OrderStatus.DELETED.value)
            return queryset.filter(status__in=final_statuses)
        return queryset


class CanTransitionToFilter(admin.SimpleListFilter):
    """
    Filter orders that can transition to a specific status.
    """
    title = _('Can Transition To')
    parameter_name = 'can_transition_to'

    def lookups(self, request, model_admin):
        # Common target statuses for filtering
        return (
            ('cancelled', _('Can Cancel')),
            ('completed', _('Can Complete')),
            ('approved', _('Can Approve')),
            ('in_progress', _('Can Start (In Progress)')),
            ('submitted', _('Can Submit')),
            ('revision_requested', _('Can Request Revision')),
            ('on_hold', _('Can Put On Hold')),
            ('reassigned', _('Can Reassign')),
            ('closed', _('Can Close')),
            ('archived', _('Can Archive')),
        )

    def queryset(self, request, queryset):
        from orders.services.status_transition_service import VALID_TRANSITIONS
        
        if not self.value():
            return queryset
        
        target_status = self.value()
        
        # Find all statuses that can transition to target_status
        can_transition_statuses = []
        for from_status, allowed_transitions in VALID_TRANSITIONS.items():
            if target_status in allowed_transitions:
                can_transition_statuses.append(from_status)
        
        if can_transition_statuses:
            return queryset.filter(status__in=can_transition_statuses)
        return queryset.none()


class RecentlyTransitionedFilter(admin.SimpleListFilter):
    """
    Filter orders that have recently transitioned (in last X hours).
    """
    title = _('Recently Transitioned')
    parameter_name = 'recently_transitioned'

    def lookups(self, request, model_admin):
        return (
            ('1h', _('Last Hour')),
            ('6h', _('Last 6 Hours')),
            ('24h', _('Last 24 Hours')),
            ('7d', _('Last 7 Days')),
        )

    def queryset(self, request, queryset):
        from django.utils import timezone
        from datetime import timedelta
        from orders.models import OrderTransitionLog
        
        if not self.value():
            return queryset
        
        # Parse time period
        period_map = {
            '1h': timedelta(hours=1),
            '6h': timedelta(hours=6),
            '24h': timedelta(hours=24),
            '7d': timedelta(days=7),
        }
        
        cutoff = timezone.now() - period_map.get(self.value(), timedelta(hours=24))
        
        # Get order IDs that have recent transitions
        recent_order_ids = OrderTransitionLog.objects.filter(
            timestamp__gte=cutoff
        ).values_list('order_id', flat=True).distinct()
        
        return queryset.filter(id__in=recent_order_ids)


class NeedsAttentionFilter(admin.SimpleListFilter):
    """
    Filter orders that need attention (overdue, stuck, etc.)
    """
    title = _('Needs Attention')
    parameter_name = 'needs_attention'

    def lookups(self, request, model_admin):
        return (
            ('overdue', _('Overdue')),
            ('stuck', _('Stuck (No Activity)')),
            ('unassigned', _('Unassigned (Needs Writer)')),
            ('unpaid', _('Unpaid (Needs Payment)')),
            ('on_hold', _('On Hold')),
            ('disputed', _('Disputed')),
        )

    def queryset(self, request, queryset):
        from django.utils import timezone
        from datetime import timedelta
        
        if self.value() == 'overdue':
            now = timezone.now()
            return queryset.filter(
                client_deadline__lt=now,
                status__in=[
                    OrderStatus.IN_PROGRESS.value,
                    OrderStatus.ON_HOLD.value,
                    OrderStatus.SUBMITTED.value,
                    OrderStatus.PENDING.value,
                    OrderStatus.AVAILABLE.value,
                ]
            )
        elif self.value() == 'stuck':
            # Orders with no activity in last 7 days and in active states
            cutoff = timezone.now() - timedelta(days=7)
            return queryset.filter(
                updated_at__lt=cutoff,
                status__in=[
                    OrderStatus.IN_PROGRESS.value,
                    OrderStatus.ON_HOLD.value,
                    OrderStatus.AVAILABLE.value,
                    OrderStatus.PENDING_WRITER_ASSIGNMENT.value,
                ]
            )
        elif self.value() == 'unassigned':
            return queryset.filter(
                assigned_writer__isnull=True,
                status__in=[
                    OrderStatus.AVAILABLE.value,
                    OrderStatus.PENDING_WRITER_ASSIGNMENT.value,
                    OrderStatus.PENDING_PREFERRED.value,
                ]
            )
        elif self.value() == 'unpaid':
            return queryset.filter(
                is_paid=False,
                status__in=[
                    OrderStatus.UNPAID.value,
                    OrderStatus.PENDING.value,
                ]
            )
        elif self.value() == 'on_hold':
            return queryset.filter(status=OrderStatus.ON_HOLD.value)
        elif self.value() == 'disputed':
            return queryset.filter(status=OrderStatus.DISPUTED.value)
        
        return queryset


class TransitionCountFilter(admin.SimpleListFilter):
    """
    Filter orders by number of status transitions.
    """
    title = _('Transition Count')
    parameter_name = 'transition_count'

    def lookups(self, request, model_admin):
        return (
            ('none', _('No Transitions')),
            ('few', _('Few (1-3)')),
            ('many', _('Many (4-10)')),
            ('excessive', _('Excessive (10+)')),
        )

    def queryset(self, request, queryset):
        from orders.models import OrderTransitionLog
        from django.db.models import Count
        
        # Annotate queryset with transition count
        queryset = queryset.annotate(
            transition_count=Count('order_transition_logs')
        )
        
        if self.value() == 'none':
            return queryset.filter(transition_count=0)
        elif self.value() == 'few':
            return queryset.filter(transition_count__gte=1, transition_count__lte=3)
        elif self.value() == 'many':
            return queryset.filter(transition_count__gte=4, transition_count__lte=10)
        elif self.value() == 'excessive':
            return queryset.filter(transition_count__gt=10)
        
        return queryset

