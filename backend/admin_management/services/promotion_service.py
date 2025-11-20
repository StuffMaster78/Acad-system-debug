from django.utils.timezone import now
from admin_management.models import AdminPromotionRequest
from django.db import transaction

class AdminPromotionService:

    @staticmethod
    @transaction.atomic
    def create_request(user, website, role="superadmin", reason=None):
        if not user.admin_profile.is_active:
            raise ValueError("Cannot request promotion for an inactive admin.")

        return AdminPromotionRequest.objects.create(
            website=website,
            requested_by=user,
            requested_role=role,
            reason=reason,
        )

    @staticmethod
    @transaction.atomic
    def approve_request(request: AdminPromotionRequest, approved_by):
        request.status = "approved"
        request.approved_by = approved_by
        request.approved_at = now()
        request.save(update_fields=["status", "approved_by", "approved_at"])

        # Promote the user
        profile = request.requested_by.admin_profile
        profile.is_superadmin = True
        profile.save(update_fields=["is_superadmin"])

    @staticmethod
    def reject_request(request: AdminPromotionRequest, rejected_by):
        request.status = "rejected"
        request.rejected_by = rejected_by
        request.rejected_at = now()
        request.save(update_fields=["status", "rejected_by", "rejected_at"])

    @staticmethod
    def get_pending_requests(website):
        return AdminPromotionRequest.objects.filter(
            website=website,
            status="pending"
        ).select_related("requested_by", "approved_by", "rejected_by")
    
    @staticmethod
    @transaction.atomic
    def submit_promotion_request(request, serializer):
        user = request.user
        if not user.admin_profile.is_active:
            raise ValueError("Inactive admins cannot request promotion.")

        serializer.save(requested_by=user)

    @staticmethod
    @transaction.atomic
    def approve_promotion_request(instance, approver):
        if instance.status != "pending":
            raise ValueError("Only pending requests can be approved.")
        
        instance.status = "approved"
        instance.approved_by = approver
        instance.approved_at = now()
        instance.save(update_fields=["status", "approved_by", "approved_at"])

        # Upgrade their admin profile
        profile = instance.requested_by.admin_profile
        profile.is_superadmin = True
        profile.save(update_fields=["is_superadmin"])

    @staticmethod
    @transaction.atomic
    def reject_promotion_request(instance, rejector):
        if instance.status != "pending":
            raise ValueError("Only pending requests can be rejected.")
        
        instance.status = "rejected"
        instance.rejected_by = rejector
        instance.rejected_at = now()
        instance.save(update_fields=["status", "rejected_by", "rejected_at"])


    @staticmethod
    def get_all_requests(website):
        return AdminPromotionRequest.objects.filter(
            website=website
        ).select_related("requested_by", "approved_by", "rejected_by")
    
    @staticmethod
    def get_request_by_id(request_id):
        try:
            return AdminPromotionRequest.objects.get(id=request_id)
        except AdminPromotionRequest.DoesNotExist:
            raise ValueError("Promotion request not found.")