from writer_management.models.discipline import (
    WriterBlacklist, WriterDisciplineConfig,
    WriterStrike, WriterStrikeHistory, WriterSuspension
)
from django.utils import timezone
from datetime import timedelta
    # already imported: WriterStrike, WriterSuspension, WriterDisciplineConfig
from writer_management.models.profile import WriterProfile
from websites.models import Website
from django.db import transaction

class DisciplineService:
    @staticmethod
    def evaluate_strikes(writer):
        website = writer.website
        config = WriterDisciplineConfig.objects.get(website=website)
        strike_count = writer.strikes.count()

        # Blacklist logic
        if strike_count >= config.auto_blacklist_strikes and not DisciplineService.is_blacklisted(writer):
            WriterBlacklist.objects.create(
                website=website,
                writer=writer,
                reason="Auto-blacklisted due to excessive strikes",
                auto_triggered=True
            )
            return "blacklisted"

        # Suspension logic
        if strike_count >= config.max_strikes and not DisciplineService.is_currently_suspended(writer):
            WriterSuspension.objects.create(
                website=website,
                writer=writer,
                end_date=timezone.now() + timedelta(days=config.auto_suspend_days),
                reason="Auto-suspension due to excessive strikes",
                auto_triggered=True
            )
            return "suspended"

        return "ok"

    @staticmethod
    def is_currently_suspended(writer):
        return WriterSuspension.objects.filter(
            writer=writer,
            is_active=True,
            end_date__gt=timezone.now()
        ).exists()

    @staticmethod
    def is_blacklisted(writer):
        return WriterBlacklist.objects.filter(
            writer=writer, is_active=True
        ).exists()