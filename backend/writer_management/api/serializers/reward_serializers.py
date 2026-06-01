from rest_framework import serializers
from writer_management.models.writer_reward import WriterReward, WriterRewardCriteria


class WriterRewardSerializer(serializers.ModelSerializer):
    class Meta:
        model = WriterReward
        fields = [
            "id",
            "writer",
            "criteria",
            "title",
            "prize_description",
            "prize_amount",
            "is_auto_awarded",
            "has_financial_component",
            "notes",
            "metadata",
            "awarded_at",
        ]
        read_only_fields = fields


class WriterRewardCriteriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = WriterRewardCriteria
        fields = [
            "id",
            "name",
            "description",
            "evaluation_period",
            "min_completed_orders",
            "min_avg_rating",
            "min_earnings",
            "min_composite_score",
            "max_lateness_rate",
            "max_revision_rate",
            "reward_title",
            "prize_description",
            "prize_amount",
            "is_active",
        ]