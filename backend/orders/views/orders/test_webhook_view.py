from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from orders.webhooks.tasks import deliver_webhook_task
from orders.models import Order
from django.shortcuts import get_object_or_404


class TestWebhookView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        settings = getattr(user, "webhook_settings", None)
        if not settings or not settings.enabled:
            return Response({"error": "Webhook not configured."}, status=400)

        order = Order.objects.filter(assigned_writer=user).last()
        if not order:
            return Response({"error": "No order found."}, status=404)

        deliver_webhook_task.delay(
            user_id=user.id,
            platform=settings.platform,
            webhook_url=settings.webhook_url,
            event="test_event",
            order_id=order.id,
            triggered_by_id=user.id,
            test=True,
            fallback_icon="https://yourcdn.com/imgs/test-icon.png"
        )

        return Response({"status": "Webhook test sent!"})