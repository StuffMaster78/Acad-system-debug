from __future__ import annotations

from typing import TYPE_CHECKING, Optional, cast

from django.db.models import QuerySet

from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from orders.enums import (
    OrderStatus,
    OrderVisibilityMode,
    PreferredWriterStatus,
)
from websites.models.websites import Website
if TYPE_CHECKING:
    from orders.models.orders.order_assignment import OrderAssignment


class OrderQuerySet(models.QuerySet):
    """
    Provide reusable queryset helpers for orders.
    """

    def active(self) -> "OrderQuerySet":
        """
        Return orders that are not soft deleted.

        Returns:
            OrderQuerySet:
                Queryset excluding soft deleted records.
        """
        return self.filter(is_deleted=False)

    def with_deleted(self) -> "OrderQuerySet":
        """
        Return all orders, including soft deleted ones.

        Returns:
            OrderQuerySet:
                Unfiltered queryset.
        """
        return self.all()

    def deleted_only(self) -> "OrderQuerySet":
        """
        Return only soft deleted orders.

        Returns:
            OrderQuerySet:
                Queryset containing soft deleted records.
        """
        return self.filter(is_deleted=True)


class OrderManager(models.Manager):
    """
    Default manager that excludes soft deleted orders.
    """

    def get_queryset(self) -> OrderQuerySet:
        """
        Return the default active queryset.

        Returns:
            OrderQuerySet:
                Queryset excluding soft deleted orders.
        """
        return OrderQuerySet(
            model=self.model,
            using=self._db,
        ).active()

    def with_deleted(self) -> OrderQuerySet:
        """
        Return all orders, including soft deleted ones.

        Returns:
            OrderQuerySet:
                Unfiltered queryset.
        """
        return OrderQuerySet(
            model=self.model,
            using=self._db,
        ).with_deleted()

    def deleted_only(self) -> OrderQuerySet:
        """
        Return only soft deleted orders.

        Returns:
            OrderQuerySet:
                Queryset containing only soft deleted orders.
        """
        return OrderQuerySet(
            model=self.model,
            using=self._db,
        ).deleted_only()

class Order(models.Model):
    """
    Represent a client order within a tenant website.

    Responsibilities:
        1. Store durable order identity and workflow state.
        2. Hold summary commercial fields for read efficiency.
        3. Reference client, writer, and configuration models.

    Non responsibilities:
        1. It does not calculate prices in save().
        2. It does not mutate paid scope directly.
        3. It does not interpret payment callbacks.
        4. It does not post to ledger or wallet systems.
    """

    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="orders",
        help_text="Tenant website that owns this order.",
    )
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders_as_client",
        null=True,
        blank=True,
        help_text="Client who placed the order.",
    )
    topic = models.CharField(
        max_length=255,
        help_text="Topic or working title of the order.",
    )
    paper_type = models.ForeignKey(
        "order_configs.PaperType",
        on_delete=models.PROTECT,
        related_name="orders",
        help_text="Requested paper type.",
    )
    academic_level = models.ForeignKey(
        "order_configs.AcademicLevel",
        on_delete=models.PROTECT,
        related_name="orders",
        null=True,
        blank=True,
        help_text="Requested academic level.",
    )
    formatting_style = models.ForeignKey(
        "order_configs.FormattingandCitationStyle",
        on_delete=models.SET_NULL,
        related_name="orders",
        null=True,
        blank=True,
        help_text="Formatting or citation style.",
    )
    subject = models.ForeignKey(
        "order_configs.Subject",
        on_delete=models.SET_NULL,
        related_name="orders",
        null=True,
        blank=True,
        help_text="Academic subject area.",
    )
    type_of_work = models.ForeignKey(
        "order_configs.TypeOfWork",
        on_delete=models.SET_NULL,
        related_name="orders",
        null=True,
        blank=True,
        help_text="Requested type of work.",
    )
    english_type = models.ForeignKey(
        "order_configs.EnglishType",
        on_delete=models.SET_NULL,
        related_name="orders",
        null=True,
        blank=True,
        help_text="Requested English variant.",
    )
    writer_level = models.ForeignKey(
        "pricing_configs.WriterLevelOptionConfig",
        on_delete=models.SET_NULL,
        related_name="orders",
        null=True,
        blank=True,
        help_text="Requested writer level option.",
    )
    discount = models.ForeignKey(
        "discounts.Discount",
        on_delete=models.SET_NULL,
        related_name="orders",
        null=True,
        blank=True,
        help_text="Discount applied to the order, if any.",
    )
    discount_code_used = models.CharField(
        max_length=100,
        blank=True,
        help_text="Discount code applied to the order.",
    )
    is_follow_up = models.BooleanField(
        default=False,
        help_text="Whether this order is a follow up order.",
    )
    previous_order = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        related_name="follow_up_orders",
        null=True,
        blank=True,
        help_text="Previous order this order follows up on.",
    )
    status = models.CharField(
        max_length=32,
        choices=OrderStatus.choices,
        default=OrderStatus.CREATED,
        help_text="Current order workflow status.",
    )
    visibility_mode = models.CharField(
        max_length=32,
        choices=OrderVisibilityMode.choices,
        default=OrderVisibilityMode.HIDDEN,
        help_text="How the order is exposed to eligible writers.",
    )
    preferred_writer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="preferred_orders",
        null=True,
        blank=True,
        help_text="Preferred writer chosen for the order.",
    )
    preferred_writer_status = models.CharField(
        max_length=32,
        choices=PreferredWriterStatus.choices,
        default=PreferredWriterStatus.NOT_REQUESTED,
        help_text="Preferred writer routing status.",
    )
    preferred_writer_fee_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Additional fee charged for preferred writer routing.",
    )
    flags = models.JSONField(
        default=list,
        blank=True,
        help_text="Structured list of order flags.",
    )
    client_deadline = models.DateTimeField(
        help_text="Deadline visible to the client.",
    )
    writer_deadline = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Internal writer deadline.",
    )
    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Current commercial total for the order.",
    )
    writer_compensation = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Current writer compensation summary.",
    )
    is_paid = models.BooleanField(
        default=False,
        help_text="Whether the base order receivable is fully settled.",
    )
    is_urgent = models.BooleanField(
        default=False,
        help_text="Whether the order is operationally urgent.",
    )
    requires_editing = models.BooleanField(
        null=True,
        blank=True,
        default=None,
        help_text="Editing override. None means use policy defaults.",
    )
    editing_skip_reason = models.CharField(
        max_length=255,
        blank=True,
        help_text="Reason editing was skipped when applicable.",
    )
    created_by_admin = models.BooleanField(
        default=False,
        help_text="Whether the order was created by staff.",
    )
    order_instructions = models.TextField(
        help_text="Detailed instructions for the order.",
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the order was operationally completed.",
    )
    completed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="completed_orders",
        null=True,
        blank=True,
        help_text="User who completed the order workflow, if completed manually.",
    )
    completion_notes = models.TextField(
        blank=True,
        help_text="Notes recorded when the order was completed.",
    )
    submitted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the final deliverable was submitted.",
    )
    external_contact_name = models.CharField(
        max_length=255,
        blank=True,
        help_text="External contact name for unattributed orders.",
    )
    external_contact_email = models.EmailField(
        blank=True,
        help_text="External contact email for unattributed orders.",
    )
    external_contact_phone = models.CharField(
        max_length=20,
        blank=True,
        help_text="External contact phone for unattributed orders.",
    )
    allow_unpaid_access = models.BooleanField(
        default=False,
        help_text="Whether access is allowed before payment.",
    )
    is_deleted = models.BooleanField(
        default=False,
        help_text="Soft delete flag.",
    )
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the order was soft deleted.",
    )
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="deleted_orders",
        null=True,
        blank=True,
        help_text="Actor who soft deleted the order.",
    )
    delete_reason = models.CharField(
        max_length=255,
        blank=True,
        help_text="Reason recorded for soft deletion.",
    )
    restored_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the order was restored.",
    )
    restored_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="restored_orders",
        null=True,
        blank=True,
        help_text="Actor who restored the order.",
    )
    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
    )
    cancelled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="cancelled_orders",
    )
    cancellation_reason = models.TextField(
        blank=True,
        default="",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the order was created.",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the order was last updated.",
    )
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the order was explicitly or automatically approved.",
    )

    archived_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the order was archived.",
    )

    last_writer_acknowledged_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the assigned writer last acknowledged the order.",
    )

    objects = OrderManager()
    all_objects = models.Manager()

    class Meta:
        """
        Configure ordering, indexes, and constraints for orders.
        """

        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["website", "status"]),
            models.Index(fields=["client", "status"]),
            models.Index(fields=["visibility_mode", "status"]),
            models.Index(fields=["preferred_writer", "status"]),
            models.Index(fields=["status", "is_paid"]),
            models.Index(fields=["website", "is_deleted"]),
            models.Index(fields=["created_at"]),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(total_price__gte=0),
                name="orders_order_total_price_gte_zero",
            ),
            models.CheckConstraint(
                condition=models.Q(writer_compensation__gte=0),
                name="orders_order_writer_comp_gte_zero",
            ),
            models.CheckConstraint(
                condition=models.Q(preferred_writer_fee_amount__gte=0),
                name="orders_order_pref_fee_gte_zero",
            ),
        ]

    def __str__(self) -> str:
        """
        Return a readable order description.

        Returns:
            str:
                Human readable order representation.
        """
        return f"Order #{self.pk} {self.topic}"

    @property
    def status_enum(self) -> OrderStatus:
        """
        Return the current status as an OrderStatus enum.

        Returns:
            OrderStatus:
                Enum representation of the current status.
        """
        return OrderStatus(self.status)

    @property
    def active_flags(self) -> list[str]:
        """
        Return stored order flags as a list.

        Returns:
            list[str]:
                Flags stored on the order.
        """
        return list(self.flags or [])

    @property
    def current_assignment(self) -> Optional[OrderAssignment]:
        """
        Return the current active assignment for the order.

        Returns:
            Optional[OrderAssignment]:
                Current active assignment when present, otherwise None.
        """
        assignments = cast(
            "QuerySet[OrderAssignment]",
            getattr(self, "assignments"),
        )
        return assignments.filter(
            is_current=True,
        ).select_related("writer").first()
    
    @property
    def assigned_writer(self):
        """
        Return the current assigned writer for compatibility.

        Returns:
            users.User | None:
                Writer on the current active assignment, if any.
        """
        current = self.current_assignment
        if current is None:
            return None
        return current.writer

    def clean(self) -> None:
        """
        Validate order level invariants.

        Raises:
            ValidationError:
                Raised when model invariants are violated.
        """
        if self.deleted_at is not None and not self.is_deleted:
            raise ValidationError(
                "deleted_at cannot be set when is_deleted is False."
            )

        if self.restored_at is not None and self.is_deleted:
            raise ValidationError(
                "restored_at cannot be set while order is deleted."
            )

        if self.client is not None and self.website is not None:
            client_website_id = getattr(self.client, "website_id", None)
            if client_website_id is not None:
                if client_website_id != self.website.pk:
                    raise ValidationError(
                        "Client website must match order website."
                    )

        if self.preferred_writer is not None and self.website is not None:
            writer_website_id = getattr(
                self.preferred_writer,
                "website_id",
                None,
            )
            if writer_website_id is not None:
                if writer_website_id != self.website.pk:
                    raise ValidationError(
                        "Assigned writer website must match order website."
                    )