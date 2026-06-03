from rest_framework import serializers
from .models import VettingChoice, VettingQuestion, VettingQuiz


class VettingChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = VettingChoice
        fields = ["id", "text", "is_correct", "order"]


class VettingQuestionSerializer(serializers.ModelSerializer):
    choices = VettingChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = VettingQuestion
        fields = [
            "id", "quiz", "question_type", "text", "explanation",
            "points", "order", "is_active", "choices",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class VettingQuizListSerializer(serializers.ModelSerializer):
    question_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = VettingQuiz
        fields = [
            "id", "quiz_type", "title", "description",
            "pass_score", "time_limit_minutes", "max_attempts",
            "is_active", "question_count", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class VettingQuizDetailSerializer(VettingQuizListSerializer):
    questions = VettingQuestionSerializer(many=True, read_only=True)

    class Meta(VettingQuizListSerializer.Meta):
        fields = VettingQuizListSerializer.Meta.fields + [
            "instructions", "questions",
        ]


class VettingChoiceWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = VettingChoice
        fields = ["id", "text", "is_correct", "order"]


class VettingQuestionWriteSerializer(serializers.ModelSerializer):
    choices = VettingChoiceWriteSerializer(many=True, required=False)

    class Meta:
        model = VettingQuestion
        fields = [
            "id", "quiz", "question_type", "text", "explanation",
            "points", "order", "is_active", "choices",
        ]

    def create(self, validated_data):
        choices_data = validated_data.pop("choices", [])
        question = VettingQuestion.objects.create(**validated_data)
        for c in choices_data:
            VettingChoice.objects.create(question=question, **c)
        return question

    def update(self, instance, validated_data):
        choices_data = validated_data.pop("choices", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if choices_data is not None:
            # Replace choices wholesale
            instance.choices.all().delete()
            for c in choices_data:
                c.pop("id", None)
                VettingChoice.objects.create(question=instance, **c)

        return instance
