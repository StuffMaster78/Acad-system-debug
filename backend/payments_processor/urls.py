from django.urls import path

from payments_processor.api.views.checkout_views import PaymentCheckoutView
# from payments.api.views.webhook_views import FlutterwaveWebhookView

app_name = "payments"

urlpatterns = [
    path(
        "checkout/",
        PaymentCheckoutView.as_view(),
        name="checkout",
    ),
    # path(
    #     "webhooks/flutterwave/",
    #     FlutterwaveWebhookView.as_view(),
    #     name="flutterwave-webhook",
    # ),
]