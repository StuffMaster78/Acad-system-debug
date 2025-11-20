# Order Placement Workflow

## Overview
This document outlines the complete workflow for order placement and payment processing in the writing system backend.

---

## Standard Order Placement Flow

### 1. **Order Creation Phase**

**Endpoint:** `POST /api/v1/orders/orders/`

**Steps:**
1. Client submits order data via API
2. `OrderCreateSerializer` validates:
   - Deadline must be in future
   - Preferred writer must be available
   - Required fields (topic, paper_type, pages, etc.)

3. `CreateOrderService.create_order()` is called:
   - Creates `Order` instance with status `CREATED` or `CRITICAL` (if urgent deadline)
   - Auto-calculates `total_price` via `PricingCalculatorService.calculate_total_price()`
   - Components included:
     - Base price (pages/slides)
     - Extra services
     - Writer level premium
     - Preferred writer fee
     - Deadline multiplier (urgency)
     - Discount deductions
   - Saves pricing snapshot via `OrderPricingSnapshotService`
   - Sends "order.created" notification

**Initial Order Status:** `CREATED` (or `CRITICAL` if urgent)
**Payment Status:** `is_paid = False`
**Order Status:** `UNPAID` (implied)

---

### 2. **Pricing Calculation**

**Automatic on save:**
- `Order.save()` triggers `PricingCalculatorService.calculate_total_price()`
- Price includes:
  - Base: `pages × base_price_per_page + slides × base_price_per_slide`
  - Writer Level: Premium for selected writer level
  - Extra Services: Additional fees
  - Deadline Multiplier: Urgency fee
  - Discount: Applied discount code reduction
- Price snapshot saved for audit trail

---

### 3. **Payment Processing Phase** ⚠️ **GAP IDENTIFIED**

**Current State:**
- No clear unified payment endpoint for standard orders
- Payment handling appears fragmented:
  - `PaymentViewSet.process_payment()` only handles `RequestPayment` (for page increases)
  - No clear service to create `OrderPayment` for new orders

**What Should Happen:**
1. Client initiates payment (via Stripe/PayPal/wallet)
2. Create `OrderPayment` record:
   ```python
   OrderPayment.objects.create(
       order=order,
       client=client,
       website=order.website,
       payment_type="standard",
       amount=order.total_price,
       original_amount=order.total_price,
       discounted_amount=order.total_price - discount_amount,
       status="pending",
       transaction_id=generate_reference_id(),
       payment_method=payment_method,  # stripe, wallet, etc.
   )
   ```

3. Process payment:
   - **Stripe**: Create PaymentIntent, await webhook confirmation
   - **Wallet**: Deduct from `ClientWallet.balance`
   - **External**: Admin processes manually

4. On successful payment:
   - Update `OrderPayment.status = "completed"`
   - Signal `update_order_status` fires → calls `process_successful_payment()`
   - Order status transitions: `UNPAID` → `PENDING` or `IN_PROGRESS`
   - `order.is_paid = True`
   - Notification sent to client

**Current Signal Handler:**
```python
@receiver(post_save, sender=OrderPayment)
def update_order_status(sender, instance, created, **kwargs):
    if instance.status == "completed":
        instance.order.mark_paid()  # Sets status to 'in_progress'
        # Sends notification
```

---

### 4. **Order Status Transitions**

**After Payment:**
- `Order.mark_paid()` sets:
  - `status = 'in_progress'` (from `'unpaid'`)
  - `is_paid = True`

**Order Lifecycle (Post-Payment):**
1. `UNPAID` → Payment → `PENDING` or `IN_PROGRESS`
2. `IN_PROGRESS` → Writer assigned → `ASSIGNED`
3. `ASSIGNED` → Writer starts → Still `IN_PROGRESS`
4. `IN_PROGRESS` → Writer submits → `SUBMITTED`
5. `SUBMITTED` → Auto-transition → `UNDER_EDITING`
6. `UNDER_EDITING` → Editing complete → `COMPLETED`
7. `COMPLETED` → Client rates → `RATED`
8. `RATED` → Admin reviews → `REVIEWED` → `CLOSED`

---

## Special Order Placement Flow

### 1. **Special Order Creation**

**Endpoint:** Special orders service
**Service:** `create_special_order(data, user)`

**Steps:**
1. Validate special order data
2. Create `SpecialOrder` instance
3. If `order_type == 'predefined'`:
   - Calculate predefined price
   - Set `total_cost`
4. Generate installments via `InstallmentPaymentService`
5. Order status: Created with installments

**Payment Flow:**
- Uses `InstallmentPayment` model
- Payments processed incrementally
- Each installment creates separate payment records

---

## Class Bundle Purchase Flow

**Service:** `handle_purchase_request(user, data, website)`

**Steps:**
1. Calculate price based on program/duration/bundle_size
2. Create `ClassPurchase` record
3. Charge wallet immediately (or allow negative balance)
4. Mark as `paid` immediately

**No separate payment model** - wallet transaction handled directly

---

## Payment Gateway Integration Note

**Important:** Payment gateway integration (Stripe/PayPal through middle website) will be implemented later. The current system is structured to support this:

- Payment records can be created with `status='pending'`
- `OrderPaymentService.confirm_external_payment()` method is ready for webhook integration
- Payment status synchronization via signals will work automatically once gateway confirms payments

For now, the system supports:
- ✅ Wallet payments (immediate processing)
- ✅ Manual admin payments (external processing)
- ✅ Payment record creation for future gateway integration

---

## Issues & Missing Components ⚠️

### ✅ **FIXED:**
1. ✅ **Order.mark_paid() status mismatch** - Fixed to check for 'completed'/'succeeded' instead of 'paid'
2. ✅ **Wallet payment processing** - Now uses atomic transactions with row locking
3. ✅ **OrderPaymentService** - Created service layer for payment operations
4. ✅ **Payment initiation endpoint** - Added `POST /api/v1/order-payments/orders/{id}/initiate/`
5. ✅ **OrderPayment.save() auto-sync** - Removed redundant logic, relies on signals
6. ✅ **Payment validation before IN_PROGRESS** - Added validation in StatusTransitionService and MarkOrderPaidService
7. ✅ **Discount application consistency** - Service now uses order discount if exists, or applies discount code
8. ✅ **Payment method validation** - Added VALID_PAYMENT_METHODS list and validation
9. ✅ **PaymentRecord documentation** - Clarified usage vs OrderPayment

### 🔴 **REMAINING CRITICAL GAPS:**

1. **Payment Gateway Integration** (Will be added later)
   - Missing: Stripe/PayPal integration via middle website
   - Missing: Webhook handlers for payment confirmations
   - Missing: PaymentIntent creation for external gateways
   - **Note:** Structure is ready - `OrderPaymentService.confirm_external_payment()` available
   - **Workaround:** Manual admin confirmation for external payments

2. **Incomplete Payment Status Sync** 🔴 **FIXED - VERIFY**
   - `Order.mark_paid()` (line 390-404) uses lazy import:
     ```python
     Payment = apps.get_model('order_payments_management', 'OrderPayment')
     payment = Payment.objects.filter(order=self, status='paid')
     ```
   - But `OrderPayment.status` uses `'completed'` not `'paid'` (see STATUS_CHOICES)
   - **Bug:** Status check will never match - `Order.mark_paid()` is broken
   - **Status:** ✅ Fixed in `Order.update_status_based_on_payment()` and `Order.mark_paid()`
   - Now checks for 'completed'/'succeeded' status correctly

3. **OrderPayment.save() Auto-Sync Issues** ✅ **FIXED**
   - **Status:** Removed redundant auto-sync logic from `OrderPayment.save()`
   - Now relies solely on signals for order status updates
   - Keeps logic centralized and avoids duplicate processing

4. **Order Status Validation Missing** ✅ **FIXED**
   - **Status:** Added payment validation in `StatusTransitionService.transition_order_to_status()`
   - Validates payment before allowing transition to `in_progress`, `available`, or `pending_writer_assignment`
   - Also added validation in `MarkOrderPaidService.mark_paid()`
   - Enforces: `UNPAID` → (Payment Required) → `PENDING`/`IN_PROGRESS`

5. **Discount Application Inconsistency** ✅ **FIXED**
   - **Status:** Fixed in `OrderPaymentService.create_payment()`
   - If order has discount and no discount_code provided → uses order discount
   - If discount_code provided → applies discount code (overrides order discount)
   - Payment always reflects the final discount applied

6. **Payment Reminders Not Integrated**
   - `PaymentReminderSettings` exists but no task/service to send reminders
   - No automatic reminder system for unpaid orders

7. **Missing Order Expiration on Non-Payment**
   - Orders can sit in `UNPAID` status indefinitely
   - No automatic cancellation after X hours/days without payment

8. **Split Payment Support Incomplete**
   - `SplitPayment` model exists
   - But no endpoint or service to actually create split payments
   - `process_split_payment()` exists but unused

9. **Payment Record vs OrderPayment Confusion** ✅ **CLARIFIED**
    - **Status:** Added documentation to `PaymentRecord` model
    - `PaymentRecord`: Future unified payment tracking (not currently used for orders)
    - `OrderPayment`: Currently used for all order-related payments
    - Clear separation of concerns documented

---

### 🟡 **MEDIUM PRIORITY GAPS:**

11. **Order Status Flow Validation**
    - Order can be created with any status
    - No validation that payment is required before `IN_PROGRESS`
    - Should enforce: `UNPAID` → (Payment) → `PENDING` → `IN_PROGRESS`

12. **Pricing Snapshot on Payment**
    - Price snapshot saved on order creation
    - But not saved when payment is processed (price might change)
    - Should snapshot final paid amount

13. **Failed Payment Retry Logic**
    - `FailedPayment` model tracks retries
    - But no actual retry mechanism/service
    - Retry button/logic missing

14. **Refund to Wallet Integration**
    - `Refund.process_refund()` handles wallet refunds
    - But doesn't create `WalletTransaction` record for audit
    - Should use proper wallet service

15. **Payment Dispute Workflow Incomplete**
    - Dispute model exists
    - But no clear resolution workflow
    - No admin interface for dispute management

---

### 🟢 **LOW PRIORITY IMPROVEMENTS:**

16. **Payment Method Validation** ✅ **FIXED**
    - **Status:** Added `VALID_PAYMENT_METHODS` list in `OrderPaymentService`
    - Validates payment method on payment creation
    - Supports: wallet, manual, stripe, paypal, credit_card, bank_transfer

17. **Currency Support**
    - `PaymentRecord` has `currency` field
    - But order pricing is always in one currency
    - No multi-currency conversion

18. **Payment Receipt Generation**
    - `PaymentReceipt` model exists
    - But no automatic generation on payment completion
    - No email/SMS delivery of receipts

---

## Recommended Implementation Priority

### Phase 1: Critical Fixes
1. ✅ Fix `Order.mark_paid()` to use `OrderPayment` with `status='completed'`
2. ✅ Create `OrderPaymentService` for payment processing
3. ✅ Add unified payment endpoint: `POST /api/v1/order-payments/orders/{id}/pay/`
4. ✅ Fix wallet payment processing (atomic transactions)
5. ✅ Integrate Stripe webhook handlers

### Phase 2: Payment Workflow
6. Add payment reminders (Celery task)
7. Add order expiration for unpaid orders
8. Implement split payment endpoints
9. Add payment receipt generation

### Phase 3: Enhancements
10. Payment dispute workflow
11. Multi-currency support
12. Payment analytics/reporting
13. Automated retry logic for failed payments

---

## Data Flow Diagram

```
Client Request
    ↓
Order Creation (POST /orders/)
    ↓
Order Created (status: CREATED/UNPAID, is_paid: False)
    ↓
[GAP: No clear payment initiation]
    ↓
Payment Initiation (MISSING ENDPOINT)
    ↓
OrderPayment Created (status: pending)
    ↓
Payment Processing (Stripe/Wallet/External)
    ↓
Payment Confirmed (status: completed)
    ↓
Signal: update_order_status()
    ↓
Order.mark_paid() → status: IN_PROGRESS, is_paid: True
    ↓
Order Available for Writer Assignment
```

---

## Key Models Relationships

```
Order (1) ──→ (N) OrderPayment
OrderPayment (1) ──→ (N) Refund
OrderPayment (1) ──→ (N) FailedPayment
OrderPayment (1) ──→ (N) SplitPayment
OrderPayment (1) ──→ (1) PaymentReceipt
Order (1) ──→ (1) PaymentRecord [not used for orders]
```

---

## Notes

- **Order vs Payment Status**: Keep separate - order status tracks workflow, payment status tracks payment state
- **Atomic Transactions**: All payment operations should use `@transaction.atomic`
- **Webhooks**: External payment providers should trigger webhooks to update payment status
- **Audit Trail**: All payment actions logged via `PaymentLog` and `AdminLog`
