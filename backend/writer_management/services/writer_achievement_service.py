from __future__ import annotations

from writer_management.models.writer_achievement import (
    WriterAchievement,
)


class AchievementService:
    """
    Writer achievement orchestration layer.
    """

    @classmethod
    def award_achievement(
        cls,
        *,
        website,
        writer,
        slug: str,
        title: str,
        description: str = "",
        badge: str = "",
        metadata: dict | None = None,
    ) -> WriterAchievement:
        """
        Award immutable achievement.
        """

        achievement, _ = (
            WriterAchievement.objects.get_or_create(
                writer=writer,
                slug=slug,
                defaults={
                    "website": website,
                    "title": title,
                    "description": (
                        description
                    ),
                    "badge": badge,
                    "metadata": (
                        metadata or {}
                    ),
                },
            )
        )

        return achievement