"""
Pricing dimension validators for the order_pricing_core app.
"""

from __future__ import annotations

from decimal import Decimal

from django.core.exceptions import ValidationError

from order_pricing_core.models import SubjectRate


def validate_positive_multiplier(
    *,
    multiplier: Decimal,
    field_name: str = "multiplier",
) -> None:
    """
    Validate that a multiplier is greater than zero.
    """
    if multiplier <= Decimal("0"):
        raise ValidationError(
            {field_name: "Multiplier must be greater than zero."}
        )


def validate_non_negative_amount(
    *,
    amount: Decimal,
    field_name: str = "amount",
) -> None:
    """
    Validate that an amount is not negative.
    """
    if amount < Decimal("0.00"):
        raise ValidationError(
            {field_name: "Amount cannot be negative."}
        )


def validate_deadline_rate(
    *,
    max_hours: int,
    multiplier: Decimal,
) -> None:
    """
    Validate deadline rate fields.
    """
    if max_hours <= 0:
        raise ValidationError(
            {"max_hours": "Max hours must be greater than zero."}
        )

    validate_positive_multiplier(multiplier=multiplier)

def validate_subject_rate(subject_rate: SubjectRate) -> None:
    """
    Validate that a subject and its category belong to same website.
    """
    if subject_rate.category.website.pk != subject_rate.website.pk:
        raise ValidationError(
            {
                "category": (
                    "Subject category must belong to the same website."
                )
            }
        )

    if subject_rate.custom_multiplier is not None:
        validate_positive_multiplier(
            multiplier=subject_rate.custom_multiplier,
            field_name="custom_multiplier",
        )