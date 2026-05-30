from django.urls import path

from payments_processor.api.views.checkout_views import PaymentCheckoutView
from payments_processor.api.views.refund_views import InitiateRefundView
from payments_processor.api.views.webhook_views import PaymentWebhookView

app_name = "payments"

urlpatterns = [
    path(
        "checkout/",
        PaymentCheckoutView.as_view(),
        name="checkout",
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
]
