from reputation_system.models.writer_reputation_snapshot import (
    WriterReputationSnapshot,
)
from reputation_system.models.website_reputation_snapshot import (
    WebsiteReputationSnapshot,
)


class ReputationQueryService:
    """
    Read layer for reputation system.

    Used by:
        - bonus_service
        - dashboards
        - admin tools
        - ranking engines
    """

    @classmethod
    def get_writer_reputation(cls, writer_id: str):
        """
        Return writer reputation snapshot.
        """

        return (
            WriterReputationSnapshot.objects
            .filter(writer_id=writer_id)
            .order_by("-updated_at")
            .first()
        )

    @classmethod
    def get_website_reputation(cls, website_id: str):
        """
        Return website reputation snapshot.
        """

        return (
            WebsiteReputationSnapshot.objects
            .filter(website_id=website_id)
            .order_by("-updated_at")
            .first()
        )

    @classmethod
    def top_writers(cls, limit: int = 50):
        """
        Return top writers by rating.
        """
        return (
            WriterReputationSnapshot.objects
            .order_by("-rating", "-review_count")
            [:limit]
        )

    @staticmethod
    def top_websites(limit: int = 50):
        """
        Returns the top rated websites.
        """
        return (
            WebsiteReputationSnapshot.objects
            .order_by("-rating", "-review_count")
            [:limit]
        )