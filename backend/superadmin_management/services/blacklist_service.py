from django.db import transaction
from django.utils.timezone import now

from superadmin_management.models import Blacklist
from superadmin_management.services.writer_governance_service import (
    WriterGovernanceService,
)


class BlacklistService:

    @staticmethod
    @transaction.atomic
    def blacklist(*, superadmin, user=None, email=None, ip_address=None, reason="", website=None):

        if not user and not email and not ip_address:
            raise ValueError("Must provide target")

        entry = Blacklist.objects.create(
            user=user,
            email=email,
            ip_address=ip_address,
            reason=reason,
            blacklisted_by=superadmin,
            website=website,
            is_active=True,
        )

        if user:
            WriterGovernanceService.blacklist_writer(
                superadmin=superadmin,
                user=user,
                reason=reason,
            )

        return entry


    @staticmethod
    @transaction.atomic
    def lift_blacklist(*, superadmin, entry, reason, website=None):

        entry.is_active = False
        entry.lifted_at = now()
        entry.lift_reason = reason
        entry.save()

        if entry.user:
            WriterGovernanceService.lift_blacklist(
                superadmin=superadmin,
                user=entry.user,
                reason=reason,
            )

        return entry
