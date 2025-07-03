from decimal import Decimal

from django.core.exceptions import ValidationError
from django.utils import timezone

from audit_logging.services import log_audit_action
from orders.models import WriterRequest
from pricing_configs.models import PricingConfiguration
from discounts.services.discount_engine import DiscountEngine
from orders.services.writer_request_pricing_service import (
    WriterRequestPricingService,
)


class WriterRequestService:
    """
    Handles creation, approval, and payment of writer requests
    such as deadline extensions, page/slide increases.
    """

    @staticmethod
    def create_request(order, writer, request_type, reason, data):
        """
        Create a new writer request and calculate its estimated cost.
        """
        request = WriterRequest.objects.create(
            order=order,
            website=order.website,
            request_type=request_type,
            requested_by_writer=writer,
            request_reason=reason,
            new_deadline=data.get("new_deadline"),
            additional_pages=data.get("additional_pages"),
            additional_slides=data.get("additional_slides"),
            requires_payment=data.get("requires_payment", False),
            status=WriterRequest.RequestStatus.PENDING,
            created_at=timezone.now(),  

        )

        pricing_service = WriterRequestPricingService(request)
        pricing_service.update_writer_request_costs()

        request.requires_payment = request.final_cost > Decimal("0.00")
        request.save()

        log_audit_action(
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
    def client_respond(request, client, approve, reason=None):
        """
        Handle client response to a writer request.
        """
        if request.status != WriterRequest.RequestStatus.PENDING:
            raise ValidationError("Request has already been handled.")

        if approve:
            request.client_approval = True
            request.status = WriterRequest.RequestStatus.ACCEPTED

            if not request.requires_payment:
                WriterRequestPricingService(request).update_writer_request_costs()
                WriterRequestService._apply_request_changes(request)
        else:
            request.status = WriterRequest.RequestStatus.DECLINED

        request.save()

        log_audit_action(
            actor=client,
            action="CLIENT_RESPOND_WRITER_REQUEST",
            target="orders.WriterRequest",
            target_id=request.id,
            metadata={"approved": approve, "reason": reason},
        )

    @staticmethod
    def admin_override(request, admin, new_deadline=None):
        """
        Admin force-approves and optionally sets a new deadline.
        """
        request.admin_approval = True
        request.status = WriterRequest.RequestStatus.ACCEPTED

        if new_deadline:
            request.new_deadline = new_deadline

        WriterRequestPricingService(request).update_writer_request_costs()
        WriterRequestService._apply_request_changes(request)
        request.save()

        log_audit_action(
            actor=admin,
            action="ADMIN_OVERRIDE_WRITER_REQUEST",
            target="orders.WriterRequest",
            target_id=request.id,
            metadata={"new_deadline": new_deadline},
        )

    @staticmethod
    def mark_as_paid(request):
        """
        Mark a request as paid and apply it if fully approved.
        """
        if not request.requires_payment:
            raise ValidationError("Request does not require payment.")

        if not request.client_approval:
            raise ValidationError("Client has not approved the request.")

        request.is_paid = True
        request.save()

        WriterRequestService._apply_request_changes(request)

        log_audit_action(
            actor=request.requested_by_writer,
            action="WRITER_REQUEST_PAID",
            target="orders.WriterRequest",
            target_id=request.id,
            metadata={"final_cost": str(request.final_cost)},
        )

    @staticmethod
    def apply_discount_to_writer_request(request):
        """
        Apply discount to the writer request if available.
        Returns the estimated cost after applying the discount.
        """
        if not request.order.discount:
            return request.estimated_cost

        discount_engine = DiscountEngine(
            discount_codes=[request.order.discount.code],
            user=request.order.user,
            order=request.order,
            website=request.order.website,
            custom_cost_context={
                "additional_pages": request.additional_pages,
                "additional_slides": request.additional_slides,
            },
        )

        discount_engine.apply_discounts()
        return discount_engine.discounted_total

    @staticmethod
    def _apply_request_changes(request):
        """
        Apply changes to the order based on the accepted request.
        """
        if request.status != WriterRequest.RequestStatus.ACCEPTED:
            return

        if request.requires_payment and not request.is_paid:
            return

        order = request.order

        if (
            request.request_type == WriterRequest.RequestType.DEADLINE
            and request.new_deadline
        ):
            order.deadline = request.new_deadline

        if (
            request.request_type == WriterRequest.RequestType.PAGES
            and request.additional_pages
        ):
            order.number_of_pages += request.additional_pages

        if (
            request.request_type == WriterRequest.RequestType.SLIDES
            and request.additional_slides
        ):
            order.number_of_slides += request.additional_slides

        order.save()