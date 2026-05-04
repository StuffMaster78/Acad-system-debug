from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.db import transaction
from django.utils import timezone

from class_management.constants import (
    ClassOrderStatus,
    ClassProposalStatus,
    ClassTimelineEventType,
)
from class_management.exceptions import ClassPricingError
from class_management.integration.class_discount_integration import (
    ClassDiscountIntegrationService,
)
from class_management.models import (
    ClassOrder,
    ClassPriceCounterOffer,
    ClassPriceProposal,
)
from class_management.services.class_order_service import ClassOrderService
from class_management.services.class_timeline_service import (
    ClassTimelineService,
)
from class_management.state_machine import ClassOrderStateMachine
from notifications_system.services.notification_service import (
    NotificationService,
)


class ClassPricingService:
    """
    Service for class order pricing, proposals, and negotiation.
    """

    PROPOSAL_ALLOWED_STATUSES = {
        ClassOrderStatus.UNDER_REVIEW,
        ClassOrderStatus.NEGOTIATING,
        ClassOrderStatus.PRICE_PROPOSED,
    }

    COUNTER_ALLOWED_STATUSES = {
        ClassProposalStatus.SENT,
        ClassProposalStatus.COUNTERED,
    }

    ACCEPT_ALLOWED_STATUSES = {
        ClassProposalStatus.SENT,
        ClassProposalStatus.COUNTERED,
    }

    @classmethod
    @transaction.atomic
    def create_proposal(
        cls,
        *,
        class_order: ClassOrder,
        amount: Decimal,
        proposed_by,
        discount_amount: Decimal = Decimal("0.00"),
        message_to_client: str = "",
        internal_notes: str = "",
        pricing_snapshot: dict[str, Any] | None = None,
        discount_snapshot: dict[str, Any] | None = None,
        expires_at=None,
        send_now: bool = False,
    ) -> ClassPriceProposal:
        """
        Create a price proposal for a reviewed class order.
        """
        cls._ensure_order_can_receive_proposal(class_order=class_order)
        cls._validate_amounts(
            amount=amount,
            discount_amount=discount_amount,
        )

        final_amount = amount - discount_amount

        if final_amount <= Decimal("0.00"):
            raise ClassPricingError(
                "Final proposal amount must be greater than zero."
            )

        proposal = ClassPriceProposal.objects.create(
            class_order=class_order,
            amount=amount,
            discount_amount=discount_amount,
            final_amount=final_amount,
            currency=class_order.currency,
            status=ClassProposalStatus.DRAFT,
            message_to_client=message_to_client,
            internal_notes=internal_notes,
            pricing_snapshot=pricing_snapshot or {},
            discount_snapshot=discount_snapshot or {},
            expires_at=expires_at,
            proposed_by=proposed_by,
        )

        ClassTimelineService.record(
            class_order=class_order,
            event_type=ClassTimelineEventType.PRICE_PROPOSED,
            title="Class price proposal drafted",
            triggered_by=proposed_by,
            metadata={
                "proposal_id": proposal.pk,
                "amount": str(amount),
                "discount_amount": str(discount_amount),
                "final_amount": str(final_amount),
            },
        )

        if send_now:
            cls.send_proposal(
                proposal=proposal,
                sent_by=proposed_by,
            )

        return proposal

    @classmethod
    @transaction.atomic
    def send_proposal(
        cls,
        *,
        proposal: ClassPriceProposal,
        sent_by,
    ) -> ClassPriceProposal:
        """
        Send a drafted proposal to the client.
        """
        if proposal.status != ClassProposalStatus.DRAFT:
            raise ClassPricingError(
                "Only draft proposals can be sent."
            )

        proposal.status = ClassProposalStatus.SENT
        proposal.sent_at = timezone.now()
        proposal.save(
            update_fields=[
                "status",
                "sent_at",
                "updated_at",
            ],
        )

        class_order = ClassOrderService.mark_price_proposed(
            class_order=proposal.class_order,
            quoted_amount=proposal.amount,
            discount_amount=proposal.discount_amount,
            final_amount=proposal.final_amount,
            pricing_snapshot=proposal.pricing_snapshot,
            discount_snapshot=proposal.discount_snapshot,
            proposed_by=sent_by,
        )

        NotificationService.notify(
            event_key="class.price_proposed",
            recipient=class_order.client,
            website=class_order.website,
            context={
                "class_order_id": class_order.pk,
                "proposal_id": proposal.pk,
                "title": class_order.title,
                "amount": str(proposal.amount),
                "discount_amount": str(proposal.discount_amount),
                "final_amount": str(proposal.final_amount),
                "currency": proposal.currency,
            },
            triggered_by=sent_by,
        )

        return proposal

    @classmethod
    @transaction.atomic
    def create_counter_offer(
        cls,
        *,
        proposal: ClassPriceProposal,
        offered_amount: Decimal,
        created_by,
        message: str = "",
    ) -> ClassPriceCounterOffer:
        """
        Create a counter offer against a proposal.
        """
        cls._ensure_proposal_can_be_countered(proposal=proposal)

        if offered_amount <= Decimal("0.00"):
            raise ClassPricingError(
                "Counter offer amount must be greater than zero."
            )

        counter_offer = ClassPriceCounterOffer.objects.create(
            proposal=proposal,
            offered_amount=offered_amount,
            message=message,
            created_by=created_by,
        )

        proposal.status = ClassProposalStatus.COUNTERED
        proposal.save(update_fields=["status", "updated_at"])

        class_order = ClassOrderStateMachine.transition(
            class_order=proposal.class_order,
            to_status=ClassOrderStatus.NEGOTIATING,
            triggered_by=created_by,
            metadata={
                "proposal_id": proposal.pk,
                "counter_offer_id": counter_offer.pk,
                "offered_amount": str(offered_amount),
            },
        )

        NotificationService.notify(
            event_key="class.price_countered",
            recipient=proposal.proposed_by,
            website=class_order.website,
            context={
                "class_order_id": class_order.pk,
                "proposal_id": proposal.pk,
                "counter_offer_id": counter_offer.pk,
                "offered_amount": str(offered_amount),
                "currency": proposal.currency,
            },
            triggered_by=created_by,
        )

        return counter_offer

    @classmethod
    @transaction.atomic
    def revise_proposal(
        cls,
        *,
        proposal: ClassPriceProposal,
        amount: Decimal,
        revised_by,
        discount_amount: Decimal = Decimal("0.00"),
        message_to_client: str = "",
        internal_notes: str = "",
        pricing_snapshot: dict[str, Any] | None = None,
        discount_snapshot: dict[str, Any] | None = None,
        expires_at=None,
        send_now: bool = True,
    ) -> ClassPriceProposal:
        """
        Revise an existing proposal during negotiation.
        """
        if proposal.status in {
            ClassProposalStatus.ACCEPTED,
            ClassProposalStatus.CANCELLED,
            ClassProposalStatus.EXPIRED,
        }:
            raise ClassPricingError(
                "Cannot revise a closed proposal."
            )

        proposal.status = ClassProposalStatus.CANCELLED
        proposal.save(update_fields=["status", "updated_at"])

        return cls.create_proposal(
            class_order=proposal.class_order,
            amount=amount,
            discount_amount=discount_amount,
            message_to_client=message_to_client,
            internal_notes=internal_notes,
            pricing_snapshot=pricing_snapshot,
            discount_snapshot=discount_snapshot,
            expires_at=expires_at,
            proposed_by=revised_by,
            send_now=send_now,
        )

    @classmethod
    @transaction.atomic
    def accept_proposal(
        cls,
        *,
        proposal: ClassPriceProposal,
        accepted_by,
    ) -> ClassPriceProposal:
        """
        Accept a proposal and update the class order price.
        """
        cls._ensure_proposal_can_be_accepted(proposal=proposal)
        cls._ensure_not_expired(proposal=proposal)

        proposal.status = ClassProposalStatus.ACCEPTED
        proposal.accepted_by = accepted_by
        proposal.accepted_at = timezone.now()
        proposal.save(
            update_fields=[
                "status",
                "accepted_by",
                "accepted_at",
                "updated_at",
            ],
        )

        class_order = proposal.class_order
        discount_code = proposal.discount_snapshot.get("discount_code", "")

        if discount_code:
            discount_result = (
                ClassDiscountIntegrationService.apply_class_discount(
                    class_order=class_order,
                    subtotal=proposal.amount,
                    entered_code=discount_code,
                    lifetime_spend=None,
                    has_prior_paid_purchase=True,
                )
            )

            class_order.discount_code = discount_result.discount_code or ""
            class_order.discount_amount = discount_result.discount_amount
            class_order.final_amount = discount_result.final_amount
            class_order.balance_amount = discount_result.final_amount
        else:
            class_order.discount_code = ""
            class_order.discount_amount = proposal.discount_amount
            class_order.final_amount = proposal.final_amount
            class_order.balance_amount = proposal.final_amount

        class_order.quoted_amount = proposal.amount
        class_order.pricing_snapshot = proposal.pricing_snapshot
        class_order.discount_snapshot = proposal.discount_snapshot
        class_order.updated_by = accepted_by
        class_order.save(
            update_fields=[
                "discount_code",
                "quoted_amount",
                "discount_amount",
                "final_amount",
                "balance_amount",
                "pricing_snapshot",
                "discount_snapshot",
                "updated_by",
                "updated_at",
            ],
        )

        class_order = ClassOrderService.accept_price(
            class_order=class_order,
            accepted_by=accepted_by,
        )

        NotificationService.notify(
            event_key="class.price_accepted",
            recipient=proposal.proposed_by,
            website=class_order.website,
            context={
                "class_order_id": class_order.pk,
                "proposal_id": proposal.pk,
                "accepted_amount": str(class_order.accepted_amount),
                "currency": proposal.currency,
            },
            triggered_by=accepted_by,
        )

        return proposal

    @classmethod
    @transaction.atomic
    def reject_proposal(
        cls,
        *,
        proposal: ClassPriceProposal,
        rejected_by,
        reason: str = "",
    ) -> ClassPriceProposal:
        """
        Reject an active proposal.
        """
        if proposal.status not in cls.ACCEPT_ALLOWED_STATUSES:
            raise ClassPricingError(
                "Only active proposals can be rejected."
            )

        proposal.status = ClassProposalStatus.REJECTED
        proposal.rejected_at = timezone.now()
        proposal.save(
            update_fields=[
                "status",
                "rejected_at",
                "updated_at",
            ],
        )

        class_order = ClassOrderStateMachine.transition(
            class_order=proposal.class_order,
            to_status=ClassOrderStatus.NEGOTIATING,
            triggered_by=rejected_by,
            reason=reason,
            metadata={
                "proposal_id": proposal.pk,
            },
        )

        ClassTimelineService.record(
            class_order=class_order,
            event_type=ClassTimelineEventType.PRICE_REJECTED,
            title="Class price proposal rejected",
            description=reason,
            triggered_by=rejected_by,
            metadata={
                "proposal_id": proposal.pk,
            },
        )

        NotificationService.notify(
            event_key="class.price_rejected",
            recipient=proposal.proposed_by,
            website=class_order.website,
            context={
                "class_order_id": class_order.pk,
                "proposal_id": proposal.pk,
                "reason": reason,
            },
            triggered_by=rejected_by,
        )

        return proposal

    @classmethod
    @transaction.atomic
    def expire_old_proposals(cls) -> int:
        """
        Mark expired sent or countered proposals as expired.
        """
        now = timezone.now()

        proposals = ClassPriceProposal.objects.filter(
            status__in=[
                ClassProposalStatus.SENT,
                ClassProposalStatus.COUNTERED,
            ],
            expires_at__isnull=False,
            expires_at__lte=now,
        )

        return proposals.update(
            status=ClassProposalStatus.EXPIRED,
            updated_at=now,
        )

    @classmethod
    def get_latest_active_proposal(
        cls,
        *,
        class_order: ClassOrder,
    ) -> ClassPriceProposal | None:
        """
        Return the latest proposal still open for client action.
        """
        return (
            ClassPriceProposal.objects.filter(
                class_order=class_order,
                status__in=[
                    ClassProposalStatus.SENT,
                    ClassProposalStatus.COUNTERED,
                ],
            )
            .order_by("-created_at")
            .first()
        )

    @classmethod
    @transaction.atomic
    def create_discounted_proposal(
        cls,
        *,
        class_order: ClassOrder,
        amount: Decimal,
        proposed_by,
        client,
        discount_code: str = "",
        message_to_client: str = "",
        internal_notes: str = "",
        pricing_snapshot: dict[str, Any] | None = None,
        expires_at=None,
        send_now: bool = False,
        metadata: dict[str, Any] | None = None,
    ) -> ClassPriceProposal:
        """
        Create a proposal after previewing an optional discount code.
        """
        lifetime_spend = getattr(client, "lifetime_spend", None)
        has_prior_paid_purchase = bool(
            getattr(client, "has_prior_paid_purchase", False)
        )

        discount_result = (
            ClassDiscountIntegrationService.preview_class_discount(
                class_order=class_order,
                subtotal=amount,
                entered_code=discount_code,
                lifetime_spend=lifetime_spend,
                has_prior_paid_purchase=has_prior_paid_purchase,
            )
        )

        discount_snapshot = {
            "discount_code": discount_result.discount_code,
            "discount_amount": str(discount_result.discount_amount),
            "final_amount": str(discount_result.final_amount),
            **(metadata or {}),
        }

        return cls.create_proposal(
            class_order=class_order,
            amount=amount,
            discount_amount=discount_result.discount_amount,
            message_to_client=message_to_client,
            internal_notes=internal_notes,
            pricing_snapshot=pricing_snapshot,
            discount_snapshot=discount_snapshot,
            expires_at=expires_at,
            proposed_by=proposed_by,
            send_now=send_now,
        )

    @classmethod
    def _ensure_order_can_receive_proposal(
        cls,
        *,
        class_order: ClassOrder,
    ) -> None:
        """
        Validate that an order may receive a price proposal.
        """
        if class_order.status not in cls.PROPOSAL_ALLOWED_STATUSES:
            raise ClassPricingError(
                "Cannot create a proposal while class order status is "
                f"{class_order.status}."
            )

    @classmethod
    def _ensure_proposal_can_be_countered(
        cls,
        *,
        proposal: ClassPriceProposal,
    ) -> None:
        """
        Validate that a proposal can receive a counter offer.
        """
        if proposal.status not in cls.COUNTER_ALLOWED_STATUSES:
            raise ClassPricingError(
                "Only sent or countered proposals can receive "
                "counter offers."
            )

        cls._ensure_not_expired(proposal=proposal)

    @classmethod
    def _ensure_proposal_can_be_accepted(
        cls,
        *,
        proposal: ClassPriceProposal,
    ) -> None:
        """
        Validate that a proposal can be accepted.
        """
        if proposal.status not in cls.ACCEPT_ALLOWED_STATUSES:
            raise ClassPricingError(
                "Only sent or countered proposals can be accepted."
            )

    @staticmethod
    def _ensure_not_expired(*, proposal: ClassPriceProposal) -> None:
        """
        Raise when a proposal is expired.
        """
        if proposal.expires_at and proposal.expires_at <= timezone.now():
            proposal.status = ClassProposalStatus.EXPIRED
            proposal.save(update_fields=["status", "updated_at"])

            raise ClassPricingError(
                "This price proposal has expired."
            )

    @staticmethod
    def _validate_amounts(
        *,
        amount: Decimal,
        discount_amount: Decimal,
    ) -> None:
        """
        Validate proposal money values.
        """
        if amount <= Decimal("0.00"):
            raise ClassPricingError(
                "Proposal amount must be greater than zero."
            )

        if discount_amount < Decimal("0.00"):
            raise ClassPricingError(
                "Discount amount cannot be negative."
            )

        if discount_amount >= amount:
            raise ClassPricingError(
                "Discount amount must be less than proposal amount."
            )