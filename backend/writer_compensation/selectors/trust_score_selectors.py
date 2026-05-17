from writer_compensation.models.writer_trust_score import (
    WriterTrustScore,
)


class TrustScoreSelectors:

    @staticmethod
    def get_writer_score(*, writer_id: str):
        return (
            WriterTrustScore.objects.filter(
                writer_id=writer_id,
            )
            .select_related("writer")
            .first()
        )

    @staticmethod
    def leaderboard(*, website_id: str, limit: int = 50):
        return (
            WriterTrustScore.objects.filter(
                website_id=website_id,
            )
            .order_by("-score")[:limit]
        )