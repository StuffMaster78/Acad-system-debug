from __future__ import annotations

from django.conf import settings
from django.db import models


class QAChecklistTemplate(models.Model):
    """
    Reusable QA checklist template used by editors/admins when reviewing
    delivered orders before client approval.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="qa_checklist_templates",
        null=True,
        blank=True,
        help_text="Null = platform-wide template.",
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    is_default = models.BooleanField(
        default=False,
        help_text="Automatically attached to new QA review tasks.",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_qa_templates",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_default", "name"]

    def __str__(self) -> str:
        return self.name


class QAChecklistItem(models.Model):
    """A single check within a QA checklist template."""

    CATEGORY_CHOICES = [
        ("content", "Content quality"),
        ("formatting", "Formatting & citations"),
        ("instructions", "Instructions followed"),
        ("plagiarism", "Originality"),
        ("delivery", "Delivery & files"),
        ("other", "Other"),
    ]

    template = models.ForeignKey(
        QAChecklistTemplate,
        on_delete=models.CASCADE,
        related_name="items",
    )
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="content")
    text = models.CharField(max_length=500)
    is_required = models.BooleanField(default=True, help_text="Blocking — reviewer cannot pass without checking this.")
    display_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["display_order", "id"]

    def __str__(self) -> str:
        return self.text[:80]


class QAChecklistResult(models.Model):
    """
    A completed QA review for a specific order.
    Records which items were checked, any notes, and the final pass/fail.
    """

    VERDICT_CHOICES = [
        ("passed", "Passed"),
        ("failed", "Failed — return to writer"),
        ("passed_with_notes", "Passed with notes"),
    ]

    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="qa_results",
    )
    template = models.ForeignKey(
        QAChecklistTemplate,
        on_delete=models.PROTECT,
        related_name="results",
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="qa_reviews",
    )
    checked_items = models.JSONField(
        default=list,
        help_text="List of QAChecklistItem PKs that passed.",
    )
    verdict = models.CharField(max_length=30, choices=VERDICT_CHOICES, null=True, blank=True)
    notes = models.TextField(blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["order", "reviewer"]),
        ]

    @property
    def pass_rate(self) -> float:
        total = self.template.items.count()
        return len(self.checked_items) / total if total else 0.0

    def __str__(self) -> str:
        return f"QA #{self.pk} for order #{self.order_id} — {self.verdict or 'in progress'}"
