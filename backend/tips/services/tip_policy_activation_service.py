from __future__ import annotations

from django.db import transaction

from tips.models.tip_policy import TipPolicy


class TipPolicyActivationService:
    """
    Activates a specific tipping policy.
    """

    @classmethod
    @transaction.atomic
    def activate(cls, *, policy: TipPolicy, triggered_by):

        TipPolicy.objects.filter(
            is_active=True
        ).update(is_active=False)

        policy.is_active = True
        policy.save(update_fields=["is_active"])

        return policy