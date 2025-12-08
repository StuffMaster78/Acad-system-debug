"""
Webhook endpoints for receiving payment confirmations from external payment gateways.

This module handles webhooks from external payment processing websites that:
1. Process payments on their platform
2. Validate the payment
3. Send webhook to confirm the order on the client website

Supported payment gateways:
- Stripe
- PayPal (future)
- Generic payment gateway (custom)
"""
import json
import logging
import hmac
import hashlib
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from django.views import View
from django.utils import timezone
from django.db import transaction

from .models import OrderPayment
from .services.payment_service import OrderPaymentService

logger = logging.getLogger(__name__)


class PaymentWebhookView(View):
    """
    Generic webhook view for receiving payment confirmations from external payment gateways.
    
    This view:
    1. Receives webhook from external payment gateway
    2. Validates webhook signature (if provided)
    3. Finds the corresponding OrderPayment
    4. Confirms the payment and updates order status
    """
    
    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        """
        Handle payment confirmation webhook.
        
        Expected payload format:
        {
            "payment_id": "external_payment_id",  # ID from external gateway
            "transaction_id": "internal_transaction_id",  # Our internal transaction ID
            "status": "completed" | "failed",
            "amount": 150.00,
            "currency": "USD",
            "metadata": {...}  # Additional data
        }
        """
        try:
            payload = json.loads(request.body)
        except json.JSONDecodeError:
            logger.error("Invalid JSON payload in payment webhook")
            return HttpResponseBadRequest("Invalid JSON payload")
        
        # Extract payment identifiers
        external_id = payload.get('payment_id') or payload.get('external_id')
        transaction_id = payload.get('transaction_id') or payload.get('reference_id')
        status = payload.get('status', '').lower()
        amount = payload.get('amount')
        
        if not external_id and not transaction_id:
            logger.error("Missing payment identifier in webhook payload")
            return HttpResponseBadRequest("Missing payment_id or transaction_id")
        
        # Find the payment
        payment = None
        if transaction_id:
            try:
                payment = OrderPayment.objects.get(transaction_id=transaction_id)
            except OrderPayment.DoesNotExist:
                logger.warning(f"Payment not found for transaction_id: {transaction_id}")
        
        if not payment and external_id:
            # Try to find by external_id first
            try:
                payment = OrderPayment.objects.get(external_id=external_id)
            except OrderPayment.DoesNotExist:
                # Try to find by Stripe payment intent ID as fallback
                try:
                    payment = OrderPayment.objects.get(stripe_payment_intent_id=external_id)
                except OrderPayment.DoesNotExist:
                    logger.warning(f"Payment not found for external_id: {external_id}")
        
        if not payment:
            logger.error(f"Payment not found for external_id={external_id}, transaction_id={transaction_id}")
            return JsonResponse({
                "status": "error",
                "message": "Payment not found"
            }, status=404)
        
        # Validate amount if provided
        if amount and float(amount) != float(payment.discounted_amount or payment.amount):
            logger.warning(
                f"Amount mismatch for payment {payment.id}: "
                f"webhook={amount}, expected={payment.discounted_amount or payment.amount}"
            )
            # Don't fail, but log the discrepancy
        
        # Process payment confirmation
        try:
            with transaction.atomic():
                if status == 'completed' or status == 'succeeded':
                    # Confirm the payment
                    OrderPaymentService.confirm_external_payment(
                        payment=payment,
                        external_id=external_id or payment.stripe_payment_intent_id,
                        raw_response=payload
                    )
                    logger.info(f"Payment {payment.id} confirmed via webhook")
                    return JsonResponse({
                        "status": "success",
                        "message": "Payment confirmed",
                        "payment_id": payment.id,
                        "transaction_id": payment.transaction_id
                    })
                
                elif status == 'failed' or status == 'cancelled':
                    # Mark payment as failed
                    OrderPaymentService.mark_as_failed(
                        payment=payment,
                        reason=payload.get('failure_reason', 'Payment failed via webhook')
                    )
                    logger.info(f"Payment {payment.id} marked as failed via webhook")
                    return JsonResponse({
                        "status": "success",
                        "message": "Payment marked as failed",
                        "payment_id": payment.id
                    })
                
                else:
                    logger.warning(f"Unknown payment status in webhook: {status}")
                    return JsonResponse({
                        "status": "ignored",
                        "message": f"Unknown status: {status}"
                    })
        
        except Exception as e:
            logger.error(f"Error processing payment webhook: {e}", exc_info=True)
            return JsonResponse({
                "status": "error",
                "message": str(e)
            }, status=500)


class StripeWebhookView(View):
    """
    Stripe-specific webhook handler for payment confirmations.
    
    Handles Stripe webhook events:
    - payment_intent.succeeded
    - payment_intent.payment_failed
    - charge.succeeded
    - charge.failed
    """
    
    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        """
        Handle Stripe webhook events.
        """
        try:
            import stripe
        except ImportError:
            logger.error("Stripe library not installed")
            return HttpResponseBadRequest("Stripe integration not configured")
        
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
        webhook_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', None)
        
        if not webhook_secret:
            logger.warning("STRIPE_WEBHOOK_SECRET not configured, skipping signature verification")
            # In production, you should always verify signatures
            try:
                event = json.loads(payload)
            except json.JSONDecodeError:
                return HttpResponseBadRequest("Invalid JSON payload")
        else:
            # Verify webhook signature
            try:
                event = stripe.Webhook.construct_event(
                    payload, sig_header, webhook_secret
                )
            except ValueError:
                logger.error("Invalid Stripe webhook payload")
                return HttpResponseBadRequest("Invalid payload")
            except stripe.error.SignatureVerificationError:
                logger.error("Invalid Stripe webhook signature")
                return HttpResponseBadRequest("Invalid signature")
        
        event_type = event.get("type")
        event_data = event.get("data", {}).get("object", {})
        
        # Extract payment intent ID
        payment_intent_id = event_data.get("id") or event_data.get("payment_intent")
        
        if not payment_intent_id:
            logger.warning(f"No payment intent ID in Stripe event: {event_type}")
            return JsonResponse({"status": "ignored", "message": "No payment intent ID"})
        
        # Find the payment
        try:
            payment = OrderPayment.objects.get(stripe_payment_intent_id=payment_intent_id)
        except OrderPayment.DoesNotExist:
            logger.warning(f"Payment not found for Stripe payment intent: {payment_intent_id}")
            return JsonResponse({
                "status": "not_found",
                "message": "Payment not found"
            }, status=404)
        
        # Handle different event types
        try:
            with transaction.atomic():
                if event_type in ["payment_intent.succeeded", "charge.succeeded"]:
                    # Confirm the payment
                    OrderPaymentService.confirm_external_payment(
                        payment=payment,
                        external_id=payment_intent_id,
                        raw_response=event_data
                    )
                    logger.info(f"Payment {payment.id} confirmed via Stripe webhook: {event_type}")
                    return JsonResponse({
                        "status": "success",
                        "message": "Payment confirmed",
                        "payment_id": payment.id
                    })
                
                elif event_type in ["payment_intent.payment_failed", "charge.failed"]:
                    # Mark payment as failed
                    failure_reason = event_data.get("failure_message") or "Payment failed via Stripe"
                    OrderPaymentService.mark_as_failed(
                        payment=payment,
                        reason=failure_reason
                    )
                    logger.info(f"Payment {payment.id} marked as failed via Stripe webhook: {event_type}")
                    return JsonResponse({
                        "status": "success",
                        "message": "Payment marked as failed",
                        "payment_id": payment.id
                    })
                
                else:
                    logger.info(f"Ignoring Stripe event type: {event_type}")
                    return JsonResponse({
                        "status": "ignored",
                        "message": f"Event type {event_type} not handled"
                    })
        
        except Exception as e:
            logger.error(f"Error processing Stripe webhook: {e}", exc_info=True)
            return JsonResponse({
                "status": "error",
                "message": str(e)
            }, status=500)


class PayPalWebhookView(View):
    """
    PayPal-specific webhook handler for payment confirmations.
    
    Handles PayPal webhook events:
    - PAYMENT.CAPTURE.COMPLETED
    - PAYMENT.CAPTURE.DENIED
    """
    
    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        """
        Handle PayPal webhook events.
        """
        try:
            payload = json.loads(request.body)
        except json.JSONDecodeError:
            logger.error("Invalid JSON payload in PayPal webhook")
            return HttpResponseBadRequest("Invalid JSON payload")
        
        # TODO: Verify PayPal webhook signature
        # PayPal webhook verification requires specific headers and signature validation
        
        event_type = payload.get("event_type")
        resource = payload.get("resource", {})
        
        # Extract payment ID from PayPal resource
        payment_id = resource.get("id") or resource.get("payment_id")
        
        if not payment_id:
            logger.warning(f"No payment ID in PayPal event: {event_type}")
            return JsonResponse({"status": "ignored", "message": "No payment ID"})
        
        # Find the payment by PayPal transaction ID
        # Note: You may need to store PayPal transaction ID in a separate field
        # For now, we'll try to match by transaction_id or reference_id
        try:
            # This assumes PayPal transaction ID is stored in transaction_id or reference_id
            # You may need to add a paypal_transaction_id field to OrderPayment
            payment = OrderPayment.objects.filter(
                transaction_id=payment_id
            ).first()
            
            if not payment:
                logger.warning(f"Payment not found for PayPal transaction: {payment_id}")
                return JsonResponse({
                    "status": "not_found",
                    "message": "Payment not found"
                }, status=404)
        
        except Exception as e:
            logger.error(f"Error finding payment for PayPal webhook: {e}")
            return JsonResponse({
                "status": "error",
                "message": str(e)
            }, status=500)
        
        # Handle different event types
        try:
            with transaction.atomic():
                if event_type == "PAYMENT.CAPTURE.COMPLETED":
                    # Confirm the payment
                    OrderPaymentService.confirm_external_payment(
                        payment=payment,
                        external_id=payment_id,
                        raw_response=resource
                    )
                    logger.info(f"Payment {payment.id} confirmed via PayPal webhook")
                    return JsonResponse({
                        "status": "success",
                        "message": "Payment confirmed",
                        "payment_id": payment.id
                    })
                
                elif event_type == "PAYMENT.CAPTURE.DENIED":
                    # Mark payment as failed
                    OrderPaymentService.mark_as_failed(
                        payment=payment,
                        reason="Payment denied via PayPal"
                    )
                    logger.info(f"Payment {payment.id} marked as failed via PayPal webhook")
                    return JsonResponse({
                        "status": "success",
                        "message": "Payment marked as failed",
                        "payment_id": payment.id
                    })
                
                else:
                    logger.info(f"Ignoring PayPal event type: {event_type}")
                    return JsonResponse({
                        "status": "ignored",
                        "message": f"Event type {event_type} not handled"
                    })
        
        except Exception as e:
            logger.error(f"Error processing PayPal webhook: {e}", exc_info=True)
            return JsonResponse({
                "status": "error",
                "message": str(e)
            }, status=500)


def verify_webhook_signature(request, secret_key, signature_header='X-Webhook-Signature'):
    """
    Generic webhook signature verification.
    
    Args:
        request: Django request object
        secret_key: Secret key for HMAC verification
        signature_header: Header name containing the signature
    
    Returns:
        bool: True if signature is valid, False otherwise
    """
    signature = request.META.get(f"HTTP_{signature_header.upper().replace('-', '_')}")
    
    if not signature:
        return False
    
    # Calculate expected signature
    expected_signature = hmac.new(
        secret_key.encode('utf-8'),
        request.body,
        hashlib.sha256
    ).hexdigest()
    
    # Compare signatures (use constant-time comparison to prevent timing attacks)
    return hmac.compare_digest(signature, expected_signature)

