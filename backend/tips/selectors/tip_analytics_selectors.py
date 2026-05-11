from django.db.models import Sum, Count

from tips.models.tip import Tip
from tips.enums.tip_status import TipStatus


def get_tip_volume_stats(*, user_id: int) -> dict:
    """
    Lightweight analytics snapshot.
    """

    qs = Tip.objects.filter(receiver_id=user_id)

    return {
        "total_tips": qs.count(),
        "successful_tips": qs.filter(status=TipStatus.SUCCEEDED).count(),
        "failed_tips": qs.filter(status=TipStatus.FAILED).count(),
        "pending_tips": qs.filter(
            status__in=[
                TipStatus.PAYMENT_INITIATED,
                TipStatus.PROCESSING,
            ]
        ).count(),
    }


def get_top_tippers(*, user_id: int, limit: int = 10):
    """
    Users who send the most tips to a receiver.
    """
    return (
        Tip.objects
        .filter(receiver_id=user_id, status=TipStatus.SUCCEEDED)
        .values("sender_id")
        .annotate(total=Count("id"))
        .order_by("-total")[:limit]
    )


def get_writer_stats(*, writer_id: int):
    """
    Aggregate writer earnings and tip count.
    """

    return (
        Tip.objects.filter(receiver_id=writer_id)
        .aggregate(
            total_earned=Sum("writer_share_cents"),
            total_tips=Count("id"),
        )
    )