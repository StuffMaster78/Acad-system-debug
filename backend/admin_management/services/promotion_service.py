from django.utils.timezone import now
from django.db import transaction
from admin_management.models import AdminPromotionRequest


class AdminPromotionService:

    @staticmethod
    @transaction.atomic
    def create_request(user, website, role="superadmin", reason=None):
        """Create a new promotion request for an active admin."""
        if not user.admin_profile.is_active:
            raise ValueError("Inactive admins cannot request promotion.")

        return AdminPromotionRequest.objects.create(
            website=website,
            requested_by=user,
            requested_role=role,
            reason=reason,
        )

    @staticmethod
    @transaction.atomic
    def approve_request(instance, approver):
        """Approve a pending promotion request and elevate the admin."""
        if instance.status != "pending":
            raise ValueError("Only pending requests can be approved.")

        instance.status = "approved"
        instance.approved_by = approver
        instance.approved_at = now()
        instance.save(update_fields=["status", "approved_by", "approved_at"])

        profile = instance.requested_by.admin_profile
        profile.is_superadmin = True
        profile.save(update_fields=["is_superadmin"])

    @staticmethod
    @transaction.atomic
    def reject_request(instance, rejector):
        """Reject a pending promotion request."""
        if instance.status != "pending":
            raise ValueError("Only pending requests can be rejected.")

        instance.status = "rejected"
        instance.rejected_by = rejector
        instance.rejected_at = now()
        instance.save(update_fields=["status", "rejected_by", "rejected_at"])

    @staticmethod
    def get_pending_requests(website):
        """Return all pending promotion requests for a website."""
        return (
            AdminPromotionRequest.objects
            .filter(website=website, status="pending")
            .select_related("requested_by", "approved_by", "rejected_by")
        )

    @staticmethod
    def get_all_requests(website):
        """Return all promotion requests for a website."""
        return (
            AdminPromotionRequest.objects
            .filter(website=website)
            .select_related("requested_by", "approved_by", "rejected_by")
        )

    @staticmethod
    def get_request_by_id(request_id):
        """Fetch a single promotion request or raise if not found."""
        try:
            return AdminPromotionRequest.objects.get(id=request_id)
        except AdminPromotionRequest.DoesNotExist:
            raise ValueError(f"Promotion request {request_id} not found.")