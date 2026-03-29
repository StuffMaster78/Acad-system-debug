from __future__ import annotations

from typing import Callable, Dict, List, Optional

from notifications_system.services.notification_service import (
    NotificationService,
)
from writer_management.models.badges import Badge, WriterBadge
from writer_management.models.profile import WriterProfile


class AutoBadgeAwardService:
    """Automatically award writer badges and trigger notifications."""

    BADGE_MILESTONES = {
        1: "First Badge",
        5: "Badge Collector",
        10: "Badge Master",
        20: "Badge Legend",
        50: "Badge God",
    }

    BADGE_RULES: Dict[str, Callable] = {
        "consistent_pro": (
            lambda metrics: metrics.top_10_streak_weeks >= 3
        ),
        "big_earner": (
            lambda metrics: metrics.total_earned_usd >= 1000
        ),
        "no_revisions": (
            lambda metrics: metrics.zero_revision_orders >= 10
        ),
        "cool_head": (
            lambda metrics: (
                metrics.completed_orders >= 20
                and metrics.dispute_rate == 0
            )
        ),
        "hot_streak": (
            lambda metrics: metrics.activity_streak_days >= 7
        ),
        "chosen_one": (
            lambda metrics: metrics.preferred_by_count >= 5
        ),
    }

    @staticmethod
    def run(writer: WriterProfile) -> List[str]:
        """
        Award eligible badges and trigger milestone notifications.

        Args:
            writer: The writer profile to evaluate.

        Returns:
            A list of awarded badge rule codes.
        """
        metrics = getattr(writer, "performance_metrics", None)
        if not metrics:
            return []

        awarded_rule_codes: List[str] = []

        for rule_code, rule in AutoBadgeAwardService.BADGE_RULES.items():
            if not rule(metrics):
                continue

            badge = AutoBadgeAwardService._award_badge(
                writer=writer,
                rule_code=rule_code,
            )
            if not badge:
                continue

            awarded_rule_codes.append(rule_code)

            AutoBadgeAwardService._notify_badge_awarded(
                writer=writer,
                badge=badge,
                rule_code=rule_code,
            )

        if not awarded_rule_codes:
            return awarded_rule_codes

        total_badges = WriterBadge.objects.filter(
            writer=writer,
            revoked=False,
        ).count()

        milestone_name = AutoBadgeAwardService.BADGE_MILESTONES.get(
            total_badges
        )
        if milestone_name:
            AutoBadgeAwardService._notify_badge_milestone(
                writer=writer,
                milestone_name=milestone_name,
                milestone_count=total_badges,
                new_badges=awarded_rule_codes,
            )

        return awarded_rule_codes

    @staticmethod
    def _award_badge(
        *,
        writer: WriterProfile,
        rule_code: str,
    ) -> Optional[Badge]:
        """
        Award a badge if it exists for the writer's website and is not
        already active.

        Args:
            writer: Writer profile receiving the badge.
            rule_code: Stable internal badge rule code.

        Returns:
            Badge instance if newly awarded, else None.
        """
        website = getattr(writer, "website", None)
        if not website:
            return None

        try:
            badge = Badge.objects.get(
                website=website,
                rule_code=rule_code,
                auto_award=True,
                is_active=True,
            )
        except Badge.DoesNotExist:
            return None

        already_awarded = WriterBadge.objects.filter(
            writer=writer,
            badge=badge,
            revoked=False,
        ).exists()

        if already_awarded:
            return None

        WriterBadge.objects.create(
            writer=writer,
            badge=badge,
            is_auto_awarded=True,
        )
        return badge

    @staticmethod
    def _notify_badge_awarded(
        *,
        writer: WriterProfile,
        badge: Badge,
        rule_code: str,
    ) -> None:
        """
        Notify the writer that a badge has been awarded.

        Args:
            writer: Writer profile.
            badge: Awarded badge instance.
            rule_code: Stable internal badge rule code.
        """
        user = getattr(writer, "user", None)
        website = getattr(writer, "website", None)

        if not user or not website:
            return

        NotificationService.notify(
            event_key="writer.badges.awarded",
            recipient=user,
            website=website,
            context={
                "writer_id": writer.id,
                "writer_name": user.get_full_name() or user.username,
                "badge_id": badge.id,
                "badge_name": badge.name,
                "badge_icon": badge.icon,
                "badge_rule_code": rule_code,
                "badge_type": badge.type,
                "is_auto_awarded": True,
            },
            triggered_by=None,
            is_digest=True,
            digest_group="writer_badges",
        )

    @staticmethod
    def _notify_badge_milestone(
        *,
        writer: WriterProfile,
        milestone_name: str,
        milestone_count: int,
        new_badges: List[str],
    ) -> None:
        """
        Notify the writer that a badge milestone has been reached.

        Args:
            writer: Writer profile.
            milestone_name: Human readable milestone title.
            milestone_count: Badge total milestone reached.
            new_badges: Newly awarded badge rule codes.
        """
        user = getattr(writer, "user", None)
        website = getattr(writer, "website", None)

        if not user or not website:
            return

        NotificationService.notify(
            event_key="writer.badges.milestone_reached",
            recipient=user,
            website=website,
            context={
                "writer_id": writer.id,
                "writer_name": user.get_full_name() or user.username,
                "milestone_name": milestone_name,
                "milestone_count": milestone_count,
                "total_badges": milestone_count,
                "new_badges": new_badges,
            },
            triggered_by=None,
            is_digest=True,
            digest_group="writer_badges",
        )