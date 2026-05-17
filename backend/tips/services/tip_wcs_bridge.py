from __future__ import annotations

import logging

from writer_compensation.enums.compensation_enums import EventType
from writer_compensation.exceptions.exceptions import NoOpenWindowError
from writer_compensation.services.event_intake_service import EventIntakeService

logger = logging.getLogger(__name__)


class TipWCSBridge:
    """
    Single boundary between the tips app and the WCS.
    Only this file imports from writer_compensation.
    """

    @staticmethod
    def fire(tip) -> tuple:
        """
        Creates a TIP CompensationEvent for a confirmed tip.

        Field mapping from Tip model:
            tip.sender          → client (tipper) — User instance
            tip.receiver        → writer recipient — User instance
            tip.receiver.writer_profile → WriterProfile (what WCS needs)
            tip.gross_amount    → amount
            tip.client_note     → notes
            tip.source_type     → source_type
            tip.sender.website  → website

        Returns (event, created: bool).
        Raises NoOpenWindowError if no open window — caller handles FAILED.
        Raises ValueError if website or writer_profile cannot be resolved.
        """
        website = getattr(tip.sender, "website", None)
        if website is None:
            raise ValueError(
                f"Cannot fire TIP event — tip.sender has no website. "
                f"tip.pk={tip.pk}"
            )

        # FIX 1: receiver is a User — resolve WriterProfile for WCS.
        # Adjust the accessor if your related_name differs.
        writer_profile = getattr(tip.receiver, "writer_profile", None)
        if writer_profile is None:
            raise ValueError(
                f"Cannot fire TIP event — tip.receiver has no writer_profile. "
                f"tip.pk={tip.pk} receiver.pk={tip.receiver.pk}"
            )

        # Stable idempotency key — retries return the existing event,
        # never create a duplicate.
        idempotency_key = f"tip-wcs-{tip.pk}"

        source_id = _resolve_source_id(tip)

        return EventIntakeService.record(
            website=website,
            writer=writer_profile,          # FIX 1: WriterProfile not User
            event_type=EventType.TIP,
            amount=tip.gross_amount,
            source_type=tip.source_type or "",
            source_id=source_id,
            notes=(
                f"Client tip"
                f"{' — ' + tip.client_note if tip.client_note else ''}"
            ),
            idempotency_key=idempotency_key,
            created_by=None,
        )

    @staticmethod
    def fire_safe(tip) -> bool:
        """
        Fire the WCS event and update tip fields in place.
        Returns True on success, False on any error.
        Caller is responsible for calling tip.save() after this.

        Fields updated on tip:
            tip.status          → TipStatus.CONFIRMED or TipStatus.FAILED
            tip.settlement_reference → WCS event PK (stored as string)
            tip.paid_at         → timestamp of confirmation

        FIX 2: compensation_event is not a model field on Tip.
                Storing the WCS event reference in settlement_reference.
        FIX 3: confirmed_at is not a model field on Tip.
                Using paid_at which exists on the model.
        FIX 4: Using TipStatus enum values not raw strings.
        """
        from django.utils import timezone
        from tips.enums.tip_status import TipStatus

        try:
            event, _ = TipWCSBridge.fire(tip)

            # FIX 2: no compensation_event FK on Tip — store ref in
            # settlement_reference (existing CharField on model).
            tip.settlement_reference = str(event.pk)

            # FIX 3: no confirmed_at field — use paid_at.
            tip.paid_at = timezone.now()

            # FIX 4: use enum value not raw string.
            tip.status = TipStatus.SUCCEEDED

            logger.info(
                "TipWCSBridge: fired TIP event %s for tip %s",
                event.pk, tip.pk,
            )
            return True

        except NoOpenWindowError:
            logger.warning(
                "TipWCSBridge: no open window for tip %s — marking FAILED",
                tip.pk,
            )
            tip.status = TipStatus.FAILED  # FIX 4
            return False

        except Exception:
            logger.exception(
                "TipWCSBridge: unexpected error for tip %s", tip.pk,
            )
            tip.status = TipStatus.FAILED  # FIX 4
            return False


def _resolve_source_id(tip) -> int | None:
    """
    Resolve source object ID from the tip's attribution.
    Falls back to None for direct tips with no attribution.
    """
    try:
        attribution = tip.attributions.first()
        if attribution is None:
            return None
        if attribution.order_id:
            return attribution.order_id
        if attribution.special_order_id:
            return attribution.special_order_id
        if attribution.class_purchase_id:
            return attribution.class_purchase_id
    except Exception:
        pass
    return None