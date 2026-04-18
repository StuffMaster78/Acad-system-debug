from __future__ import annotations

from typing import Any, cast
from unittest.mock import patch

from django.test import SimpleTestCase
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response as DRFResponse
from rest_framework.test import APIRequestFactory, force_authenticate

from orders.api.views.staffing.staffing_views import (
    AssignDirectView,
    ExpressInterestView,
    RouteOrderToStaffingView,
    TakeOrderView,
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


class StaffingAPITests(SimpleTestCase):
    def setUp(self) -> None:
        self.factory = APIRequestFactory()

        class Website:
            pk = 1

        self.website = Website()

        self.staff_user = FakeUser(
            pk=1,
            website=self.website,
            is_staff=True,
        )
        self.writer_user = FakeUser(
            pk=2,
            website=self.website,
            is_staff=False,
        )

        self.order = type(
            "OrderStub",
            (),
            {
                "pk": 100,
                "website": self.website,
                "status": "paid",
                "visibility_mode": "hidden",
            },
        )()

    def _auth_post(
        self,
        *,
        path: str,
        user: FakeUser,
        data: dict[str, Any] | None = None,
    ) -> Request:
        request = self.factory.post(path, data or {}, format="json")
        force_authenticate(request, user=cast(Any, user))
        return cast(Request, request)

    @staticmethod
    def _data(response: DRFResponse) -> dict[str, Any]:
        assert response.data is not None
        return cast(dict[str, Any], response.data)

    # =========================
    # ROUTE TO STAFFING
    # =========================
    @patch(
        "orders.api.views.staffing.staffing_views."
        "OrderStaffingService.route_to_staffing"
    )
    @patch.object(RouteOrderToStaffingView, "_get_order_for_tenant")
    def test_route_to_staffing(
        self,
        mock_get_order: Any,
        mock_service: Any,
    ) -> None:
        mock_get_order.return_value = self.order
        mock_service.return_value = self.order

        view = RouteOrderToStaffingView.as_view()
        request = self._auth_post(
            path="/orders/100/route/",
            user=self.staff_user,
        )

        with patch.object(
            RouteOrderToStaffingView,
            "check_object_permissions",
            return_value=None,
        ):
            response = cast(DRFResponse, view(request, order_id=100))

        data = self._data(response)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data["order_id"], 100)

        mock_service.assert_called_once()

    # =========================
    # EXPRESS INTEREST
    # =========================
    @patch(
        "orders.api.views.staffing.staffing_views."
        "OrderStaffingService.express_interest"
    )
    @patch.object(ExpressInterestView, "_get_order_for_tenant")
    def test_express_interest(
        self,
        mock_get_order: Any,
        mock_service: Any,
    ) -> None:
        interest = type(
            "InterestStub",
            (),
            {"pk": 200, "status": "pending"},
        )()

        mock_get_order.return_value = self.order
        mock_service.return_value = interest

        view = ExpressInterestView.as_view()
        request = self._auth_post(
            path="/orders/100/interest/",
            user=self.writer_user,
            data={"interest_type": "show_interest"},
        )

        with patch.object(
            ExpressInterestView,
            "check_object_permissions",
            return_value=None,
        ):
            response = cast(DRFResponse, view(request, order_id=100))

        data = self._data(response)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(data["interest_id"], 200)

        mock_service.assert_called_once()

    # =========================
    # TAKE ORDER
    # =========================
    @patch(
        "orders.api.views.staffing.staffing_views."
        "OrderStaffingService.take_order"
    )
    @patch.object(TakeOrderView, "_get_order_for_tenant")
    def test_take_order(
        self,
        mock_get_order: Any,
        mock_service: Any,
    ) -> None:
        assignment = type(
            "AssignmentStub",
            (),
            {
                "pk": 300,
                "status": "active",
                "writer": self.writer_user,
                "order": self.order,
            },
        )()

        mock_get_order.return_value = self.order
        mock_service.return_value = assignment

        view = TakeOrderView.as_view()
        request = self._auth_post(
            path="/orders/100/take/",
            user=self.writer_user,
        )

        with patch.object(
            TakeOrderView,
            "check_object_permissions",
            return_value=None,
        ):
            response = cast(DRFResponse, view(request, order_id=100))

        data = self._data(response)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data["assignment_id"], 300)

        mock_service.assert_called_once()

    # =========================
    # DIRECT ASSIGN
    # =========================
    @patch(
        "orders.api.views.staffing.staffing_views."
        "OrderStaffingService.assign_direct"
    )
    @patch.object(AssignDirectView, "_get_order_for_tenant")
    @patch.object(AssignDirectView, "_get_writer_for_tenant")
    def test_assign_direct(
        self,
        mock_get_writer: Any,
        mock_get_order: Any,
        mock_service: Any,
    ) -> None:
        assignment = type(
            "AssignmentStub",
            (),
            {
                "pk": 400,
                "status": "active",
                "writer": self.writer_user,
                "order": self.order,
            },
        )()

        mock_get_order.return_value = self.order
        mock_get_writer.return_value = self.writer_user
        mock_service.return_value = assignment

        view = AssignDirectView.as_view()
        request = self._auth_post(
            path="/orders/100/assign/",
            user=self.staff_user,
            data={"writer_id": 2},
        )

        with patch.object(
            AssignDirectView,
            "check_object_permissions",
            return_value=None,
        ):
            response = cast(DRFResponse, view(request, order_id=100))

        data = self._data(response)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data["assignment_id"], 400)

        mock_service.assert_called_once()