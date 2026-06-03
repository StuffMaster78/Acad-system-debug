from rest_framework import serializers
from .models import VettingChoice, VettingQuestion, VettingQuiz, WriterTestAttempt, WriterTestAnswer


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


# ── Writer-facing serializers ─────────────────────────────────────────────────

class WriterQuizChoiceSerializer(serializers.ModelSerializer):
    """Choices shown to writer — hides is_correct until after submission."""
    class Meta:
        model = VettingChoice
        fields = ["id", "text", "order"]


class WriterQuizQuestionSerializer(serializers.ModelSerializer):
    choices = WriterQuizChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = VettingQuestion
        fields = ["id", "question_type", "text", "order", "points", "choices"]


class WriterQuizSerializer(serializers.ModelSerializer):
    """Quiz card shown in the writer's vetting dashboard (no questions yet)."""
    question_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = VettingQuiz
        fields = [
            "id", "quiz_type", "title", "description", "instructions",
            "pass_score", "time_limit_minutes", "max_attempts",
            "question_count",
        ]


class WriterQuizDetailSerializer(WriterQuizSerializer):
    """Full quiz with questions — shown when starting/continuing an attempt."""
    questions = WriterQuizQuestionSerializer(many=True, read_only=True)

    class Meta(WriterQuizSerializer.Meta):
        fields = WriterQuizSerializer.Meta.fields + ["questions"]


class AttemptAnswerSerializer(serializers.ModelSerializer):
    """One answer row returned inside an attempt."""
    question_text = serializers.CharField(source="question.text", read_only=True)
    question_type = serializers.CharField(source="question.question_type", read_only=True)
    explanation = serializers.CharField(source="question.explanation", read_only=True)

    class Meta:
        model = WriterTestAnswer
        fields = [
            "id", "question", "question_text", "question_type",
            "selected_choice", "essay_response",
            "is_correct", "points_earned", "explanation",
        ]


class WriterAttemptSerializer(serializers.ModelSerializer):
    """Attempt summary — shown in the quiz list."""
    quiz_title = serializers.CharField(source="quiz.title", read_only=True)
    quiz_type  = serializers.CharField(source="quiz.quiz_type", read_only=True)
    pass_score = serializers.IntegerField(source="quiz.pass_score", read_only=True)

    class Meta:
        model = WriterTestAttempt
        fields = [
            "id", "quiz", "quiz_title", "quiz_type", "pass_score",
            "attempt_number", "status", "score", "passed",
            "started_at", "submitted_at", "reviewer_notes",
        ]


class WriterAttemptDetailSerializer(WriterAttemptSerializer):
    """Full attempt with answers — shown after submission."""
    answers = AttemptAnswerSerializer(many=True, read_only=True)

    class Meta(WriterAttemptSerializer.Meta):
        fields = WriterAttemptSerializer.Meta.fields + ["answers"]


class SubmitAnswerSerializer(serializers.Serializer):
    """One answer in the submission payload."""
    question_id      = serializers.IntegerField()
    selected_choice_id = serializers.IntegerField(required=False, allow_null=True)
    essay_response   = serializers.CharField(required=False, allow_blank=True, default="")
