from __future__ import annotations

from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import patch

from django.test import SimpleTestCase

from orders.services.progressive_delivery_service import (
    ProgressiveDeliveryService,
)


class ProgressiveDeliveryServiceTests(SimpleTestCase):
    def _order(self) -> Any:
        return cast(
            Any,
            SimpleNamespace(
                pk=100,
                website=SimpleNamespace(pk=10),
            ),
        )

    @patch(
        "orders.services.progressive_delivery_service."
        "OrderMilestone.objects.create"
    )
    @patch(
        "orders.services.progressive_delivery_service."
        "OrderProgressivePlan.objects.create"
    )
    def test_create_plan_creates_plan_and_milestones(
        self,
        mock_plan_create: Any,
        mock_milestone_create: Any,
    ) -> None:
        order = self._order()
        plan = SimpleNamespace(pk=1)
        mock_plan_create.return_value = plan

        result = ProgressiveDeliveryService.create_plan(
            order=order,
            milestones=[
                {
                    "title": "50% draft",
                    "description": "Halfway draft.",
                    "due_at": "2026-05-01T12:00:00Z",
                    "percentage": 50,
                },
                {
                    "title": "Final draft",
                    "description": "Complete draft.",
                    "due_at": "2026-05-02T12:00:00Z",
                    "percentage": 100,
                },
            ],
            created_by=SimpleNamespace(pk=20),
        )

        self.assertEqual(result, plan)
        mock_plan_create.assert_called_once_with(
            website=order.website,
            order=order,
            is_required=True,
        )
        self.assertEqual(mock_milestone_create.call_count, 2)