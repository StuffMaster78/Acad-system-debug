from __future__ import annotations

from django.db.models import Sum

from tips.models.tip import Tip
from tips.enums.tip_status import TipStatus


def get_total_earned_by_user(*, user_id: int) -> int:
    """
    Total writer earnings from tips in cents.
    Ledger-aligned.
    """
    
    return (
        Tip.objects
        .filter(
            receiver_id=user_id,
            status=TipStatus.SUCCEEDED,
        )
        .aggregate(total=Sum("writer_share_cents"))
        .get("total")
        or 0
    )


def get_platform_revenue() -> int:
    """
    Platform revenue from a user's tips.
    """
    return (
        Tip.objects
        .filter(status=TipStatus.SUCCEEDED)
        .aggregate(total=Sum("platform_fee_cents"))
        .get("total")
        or 0
    )


def get_total_sent_by_user(*, user_id: int) -> int:
    """
    Retrieve all tips sent by a user.
    """
    return (
        Tip.objects
        .filter(sender_id=user_id)
        .aggregate(total=Sum("gross_amount_cents"))
        .get("total")
        or 0
    )