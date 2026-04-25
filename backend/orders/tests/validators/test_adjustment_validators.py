from __future__ import annotations

from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from orders.validators.adjustment_validators import AdjustmentValidator


class AdjustmentValidatorTests(SimpleTestCase):
    def test_validate_scope_increment_passes(self) -> None:
        AdjustmentValidator.validate_scope_increment(
            current_quantity=4,
            requested_quantity=6,
            unit_type="page",
        )

    def test_validate_scope_increment_requires_unit_type(self) -> None:
        with self.assertRaises(ValidationError):
            AdjustmentValidator.validate_scope_increment(
                current_quantity=4,
                requested_quantity=6,
                unit_type="",
            )

    def test_validate_scope_increment_rejects_non_increment(self) -> None:
        with self.assertRaises(ValidationError):
            AdjustmentValidator.validate_scope_increment(
                current_quantity=4,
                requested_quantity=4,
                unit_type="page",
            )

    def test_validate_counter_quantity_passes(self) -> None:
        AdjustmentValidator.validate_counter_quantity(
            current_quantity=4,
            requested_quantity=6,
            countered_quantity=5,
        )

    def test_validate_counter_quantity_must_exceed_current(self) -> None:
        with self.assertRaises(ValidationError):
            AdjustmentValidator.validate_counter_quantity(
                current_quantity=4,
                requested_quantity=6,
                countered_quantity=4,
            )

    def test_validate_counter_quantity_cannot_exceed_requested(self) -> None:
        with self.assertRaises(ValidationError):
            AdjustmentValidator.validate_counter_quantity(
                current_quantity=4,
                requested_quantity=6,
                countered_quantity=7,
            )

    def test_validate_extra_service_requires_code(self) -> None:
        with self.assertRaises(ValidationError):
            AdjustmentValidator.validate_extra_service(
                extra_service_code="",
            )

    def test_validate_extra_service_passes(self) -> None:
        AdjustmentValidator.validate_extra_service(
            extra_service_code="speaker_notes",
        )