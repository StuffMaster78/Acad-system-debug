from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from orders.models import WebhookDeliveryLog
from orders.webhooks.tasks import deliver_webhook_task

class RetryWebhookView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, log_id):
        log = WebhookDeliveryLog.objects.get(pk=log_id)
        deliver_webhook_task.delay(
            user_id=log.user_id,
            order_id=log.request_payload.get("order_id"),
            webhook_url=log.url,
            event=log.event,
            triggered_by_id=log.user_id,
            platform="slack",  # or extract from somewhere
            test=log.test_mode,
            retry_count=log.retry_count + 1
        )
        return Response({"status": "Retry enqueued"})
