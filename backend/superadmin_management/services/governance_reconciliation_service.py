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
            website = getattr(user, "website", None)
            if not website:
                logger.warning(
                    "Writer reconciliation skipped suspension for user=%s: "
                    "no website context.",
                    user.pk,
                )
                return

            from accounts.models import AccountProfile
            from accounts.services.account_activation_service import (
                AccountActivationService,
            )
            from accounts.services.account_service import AccountService

            account_profile = AccountService.get_or_create_account_profile(
                website=website,
                user=user,
                is_primary=not AccountProfile.objects.filter(user=user).exists(),
                metadata={"source": "governance_reconciliation"},
            )
            AccountActivationService.suspend_account(
                account_profile=account_profile,
                reason="Writer profile missing (reconciled)",
                metadata={"source": "governance_reconciliation"},
            )

    @staticmethod
    def _reconcile_non_writer(user):
        # placeholder for future consistency checks
        pass
