from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models

from class_management.constants import (
    ClassComplexityLevel,
    ClassItemType,
    ClassTaskStatus,
)


class ClassScopeAssessment(models.Model):
    """
    Summary of the expected workload for a class order.
    """

    class_order = models.OneToOneField(
        "class_management.ClassOrder",
        on_delete=models.CASCADE,
        related_name="scope_assessment",
    )

    discussion_posts_count = models.PositiveIntegerField(default=0)
    discussion_responses_count = models.PositiveIntegerField(default=0)
    quizzes_count = models.PositiveIntegerField(default=0)
    exams_count = models.PositiveIntegerField(default=0)
    assignments_count = models.PositiveIntegerField(default=0)
    research_papers_count = models.PositiveIntegerField(default=0)
    term_papers_count = models.PositiveIntegerField(default=0)
    coursework_items_count = models.PositiveIntegerField(default=0)
    projects_count = models.PositiveIntegerField(default=0)
    presentations_count = models.PositiveIntegerField(default=0)
    labs_count = models.PositiveIntegerField(default=0)

    estimated_hours = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    complexity_level = models.CharField(
        max_length=30,
        choices=ClassComplexityLevel.choices,
        default=ClassComplexityLevel.MEDIUM,
    )

    weekly_workload_notes = models.TextField(blank=True)
    grading_weight_notes = models.TextField(blank=True)
    client_scope_notes = models.TextField(blank=True)
    admin_assessment_notes = models.TextField(blank=True)

    assessed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="class_scope_assessments",
    )

    assessed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ClassScopeItem(models.Model):
    """
    A workload item inside a class order.
    """

    class_order = models.ForeignKey(
        "class_management.ClassOrder",
        on_delete=models.CASCADE,
        related_name="scope_items",
    )

    item_type = models.CharField(
        max_length=80,
        choices=ClassItemType.choices,
        db_index=True,
    )

    title = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=1)

    due_at = models.DateTimeField(null=True, blank=True)

    estimated_pages = models.PositiveIntegerField(null=True, blank=True)
    estimated_words = models.PositiveIntegerField(null=True, blank=True)
    estimated_hours = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
    )

    complexity_level = models.CharField(
        max_length=30,
        choices=ClassComplexityLevel.choices,
        default=ClassComplexityLevel.MEDIUM,
    )

    notes = models.TextField(blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_class_scope_items",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["due_at", "created_at"]
        indexes = [
            models.Index(fields=["class_order", "item_type"]),
            models.Index(fields=["due_at"]),
        ]

    def __str__(self) -> str:
        return self.title


class ClassTask(models.Model):
    """
    Track execution of an actual task from the class workload.
    """

    class_order = models.ForeignKey(
        "class_management.ClassOrder",
        on_delete=models.CASCADE,
        related_name="tasks",
    )
    scope_item = models.ForeignKey(
        "class_management.ClassScopeItem",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks",
    )

    assigned_writer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="class_tasks",
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    status = models.CharField(
        max_length=40,
        choices=ClassTaskStatus.choices,
        default=ClassTaskStatus.PENDING,
        db_index=True,
    )

    due_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    client_visible_notes = models.TextField(blank=True)
    writer_notes = models.TextField(blank=True)
    admin_internal_notes = models.TextField(blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_class_tasks",
    )
    requires_portal_work = models.BooleanField(default=False)
    writer_may_upload_to_portal = models.BooleanField(default=True)
    writer_may_download_files = models.BooleanField(default=True)
    portal_submission_required = models.BooleanField(default=False)
    portal_submitted_at = models.DateTimeField(null=True, blank=True)
    portal_submission_notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["due_at", "created_at"]
        indexes = [
            models.Index(fields=["class_order", "status"]),
            models.Index(fields=["assigned_writer", "status"]),
            models.Index(fields=["due_at"]),
        ]

    def __str__(self) -> str:
        return self.title