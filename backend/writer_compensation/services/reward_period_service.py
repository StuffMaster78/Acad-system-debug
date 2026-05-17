from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

from django.utils import timezone


@dataclass(frozen=True)
class RewardPeriod:
    """
    Immutable reward evaluation period.
    """

    start_date: date
    end_date: date


class RewardPeriodService:
    """
    Centralized reward period calculations.

    Avoids duplicated date math across:
        - schedulers
        - evaluations
        - analytics
        - reporting
    """

    @staticmethod
    def current_week() -> RewardPeriod:
        """
        Monday -> Sunday.
        """

        today = timezone.localdate()

        start = today - timedelta(days=today.weekday())
        end = start + timedelta(days=6)

        return RewardPeriod(
            start_date=start,
            end_date=end,
        )

    @staticmethod
    def previous_week() -> RewardPeriod:
        """
        Previous Monday -> Sunday.
        """

        current = RewardPeriodService.current_week()

        end = current.start_date - timedelta(days=1)
        start = end - timedelta(days=6)

        return RewardPeriod(
            start_date=start,
            end_date=end,
        )

    @staticmethod
    def current_month() -> RewardPeriod:
        """
        First day -> last day of current month.
        """

        today = timezone.localdate()

        start = today.replace(day=1)

        if today.month == 12:
            next_month = today.replace(
                year=today.year + 1,
                month=1,
                day=1,
            )
        else:
            next_month = today.replace(
                month=today.month + 1,
                day=1,
            )

        end = next_month - timedelta(days=1)

        return RewardPeriod(
            start_date=start,
            end_date=end,
        )

    @staticmethod
    def previous_month() -> RewardPeriod:
        """
        First day -> last day of previous month.
        """

        current = RewardPeriodService.current_month()

        end = current.start_date - timedelta(days=1)

        start = end.replace(day=1)

        return RewardPeriod(
            start_date=start,
            end_date=end,
        )