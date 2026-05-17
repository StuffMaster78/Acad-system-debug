import logging

from writer_management.models.writer_profile import WriterProfile
from writer_management.services.discipline_service import DisciplineService

logger = logging.getLogger(__name__)


class WriterGovernanceService:

    @staticmethod
    def suspend_writer(*, superadmin, user, reason, duration_days=None):

        try:
            writer = WriterProfile.objects.get(account_profile__user=user)

            DisciplineService.suspend(
                writer=writer,
                reason=reason,
                suspended_by=superadmin,
                duration_days=duration_days,
            )

        except WriterProfile.DoesNotExist:
            logger.warning("WriterProfile missing for user=%s", user.pk)


    @staticmethod
    def lift_suspension(*, superadmin, user, reason):

        try:
            writer = WriterProfile.objects.get(account_profile__user=user)

            DisciplineService.lift_suspension(
                writer=writer,
                lifted_by=superadmin,
                reason=reason,
            )

        except WriterProfile.DoesNotExist:
            logger.warning("WriterProfile missing for user=%s", user.pk)


    @staticmethod
    def blacklist_writer(*, superadmin, user, reason):

        try:
            writer = WriterProfile.objects.get(account_profile__user=user)

            DisciplineService.blacklist(
                writer=writer,
                reason=reason,
                blacklisted_by=superadmin,
            )

        except WriterProfile.DoesNotExist:
            logger.warning("WriterProfile missing for user=%s", user.pk)


    @staticmethod
    def lift_blacklist(*, superadmin, user, reason):

        try:
            writer = WriterProfile.objects.get(account_profile__user=user)

            DisciplineService.lift_blacklist(
                writer=writer,
                lifted_by=superadmin,
                reason=reason,
            )

        except WriterProfile.DoesNotExist:
            logger.warning("WriterProfile missing for user=%s", user.pk)