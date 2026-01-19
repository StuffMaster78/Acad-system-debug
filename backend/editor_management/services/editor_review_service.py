"""
Service for editors to submit reviews and complete editing tasks.
"""

from django.db import transaction
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from typing import Optional, Dict, Any
from decimal import Decimal

from editor_management.models import (
    EditorProfile,
    EditorTaskAssignment,
    EditorReviewSubmission,
    EditorActionLog
)
from orders.models import Order
from orders.order_enums import OrderStatus
from orders.services.transition_helper import OrderTransitionHelper
from notifications_system.services.notification_helper import NotificationHelper
from audit_logging.services.audit_log_service import AuditLogService


class EditorReviewService:
    """
    Handles editor review submission and task completion.
    """
    
    @staticmethod
    @transaction.atomic
    def start_review(
        task_assignment: EditorTaskAssignment,
        editor: EditorProfile
    ) -> EditorTaskAssignment:
        """
        Start reviewing an assigned task.
        
        Args:
            task_assignment: The task assignment to start
            editor: The editor starting the review
            
        Returns:
            Updated EditorTaskAssignment
        """
        if task_assignment.assigned_editor != editor:
            raise ValidationError(
                "Only the assigned editor can start reviewing this task."
            )
        
        task_assignment.start_review()
        
        # Log action
        EditorActionLog.objects.create(
            editor=editor,
            action_type="started_review",
            action=f"Started reviewing order {task_assignment.order.id}",
            related_order=task_assignment.order,
            related_task=task_assignment,
        )
        
        AuditLogService.log_auto(
            actor=editor.user,
            action="Editor started review",
            target=task_assignment.order,
            changes={"review_status": "in_review"},
        )
        
        return task_assignment
    
    @staticmethod
    @transaction.atomic
    def submit_review(
        task_assignment: EditorTaskAssignment,
        editor: EditorProfile,
        quality_score: Optional[Decimal] = None,
        issues_found: str = "",
        corrections_made: str = "",
        recommendations: str = "",
        is_approved: bool = True,
        requires_revision: bool = False,
        revision_notes: str = "",
        edited_files: Optional[list] = None,
    ) -> EditorReviewSubmission:
        """
        Submit a review for an order.
        
        Args:
            task_assignment: The task assignment being reviewed
            editor: The editor submitting the review
            quality_score: Quality score (0.00-10.00)
            issues_found: Issues/problems found
            corrections_made: Corrections made
            recommendations: Recommendations
            is_approved: Whether work is approved for delivery
            requires_revision: Whether revision is needed from writer
            revision_notes: Notes for writer if revision needed
            edited_files: List of file IDs that were edited
            
        Returns:
            EditorReviewSubmission
        """
        if task_assignment.assigned_editor != editor:
            raise ValidationError(
                "Only the assigned editor can submit a review for this task."
            )
        
        if task_assignment.review_status != 'in_review':
            raise ValidationError(
                f"Cannot submit review from status: {task_assignment.review_status}"
            )
        
        order = task_assignment.order
        
        # Validate quality_score
        if quality_score is not None:
            if quality_score < Decimal('0.00') or quality_score > Decimal('10.00'):
                raise ValidationError("Quality score must be between 0.00 and 10.00")
        
        # Create or update review submission
        review_submission, created = EditorReviewSubmission.objects.get_or_create(
            task_assignment=task_assignment,
            defaults={
                'editor': editor,
                'order': order,
                'quality_score': quality_score,
                'issues_found': issues_found,
                'corrections_made': corrections_made,
                'recommendations': recommendations,
                'is_approved': is_approved,
                'requires_revision': requires_revision,
                'revision_notes': revision_notes,
                'edited_files': edited_files or [],
            }
        )
        
        if not created:
            # Update existing submission
            review_submission.quality_score = quality_score
            review_submission.issues_found = issues_found
            review_submission.corrections_made = corrections_made
            review_submission.recommendations = recommendations
            review_submission.is_approved = is_approved
            review_submission.requires_revision = requires_revision
            review_submission.revision_notes = revision_notes
            review_submission.edited_files = edited_files or []
            review_submission.save()
        
        # Update task status based on review
        if is_approved and not requires_revision:
            # Approved - complete the task
            task_assignment.complete_review()

            # Move order to appropriate status using unified transition helper
            # If the order is currently under_editing, transition it to reviewed.
            if order.status == OrderStatus.UNDER_EDITING.value:
                OrderTransitionHelper.transition_order(
                    order=order,
                    target_status=OrderStatus.REVIEWED.value,
                    user=editor.user if hasattr(editor, "user") else None,
                    reason="Editor approved order after editing",
                    action="editor_approve_after_editing",
                    is_automatic=False,
                    skip_payment_check=True,
                    metadata={
                        "editor_profile_id": getattr(editor, "id", None),
                        "editor_task_id": getattr(task_assignment, "id", None),
                    },
                )
            
            # Log action
            EditorActionLog.objects.create(
                editor=editor,
                action_type="submitted_review",
                action=f"Submitted review for order {order.id} - Approved",
                related_order=order,
                related_task=task_assignment,
                metadata={
                    'quality_score': float(quality_score) if quality_score else None,
                    'is_approved': True,
                }
            )
            
            # Notify client
            if order.client:
                NotificationHelper.send_notification(
                    user=order.client,
                    event="order.reviewed",
                    payload={
                        "order_id": order.id,
                        "order_topic": order.topic,
                        "reviewed_by": editor.name,
                        "approved": True,
                        "website_id": order.website_id,
                    },
                    website=order.website
                )
        else:
            # Requires revision - keep in review but mark task appropriately
            task_assignment.notes = (task_assignment.notes or '') + f"\n[Revision Required: {revision_notes}]"
            task_assignment.save()
            
            # Move order to revision_requested status
            if order.status == OrderStatus.UNDER_EDITING.value:
                order.status = OrderStatus.REVISION_REQUESTED.value
                order.save(update_fields=['status'])
            
            # Log action
            EditorActionLog.objects.create(
                editor=editor,
                action_type="submitted_review",
                action=f"Submitted review for order {order.id} - Revision Required",
                related_order=order,
                related_task=task_assignment,
                metadata={
                    'quality_score': float(quality_score) if quality_score else None,
                    'requires_revision': True,
                }
            )
            
            # Notify writer
            if order.assigned_writer:
                NotificationHelper.send_notification(
                    user=order.assigned_writer,
                    event="order.revision_requested",
                    payload={
                        "order_id": order.id,
                        "order_topic": order.topic,
                        "revision_notes": revision_notes,
                        "requested_by": editor.name,
                        "website_id": order.website_id,
                    },
                    website=order.website
                )
        
        AuditLogService.log_auto(
            actor=editor.user,
            action="Editor submitted review",
            target=order,
            changes={
                "review_submission_id": review_submission.id,
                "is_approved": is_approved,
                "requires_revision": requires_revision,
            },
        )
        
        return review_submission
    
    @staticmethod
    @transaction.atomic
    def complete_task(
        task_assignment: EditorTaskAssignment,
        editor: EditorProfile,
        final_notes: str = ""
    ) -> EditorTaskAssignment:
        """
        Mark a task as completed (after review has been submitted and approved).
        
        Args:
            task_assignment: The task assignment to complete
            editor: The editor completing the task
            final_notes: Optional final notes
            
        Returns:
            Updated EditorTaskAssignment
        """
        if task_assignment.assigned_editor != editor:
            raise ValidationError(
                "Only the assigned editor can complete this task."
            )
        
        if task_assignment.review_status not in ['in_review', 'completed']:
            raise ValidationError(
                f"Cannot complete task from status: {task_assignment.review_status}"
            )
        
        # Check if review was submitted
        if not hasattr(task_assignment, 'review_submission'):
            raise ValidationError(
                "Cannot complete task without submitting a review first."
            )
        
        task_assignment.complete_review()
        
        if final_notes:
            task_assignment.notes = (task_assignment.notes or '') + f"\n[Final Notes: {final_notes}]"
            task_assignment.save()
        
        # Log action
        EditorActionLog.objects.create(
            editor=editor,
            action_type="completed_task",
            action=f"Completed task for order {task_assignment.order.id}",
            related_order=task_assignment.order,
            related_task=task_assignment,
        )
        
        AuditLogService.log_auto(
            actor=editor.user,
            action="Editor completed task",
            target=task_assignment.order,
            changes={"review_status": "completed"},
        )
        
        return task_assignment
    
    @staticmethod
    @transaction.atomic
    def reject_task(
        task_assignment: EditorTaskAssignment,
        editor: EditorProfile,
        reason: str
    ) -> EditorTaskAssignment:
        """
        Reject a task (e.g., order quality too poor, needs admin review).
        
        Args:
            task_assignment: The task assignment to reject
            editor: The editor rejecting the task
            reason: Reason for rejection
            
        Returns:
            Updated EditorTaskAssignment
        """
        if task_assignment.assigned_editor != editor:
            raise ValidationError(
                "Only the assigned editor can reject this task."
            )
        
        task_assignment.review_status = 'rejected'
        task_assignment.notes = (task_assignment.notes or '') + f"\n[Rejected: {reason}]"
        task_assignment.reviewed_at = now()
        task_assignment.save()
        
        # Log action
        EditorActionLog.objects.create(
            editor=editor,
            action_type="rejected_task",
            action=f"Rejected task for order {task_assignment.order.id}",
            related_order=task_assignment.order,
            related_task=task_assignment,
            metadata={'reason': reason}
        )
        
        AuditLogService.log_auto(
            actor=editor.user,
            action="Editor rejected task",
            target=task_assignment.order,
            changes={"review_status": "rejected", "reason": reason},
        )
        
        # Notify admin/support
        from users.models import User
        admins = User.objects.filter(role__in=['admin', 'superadmin'], is_active=True)
        for admin in admins:
            NotificationHelper.send_notification(
                event_key="editor.task_rejected",
                user=admin,
                context={
                    "order_id": task_assignment.order.id,
                    "editor": editor.name,
                    "reason": reason,
                },
            )
        
        return task_assignment

