"""
Service for managing editor task assignments.
Supports auto-assignment, manual assignment, and self-claiming.
"""

from django.db import transaction
from django.db.models import Count, F
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from typing import Optional

from editor_management.models import EditorProfile, EditorTaskAssignment
from orders.models import Order
from orders.order_enums import OrderStatus
from notifications_system.services.notification_helper import NotificationHelper
from audit_logging.services.audit_log_service import AuditLogService


class EditorAssignmentService:
    """
    Handles assignment of orders to editors for review/editing.
    """
    
    @staticmethod
    @transaction.atomic
    def auto_assign_order(order: Order, website=None) -> Optional[EditorTaskAssignment]:
        """
        Automatically assign an order to an available editor.
        
        Assignment logic:
        1. Find active editors who can take more tasks
        2. Prioritize editors with matching expertise (subject, paper type)
        3. Prioritize editors with fewer active tasks
        4. Create EditorTaskAssignment with assignment_type='auto'
        
        Args:
            order: The order to assign
            website: Optional website to filter editors
            
        Returns:
            EditorTaskAssignment if assignment successful, None otherwise
        """
        if order.status != OrderStatus.UNDER_EDITING.value:
            raise ValidationError(
                f"Order {order.id} must be in 'under_editing' status for editor assignment."
            )
        
        # Check if already assigned
        if hasattr(order, 'editor_assignment') and order.editor_assignment.assigned_editor:
            return order.editor_assignment
        
        # Get website from order if not provided
        website = website or order.website
        
        # Find available editors
        from django.db.models import Q
        editors = EditorProfile.objects.filter(
            website=website,
            is_active=True
        ).annotate(
            active_tasks_count=Count(
                'assigned_tasks',
                filter=Q(
                    assigned_tasks__review_status__in=['pending', 'in_review']
                )
            )
        ).filter(
            active_tasks_count__lt=F('max_concurrent_tasks')
        ).order_by('active_tasks_count', 'orders_reviewed')
        
        if not editors.exists():
            # No available editors, create unclaimed assignment
            assignment, created = EditorTaskAssignment.objects.get_or_create(
                order=order,
                defaults={
                    'assignment_type': 'auto',
                    'review_status': 'unclaimed',
                    'assigned_at': now(),
                }
            )
            return assignment
        
        # Try to find editor with matching expertise
        best_editor = None
        if order.subject:
            matching_editors = editors.filter(
                expertise_subjects=order.subject
            ).first()
            if matching_editors:
                best_editor = matching_editors
        
        if not best_editor and order.paper_type:
            matching_editors = editors.filter(
                expertise_paper_types=order.paper_type
            ).first()
            if matching_editors:
                best_editor = matching_editors
        
        # Fallback to any available editor
        if not best_editor:
            best_editor = editors.first()
        
        # Create assignment
        assignment, created = EditorTaskAssignment.objects.get_or_create(
            order=order,
            defaults={
                'assigned_editor': best_editor,
                'assignment_type': 'auto',
                'assigned_at': now(),
                'review_status': 'pending',
            }
        )
        
        if created or not assignment.assigned_editor:
            assignment.assigned_editor = best_editor
            assignment.assignment_type = 'auto'
            assignment.review_status = 'pending'
            assignment.save()
        
        # Log action
        AuditLogService.log_auto(
            actor=None,  # System action
            action="Editor task auto-assigned",
            target=order,
            changes={
                "assigned_editor": best_editor.user.username,
                "assignment_type": "auto",
            },
        )
        
        # Send notification
        NotificationHelper.send_notification(
            event_key="editor.task_assigned",
            user=best_editor.user,
            context={
                "order_id": order.id,
                "order_topic": order.topic,
                "assignment_type": "auto",
            },
        )
        
        return assignment
    
    @staticmethod
    @transaction.atomic
    def manually_assign_order(
        order: Order,
        editor: EditorProfile,
        assigned_by: 'User',
        notes: Optional[str] = None
    ) -> EditorTaskAssignment:
        """
        Manually assign an order to a specific editor (by admin/superadmin).
        
        Args:
            order: The order to assign
            editor: The editor to assign to
            assigned_by: User making the assignment (admin/superadmin)
            notes: Optional notes about the assignment
            
        Returns:
            EditorTaskAssignment
        """
        if order.status != OrderStatus.UNDER_EDITING.value:
            raise ValidationError(
                f"Order {order.id} must be in 'under_editing' status for editor assignment."
            )
        
        if not editor.can_take_more_tasks():
            raise ValidationError(
                f"Editor {editor.name} has reached maximum concurrent tasks ({editor.max_concurrent_tasks})."
            )
        
        # Check if already assigned
        assignment, created = EditorTaskAssignment.objects.get_or_create(
            order=order,
            defaults={
                'assigned_editor': editor,
                'assignment_type': 'manual',
                'assigned_by': assigned_by,
                'assigned_at': now(),
                'review_status': 'pending',
                'notes': notes or '',
            }
        )
        
        if not created:
            # Reassign to new editor
            assignment.assigned_editor = editor
            assignment.assignment_type = 'manual'
            assignment.assigned_by = assigned_by
            assignment.assigned_at = now()
            assignment.review_status = 'pending'
            if notes:
                assignment.notes = notes
            assignment.save()
        
        # Log action
        AuditLogService.log_auto(
            actor=assigned_by,
            action="Editor task manually assigned",
            target=order,
            changes={
                "assigned_editor": editor.user.username,
                "assigned_by": assigned_by.username,
                "assignment_type": "manual",
            },
        )
        
        # Send notification
        NotificationHelper.send_notification(
            event_key="editor.task_assigned",
            user=editor.user,
            context={
                "order_id": order.id,
                "order_topic": order.topic,
                "assignment_type": "manual",
                "assigned_by": assigned_by.username,
            },
        )
        
        return assignment
    
    @staticmethod
    @transaction.atomic
    def claim_order(
        order: Order,
        editor: EditorProfile
    ) -> EditorTaskAssignment:
        """
        Allow an editor to claim an unassigned or unclaimed order.
        
        Args:
            order: The order to claim
            editor: The editor claiming the order
            
        Returns:
            EditorTaskAssignment
        """
        if order.status != OrderStatus.UNDER_EDITING.value:
            raise ValidationError(
                f"Order {order.id} must be in 'under_editing' status to be claimed."
            )
        
        if not editor.can_self_assign:
            raise ValidationError(
                f"Editor {editor.name} is not allowed to self-assign tasks."
            )
        
        if not editor.can_take_more_tasks():
            raise ValidationError(
                f"Editor {editor.name} has reached maximum concurrent tasks ({editor.max_concurrent_tasks})."
            )
        
        # Get or create assignment
        assignment, created = EditorTaskAssignment.objects.get_or_create(
            order=order,
            defaults={
                'assigned_editor': editor,
                'assignment_type': 'claimed',
                'assigned_by': editor.user,
                'assigned_at': now(),
                'review_status': 'pending',
            }
        )
        
        if not created:
            # Already exists - check if can be claimed
            if assignment.assigned_editor and assignment.assigned_editor != editor:
                raise ValidationError(
                    f"Order {order.id} is already assigned to {assignment.assigned_editor.name}."
                )
            
            if assignment.review_status not in ['pending', 'unclaimed']:
                raise ValidationError(
                    f"Order {order.id} cannot be claimed (current status: {assignment.review_status})."
                )
            
            # Claim it
            assignment.assigned_editor = editor
            assignment.assignment_type = 'claimed'
            assignment.assigned_by = editor.user
            assignment.review_status = 'pending'
            assignment.save()
        
        # Log action
        from editor_management.models import EditorActionLog
        EditorActionLog.objects.create(
            editor=editor,
            action_type="claimed_task",
            action=f"Claimed order {order.id}",
            related_order=order,
            related_task=assignment,
        )
        
        AuditLogService.log_auto(
            actor=editor.user,
            action="Editor claimed task",
            target=order,
            changes={
                "assigned_editor": editor.user.username,
                "assignment_type": "claimed",
            },
        )
        
        return assignment
    
    @staticmethod
    @transaction.atomic
    def unclaim_order(
        assignment: EditorTaskAssignment,
        editor: EditorProfile
    ) -> EditorTaskAssignment:
        """
        Allow an editor to unclaim an order (make it available again).
        
        Args:
            assignment: The task assignment to unclaim
            editor: The editor unclaiming the order
            
        Returns:
            Updated EditorTaskAssignment
        """
        if assignment.assigned_editor != editor:
            raise ValidationError("Only the assigned editor can unclaim this task.")
        
        if assignment.review_status == 'completed':
            raise ValidationError("Cannot unclaim a completed task.")
        
        assignment.assigned_editor = None
        assignment.review_status = 'unclaimed'
        assignment.notes = (assignment.notes or '') + f"\n[Unclaimed by {editor.name} at {now()}]"
        assignment.save()
        
        # Log action
        from editor_management.models import EditorActionLog
        EditorActionLog.objects.create(
            editor=editor,
            action_type="unclaimed_task",
            action=f"Unclaimed order {assignment.order.id}",
            related_order=assignment.order,
            related_task=assignment,
        )
        
        return assignment

