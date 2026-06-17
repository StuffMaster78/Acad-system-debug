from __future__ import annotations

from dataclasses import dataclass
from typing import Any, cast
from unittest.mock import patch

from django.test import SimpleTestCase
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response as DRFResponse
from rest_framework.test import APIRequestFactory, force_authenticate

from orders.api.views.lifecycle.order_lifecycle_views import (
    OrderLifecycleView,
)
from orders.services.order_available_actions_service import (
    OrderAvailableActionsService,
)
from orders.services.order_lifecycle_read_service import OrderLifecycleSnapshot


@dataclass
class FakeUser:
    """
    Lightweight authenticated user test double.
    """

    pk: int
    website: Any
    is_staff: bool = False
    role: str = "client"

    @property
    def id(self) -> int:
        return self.pk

    @property
    def website_id(self) -> Any:
        return getattr(self.website, "pk", None)

    @property
    def is_authenticated(self) -> bool:
        return True


class LifecycleAPITests(SimpleTestCase):
    def setUp(self) -> None:
        self.factory = APIRequestFactory()

        class Website:
            pk = 1

        self.website = Website()

        self.client_user = FakeUser(
            pk=10,
            website=self.website,
            is_staff=False,
        )
        self.writer_user = FakeUser(
            pk=20,
            website=self.website,
            is_staff=False,
            role="writer",
        )
        self.staff_user = FakeUser(
            pk=30,
            website=self.website,
            is_staff=True,
        )

        self.order = type(
            "OrderStub",
            (),
            {
                "pk": 100,
                "website": self.website,
                "client": self.client_user,
            },
        )()

        self.snapshot = OrderLifecycleSnapshot(
            order_id=100,
            order_status="in_progress",
            website_id=1,
            client_id=10,
            current_assignment_id=200,
            current_writer_id=20,
            current_writer_registration_id="WR-0020",
            has_current_assignment=True,
            active_hold_id=None,
            has_active_hold=False,
            pending_reassignment_request_id=None,
            has_pending_reassignment_request=False,
            active_dispute_id=None,
            has_active_dispute=False,
            latest_adjustment_request_id=300,
            latest_adjustment_status="funding_pending",
            latest_revision_request_id=None,
            latest_revision_status=None,
            is_revision_window_open=False,
            revision_window_days=14,
            pending_preferred_invitation_interest_id=None,
        )

    def _authenticated_get(
        self,
        *,
        path: str,
        user: FakeUser,
    ) -> Request:
        request = self.factory.get(path)
        force_authenticate(request, user=cast(Any, user))
        return cast(Request, request)

    @staticmethod
    def _response_data(response: DRFResponse) -> dict[str, Any]:
        assert response.data is not None
        return cast(dict[str, Any], response.data)

    @patch.object(OrderAvailableActionsService, "build_blocked_reasons", return_value={})
    @patch.object(OrderAvailableActionsService, "build_actions", return_value=["submit_for_qa"])
    @patch(
        "orders.api.views.lifecycle.order_lifecycle_views."
        "OrderLifecycleReadService.build_snapshot"
    )
    @patch.object(OrderLifecycleView, "_get_order_for_tenant")
    def test_lifecycle_view_returns_200_for_staff(
        self,
        mock_get_order: Any,
        mock_build_snapshot: Any,
        _mock_actions: Any,
        _mock_blocked: Any,
    ) -> None:
        mock_get_order.return_value = self.order
        mock_build_snapshot.return_value = self.snapshot

        view = OrderLifecycleView.as_view()
        request = self._authenticated_get(
            path="/api/orders/orders/100/lifecycle/",
            user=self.staff_user,
        )

        with patch.object(
            OrderLifecycleView,
            "check_object_permissions",
            return_value=None,
        ):
            response = cast(DRFResponse, view(request, order_id=100))

        data = self._response_data(response)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data["order_id"], 100)
        self.assertEqual(data["order_status"], "in_progress")
        self.assertEqual(data["current_assignment_id"], 200)
        self.assertEqual(data["current_writer_id"], 20)
        self.assertEqual(data["latest_adjustment_status"], "funding_pending")
        self.assertFalse(data["is_revision_window_open"])

        mock_build_snapshot.assert_called_once_with(order=self.order, for_writer=None)

    @patch.object(OrderAvailableActionsService, "build_blocked_reasons", return_value={})
    @patch.object(OrderAvailableActionsService, "build_actions", return_value=[])
    @patch(
        "orders.api.views.lifecycle.order_lifecycle_views."
        "OrderLifecycleReadService.build_snapshot"
    )
    @patch.object(OrderLifecycleView, "_get_order_for_tenant")
    def test_lifecycle_view_returns_200_for_client(
        self,
        mock_get_order: Any,
        mock_build_snapshot: Any,
        _mock_actions: Any,
        _mock_blocked: Any,
    ) -> None:
        mock_get_order.return_value = self.order
        mock_build_snapshot.return_value = self.snapshot

        view = OrderLifecycleView.as_view()
        request = self._authenticated_get(
            path="/api/orders/orders/100/lifecycle/",
            user=self.client_user,
        )

        with patch.object(
            OrderLifecycleView,
            "check_object_permissions",
            return_value=None,
        ):
            response = cast(DRFResponse, view(request, order_id=100))

        data = self._response_data(response)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data["client_id"], 10)
        self.assertTrue(data["has_current_assignment"])

    @patch.object(OrderAvailableActionsService, "build_blocked_reasons", return_value={})
    @patch.object(OrderAvailableActionsService, "build_actions", return_value=["submit_for_qa"])
    @patch(
        "orders.api.views.lifecycle.order_lifecycle_views."
        "OrderLifecycleReadService.build_snapshot"
    )
    @patch.object(OrderLifecycleView, "_get_order_for_tenant")
    def test_lifecycle_view_returns_200_for_writer(
        self,
        mock_get_order: Any,
        mock_build_snapshot: Any,
        _mock_actions: Any,
        _mock_blocked: Any,
    ) -> None:
        mock_get_order.return_value = self.order
        mock_build_snapshot.return_value = self.snapshot

        view = OrderLifecycleView.as_view()
        request = self._authenticated_get(
            path="/api/orders/orders/100/lifecycle/",
            user=self.writer_user,
        )

        with patch.object(
            OrderLifecycleView,
            "check_object_permissions",
            return_value=None,
        ):
            response = cast(DRFResponse, view(request, order_id=100))

        data = self._response_data(response)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data["current_writer_id"], 20)
        mock_build_snapshot.assert_called_once_with(
            order=self.order, for_writer=self.writer_user
        )

    @patch.object(OrderLifecycleView, "_get_order_for_tenant")
    def test_lifecycle_view_denies_when_permissions_fail(
        self,
        mock_get_order: Any,
    ) -> None:
        mock_get_order.return_value = self.order

        view = OrderLifecycleView.as_view()
        request = self._authenticated_get(
            path="/api/orders/orders/100/lifecycle/",
            user=self.writer_user,
        )

        with patch.object(
            OrderLifecycleView,
            "check_object_permissions",
            side_effect=PermissionError("forbidden"),
        ):
            with self.assertRaises(PermissionError):
                view(request, order_id=100)

    @patch.object(OrderAvailableActionsService, "build_blocked_reasons", return_value={})
    @patch.object(OrderAvailableActionsService, "build_actions", return_value=[])
    @patch(
        "orders.api.views.lifecycle.order_lifecycle_views."
        "OrderLifecycleReadService.build_snapshot"
    )
    @patch.object(OrderLifecycleView, "_get_order_for_tenant")
    def test_lifecycle_view_returns_nullables_cleanly(
        self,
        mock_get_order: Any,
        mock_build_snapshot: Any,
        _mock_actions: Any,
        _mock_blocked: Any,
    ) -> None:
        empty_snapshot = OrderLifecycleSnapshot(
            order_id=100,
            order_status="completed",
            website_id=1,
            client_id=10,
            current_assignment_id=None,
            current_writer_id=None,
            current_writer_registration_id=None,
            has_current_assignment=False,
            active_hold_id=None,
            has_active_hold=False,
            pending_reassignment_request_id=None,
            has_pending_reassignment_request=False,
            active_dispute_id=None,
            has_active_dispute=False,
            latest_adjustment_request_id=None,
            latest_adjustment_status=None,
            latest_revision_request_id=None,
            latest_revision_status=None,
            is_revision_window_open=True,
            revision_window_days=14,
            pending_preferred_invitation_interest_id=None,
        )

        mock_get_order.return_value = self.order
        mock_build_snapshot.return_value = empty_snapshot

        view = OrderLifecycleView.as_view()
        request = self._authenticated_get(
            path="/api/orders/orders/100/lifecycle/",
            user=self.staff_user,
        )

        with patch.object(
            OrderLifecycleView,
            "check_object_permissions",
            return_value=None,
        ):
            response = cast(DRFResponse, view(request, order_id=100))

        data = self._response_data(response)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(data["current_assignment_id"])
        self.assertIsNone(data["current_writer_id"])
        self.assertIsNone(data["latest_adjustment_request_id"])
        self.assertIsNone(data["latest_revision_request_id"])
        self.assertTrue(data["is_revision_window_open"])