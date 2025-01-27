from rest_framework import serializers
from .models import (
    PredefinedSpecialOrderConfig, SpecialOrder, Milestone, ProgressLog, WriterBonus
)


class PredefinedSpecialOrderConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = PredefinedSpecialOrderConfig
        fields = '__all__'


class SpecialOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecialOrder
        fields = '__all__'


class MilestoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Milestone
        fields = '__all__'


class ProgressLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgressLog
        fields = '__all__'


class WriterBonusSerializer(serializers.ModelSerializer):
    class Meta:
        model = WriterBonus
        fields = '__all__'