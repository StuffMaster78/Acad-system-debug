from __future__ import annotations

from django.db import models

from websites.models.websites import Website


class BillingBaseModel(models.Model):
    """
    Provide a shared base model for billing domain records.

    This base model enforces tenant scoping and timestamp tracking for
    all billing records.
    """

    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="%(class)s_billing_records",
        help_text="Tenant context that owns this billing record.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the record was created.",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the record was last updated.",
    )

    class Meta:
        """
        Mark this model as abstract.

        Concrete billing models should inherit from this base.
        """

        abstract = True