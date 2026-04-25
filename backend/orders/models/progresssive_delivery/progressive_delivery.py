from __future__ import annotations

from django.db import models


class OrderProgressivePlan(models.Model):
    """
    Defines progressive delivery structure for an order.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="progressive_plans",
    )
    order = models.OneToOneField(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="progressive_plan",
    )

    is_required = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)


class OrderMilestone(models.Model):
    """
    Represents a milestone (draft checkpoint).
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
    )
    plan = models.ForeignKey(
        OrderProgressivePlan,
        on_delete=models.CASCADE,
        related_name="milestones",
    )
    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.CASCADE,
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    due_at = models.DateTimeField()

    percentage = models.PositiveIntegerField(
        help_text="Progress percentage (e.g. 30, 60, 100)"
    )

    is_completed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)