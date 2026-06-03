"""
Writer Vetting — quiz and essay question bank.

Admins build quizzes composed of multiple-choice, true/false, or open-ended
essay questions. Quizzes are used during writer onboarding to vet candidates
before their application is approved.

Quiz types
----------
grammar        MCQ / true-false questions assessing grammar and style.
               Machine-scorable. Linked to grammar_test runtime config.

subject        MCQ / true-false on a specific subject area.

essay          Open-ended writing prompts reviewed manually by staff.
"""
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class QuizType(models.TextChoices):
    GRAMMAR = "grammar", _("Grammar test")
    SUBJECT = "subject", _("Subject knowledge")
    ESSAY   = "essay",   _("Essay / writing prompt")


class QuestionType(models.TextChoices):
    MULTIPLE_CHOICE = "multiple_choice", _("Multiple choice")
    TRUE_FALSE      = "true_false",      _("True / False")
    ESSAY           = "essay",           _("Open-ended essay")


class VettingQuiz(models.Model):
    """A named quiz belonging to a tenant website."""

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="vetting_quizzes",
    )
    quiz_type = models.CharField(
        max_length=20,
        choices=QuizType.choices,
        default=QuizType.GRAMMAR,
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    instructions = models.TextField(
        blank=True,
        help_text="Instructions shown to the writer before they start.",
    )

    # Scoring (not applicable to essay quizzes)
    pass_score = models.PositiveSmallIntegerField(
        default=75,
        help_text="Minimum percentage score to pass (MCQ/true-false quizzes only).",
    )
    time_limit_minutes = models.PositiveSmallIntegerField(
        default=30,
        help_text="0 = no time limit.",
    )
    max_attempts = models.PositiveSmallIntegerField(
        default=3,
        help_text="0 = unlimited.",
    )

    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="created_vetting_quizzes",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["quiz_type", "title"]
        verbose_name = "Vetting Quiz"
        verbose_name_plural = "Vetting Quizzes"
        indexes = [
            models.Index(fields=["website", "quiz_type", "is_active"]),
        ]

    def __str__(self) -> str:
        return f"{self.title} ({self.get_quiz_type_display()})"

    @property
    def question_count(self) -> int:
        return self.questions.filter(is_active=True).count()


class VettingQuestion(models.Model):
    """A single question inside a quiz."""

    quiz = models.ForeignKey(
        VettingQuiz,
        on_delete=models.CASCADE,
        related_name="questions",
    )
    question_type = models.CharField(
        max_length=20,
        choices=QuestionType.choices,
        default=QuestionType.MULTIPLE_CHOICE,
    )
    text = models.TextField(help_text="Question text shown to the writer.")
    explanation = models.TextField(
        blank=True,
        help_text="Explanation shown after answering (optional — good for learning).",
    )
    points = models.PositiveSmallIntegerField(
        default=1,
        help_text="Points awarded for a correct answer (MCQ/true-false).",
    )
    order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Vetting Question"

    def __str__(self) -> str:
        return f"Q{self.order}: {self.text[:60]}"


class VettingChoice(models.Model):
    """An answer choice for a multiple-choice or true/false question."""

    question = models.ForeignKey(
        VettingQuestion,
        on_delete=models.CASCADE,
        related_name="choices",
    )
    text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Answer Choice"

    def __str__(self) -> str:
        tick = "✓" if self.is_correct else "✗"
        return f"{tick} {self.text[:60]}"
