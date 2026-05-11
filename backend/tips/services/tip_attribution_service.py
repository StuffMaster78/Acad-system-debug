from __future__ import annotations

from tips.enums.tip_context_type import TipContextType
from tips.exceptions import TipValidationError
from tips.models.tip_attribution import TipAttribution


class TipAttributionService:
    """
    Ensures tip context integrity and persistence.

    Responsibilities:
    - validate context consistency
    - persist correct relational attribution
    """

    # ------------------------------------------------------------ #
    # VALIDATION
    # ------------------------------------------------------------ #

    @staticmethod
    def validate(
        *,
        context_type: str,
        order_id=None,
        special_order_id=None,
        class_purchase_id=None,
        reason: str = "",
    ) -> None:

        if (
            context_type == TipContextType.ORDER
            and not order_id
        ):
            raise TipValidationError(
                "Order attribution requires order_id."
            )

        if (
            context_type
            == TipContextType.SPECIAL_ORDER
            and not special_order_id
        ):
            raise TipValidationError(
                "Special order attribution requires ID."
            )

        if (
            context_type == TipContextType.CLASS
            and not class_purchase_id
        ):
            raise TipValidationError(
                "Class attribution requires ID."
            )

        if (
            context_type == TipContextType.OTHER
            and not reason
        ):
            raise TipValidationError(
                "Reason is required for OTHER context."
            )

    # ------------------------------------------------------------ #
    # CREATION
    # ------------------------------------------------------------ #

    @staticmethod
    def create_attribution(
        *,
        tip,
        context_type: str,
        order_id: int | None = None,
        special_order_id: int | None = None,
        class_purchase_id: int | None = None,
        reason: str = "",
    ) -> TipAttribution:
        """
        Persist structured attribution safely.
        """

        return TipAttribution.objects.create(
            tip=tip,
            context_type=context_type,
            order_id=order_id,
            special_order_id=special_order_id,
            class_purchase_id=class_purchase_id,
            reason=reason,
        )