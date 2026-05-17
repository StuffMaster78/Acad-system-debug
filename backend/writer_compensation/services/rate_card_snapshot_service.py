"""
Immutable rate-card snapshot service.

Purpose
-------
Capture ALL compensation-driving values at assignment time so that:
- future level changes NEVER affect historical orders
- earnings calculations remain reproducible forever
- payouts remain audit-safe
- pricing logic changes do not mutate old compensation

Critical Rule
-------------
This service MUST be called inside the SAME database transaction
as the assignment itself.

If snapshot creation fails:
    → assignment MUST fail
    → transaction MUST roll back

Architecture
------------
WriterLevelSettings
    ↓
RateCardSnapshotService.capture()
    ↓
RateCardSnapshot (immutable by-value record)
    ↓
EarningsCalculationService
    ↓
CompensationEvent

Important
---------
- Never calculate earnings from live WriterLevelSettings
- Never mutate snapshots after creation
- Never recreate snapshots for existing orders
- Snapshot EVERYTHING required for payout reproducibility
"""

from __future__ import annotations

import logging

from django.db import IntegrityError
from django.db import transaction
from django.db.models import QuerySet

from writer_compensation.models.rate_card_snapshot import (
    RateCardSnapshot,
)
from writer_management.exceptions import (
    LevelSettingsMissingError,
)

logger = logging.getLogger(__name__)


class RateCardSnapshotService:
    """
    Immutable rate-card snapshot orchestration service.
    """

    @staticmethod
    def _validate_writer_level(writer_profile) -> tuple:
        """
        Validate writer level configuration integrity.

        Returns:
            tuple(level, settings)

        Raises:
            LevelSettingsMissingError
        """
        level = writer_profile.writer_level

        if level is None:
            raise LevelSettingsMissingError(
                f"Writer {writer_profile.registration_id} "
                f"has no WriterLevel assigned."
            )

        settings = getattr(level, "settings", None)

        if settings is None:
            raise LevelSettingsMissingError(
                f"WriterLevel '{level.name}' "
                f"(pk={level.pk}) has no settings configured."
            )

        required_fields = (
            "earning_mode",
            "base_pay_per_page",
            "base_pay_per_slide",
            "base_pay_per_chart",
            "additional_page_pay",
            "additional_slide_pay",
            "additional_chart_pay",
            "urgent_time_threshold_hours",
            "urgent_order_surcharge",
            "urgent_multiplier",
            "tip_percentage",
        )

        missing_fields = [
            field
            for field in required_fields
            if not hasattr(settings, field)
        ]

        if missing_fields:
            raise LevelSettingsMissingError(
                f"WriterLevelSettings for level '{level.name}' "
                f"is missing required fields: {missing_fields}"
            )

        return level, settings

    @staticmethod
    @transaction.atomic
    def capture(
        *,
        writer_profile,
        order,
    ) -> RateCardSnapshot:
        """
        Capture immutable compensation terms for an order.

        This method is IDEMPOTENT.
        If a snapshot already exists for the order,
        the existing snapshot is returned.

        Args:
            writer_profile:
                WriterProfile instance.

            order:
                Order instance.

        Returns:
            RateCardSnapshot

        Raises:
            LevelSettingsMissingError
            IntegrityError
        """

        existing_snapshot = (
            RateCardSnapshot.objects
            .select_related("writer")
            .filter(order=order)
            .first()
        )

        if existing_snapshot is not None:
            logger.warning(
                "RateCardSnapshot already exists "
                "for order=%s. Returning existing snapshot.",
                order.pk,
            )
            return existing_snapshot

        level, settings = (
            RateCardSnapshotService
            ._validate_writer_level(writer_profile)
        )

        snapshot_defaults = {
            # Ownership
            "website": order.website,
            "writer": writer_profile,

            # Snapshot metadata
            "currency": getattr(
                settings,
                "currency",
                "USD",
            ),
            "rate_card_version": getattr(
                settings,
                "rate_card_version",
                1,
            ),
            "settings_updated_at": getattr(
                settings,
                "updated_at",
                None,
            ),

            # Level identity (by value)
            "level_name": level.name,

            # Earnings structure
            "earning_mode": settings.earning_mode,

            # Base earnings
            "base_pay_per_page": settings.base_pay_per_page,
            "base_pay_per_slide": settings.base_pay_per_slide,
            "base_pay_per_chart": settings.base_pay_per_chart,

            # Additional work
            "additional_page_pay": settings.additional_page_pay,
            "additional_slide_pay": settings.additional_slide_pay,
            "additional_chart_pay": settings.additional_chart_pay,

            # Urgency pricing
            "urgent_time_threshold_hours": (
                settings.urgent_time_threshold_hours
            ),
            "urgent_order_surcharge": (
                settings.urgent_order_surcharge
            ),
            "urgent_multiplier": settings.urgent_multiplier,

            # Tips
            "tip_percentage": settings.tip_percentage,
        }

        try:
            snapshot, created = (
                RateCardSnapshot.objects.get_or_create(
                    order=order,
                    defaults=snapshot_defaults,
                )
            )

        except IntegrityError as exc:
            logger.exception(
                "Failed creating RateCardSnapshot "
                "for order=%s writer=%s",
                order.pk,
                writer_profile.registration_id,
            )
            raise IntegrityError(
                "Failed to create immutable rate card snapshot."
            ) from exc

        if not created:
            logger.warning(
                "Duplicate snapshot capture prevented "
                "for order=%s",
                order.pk,
            )
            return snapshot

        logger.info(
            "RateCardSnapshot captured "
            "order=%s writer=%s level=%s version=%s",
            order.pk,
            writer_profile.registration_id,
            level.name,
            snapshot.rate_card_version,
        )

        return snapshot

    @staticmethod
    def get_for_order(
        *,
        order,
    ) -> RateCardSnapshot:
        """
        Retrieve immutable snapshot for an order.

        Raises:
            RateCardSnapshot.DoesNotExist
        """
        return (
            RateCardSnapshot.objects
            .select_related(
                "writer",
                "writer__writer_level",
            )
            .get(order=order)
        )

    @staticmethod
    def exists_for_order(
        *,
        order,
    ) -> bool:
        """
        Check whether a snapshot exists for an order.
        """
        return (
            RateCardSnapshot.objects
            .filter(order=order)
            .exists()
        )

    @staticmethod
    def get_queryset() -> QuerySet[RateCardSnapshot]:
        """
        Base optimized queryset for read services/admin.
        """
        return (
            RateCardSnapshot.objects
            .select_related(
                "website",
                "writer",
                "order",
            )
        )