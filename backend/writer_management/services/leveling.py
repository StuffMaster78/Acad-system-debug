# writer_management/services/writer_leveling_service.py

from writer_management.models.metrics import WriterPerformanceMetrics
from writer_management.models.levels import WriterLevel, WriterLevelHistory
from writer_management.models.configs import WriterLevelConfig
from notifications_system.services.notification_service import NotificationService

class WriterLevelingService:
    @staticmethod
    def assign_level(metrics: WriterPerformanceMetrics) -> str:
        """Assigns a writer level based on performance metrics."""
        writer = metrics.writer
        website = writer.website
        score = metrics.composite_score
        rating = metrics.avg_rating
        revision_rate = metrics.revision_rate
        lateness_rate = metrics.lateness_rate

        configs = WriterLevelConfig.objects.filter(
            website=website, is_active=True
        ).order_by("-priority")

        level = "Unranked"

        for config in configs:
            if (
                score >= config.min_score and
                rating >= config.min_rating and
                (config.max_revision_rate is None or
                 revision_rate <= config.max_revision_rate) and
                (config.max_lateness_rate is None or
                 lateness_rate <= config.max_lateness_rate)
            ):
                level = config.name
                break

        current = (
            WriterLevel.objects
            .filter(writer=writer)
            .first()
        )

        if not current or current.level != level:
            WriterLevel.objects.update_or_create(
                writer=writer,
                defaults={"level": level, "website": website}
            )
            WriterLevelHistory.objects.create(
                writer=writer,
                level=level,
                website=website,
                triggered_by="system"
            )
            # TO DO: Hook notification later here (e.g. send_level_change_alert())
            # send_notification(
            #     user=writer.user,
            #     title="🎉 You’ve leveled up!",
            #     message=f"You’ve been promoted to level: {level}"
            # )

            NotificationService.notify(
                event_key="writer.level_change",
                recipient=writer.user,
                website=website,
                context={
                    "new_level": level,
                    "previous_level": current.level if current else None,
                },
                channels=["email", "in_app"],
                priority="medium",
                is_critical=False,
                is_digest=False,
                is_silent=False,
                digest_group="writer_leveling"
            )


        return level
