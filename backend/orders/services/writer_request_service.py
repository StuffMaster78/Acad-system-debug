from decimal import Decimal

from django.core.exceptions import ValidationError
from django.utils import timezone

from audit_logging.services.audit_log_service import AuditLogService
from orders.models.legacy_models.requests import WriterRequest
from orders.services.old_services.writer_request_pricing_service import WriterRequestPricingService


class WriterRequestService:
    """
    Handles creation, approval, and payment of writer requests
    (deadline extensions, page/slide increases).
    """

    @staticmethod
    def create_request(order, writer, request_type, reason, data):
        request = WriterRequest.objects.create(
            order=order,
            website=order.website,
            request_type=request_type,
            requested_by_writer=writer,
            request_reason=reason,
            new_deadline=data.get("new_deadline"),
            additional_pages=data.get("additional_pages"),
            additional_slides=data.get("additional_slides"),
            requires_payment=False,
            status=WriterRequest.RequestStatus.PENDING,
            created_at=timezone.now(),
        )

        pricing_service = WriterRequestPricingService(request)
        pricing_service.update_writer_request_costs()

        request.requires_payment = (request.final_cost or Decimal("0")) > Decimal("0")
        request.save()

        AuditLogService.log_auto(
            actor=writer,
            action="CREATE_WRITER_REQUEST",
            target="orders.WriterRequest",
            target_id=request.id,
            metadata={
                "request_type": request_type,
                "estimated_cost": str(request.estimated_cost),
                "requires_payment": request.requires_payment,
                "data": data,
            },
        )

        return request

    @staticmethod
    def client_respond(request, client, approve, reason=None, counter_offer_data=None):
        if request.status != WriterRequest.RequestStatus.PENDING:
            raise ValidationError("Request has already been handled.")

        if approve:
            request.client_approval = True
            request.status = WriterRequest.RequestStatus.ACCEPTED
            if not request.requires_payment:
                WriterRequestPricingService(request).update_writer_request_costs()
                WriterRequestService._apply_request_changes(request)
        elif counter_offer_data:
            request.has_counter_offer = True
            request.client_counter_pages = counter_offer_data.get("counter_pages")
            request.client_counter_slides = counter_offer_data.get("counter_slides")
            request.client_counter_cost = counter_offer_data.get("counter_cost")
            request.client_counter_reason = counter_offer_data.get("counter_reason")
        else:
            request.status = WriterRequest.RequestStatus.DECLINED

        request.save()

        AuditLogService.log_auto(
            actor=client,
            action="CLIENT_RESPOND_WRITER_REQUEST",
            target="orders.WriterRequest",
            target_id=request.id,
            metadata={
                "approved": approve,
                "has_counter_offer": bool(counter_offer_data),
                "reason": reason,
                "counter_offer": counter_offer_data,
            },
        )

    @staticmethod
    def admin_override(request, admin, new_deadline=None):
        request.admin_approval = True
        request.status = WriterRequest.RequestStatus.ACCEPTED
        if new_deadline:
            request.new_deadline = new_deadline
        WriterRequestPricingService(request).update_writer_request_costs()
        WriterRequestService._apply_request_changes(request)
        request.save()

        AuditLogService.log_auto(
            actor=admin,
            action="ADMIN_OVERRIDE_WRITER_REQUEST",
            target="orders.WriterRequest",
            target_id=request.id,
            metadata={"new_deadline": new_deadline},
        )

    @staticmethod
    def mark_as_paid(request):
        if not request.requires_payment:
            raise ValidationError("Request does not require payment.")
        if not request.client_approval:
            raise ValidationError("Client has not approved the request.")
        request.is_paid = True
        request.save()
        WriterRequestService._apply_request_changes(request)

        AuditLogService.log_auto(
            actor=request.requested_by_writer,
            action="WRITER_REQUEST_PAID",
            target="orders.WriterRequest",
            target_id=request.id,
            metadata={"final_cost": str(request.final_cost)},
        )

    @staticmethod
    def _apply_request_changes(request):
        if request.status != WriterRequest.RequestStatus.ACCEPTED:
            return
        if request.requires_payment and not request.is_paid:
            return

        order = request.order
        pages_added = False
        slides_added = False

        if request.request_type == WriterRequest.RequestType.DEADLINE and request.new_deadline:
            order.deadline = request.new_deadline

        if request.request_type == WriterRequest.RequestType.PAGES and request.additional_pages:
            order.number_of_pages += request.additional_pages
            pages_added = True

        if request.request_type == WriterRequest.RequestType.SLIDES and request.additional_slides:
            order.number_of_slides += request.additional_slides
            slides_added = True

        order.save()

        if (pages_added or slides_added) and order.assigned_writer:
            WriterRequestService._recalculate_writer_payment(order, request)

    @staticmethod
    def _recalculate_writer_payment(order, writer_request):
        try:
            from writer_management.models.writer_profile import WriterProfile
            from writer_compensation.models import WriterPayment

            writer_profile = WriterProfile.objects.get(user=order.assigned_writer, website=order.website)
        except Exception:
            return

        if not writer_profile.writer_level:
            return

        additional_pages = writer_request.additional_pages or 0
        additional_slides = writer_request.additional_slides or 0
        if not additional_pages and not additional_slides:
            return

        try:
            additional_earnings = (
                Decimal(str(additional_pages)) * writer_profile.writer_level.base_pay_per_page
                + Decimal(str(additional_slides)) * writer_profile.writer_level.base_pay_per_slide
            )
            writer_payment, _ = WriterPayment.objects.get_or_create(
                writer=writer_profile,
                order=order,
                website=order.website,
                defaults={"amount": Decimal("0.00"), "bonuses": Decimal("0.00"),
                          "fines": Decimal("0.00"), "tips": Decimal("0.00"), "status": "Pending"},
            )
            writer_payment.amount = (writer_payment.amount or Decimal("0")) + additional_earnings
            writer_payment.save()
        except Exception:
            pass
