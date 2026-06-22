from rest_framework import serializers

from reputation_system.models.writer_reputation_snapshot import WriterReputationSnapshot
from reputation_system.models.website_reputation_snapshot import WebsiteReputationSnapshot


class WriterReputationSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = WriterReputationSnapshot
        fields = [
            "writer_id",
            "rating",
            "review_count",
            "verified_review_count",
            "trust_score",
            "metadata",
            "updated_at",
        ]


class WebsiteReputationSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebsiteReputationSnapshot
        fields = [
            "website_id",
            "rating",
            "review_count",
            "updated_at",
        ]


class LeaderboardEntrySerializer(serializers.Serializer):
    rank = serializers.IntegerField(source="leaderboard_position")
    writer_id = serializers.SerializerMethodField()
    rating = serializers.DecimalField(max_digits=4, decimal_places=2)
    review_count = serializers.IntegerField()
    trust_score = serializers.DecimalField(max_digits=6, decimal_places=2)

    def get_writer_id(self, entry):
        return str(entry.writer.pk)


class WriterRankSerializer(serializers.Serializer):
    writer_id = serializers.UUIDField()
    rank = serializers.IntegerField(allow_null=True)
    percentile = serializers.DecimalField(max_digits=5, decimal_places=2, allow_null=True)
