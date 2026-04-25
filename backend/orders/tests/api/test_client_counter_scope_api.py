from __future__ import annotations

from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import patch

from django.test import SimpleTestCase
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response as DRFResponse
from rest_framework.test import APIRequestFactory, force_authenticate

from orders.api.views.adjustments.client_counter_scope_views import (
    ClientCounterScopeIncrementView,
)


class FakeUser:
    def __init__(self, *, pk: int, website: Any) -> None:
        self.pk = pk
        self.id = pk
        self.website = website
        self.is_authenticated = True


class ClientCounterScopeAPITests(SimpleTestCase):
    def setUp(self) -> None:
        self.factory = APIRequestFactory()
        self.website = SimpleNamespace(pk=10)
        self.client = FakeUser(pk=1, website=self.website)

    def _post(self, data: dict[str, Any]) -> Request:
        request = self.factory.post(
            "/orders/adjustments/5/counter-scope/",
            data,
            format="json",
        )
        force_authenticate(request, user=cast(Any, self.client))
        return cast(Request, request)

    @patch(
        "orders.api.views.adjustments.client_counter_scope_views."
        "AdjustmentNegotiationService.client_counter_scope_increment"
    )
    @patch(
        "orders.api.views.adjustments.client_counter_scope_views."
        "get_object_or_404"
    )
    def test_client_counter_scope_increment(
        self,
        mock_get_object: Any,
        mock_service: Any,
    ) -> None:
        adjustment = SimpleNamespace(
            pk=5,
            order=SimpleNamespace(client=self.client),
            status="pending_client_response",
        )
        updated = SimpleNamespace(
            pk=5,
            status="client_countered",
            countered_quantity=5,
            counter_total_amount="30.00",
        )
        mock_get_object.return_value = adjustment
        mock_service.return_value = updated

        view = ClientCounterScopeIncrementView.as_view()
        response = cast(
            DRFResponse,
            view(
                self._post(
                    {
                        "countered_quantity": 5,
                        "countered_note": "One extra page is enough.",
                    }
                ),
                adjustment_id=5,
            ),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_service.assert_called_once()

    def test_client_counter_scope_rejects_missing_quantity(self) -> None:
        view = ClientCounterScopeIncrementView.as_view()
        response = cast(
            DRFResponse,
            view(self._post({"countered_note": "No quantity"}), adjustment_id=5),
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)