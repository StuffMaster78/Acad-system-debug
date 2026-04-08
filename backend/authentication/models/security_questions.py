from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.db import models
from django.utils.translation import gettext_lazy as _


class SecurityQuestion(models.Model):
    """
    Predefined security questions that users can choose from.
    """

    question_text = models.CharField(
        max_length=500,
        unique=True,
        help_text=_("The security question text."),
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_("Whether this question is available."),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["question_text"]
        verbose_name = _("Security Question")
        verbose_name_plural = _("Security Questions")

    def __str__(self) -> str:
        return self.question_text


class UserSecurityQuestion(models.Model):
    """
    Store a user's selected recovery question and hashed answer.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="security_questions",
        help_text=_("User who owns this recovery question."),
    )
    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="user_security_questions",
        help_text=_("Website context."),
    )
    question = models.ForeignKey(
        SecurityQuestion,
        on_delete=models.CASCADE,
        related_name="user_questions",
        help_text=_("Selected recovery question."),
    )
    answer_hash = models.CharField(
        max_length=255,
        help_text=_("Hashed normalized answer."),
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_("Whether this question is active."),
    )
    failed_attempts = models.PositiveIntegerField(
        default=0,
        help_text=_("Number of failed verification attempts."),
    )
    last_verified_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("Last successful verification time."),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "website", "question"],
                name="unique_security_question_per_user_website_question",
            ),
        ]
        indexes = [
            models.Index(fields=["user", "website", "is_active"]),
        ]
        verbose_name = _("User Security Question")
        verbose_name_plural = _("User Security Questions")

    @staticmethod
    def normalize_answer(answer: str) -> str:
        """
        Normalize an answer before hashing or verification.
        """
        return " ".join(answer.strip().lower().split())

    def set_answer(self, answer: str) -> None:
        """
        Normalize and hash the answer.
        """
        normalized = self.normalize_answer(answer)
        self.answer_hash = make_password(normalized)

    def verify_answer(self, answer: str) -> bool:
        """
        Verify a normalized answer against the stored hash.
        """
        normalized = self.normalize_answer(answer)
        return check_password(normalized, self.answer_hash)

    def get_question_text(self) -> str:
        """
        Return the question text.
        """
        return self.question.question_text

    def __str__(self) -> str:
        return f"Security question for {self.user.email}"