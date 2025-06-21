from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from orders.webhooks.payloads import build_webhook_payload
from orders.models import Order


class WebhookPreviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        order = Order.objects.get(pk=order_id)
        payload = build_webhook_payload(
            event="order_assigned",
            order=order,
            triggered_by=request.user,
            platform=request.GET.get("platform", "slack"),
            test=True,
            fallback_icon="https://yourcdn.com/default.png"
        )
        return Response(payload)