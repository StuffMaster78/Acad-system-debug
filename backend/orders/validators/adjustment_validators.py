from __future__ import annotations

from django.core.exceptions import ValidationError

from orders.models.orders.constants import (
    ORDER_ADJUSTMENT_KIND_EXTRA_SERVICE,
    ORDER_ADJUSTMENT_KIND_SCOPE_INCREMENT,
)



class AdjustmentValidator:
    """
    Validator for order adjustments. It validates the adjustment request
    inputs.

    Services should call this before creating or updating an
    order adjustment request to ensure the request is valid.
    """

    @staticmethod
    def validate_scope_increment(
        *,
        current_quantity: int,
        requested_quantity: int,
        unit_type: str,
    ) -> None:
        """
        Validate a scope increment adjustment request.

        It checks that the requested quantity is greater than the current
        quantity for scope increment adjustments, and that the unit type
        is valid.

        Args:
            current_quantity: The current quantity of the order item.
            requested_quantity: The requested quantity in the adjustment.
            unit_type: The unit type of the order item.
        Raises:
            ValidationError: If the requested quantity is not greater than
                the current quantity, or if the unit type is invalid
                for scope increment adjustments.
        """
        if not unit_type:
            raise ValidationError(
                "Unit type is required for scope increment adjustments."
            )
        
        if requested_quantity <= current_quantity:
            raise ValidationError(
                "Requested quantity must be greater than current quantity for scope increment adjustments."
            )



    @staticmethod
    def validate_counter_quantity(
        *,
        current_quantity: int,
        requested_quantity: int,
        countered_quantity: int,
    ) -> None:
        """
        Validate that the countered quantity does not exceed the requested quantity.
        Args:
            current_quantity: The current quantity of the order item.
            requested_quantity: The requested quantity in the adjustment.
            countered_quantity: The quantity proposed in the counteroffer.
        Raises:
            ValidationError: If the countered quantity exceeds the requested quantity.
        """
        if countered_quantity < 0:
            raise ValidationError(
                "Countered quantity cannot be negative."
            )
        if requested_quantity < 0:
            raise ValidationError(
                "Requested quantity cannot be negative."
            )
        
        if countered_quantity > current_quantity:
            raise ValidationError(
                "Countered quantity cannot exceed current quantity."
            )
        
        if countered_quantity > requested_quantity:
            raise ValidationError(
                "Countered quantity cannot exceed requested quantity."
            )


    @staticmethod
    def validate_extra_service(
        *,
        extra_service_code: str,
    ) -> None:
        """
        Validate that the extra service code is provided for extra service adjustments.
        Args:
            extra_service_code: The code of the extra service being added.
            
            Raises:
                ValidationError: If the extra service code is not provided for
                extra service adjustments.
        """
        if not extra_service_code:
            raise ValidationError(
                "Extra service code is required for extra service adjustments."
            )


    @staticmethod
    def validate_adjustment_kind(
        *,
        adjustment_kind: str,
    ) -> None:
        """
        Validate that the adjustment kind is one of the allowed kinds.
        Args:
            adjustment_kind: The kind of the adjustment being requested.
        Raises:
            ValidationError: If the adjustment kind is not recognized.
        """
        allowed_kinds = {
            ORDER_ADJUSTMENT_KIND_SCOPE_INCREMENT,
            ORDER_ADJUSTMENT_KIND_EXTRA_SERVICE,
        }
        if adjustment_kind not in allowed_kinds:
            raise ValidationError(
                f"Invalid adjustment kind: {adjustment_kind}. Allowed kinds are: {allowed_kinds}."
            )
