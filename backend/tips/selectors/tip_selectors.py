from django.db.models import Sum

from tips.models.tip import Tip
from tips.enums.tip_status import TipStatus


def get_tip_by_id(*, tip_id: int):
    """
    Fetch a single tip with related sender and receiver.
    """

    return Tip.objects.select_related(
        "payment_intent",
        "sender",
        "receiver",
    ).filter(id=tip_id).first()


def get_tips_sent_by_user(*, user_id: int):
    """
    Retrieve all tips sent by a user.
    """

    return (
        Tip.objects.select_related(
            "payment_intent",
            "receiver",
        )
        .filter(sender_id=user_id)
        .order_by("-created_at")
    )


def get_tips_received_by_user(*, user_id: int):
    """
    Retrieve all tips received by a user.
    """

    return (
        Tip.objects.select_related(
            "payment_intent",
            "sender",
        )
        .filter(receiver_id=user_id)
        .order_by("-created_at")
    )


def get_successful_tips(*, user_id: int):
    """
    Retrieve successful tips sent by a user.
    """

    return (
        Tip.objects.filter(
            sender_id=user_id,
            status=TipStatus.SUCCEEDED,
        )
        .order_by("-created_at")
    )