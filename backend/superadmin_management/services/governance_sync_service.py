import logging

logger = logging.getLogger(__name__)


class GovernanceSyncService:
    """
    Syncs governance state across multiple websites / tenants.
    """

    @staticmethod
    def sync_user_state(user, websites):
        for site in websites:
            logger.info("Syncing user=%s to site=%s", user.pk, site)