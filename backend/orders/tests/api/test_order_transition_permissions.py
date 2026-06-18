from types import SimpleNamespace

from django.test import SimpleTestCase

from orders.views.orders.base import OrderBaseViewSet


class OrderTransitionPermissionTests(SimpleTestCase):
    def test_client_cannot_use_generic_transition_endpoint(self) -> None:
        view = OrderBaseViewSet()
        view.get_object = lambda: SimpleNamespace(
            pk=123,
            status="submitted",
        )
        request = SimpleNamespace(
            method="POST",
            data={
                "target_status": "completed",
                "reason": "Client acceptance",
            },
            user=SimpleNamespace(
                role="client",
                is_superuser=False,
            ),
        )

        response = view.transition_status(request, pk="123")

        self.assertEqual(response.status_code, 403)
        self.assertIn(
            "Only support or administrative staff",
            response.data["detail"],
        )
