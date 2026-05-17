# superadmin_management/services/writer_profile_integrity_service.py

import logging

logger = logging.getLogger(__name__)


class WriterProfileIntegrityService:
    """
    Detects orphan writer accounts.
    """

    @staticmethod
    def check(user):
        from writer_management.models.writer_profile import WriterProfile

        if user.role != "writer":
            return True

        exists = WriterProfile.objects.filter(
            account_profile__user=user
        ).exists()

        if not exists:
            logger.warning("Orphan writer detected user=%s", user.pk)
            return False

        return True