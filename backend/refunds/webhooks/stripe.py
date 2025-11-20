import stripe
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now
from django.http import JsonResponse, HttpResponseBadRequest
from django.views import View

from refunds.models import Refund
from refunds.services.refunds_processor import RefundProcessorService
from refunds.tasks import retry_external_refund

from order_payments_management.models import AdminLog


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
        return HttpResponseBadRequest("Invalid payload")
    except stripe.error.SignatureVerificationError:
        return HttpResponseBadRequest("Invalid signature")

    event_type = event["type"]

    if event_type in ["charge.refunded", "payment_intent.refunded"]:
        return handle_refund_event(event)

    return JsonResponse({"status": "ignored"})


def handle_refund_event(event):
    """
    Handles Stripe refund events and processes matching internal refunds.
    """
    data = event["data"]["object"]
    charge_id = data.get("charge")
    payment_intent = data.get("payment_intent")
    refund_id = data.get("id")

    # Find our internal refund
    refund = Refund.objects.filter(
        external_ref_id=refund_id,  # assuming you store Stripe refund ID here
        status=Refund.PENDING
    ).first()

    if not refund:
        AdminLog.log_system_event(
            action="Refund Webhook Miss",
            details=f"No matching pending refund for Stripe ID {refund_id}"
        )
        return JsonResponse({"status": "not_found"})

    try:
        RefundProcessorService.process_refund(
            refund=refund,
            processed_by=None,  # set this if you want a system user
            admin_user=None,
            reason="Stripe webhook refund"
        )
        AdminLog.log_system_event(
            action="Stripe Refund Webhook Processed",
            details=f"Refund {refund.id} processed via webhook"
        )
        return JsonResponse({"status": "processed"})
    except Exception as e:
        retry_external_refund.delay(refund.id)
        AdminLog.log_system_event(
            action="Stripe Refund Webhook Failed",
            details=f"Refund {refund.id} failed: {str(e)}"
        )
        return JsonResponse({"status": "error", "retrying": True})