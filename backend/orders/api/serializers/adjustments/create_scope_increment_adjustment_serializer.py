from __future__ import annotations

from rest_framework import serializers

from orders.models.orders.enums import OrderAdjustmentType, OrderScopeUnitType


class CreateScopeIncrementAdjustmentSerializer(serializers.Serializer):
    """
    Validate scope increment adjustment creation.
    """

    adjustment_type = serializers.ChoiceField(
        choices=[
            OrderAdjustmentType.PAGE_INCREASE,
            OrderAdjustmentType.SLIDE_INCREASE,
            OrderAdjustmentType.DIAGRAM_INCREASE,
            OrderAdjustmentType.DESIGN_CONCEPT_INCREASE,
            OrderAdjustmentType.SCOPE_EXPANSION,
        ]
    )
    unit_type = serializers.ChoiceField(
        choices=OrderScopeUnitType.choices,
    )
    requested_quantity = serializers.IntegerField(min_value=1)
    title = serializers.CharField(max_length=200)
    description = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
    )
    writer_justification = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
    )
    client_visible_note = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
    )