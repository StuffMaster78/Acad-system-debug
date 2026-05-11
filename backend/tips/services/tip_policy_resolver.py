from __future__ import annotations

from tips.models.tip_policy import TipPolicy


class TipPolicyResolver:
    """
    Resolves active tip policy.
    """

    @staticmethod
    def get_active_policy() -> TipPolicy:
        policy = (
            TipPolicy.objects.filter(
                is_active=True
            )
            .order_by("-version")
            .first()
        )

        if not policy:
            raise RuntimeError(
                "No active tip policy configured."
            )

        return policy