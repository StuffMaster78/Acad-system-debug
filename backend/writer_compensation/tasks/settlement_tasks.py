from __future__ import annotations

from celery import shared_task
from django.db import transaction

from writer_compensation.models.payment_window import (
    PaymentWindow,
)
from writer_compensation.models.settlement_period import (
    SettlementPeriod,
)

from writer_compensation.services.settlement_engine_service import (
    SettlementEngineService,
)

from writer_compensation.services.settlement_validation_layer import (
    SettlementValidationService,
)

from writer_compensation.tasks.exposure_tasks import (
    materialize_exposure_from_settlement,
)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
    max_retries=3,
)
def run_writer_settlement(
    self,
    *,
    website_id: int,
    writer_id: int,
    payment_window_id: int,
):
    """
    Full settlement orchestration task.

    Flow:
        1. Create settlement period
        2. Build settlement snapshot
        3. Create settlement items
        4. Validate settlement
        5. Finalize settlement
        6. Trigger exposure materialization

    Safe for retries and production workers.
    """

    with transaction.atomic():

        payment_window = PaymentWindow.objects.select_related(
            "website",
        ).get(
            id=payment_window_id,
        )

        website = payment_window.website

        writer = payment_window.writers.get(
            id=writer_id,
        )

        # -----------------------------------
        # Create / fetch settlement period
        # -----------------------------------
        period = SettlementEngineService.create_settlement_period(
            website=website,
            writer=writer,
            payment_window=payment_window,
        )

        # -----------------------------------
        # Build immutable financial snapshot
        # -----------------------------------
        period = SettlementEngineService.build_settlement_snapshot(
            period=period,
        )

        # -----------------------------------
        # Create settlement breakdown rows
        # -----------------------------------
        SettlementEngineService.create_settlement_items(
            period=period,
        )

        # -----------------------------------
        # Validate settlement integrity
        # -----------------------------------
        SettlementValidationService.assert_valid(
            period=period,
        )

        # -----------------------------------
        # Finalize settlement
        # -----------------------------------
        period = SettlementEngineService.finalize_settlement_period(
            period=period,
        )

    # ---------------------------------------
    # Trigger exposure projection async
    # ---------------------------------------
    materialize_exposure_from_settlement.delay(
        settlement_period_id=period.pk,
    )

    return {
        "status": "SUCCESS",
        "settlement_period_id": period.pk,
        "writer_id": writer_id,
        "payment_window_id": payment_window_id,
    }


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
    max_retries=3,
)
def finalize_existing_settlement(
    self,
    *,
    settlement_period_id: int,
):
    """
    Finalize already-built settlement period.

    Useful for:
        - admin approvals
        - manual retries
        - delayed validation workflows
    """

    with transaction.atomic():

        period = SettlementPeriod.objects.select_related(
            "website",
            "writer",
            "payment_window",
        ).get(
            id=settlement_period_id,
        )

        SettlementValidationService.assert_valid(
            period=period,
        )

        period = SettlementEngineService.finalize_settlement_period(
            period=period,
        )

    materialize_exposure_from_settlement.delay(
        settlement_period_id=period.pk,
    )

    return {
        "status": "FINALIZED",
        "settlement_period_id": period.pk,
    }