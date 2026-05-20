from __future__ import annotations

from decimal import Decimal
from typing import Any, cast

from django.db import transaction
from django.utils import timezone

from wallets.constants import WalletHoldStatus
from wallets.exceptions import WalletHoldError
from wallets.models import WalletHold
from wallets.services.wallet_hold_service import WalletHoldService
from wallets.services.writer_wallet_service import WriterWalletService


class WriterPayoutRequestService:
    """
    Canonical writer payout request workflow.

    Payout requests are represented as wallet holds so requested funds are
    reserved immediately and cannot be reused while finance reviews the request.
    """

    REFERENCE_TYPE = "writer_payout_request"
    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"
    STATUS_PROCESSED = "processed"

    @staticmethod
    def get_queryset(*, website: Any):
        return (
            WalletHold.objects.filter(
                website=website,
                reference_type=WriterPayoutRequestService.REFERENCE_TYPE,
            )
            .select_related("wallet", "wallet__owner_user", "website", "created_by")
            .order_by("-created_at", "-id")
        )

    @staticmethod
    def get_writer_queryset(*, website: Any, writer: Any):
        return WriterPayoutRequestService.get_queryset(website=website).filter(
            wallet__owner_user=writer,
        )

    @staticmethod
    @transaction.atomic
    def request_payout(
        *,
        website: Any,
        writer: Any,
        amount: Decimal,
        reason: str = "",
        created_by: Any | None = None,
        currency: str = "USD",
        metadata: dict[str, Any] | None = None,
    ) -> WalletHold:
        wallet = WriterWalletService.get_wallet(
            website=website,
            writer=writer,
            currency=currency,
        )

        active_request_exists = WalletHold.objects.filter(
            wallet=wallet,
            website=website,
            reference_type=WriterPayoutRequestService.REFERENCE_TYPE,
            status=WalletHoldStatus.ACTIVE,
            metadata__workflow_status__in=[
                WriterPayoutRequestService.STATUS_PENDING,
                WriterPayoutRequestService.STATUS_APPROVED,
            ],
        ).exists()
        if active_request_exists:
            raise WalletHoldError(
                "A pending or approved payout request already exists."
            )

        hold = WalletHoldService.create_hold(
            wallet=wallet,
            amount=amount,
            website=website,
            reason=reason or "Writer payout request",
            created_by=created_by or writer,
            reference_type=WriterPayoutRequestService.REFERENCE_TYPE,
            metadata={
                "workflow_status": WriterPayoutRequestService.STATUS_PENDING,
                "requested_by_id": getattr(created_by or writer, "id", None),
                "requested_at": timezone.now().isoformat(),
                **(metadata or {}),
            },
        )
        hold.reference = f"WPR-{cast(Any, hold).id}"
        hold.save(update_fields=["reference", "updated_at"])
        return hold

    @staticmethod
    @transaction.atomic
    def approve_request(
        *,
        hold: WalletHold,
        reviewed_by: Any,
        review_notes: str = "",
    ) -> WalletHold:
        locked_hold = WriterPayoutRequestService._get_active_request_for_update(
            hold=hold,
        )
        workflow_status = locked_hold.metadata.get("workflow_status")
        if workflow_status != WriterPayoutRequestService.STATUS_PENDING:
            raise WalletHoldError("Only pending payout requests can be approved.")

        WriterPayoutRequestService._update_metadata(
            locked_hold,
            workflow_status=WriterPayoutRequestService.STATUS_APPROVED,
            reviewed_by_id=getattr(reviewed_by, "id", None),
            reviewed_at=timezone.now().isoformat(),
            review_notes=review_notes,
        )
        return locked_hold

    @staticmethod
    @transaction.atomic
    def reject_request(
        *,
        hold: WalletHold,
        reviewed_by: Any,
        review_notes: str = "",
    ) -> WalletHold:
        locked_hold = WriterPayoutRequestService._get_active_request_for_update(
            hold=hold,
        )
        if locked_hold.metadata.get("workflow_status") not in {
            WriterPayoutRequestService.STATUS_PENDING,
            WriterPayoutRequestService.STATUS_APPROVED,
        }:
            raise WalletHoldError("Only pending or approved payout requests can be rejected.")

        released_hold = WalletHoldService.release_hold(
            hold=locked_hold,
            released_by=reviewed_by,
        )
        WriterPayoutRequestService._update_metadata(
            released_hold,
            workflow_status=WriterPayoutRequestService.STATUS_REJECTED,
            reviewed_by_id=getattr(reviewed_by, "id", None),
            reviewed_at=timezone.now().isoformat(),
            review_notes=review_notes,
        )
        return released_hold

    @staticmethod
    @transaction.atomic
    def process_request(
        *,
        hold: WalletHold,
        processed_by: Any,
        external_reference: str = "",
        review_notes: str = "",
    ) -> WalletHold:
        locked_hold = WriterPayoutRequestService._get_active_request_for_update(
            hold=hold,
        )
        if locked_hold.metadata.get("workflow_status") != WriterPayoutRequestService.STATUS_APPROVED:
            raise WalletHoldError("Only approved payout requests can be processed.")

        captured_hold = WalletHoldService.capture_hold(
            hold=locked_hold,
            captured_by=processed_by,
        )
        WriterPayoutRequestService._update_metadata(
            captured_hold,
            workflow_status=WriterPayoutRequestService.STATUS_PROCESSED,
            processed_by_id=getattr(processed_by, "id", None),
            processed_at=timezone.now().isoformat(),
            external_reference=external_reference,
            review_notes=review_notes,
        )
        return captured_hold

    @staticmethod
    def _get_active_request_for_update(*, hold: WalletHold) -> WalletHold:
        locked_hold = (
            WalletHold.objects.select_for_update()
            .select_related("wallet", "website")
            .get(id=cast(Any, hold).id)
        )
        if locked_hold.reference_type != WriterPayoutRequestService.REFERENCE_TYPE:
            raise WalletHoldError("Hold is not a writer payout request.")
        if locked_hold.status != WalletHoldStatus.ACTIVE:
            raise WalletHoldError("Payout request is no longer active.")
        return locked_hold

    @staticmethod
    def _update_metadata(hold: WalletHold, **updates: Any) -> None:
        hold.metadata = {
            **(hold.metadata or {}),
            **updates,
        }
        hold.save(update_fields=["metadata", "updated_at"])
