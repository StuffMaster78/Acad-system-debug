from django.urls import path

from payments_processor.api.views.checkout_views import CancelPrewarmView, PaymentCheckoutView
from payments_processor.api.views.gateway_status_views import PaymentGatewayStatusView
from payments_processor.api.views.refund_views import InitiateRefundView
from payments_processor.api.views.webhook_config_views import WebhookConfigView
from payments_processor.api.views.webhook_views import PaymentWebhookView

app_name = "payments"

urlpatterns = [
    path(
        "checkout/",
        PaymentCheckoutView.as_view(),
        name="checkout",
    ),
    path(
        "checkout/cancel-prewarm/",
        CancelPrewarmView.as_view(),
        name="cancel-prewarm",
    ),
    path(
        "webhooks/<str:provider>/",
        PaymentWebhookView.as_view(),
        name="webhook",
    ),
    path(
        "refunds/",
        InitiateRefundView.as_view(),
        name="refund",
    ),
    # Admin-only: Stripe gateway status (masked keys) + connectivity test
    path(
        "gateway/status/",
        PaymentGatewayStatusView.as_view(),
        name="gateway-status",
    ),
    # Admin-only: webhook behaviour configuration
    path(
        "gateway/webhook-config/",
        WebhookConfigView.as_view(),
        name="webhook-config",
    ),
]
