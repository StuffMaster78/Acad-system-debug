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
    is_required_for_approval = models.BooleanField(
        default=False,
        help_text=(
            "Block application approval until the writer has a passing attempt for this quiz."
        ),
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


class AttemptStatus(models.TextChoices):
    IN_PROGRESS     = "in_progress",     _("In progress")
    SUBMITTED       = "submitted",       _("Submitted — awaiting review")
    PASSED          = "passed",          _("Passed")
    FAILED          = "failed",          _("Failed")
    PENDING_REVIEW  = "pending_review",  _("Pending manual review (essay)")


class WriterTestAttempt(models.Model):
    """
    One attempt by a writer to complete a VettingQuiz.

    MCQ/true-false quizzes are auto-scored on submission.
    Essay quizzes go to PENDING_REVIEW for staff to grade manually.
    """

    quiz = models.ForeignKey(
        VettingQuiz,
        on_delete=models.CASCADE,
        related_name="attempts",
    )
    writer = models.ForeignKey(
        "writer_management.WriterProfile",
        on_delete=models.CASCADE,
        related_name="quiz_attempts",
    )
    attempt_number = models.PositiveSmallIntegerField(default=1)
    status = models.CharField(
        max_length=20,
        choices=AttemptStatus.choices,
        default=AttemptStatus.IN_PROGRESS,
    )

    # Score (set on submission for auto-scored quizzes)
    score = models.DecimalField(
        max_digits=5, decimal_places=2,
        null=True, blank=True,
        help_text="Percentage score 0–100. Null until graded.",
    )
    passed = models.BooleanField(
        null=True, blank=True,
        help_text="Null until scored.",
    )

    # Manual review (essay quizzes)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="reviewed_attempts",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewer_notes = models.TextField(blank=True)

    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-started_at"]
        unique_together = [["quiz", "writer", "attempt_number"]]
        verbose_name = "Writer Test Attempt"
        indexes = [
            models.Index(fields=["writer", "status"]),
            models.Index(fields=["quiz", "status"]),
        ]

    def __str__(self) -> str:
        return f"{self.writer} — {self.quiz.title} attempt #{self.attempt_number}"

    def auto_score(self) -> None:
        """
        Score all MCQ / true-false answers and set score + passed + status.
        Call after all WriterTestAnswer rows are saved.
        Does nothing for essay quizzes (those require manual review).
        """
        if self.quiz.quiz_type == QuizType.ESSAY:
            self.status = AttemptStatus.PENDING_REVIEW
            self.save(update_fields=["status", "updated_at"])
            return

        answers = self.answers.select_related("question", "selected_choice")
        total_points = sum(a.question.points for a in answers if a.question.is_active)
        if total_points == 0:
            self.score = 0
            self.passed = False
            self.status = AttemptStatus.FAILED
            self.save(update_fields=["score", "passed", "status", "updated_at"])
            return

        earned = sum(
            a.question.points
            for a in answers
            if a.is_correct and a.question.is_active
        )
        pct = (earned / total_points) * 100
        self.score = round(pct, 2)
        self.passed = pct >= self.quiz.pass_score
        self.status = AttemptStatus.PASSED if self.passed else AttemptStatus.FAILED
        self.save(update_fields=["score", "passed", "status", "updated_at"])


class WriterTestAnswer(models.Model):
    """One question's answer within a WriterTestAttempt."""

    attempt = models.ForeignKey(
        WriterTestAttempt,
        on_delete=models.CASCADE,
        related_name="answers",
    )
    question = models.ForeignKey(
        VettingQuestion,
        on_delete=models.PROTECT,
        related_name="answers",
    )
    # MCQ / true-false: writer picks a choice
    selected_choice = models.ForeignKey(
        VettingChoice,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="answers",
    )
    # Essay: writer types a response AND/OR uploads a file
    essay_response = models.TextField(blank=True)
    # UUID of the ManagedFile from files_management (optional, essay questions only)
    essay_file_id = models.CharField(max_length=36, blank=True, default="",
        help_text="UUID of the uploaded essay file (files_management.ManagedFile).")
    essay_file_name = models.CharField(max_length=255, blank=True, default="",
        help_text="Original filename stored for display.")

    # Auto-set for MCQ/T-F; set by reviewer for essay
    is_correct = models.BooleanField(null=True, blank=True)
    points_earned = models.DecimalField(
        max_digits=5, decimal_places=2,
        default=0,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [["attempt", "question"]]
        verbose_name = "Writer Test Answer"

    def __str__(self) -> str:
        return f"Attempt {self.attempt_id} Q{self.question_id}"
