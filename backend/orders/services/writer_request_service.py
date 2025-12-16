from decimal import Decimal

from django.core.exceptions import ValidationError
from django.utils import timezone

from audit_logging.services.audit_log_service import AuditLogService
from orders.models import WriterRequest
from pricing_configs.models import PricingConfiguration
from discounts.services.discount_engine import DiscountEngine
from orders.services.writer_request_pricing_service import (
    WriterRequestPricingService,
)
from writer_management.services.earnings_calculator import WriterEarningsCalculator


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
        """
        Handle client response to a writer request.
        
        Args:
            request: WriterRequest instance
            client: User instance (client)
            approve: bool - True to approve, False to reject
            reason: str - Reason for rejection (if rejecting)
            counter_offer_data: dict - Counter offer data with:
                - counter_pages: int (optional)
                - counter_slides: int (optional)
                - counter_cost: Decimal (optional)
                - counter_reason: str (required if counter offer)
        """
        if request.status != WriterRequest.RequestStatus.PENDING:
            raise ValidationError("Request has already been handled.")

        if approve:
            request.client_approval = True
            request.status = WriterRequest.RequestStatus.ACCEPTED

            if not request.requires_payment:
                WriterRequestPricingService(request).update_writer_request_costs()
                WriterRequestService._apply_request_changes(request)
        elif counter_offer_data:
            # Client made a counter offer
            request.has_counter_offer = True
            request.client_counter_pages = counter_offer_data.get('counter_pages')
            request.client_counter_slides = counter_offer_data.get('counter_slides')
            request.client_counter_cost = counter_offer_data.get('counter_cost')
            request.client_counter_reason = counter_offer_data.get('counter_reason')
            # Status remains PENDING for writer to respond
        else:
            # Client rejected without counter offer
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
                "counter_offer": counter_offer_data
            },
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

        AuditLogService.log_auto(
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

        AuditLogService.log_auto(
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
        Also recalculates writer payment if pages/slides were added.
        """
        if request.status != WriterRequest.RequestStatus.ACCEPTED:
            return

        if request.requires_payment and not request.is_paid:
            return

        order = request.order
        pages_added = False
        slides_added = False

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
            pages_added = True

        if (
            request.request_type == WriterRequest.RequestType.SLIDES
            and request.additional_slides
        ):
            order.number_of_slides += request.additional_slides
            slides_added = True

        order.save()
        
        # Recalculate writer payment if pages/slides were added
        if (pages_added or slides_added) and order.assigned_writer:
            WriterRequestService._recalculate_writer_payment_for_additional_pages(order, request)
    
    @staticmethod
    def _recalculate_writer_payment_for_additional_pages(order, writer_request):
        """
        Recalculate writer payment when additional pages/slides are added.
        Uses writer's level to calculate additional earnings.
        """
        from writer_management.models.profile import WriterProfile
        from writer_management.services.earnings_calculator import WriterEarningsCalculator
        from writer_payments_management.models import WriterPayment
        from django.utils import timezone
        
        try:
            writer_profile = WriterProfile.objects.get(
                user=order.assigned_writer,
                website=order.website
            )
        except WriterProfile.DoesNotExist:
            return  # No writer profile, skip recalculation
        
        if not writer_profile.writer_level:
            return  # No writer level, skip recalculation
        
        # Calculate additional earnings for the new pages/slides
        additional_pages = writer_request.additional_pages or 0
        additional_slides = writer_request.additional_slides or 0
        
        if additional_pages == 0 and additional_slides == 0:
            return  # No additional pages/slides
        
        # Calculate additional earnings based on writer level
        additional_earnings = (
            Decimal(str(additional_pages)) * writer_profile.writer_level.base_pay_per_page +
            Decimal(str(additional_slides)) * writer_profile.writer_level.base_pay_per_slide
        )
        
        # Find or create writer payment for this order
        writer_payment, created = WriterPayment.objects.get_or_create(
            writer=writer_profile,
            order=order,
            website=order.website,
            defaults={
                'amount': Decimal('0.00'),
                'bonuses': Decimal('0.00'),
                'fines': Decimal('0.00'),
                'tips': Decimal('0.00'),
                'status': 'Pending'
            }
        )
        
        # If admin set a custom payment amount, we need to recalculate proportionally
        # or use level-based calculation for additional pages
        if order.writer_compensation and order.writer_compensation > 0:
            # Admin set custom amount - calculate additional based on original ratio
            # or just add level-based amount for additional pages
            # For simplicity, we'll add level-based amount for additional pages
            writer_payment.amount += additional_earnings
        else:
            # Level-based payment - recalculate total payment
            # Determine if order is urgent
            is_urgent = False
            if order.writer_deadline or order.client_deadline:
                deadline = order.writer_deadline or order.client_deadline
                hours_until = (deadline - timezone.now()).total_seconds() / 3600
                is_urgent = hours_until <= writer_profile.writer_level.urgent_order_deadline_hours
            
            is_technical = getattr(order, 'is_technical', False)
            
            # Recalculate total payment with new page/slide counts
            total_payment = WriterEarningsCalculator.calculate_earnings(
                writer_profile.writer_level,
                order,
                is_urgent=is_urgent,
                is_technical=is_technical
            )
            
            writer_payment.amount = total_payment
        
        writer_payment.save()