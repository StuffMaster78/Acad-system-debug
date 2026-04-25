from __future__ import annotations

from decimal import Decimal
from typing import Any, Optional, cast

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from orders.models.adjustments.order_adjustment_proposal import (
    OrderAdjustmentProposal,
)
from orders.models.adjustments.order_adjustment_request import (
    OrderAdjustmentRequest,
)
from orders.models.orders.constants import (
    ORDER_ADJUSTMENT_KIND_EXTRA_SERVICE,
    ORDER_ADJUSTMENT_KIND_SCOPE_INCREMENT,
    ORDER_ADJUSTMENT_PROPOSAL_ROLE_CLIENT,
    ORDER_ADJUSTMENT_PROPOSAL_ROLE_STAFF,
    ORDER_ADJUSTMENT_PROPOSAL_ROLE_WRITER,
    ORDER_ADJUSTMENT_PROPOSAL_TYPE_CLIENT_COUNTER,
    ORDER_ADJUSTMENT_PROPOSAL_TYPE_FINAL_AGREEMENT,
    ORDER_ADJUSTMENT_PROPOSAL_TYPE_STAFF_OVERRIDE,
    ORDER_ADJUSTMENT_PROPOSAL_TYPE_SYSTEM_QUOTE,
    ORDER_ADJUSTMENT_STATUS_ACCEPTED,
    ORDER_ADJUSTMENT_STATUS_CLIENT_COUNTERED,
    ORDER_ADJUSTMENT_STATUS_PENDING_CLIENT_RESPONSE,
    ORDER_POST_COUNTER_ESCALATION_REASON_SCOPE_UNACCEPTABLE,
)
from orders.validators.adjustment_validators import AdjustmentValidator


class AdjustmentNegotiationService:
    """
    Own proposal-backed adjustment negotiation.
    """

    @classmethod
    @transaction.atomic
    def create_scope_increment_request(
        cls,
        *,
        website,
        order,
        requested_by,
        adjustment_type: str,
        unit_type: str,
        requested_quantity: int,
        title: str,
        description: str = "",
        writer_justification: str = "",
        client_visible_note: str = "",
        pricing_result: dict,
        source_pricing_snapshot=None,
        expires_at=None,
    ) -> OrderAdjustmentRequest:
        """
        Create writer or staff initiated scope increment request.
        """
        current_quantity = getattr(order, "base_quantity", 0)
        AdjustmentValidator.validate_scope_increment(
            current_quantity=current_quantity,
            requested_quantity=requested_quantity,
            unit_type=unit_type,
        )

        quantity_delta = requested_quantity - current_quantity
        request_amount = Decimal(str(pricing_result.get("total_price", "0.00")))
        writer_amount = Decimal(
            str(pricing_result.get("writer_compensation_amount", "0.00"))
        )

        adjustment_request = OrderAdjustmentRequest.objects.create(
            website=website,
            order=order,
            requested_by=requested_by,
            adjustment_type=adjustment_type,
            adjustment_kind=ORDER_ADJUSTMENT_KIND_SCOPE_INCREMENT,
            unit_type=unit_type,
            title=title,
            description=description,
            writer_justification=writer_justification,
            client_visible_note=client_visible_note,
            current_quantity=current_quantity,
            requested_quantity=requested_quantity,
            quantity_delta=quantity_delta,
            request_total_amount=request_amount,
            request_writer_compensation_amount=writer_amount,
            request_pricing_payload=pricing_result,
            source_pricing_snapshot=source_pricing_snapshot,
            status=ORDER_ADJUSTMENT_STATUS_PENDING_CLIENT_RESPONSE,
            expires_at=expires_at,
        )

        proposal = cls._create_proposal(
            adjustment_request=adjustment_request,
            proposed_by=requested_by,
            proposal_role=ORDER_ADJUSTMENT_PROPOSAL_ROLE_WRITER,
            proposal_type=ORDER_ADJUSTMENT_PROPOSAL_TYPE_SYSTEM_QUOTE,
            amount=request_amount,
            unit_type=unit_type,
            adjustment_kind=ORDER_ADJUSTMENT_KIND_SCOPE_INCREMENT,
            reason=writer_justification,
            scope_payload={
                "current_quantity": current_quantity,
                "requested_quantity": requested_quantity,
                "quantity_delta": quantity_delta,
                "unit_type": unit_type,
            },
            pricing_snapshot_payload=pricing_result,
        )

        typed_request = cast(Any, adjustment_request)
        typed_request.current_proposal = proposal
        typed_request.save(update_fields=["current_proposal", "updated_at"])
        return adjustment_request

    @classmethod
    @transaction.atomic
    def create_extra_service_request(
        cls,
        *,
        website,
        order,
        requested_by,
        extra_service_code: str,
        title: str,
        description: str = "",
        writer_justification: str = "",
        client_visible_note: str = "",
        pricing_result: dict,
        source_pricing_snapshot=None,
        expires_at=None,
    ) -> OrderAdjustmentRequest:
        """
        Create an extra service adjustment request.
        """
        AdjustmentValidator.validate_extra_service(
            extra_service_code=extra_service_code,
        )

        amount = Decimal(str(pricing_result.get("total_price", "0.00")))
        writer_amount = Decimal(
            str(pricing_result.get("writer_compensation_amount", "0.00"))
        )

        adjustment_request = OrderAdjustmentRequest.objects.create(
            website=website,
            order=order,
            requested_by=requested_by,
            adjustment_type="extra_service",
            adjustment_kind=ORDER_ADJUSTMENT_KIND_EXTRA_SERVICE,
            unit_type=getattr(order, "unit_type", "other"),
            extra_service_code=extra_service_code,
            title=title,
            description=description,
            writer_justification=writer_justification,
            client_visible_note=client_visible_note,
            current_quantity=0,
            requested_quantity=1,
            quantity_delta=1,
            request_total_amount=amount,
            request_writer_compensation_amount=writer_amount,
            request_pricing_payload=pricing_result,
            source_pricing_snapshot=source_pricing_snapshot,
            status=ORDER_ADJUSTMENT_STATUS_PENDING_CLIENT_RESPONSE,
            expires_at=expires_at,
        )

        proposal = cls._create_proposal(
            adjustment_request=adjustment_request,
            proposed_by=requested_by,
            proposal_role=ORDER_ADJUSTMENT_PROPOSAL_ROLE_WRITER,
            proposal_type=ORDER_ADJUSTMENT_PROPOSAL_TYPE_SYSTEM_QUOTE,
            amount=amount,
            unit_type=adjustment_request.unit_type,
            adjustment_kind=ORDER_ADJUSTMENT_KIND_EXTRA_SERVICE,
            reason=writer_justification,
            scope_payload={
                "extra_service_code": extra_service_code,
                "unit_type": adjustment_request.unit_type,
            },
            pricing_snapshot_payload=pricing_result,
        )

        typed_request = cast(Any, adjustment_request)
        typed_request.current_proposal = proposal
        typed_request.save(update_fields=["current_proposal", "updated_at"])
        return adjustment_request

    @classmethod
    @transaction.atomic
    def client_counter_scope_increment(
        cls,
        *,
        adjustment_request: OrderAdjustmentRequest,
        countered_quantity: int,
        countered_note: str,
        pricing_result: dict,
        counter_pricing_snapshot=None,
        countered_by=None,
    ) -> OrderAdjustmentRequest:
        """
        Record client counter for a scope increment request.
        """
        locked_request = cls._lock_request(adjustment_request)

        if locked_request.adjustment_kind != ORDER_ADJUSTMENT_KIND_SCOPE_INCREMENT:
            raise ValidationError("Only scope increment requests can be quantity-countered.")

        if locked_request.status != ORDER_ADJUSTMENT_STATUS_PENDING_CLIENT_RESPONSE:
            raise ValidationError("Only pending requests can be countered.")

        AdjustmentValidator.validate_counter_quantity(
            current_quantity=locked_request.current_quantity,
            requested_quantity=locked_request.requested_quantity,
            countered_quantity=countered_quantity,
        )

        cls._deactivate_current_proposal(locked_request)

        counter_delta = countered_quantity - locked_request.current_quantity
        counter_amount = Decimal(str(pricing_result.get("total_price", "0.00")))
        writer_amount = Decimal(
            str(pricing_result.get("writer_compensation_amount", "0.00"))
        )

        proposal = cls._create_proposal(
            adjustment_request=locked_request,
            proposed_by=countered_by,
            proposal_role=ORDER_ADJUSTMENT_PROPOSAL_ROLE_CLIENT,
            proposal_type=ORDER_ADJUSTMENT_PROPOSAL_TYPE_CLIENT_COUNTER,
            amount=counter_amount,
            unit_type=locked_request.unit_type,
            adjustment_kind=ORDER_ADJUSTMENT_KIND_SCOPE_INCREMENT,
            reason=countered_note,
            scope_payload={
                "current_quantity": locked_request.current_quantity,
                "countered_quantity": countered_quantity,
                "counter_quantity_delta": counter_delta,
                "unit_type": locked_request.unit_type,
            },
            pricing_snapshot_payload=pricing_result,
        )

        locked_request.countered_quantity = countered_quantity
        locked_request.countered_note = countered_note
        locked_request.countered_by = countered_by
        locked_request.countered_at = timezone.now()
        locked_request.counter_total_amount = counter_amount
        locked_request.counter_writer_compensation_amount = writer_amount
        locked_request.counter_pricing_payload = pricing_result
        locked_request.counter_pricing_snapshot = counter_pricing_snapshot
        locked_request.status = ORDER_ADJUSTMENT_STATUS_CLIENT_COUNTERED
        typed_request = cast(Any, locked_request)
        typed_request.current_proposal = proposal
        typed_request.save()
        return locked_request

    @classmethod
    @transaction.atomic
    def client_accept_extra_service(
        cls,
        *,
        adjustment_request: OrderAdjustmentRequest,
        accepted_by=None,
    ) -> OrderAdjustmentRequest:
        """
        Accept extra service request and prepare it for funding.
        """
        locked_request = cls._lock_request(adjustment_request)

        if locked_request.adjustment_kind != ORDER_ADJUSTMENT_KIND_EXTRA_SERVICE:
            raise ValidationError("Only extra service requests use this accept path.")

        if locked_request.status != ORDER_ADJUSTMENT_STATUS_PENDING_CLIENT_RESPONSE:
            raise ValidationError("Only pending requests can be accepted.")

        locked_request.status = ORDER_ADJUSTMENT_STATUS_ACCEPTED
        locked_request.accepted_at = timezone.now()
        locked_request.reviewed_by = accepted_by
        locked_request.accepted_proposal = locked_request.current_proposal
        locked_request.save(
            update_fields=[
                "status",
                "accepted_at",
                "reviewed_by",
                "accepted_proposal",
                "updated_at",
            ]
        )
        return locked_request

    @classmethod
    @transaction.atomic
    def client_accept_scope_request(
        cls,
        *,
        adjustment_request: OrderAdjustmentRequest,
        accepted_by=None,
    ) -> OrderAdjustmentRequest:
        """
        Accept original scope increment request without countering.
        """
        locked_request = cls._lock_request(adjustment_request)

        if locked_request.adjustment_kind != ORDER_ADJUSTMENT_KIND_SCOPE_INCREMENT:
            raise ValidationError("Only scope increment requests use this path.")

        if locked_request.status != ORDER_ADJUSTMENT_STATUS_PENDING_CLIENT_RESPONSE:
            raise ValidationError("Only pending requests can be accepted.")

        locked_request.status = ORDER_ADJUSTMENT_STATUS_ACCEPTED
        locked_request.accepted_at = timezone.now()
        locked_request.reviewed_by = accepted_by
        locked_request.accepted_proposal = locked_request.current_proposal
        locked_request.save(
            update_fields=[
                "status",
                "accepted_at",
                "reviewed_by",
                "accepted_proposal",
                "updated_at",
            ]
        )
        return locked_request

    @classmethod
    @transaction.atomic
    def writer_escalate_after_funded_counter(
        cls,
        *,
        adjustment_request: OrderAdjustmentRequest,
        writer,
        reason: str,
    ):
        """
        Escalate execution after client-funded counter was already applied.
        """
        locked_request = cls._lock_request(adjustment_request)

        locked_request.escalated_after_counter = True
        locked_request.escalation_reason = reason
        locked_request.save(
            update_fields=[
                "escalated_after_counter",
                "escalation_reason",
                "updated_at",
            ]
        )

        from orders.services.order_reassignment_service import (
            OrderReassignmentService,
        )

        return OrderReassignmentService.request_reassignment(
            order=locked_request.order,
            requested_by=writer,
            requester_role=ORDER_ADJUSTMENT_PROPOSAL_ROLE_WRITER,
            reason=ORDER_POST_COUNTER_ESCALATION_REASON_SCOPE_UNACCEPTABLE,
            internal_notes=reason,
            triggered_by="adjustment_negotiation_service.writer_escalate_after_funded_counter",
        )

    @classmethod
    @transaction.atomic
    def staff_resolve_post_counter_escalation(
        cls,
        *,
        adjustment_request: OrderAdjustmentRequest,
        resolution: str,
        note: str,
        resolved_by,
    ) -> OrderAdjustmentRequest:
        """
        Resolve post-counter escalation.
        """
        locked_request = cls._lock_request(adjustment_request)

        if not locked_request.escalated_after_counter:
            raise ValidationError("Adjustment has no post-counter escalation.")

        locked_request.resolved_by = resolved_by
        locked_request.resolved_at = timezone.now()
        locked_request.reviewed_by = resolved_by
        locked_request.save(
            update_fields=[
                "resolved_by",
                "resolved_at",
                "reviewed_by",
                "updated_at",
            ]
        )
        return locked_request

    @classmethod
    def _create_proposal(
        cls,
        *,
        adjustment_request,
        proposed_by,
        proposal_role: str,
        proposal_type: str,
        amount: Decimal,
        unit_type: str,
        adjustment_kind: str,
        reason: str,
        scope_payload: dict,
        pricing_snapshot_payload: dict,
    ) -> OrderAdjustmentProposal:
        """
        Create proposal row for negotiation ledger.
        """
        typed_request = cast(Any, adjustment_request)
        return OrderAdjustmentProposal.objects.create(
            website=adjustment_request.website,
            adjustment_request=adjustment_request,
            proposed_by=proposed_by,
            proposal_role=proposal_role,
            proposal_type=proposal_type,
            currency=getattr(adjustment_request.order, "currency", "USD"),
            amount=amount,
            unit_type=unit_type,
            adjustment_kind=adjustment_kind,
            reason=reason,
            scope_payload=scope_payload,
            pricing_snapshot_payload=pricing_snapshot_payload,
            is_active=True,
            supersedes_proposal=typed_request.current_proposal,
        )

    @classmethod
    def _deactivate_current_proposal(cls, adjustment_request) -> None:
        """
        Mark current proposal inactive before creating a new proposal.
        """
        proposal = adjustment_request.current_proposal
        if proposal is None:
            return

        proposal.is_active = False
        proposal.save(update_fields=["is_active"])

    @classmethod
    def _lock_request(
        cls,
        adjustment_request: OrderAdjustmentRequest,
    ) -> OrderAdjustmentRequest:
        """
        Lock and reload adjustment request.
        """
        return OrderAdjustmentRequest.objects.select_for_update().get(
            pk=adjustment_request.pk,
        )