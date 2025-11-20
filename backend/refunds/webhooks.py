# import stripe
# from django.http import HttpResponse, JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from django.conf import settings

# from orders.models import Order
# from refunds.services.refunds_processor import mark_order_refunded

# @csrf_exempt
# def stripe_webhook(request):
#     """
#     Handles Stripe webhook events and marks orders as refunded
#     when appropriate.
#     """
#     payload = request.body
#     sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
#     try:
#         event = stripe.Webhook.construct_event(
#             payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
#         )
#     except (ValueError, stripe.error.SignatureVerificationError):
#         return HttpResponse(status=400)

#     if event['type'] == 'charge.refunded':
#         charge = event['data']['object']
#         order_id = charge['metadata'].get('order_id')

#         if order_id:
#             try:
#                 order = Order.objects.get(id=order_id)
#                 amount = charge['amount_refunded'] / 100.0
#                 mark_order_refunded(
#                     order, amount,
#                     source='stripe-webhook', metadata=charge
#                 )
#             except Order.DoesNotExist:
#                 pass  # Consider logging

#     return JsonResponse({'status': 'received'})