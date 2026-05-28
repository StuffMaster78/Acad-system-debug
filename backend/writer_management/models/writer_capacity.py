"""
writer_management/models/writer_capacity.py

Runtime workload state for a writer.

This model exists separately from WriterProfile because:
    - workload changes frequently
    - assignment counters are hot-write fields
    - operational state should not pollute identity models

Responsibilities:
    - assignment eligibility gates
    - active workload counters
    - workload overrides
    - assignment preferences

Business logic does NOT live here.
Services own:
    - eligibility resolution
    - assignment routing
    - workload balancing
    - auto-assignment decisions
"""

from django.db import models


class WriterCapacity(models.Model):
    """
    Runtime workload and assignment preferences.

    Updated primarily by:
        - assignment services
        - availability services
        - discipline services
    """

    writer = models.OneToOneField(
        "writer_management.WriterProfile",
        on_delete=models.CASCADE,
        related_name="capacity",
    )

    # ============================================================
    # ASSIGNMENT ELIGIBILITY FLAGS
    # ============================================================

    can_take_orders = models.BooleanField(
        default=True,
        db_index=True,
        help_text=(
            "Platform-controlled assignment gate. "
            "Disabled during suspensions, blacklists, or restrictions."
        ),
    )

    is_accepting_orders = models.BooleanField(
        default=True,
        db_index=True,
        help_text=(
            "Writer-controlled availability toggle."
        ),
    )

    # ============================================================
    # WORKLOAD COUNTERS
    # ============================================================

    active_orders_count = models.PositiveSmallIntegerField(
        default=0,
        help_text=(
            "Cached count of active assignments."
        ),
    )

    override_max_active_orders = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text=(
            "Optional per-writer workload override."
        ),
    )

    max_orders_per_day = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text=(
            "Optional daily assignment limit."
        ),
    )

    # ============================================================
    # ASSIGNMENT PREFERENCES
    # Soft routing hints only.
    # ============================================================

    preferred_subjects = models.ManyToManyField(
        "order_configs.Subject",
        blank=True,
        related_name="preferred_writers",
    )

    preferred_types_of_work = models.ManyToManyField(
        "order_configs.TypeOfWork",
        blank=True,
        related_name="preferred_writers",
    )

    preferred_deadline_buffer_days = models.PositiveSmallIntegerField(
        default=1,
        help_text=(
            "Preferred minimum buffer before deadline."
        ),
    )

    auto_accept_orders = models.BooleanField(
        default=False,
    )

    auto_accept_preferred_only = models.BooleanField(
        default=False,
    )

    # ============================================================
    # AUDIT
    # ============================================================

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    # ============================================================
    # META
    # ============================================================

    class Meta:
        verbose_name = "Writer Capacity"
        verbose_name_plural = "Writer Capacities"

        indexes = [
            models.Index(
                fields=[
                    "can_take_orders",
                    "is_accepting_orders",
                ],
                name="writer_capacity_routing_idx",
            ),
        ]

        constraints = [
            models.CheckConstraint(
                condition=models.Q(
                    active_orders_count__gte=0,
                ),
                name="writer_capacity_active_orders_gte_0",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(
                        override_max_active_orders__isnull=True,
                    )
                    | models.Q(
                        override_max_active_orders__gte=1,
                    )
                ),
                name="writer_capacity_override_max_gte_1",
            ),
        ]

    def __str__(self) -> str:
        return f"WriterCapacity<{self.pk}>"