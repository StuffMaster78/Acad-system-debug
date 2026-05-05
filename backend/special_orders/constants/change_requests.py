from __future__ import annotations


class ChangeRequestStatus:
    """
    Lifecycle for special order scope changes.
    """

    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    QUOTED = "quoted"
    ACCEPTED = "accepted"
    CANCELLED = "cancelled"

    CHOICES = [
        (PENDING, "Pending"),
        (UNDER_REVIEW, "Under review"),
        (APPROVED, "Approved"),
        (REJECTED, "Rejected"),
        (QUOTED, "Quoted"),
        (ACCEPTED, "Accepted"),
        (CANCELLED, "Cancelled"),
    ]


class ChangeRequestPricingImpact:
    """
    Whether a change request affects price.
    """

    NO_CHARGE = "no_charge"
    ADDITIONAL_CHARGE = "additional_charge"
    PRICE_REDUCTION = "price_reduction"

    CHOICES = [
        (NO_CHARGE, "No charge"),
        (ADDITIONAL_CHARGE, "Additional charge"),
        (PRICE_REDUCTION, "Price reduction"),
    ]