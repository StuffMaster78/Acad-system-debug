from reviews_system.models import Review
from reputation_system.models.writer_reputation_snapshot import (
    WriterReputationSnapshot,
)
from reputation_system.models.website_reputation_snapshot import (
    WebsiteReputationSnapshot,
)


class ReputationSelectors:
    """
    Read selectors for reputation system.

    Unlike services, selectors are:
        - stateless
        - ORM-only
        - safe for reuse
    """

    @staticmethod
    def reviews_for_target(target_type: str, target_id: str | None):
        """
        Fetch reviews for aggregation.
        """
        qs = Review.objects.filter(
            target_type=target_type,
        )

        if target_id is not None:
            qs = qs.filter(target_id=target_id)

        return qs
    @staticmethod
    def writer_snapshot(writer_id: str):
        """
        Get or create writer snapshot.
        """

        obj, _ = WriterReputationSnapshot.objects.get_or_create(
            writer_id=writer_id,
        )
        return obj

    @staticmethod
    def website_snapshot(website_id: str):
        """
        Get or create website snapshot.
        """

        obj, _ = WebsiteReputationSnapshot.objects.get_or_create(
            website_id=website_id,
        )
        return obj