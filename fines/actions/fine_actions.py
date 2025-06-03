
from users.mixins import UserRole
from actions.permissioned import PermissionedAction
from actions.base import BaseAction
from actions.dispatcher import register_action
from fines.services.fine_services import FineService
from fines.services.fine_appeal_service import FineAppealService


@register_action("issue_fine")
class IssueFineAction(PermissionedAction):
    """Action to issue a fine for an order."""

    required_roles = [UserRole.ADMIN, UserRole.SUPERADMIN, UserRole.SUPPORT]

    def perform(self, *, order, fine_type, reason, issued_by):
        """
        Args:
            order (Order): Order to be fined.
            fine_type (str): Fine type code.
            reason (str): Reason for fine.
            issued_by (User): Actor performing the action.

        Returns:
            Fine: The issued fine instance.
        """
        return FineService.issue_fine(
            order=order,
            fine_type=fine_type,
            reason=reason,
            issued_by=issued_by
        )


@register_action("waive_fine")
class WaiveFineAction(PermissionedAction):
    """Action to waive a fine."""

    required_roles = [UserRole.ADMIN, UserRole.SUPERADMIN, UserRole.SUPPORT]

    def perform(self, *, fine, waived_by, reason=None):
        """
        Args:
            fine (Fine): Fine to waive.
            waived_by (User): Admin waiving the fine.
            reason (str, optional): Reason for waiver.

        Returns:
            Fine: The waived fine.
        """
        return FineService.waive_fine(
            fine=fine,
            waived_by=waived_by,
            reason=reason
        )


@register_action("void_fine")
class VoidFineAction(PermissionedAction):
    """Action to void a fine."""

    required_roles = [UserRole.ADMIN, UserRole.SUPERADMIN, UserRole.SUPPORT]

    def perform(self, *, fine, voided_by, reason=None):
        """
        Args:
            fine (Fine): Fine to void.
            voided_by (User): Admin voiding the fine.
            reason (str, optional): Reason for voiding.

        Returns:
            Fine: The voided fine.
        """
        return FineService.void_fine(
            fine=fine,
            voided_by=voided_by,
            reason=reason
        )


@register_action("submit_fine_appeal")
class SubmitFineAppealAction(PermissionedAction):
    """Action to submit a fine appeal."""

    required_roles = [UserRole.WRITER]

    def perform(self, *, fine, appealed_by, reason):
        """
        Args:
            fine (Fine): Fine to appeal.
            appealed_by (User): User submitting the appeal.
            reason (str): Appeal reason.

        Returns:
            FineAppeal: The submitted appeal.
        """
        return FineAppealService.submit_appeal(
            fine=fine,
            appealed_by=appealed_by,
            reason=reason
        )


@register_action("review_fine_appeal")
class ReviewFineAppealAction(PermissionedAction):
    """Action to review a fine appeal."""

    required_roles = [UserRole.ADMIN, UserRole.SUPERADMIN, UserRole.SUPPORT]

    def perform(self, *, appeal, reviewed_by, accept, review_notes=None):
        """
        Args:
            appeal (FineAppeal): Appeal to review.
            reviewed_by (User): Reviewer.
            accept (bool): Accept or reject appeal.
            review_notes (str, optional): Reviewer's notes.

        Returns:
            FineAppeal: The reviewed appeal.
        """
        return FineAppealService.review_appeal(
            appeal=appeal,
            reviewed_by=reviewed_by,
            accept=accept,
            review_notes=review_notes
        )