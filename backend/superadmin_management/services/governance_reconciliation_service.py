# superadmin_management/services/governance_reconciliation_service.py

import logging

logger = logging.getLogger(__name__)


class GovernanceReconciliationService:
    """
    Detects and fixes mismatches between:
    - User model flags
    - Writer discipline state
    - Blacklist records
    """

    @staticmethod
    def run_user_reconciliation(*, user):
        """
        Entry point for reconciling a single user.
        """

        role = getattr(user, "role", None)

        if role != "writer":
            GovernanceReconciliationService._reconcile_non_writer(user)
            return

        GovernanceReconciliationService._reconcile_writer(user)

    @staticmethod
    def _reconcile_writer(user):
        from writer_management.models.writer_profile import WriterProfile

        try:
            WriterProfile.objects.get(account_profile__user=user)
        except WriterProfile.DoesNotExist:
            logger.warning(
                "Writer reconciliation: missing profile for user=%s",
                user.pk,
            )
            # decide policy: quarantine or flag
            user.is_suspended = True
            user.suspension_reason = "Writer profile missing (reconciled)"
            user.save(update_fields=["is_suspended", "suspension_reason"])

    @staticmethod
    def _reconcile_non_writer(user):
        # placeholder for future consistency checks
        pass