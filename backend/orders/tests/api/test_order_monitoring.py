from __future__ import annotations

from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import patch

from django.test import SimpleTestCase
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response as DRFResponse
from rest_framework.test import APIRequestFactory, force_authenticate

from orders.api.views.monitoring.order_monitoring_views import (
    OrderMonitoringView,
)


class FakeUser:
    def __init__(
        self,
        *,
        pk: int,
        website: Any,
        is_staff: bool = False,
    ) -> None:
        self.pk = pk
        self.id = pk
        self.website = website
        self.website_id = getattr(website, "pk", None)
        self.is_staff = is_staff
        self.is_authenticated = True


class OrderMonitoringAPITests(SimpleTestCase):
    def setUp(self) -> None:
        self.factory = APIRequestFactory()

        self.website = SimpleNamespace(pk=1)

        self.user = FakeUser(
            pk=1,
            website=self.website,
            is_staff=True,
        )

        self.order = SimpleNamespace(
            pk=100,
            website=self.website,
        )

    def _auth_get(
        self,
        *,
        path: str,
        user: FakeUser,
    ) -> Request:
        request = self.factory.get(path)
        force_authenticate(request, user=cast(Any, user))
        return cast(Request, request)

    @staticmethod
    def _data(response: DRFResponse) -> dict[str, Any]:
        assert response.data is not None
        return cast(dict[str, Any], response.data)

    @patch(
        "orders.api.views.monitoring.order_monitoring_views."
        "OrderMonitoringService.build_operational_state"
    )
    @patch.object(
        OrderMonitoringView,
        "_get_order_for_tenant",
    )
    def test_monitoring_api_returns_state(
        self,
        mock_get_order: Any,
        mock_service: Any,
    ) -> None:
        mock_get_order.return_value = self.order

        mock_service.return_value = SimpleNamespace(
            is_late=False,
            is_critical=True,
            seconds_to_writer_deadline=500,
            state_label="critical",
        )

        view = OrderMonitoringView.as_view()
        request = self._auth_get(
            path="/orders/100/monitoring/",
            user=self.user,
        )

        with patch.object(
            OrderMonitoringView,
            "check_object_permissions",
            return_value=None,
        ):
            response = cast(DRFResponse, view(request, order_id=100))

        data = self._data(response)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data["order_id"], 100)
        self.assertEqual(data["state_label"], "critical")
        self.assertEqual(data["is_late"], False)
        self.assertEqual(data["is_critical"], True)