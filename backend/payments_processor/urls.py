from django.urls import path

from payments_processor.api.views.checkout_views import CancelPrewarmView, PaymentCheckoutView
from payments_processor.api.views.gateway_config_views import (
    PaymentGatewayConfigCreateView,
    PaymentGatewayConfigDetailView,
    PaymentGatewayConfigListView,
    PaymentNotificationEmailDetailView,
    PaymentNotificationEmailListView,
)
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
    # Admin/superadmin: per-website gateway configuration
    path(
        "gateway/configs/",
        PaymentGatewayConfigListView.as_view(),
        name="gateway-config-list",
    ),
    path(
        "gateway/configs/create/",
        PaymentGatewayConfigCreateView.as_view(),
        name="gateway-config-create",
    ),
    path(
        "gateway/configs/<int:config_id>/",
        PaymentGatewayConfigDetailView.as_view(),
        name="gateway-config-detail",
    ),
    # Admin/superadmin: payment notification email addresses
    path(
        "gateway/notification-emails/",
        PaymentNotificationEmailListView.as_view(),
        name="notification-email-list",
    ),
    path(
        "gateway/notification-emails/<int:entry_id>/",
        PaymentNotificationEmailDetailView.as_view(),
        name="notification-email-detail",
    ),
]
