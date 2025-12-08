# External Payment Webhook Implementation ✅

**Date**: December 2025  
**Status**: Complete

---

## Overview

Implemented webhook endpoints to receive payment confirmations from external payment gateway websites. This allows payments to be processed on external platforms (like Stripe, PayPal, or custom payment gateways) and then automatically confirm orders on the client website via webhook callbacks.

---

## Payment Flow

### How It Works

1. **Client initiates payment** on client website
2. **Payment redirected** to external payment gateway website
3. **External website processes payment** (validates, charges, etc.)
4. **External website sends webhook** to client website with payment confirmation
5. **Client website receives webhook** and confirms the order
6. **Order status updated** to paid/completed

---

## Webhook Endpoints

### 1. Generic Payment Webhook
**Endpoint**: `POST /api/v1/order-payments/webhooks/payment/`

**Purpose**: Generic webhook for any external payment gateway

**Payload Format**:
```json
{
  "payment_id": "external_payment_id",
  "transaction_id": "internal_transaction_id",
  "status": "completed" | "failed",
  "amount": 150.00,
  "currency": "USD",
  "metadata": {}
}
```

**Response**:
```json
{
  "status": "success",
  "message": "Payment confirmed",
  "payment_id": 123,
  "transaction_id": "TXN-123456"
}
```

### 2. Stripe Webhook
**Endpoint**: `POST /api/v1/order-payments/webhooks/stripe/`

**Purpose**: Stripe-specific webhook handler

**Handles Events**:
- `payment_intent.succeeded` - Confirms payment
- `payment_intent.payment_failed` - Marks payment as failed
- `charge.succeeded` - Confirms payment
- `charge.failed` - Marks payment as failed

**Security**: Verifies Stripe webhook signature using `STRIPE_WEBHOOK_SECRET`

### 3. PayPal Webhook
**Endpoint**: `POST /api/v1/order-payments/webhooks/paypal/`

**Purpose**: PayPal-specific webhook handler

**Handles Events**:
- `PAYMENT.CAPTURE.COMPLETED` - Confirms payment
- `PAYMENT.CAPTURE.DENIED` - Marks payment as failed

---

## Implementation Details

### Location
- `backend/order_payments_management/webhooks.py` - Webhook handlers
- `backend/order_payments_management/urls.py` - URL routing

### Key Components

1. **PaymentWebhookView**
   - Generic webhook handler
   - Accepts any payment gateway format
   - Finds payment by `transaction_id` or `external_id`
   - Validates amount (logs warning if mismatch)
   - Confirms or fails payment based on status

2. **StripeWebhookView**
   - Stripe-specific handler
   - Verifies webhook signature
   - Handles Stripe event types
   - Finds payment by `stripe_payment_intent_id`

3. **PayPalWebhookView**
   - PayPal-specific handler
   - Handles PayPal event types
   - Finds payment by transaction ID

### Payment Lookup Logic

The webhook tries to find the payment in this order:
1. By `transaction_id` (internal transaction ID)
2. By `external_id` (stored when payment is marked as pending)
3. By `stripe_payment_intent_id` (for Stripe payments)

### Security Features

1. **CSRF Exemption**
   - Webhooks are exempt from CSRF protection (external sites can't have CSRF tokens)

2. **Signature Verification**
   - Stripe webhooks verify signature using `STRIPE_WEBHOOK_SECRET`
   - Generic webhooks can use `verify_webhook_signature()` helper

3. **Idempotency**
   - Webhook handlers check payment status before processing
   - Prevents duplicate processing

4. **Transaction Safety**
   - All webhook processing wrapped in `transaction.atomic()`
   - Ensures data consistency

---

## Usage Example

### 1. Client Initiates Payment

```python
# On client website
payment = OrderPaymentService.create_payment(
    order=order,
    client=client,
    payment_method='stripe',
    amount=order.total_price
)

# Mark as pending external processing
payment = OrderPaymentService.mark_as_external_pending(
    payment=payment,
    external_id='pi_1234567890'  # Stripe PaymentIntent ID
)

# Redirect client to Stripe checkout
# Client completes payment on Stripe website
```

### 2. External Gateway Processes Payment

- Client completes payment on Stripe/PayPal website
- External gateway validates and processes payment
- External gateway sends webhook to client website

### 3. Webhook Receives Confirmation

```http
POST /api/v1/order-payments/webhooks/stripe/
Content-Type: application/json
Stripe-Signature: t=1234567890,v1=abc123...

{
  "type": "payment_intent.succeeded",
  "data": {
    "object": {
      "id": "pi_1234567890",
      "status": "succeeded",
      "amount": 15000
    }
  }
}
```

### 4. Order Confirmed

- Webhook finds payment by `stripe_payment_intent_id`
- Calls `OrderPaymentService.confirm_external_payment()`
- Payment status updated to `completed`
- Order status updated to `paid` via signals
- Client receives notification

---

## Configuration

### Environment Variables

```bash
# Stripe Webhook Secret (for signature verification)
STRIPE_WEBHOOK_SECRET=whsec_...

# Generic Webhook Secret (optional, for custom gateways)
WEBHOOK_SECRET=your_secret_key
```

### Settings

Add to `settings.py`:
```python
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')
```

---

## Error Handling

### Payment Not Found
- Returns 404 with error message
- Logs warning for monitoring

### Amount Mismatch
- Logs warning but doesn't fail
- Allows payment confirmation to proceed
- Useful for handling currency conversions or fees

### Processing Errors
- Returns 500 with error message
- Logs full exception for debugging
- Payment remains in pending state for retry

---

## Testing

### Test Webhook Locally

```bash
# Using curl
curl -X POST http://localhost:8000/api/v1/order-payments/webhooks/payment/ \
  -H "Content-Type: application/json" \
  -d '{
    "payment_id": "ext_123",
    "transaction_id": "TXN-123456",
    "status": "completed",
    "amount": 150.00
  }'
```

### Test Stripe Webhook

```bash
# Using Stripe CLI (if installed)
stripe listen --forward-to localhost:8000/api/v1/order-payments/webhooks/stripe/
```

### Test with ngrok (for local development)

```bash
# Expose local server
ngrok http 8000

# Configure webhook URL in Stripe dashboard:
# https://your-ngrok-url.ngrok.io/api/v1/order-payments/webhooks/stripe/
```

---

## Integration Steps

### For External Payment Gateway

1. **Create Payment Record**
   ```python
   payment = OrderPaymentService.create_payment(...)
   payment = OrderPaymentService.mark_as_external_pending(
       payment=payment,
       external_id='external_payment_id'
   )
   ```

2. **Redirect to External Gateway**
   - Send client to external payment website
   - Include payment reference/ID

3. **Configure Webhook URL**
   - Set webhook URL in external gateway dashboard
   - URL: `https://your-domain.com/api/v1/order-payments/webhooks/payment/`

4. **Webhook Receives Confirmation**
   - External gateway sends webhook on payment completion
   - Order automatically confirmed

---

## Security Best Practices

1. **Always Verify Signatures**
   - Use signature verification for production
   - Never skip signature verification

2. **Use HTTPS**
   - Webhooks should only be called over HTTPS
   - Prevents man-in-the-middle attacks

3. **Idempotency Keys**
   - Consider adding idempotency key handling
   - Prevents duplicate processing

4. **Rate Limiting**
   - Implement rate limiting on webhook endpoints
   - Prevents abuse

5. **Logging**
   - Log all webhook attempts
   - Monitor for suspicious activity

---

## Related Files

- `backend/order_payments_management/webhooks.py` - Webhook handlers
- `backend/order_payments_management/urls.py` - URL routing
- `backend/order_payments_management/services/payment_service.py` - Payment service
- `backend/order_payments_management/models.py` - OrderPayment model
- `backend/order_payments_management/signals.py` - Payment signals

---

## Status

✅ **COMPLETE** - Webhook endpoints are implemented and ready for integration with external payment gateways.

---

## Next Steps

1. **Configure External Gateway**
   - Set up webhook URLs in payment gateway dashboard
   - Configure webhook secrets

2. **Test Integration**
   - Test with sandbox/test environment
   - Verify payment confirmations work correctly

3. **Monitor Webhooks**
   - Set up logging and monitoring
   - Track webhook success/failure rates

4. **Add More Gateways**
   - Extend webhook handlers for additional payment gateways
   - Follow same pattern as Stripe/PayPal handlers

