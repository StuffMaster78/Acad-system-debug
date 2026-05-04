from __future__ import annotations

from django.utils import timezone

from class_management.models.class_pricing import ClassPriceProposal
from class_management.services.class_pricing_service import (
    ClassPricingService,
)


def expire_old_proposals():
    """
    Expire proposals past expiry time.
    """
    now = timezone.now()

    proposals = ClassPriceProposal.objects.filter(
        status__in=["sent", "countered"],
        expires_at__isnull=False,
        expires_at__lte=now,
    )

    for proposal in proposals:
        ClassPricingService.expire_old_proposals()