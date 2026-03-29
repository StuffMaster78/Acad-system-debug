# Streamlined Writer Payment & Bonus System

## Overview

This system streamlines how admins award writer bonuses and class payments. Key features:
- **Admin Control**: Admins can manually set payment amounts
- **Direct Wallet Deposit**: Option to add payments directly to writer's wallet
- **Privacy**: Writers cannot see what clients paid for classes
- **Unified Service**: Single service handles all payment awarding

---

## Key Components

### 1. **WriterPaymentAwardService**
Located in: `backend/writer_management/services/writer_payment_award_service.py`

Provides unified methods:
- `award_bonus()` - Award any type of bonus to a writer
- `award_class_payment()` - Award payment for a class bundle
- `pay_bonus()` - Mark existing bonus as paid and optionally add to wallet

### 2. **WriterPaymentAwardViewSet**
Located in: `backend/writer_management/views/writer_payment_award_views.py`

Provides REST API endpoints:
- `POST /api/v1/writer-management/writer-payment-awards/award-bonus/` - Award bonus
- `POST /api/v1/writer-management/writer-payment-awards/award-class-payment/` - Award class payment
- `POST /api/v1/writer-management/writer-payment-awards/pay-bonus/` - Pay existing bonus

### 3. **Enhanced Existing ViewSets**
- `WriterBonusViewSet` - Now supports `add_to_wallet` and streamlined payment
- `ClassPaymentViewSet` - New `award_writer_payment` action

---

## API Endpoints

### **Award Bonus**

**Endpoint:** `POST /api/v1/writer-management/writer-payment-awards/award-bonus/`

**Request:**
```json
{
  "writer_id": 123,
  "amount": 100.00,
  "category": "performance",  // performance, order_completion, client_tip, class_payment, other
  "reason": "Outstanding work on recent orders",
  "special_order_id": 456,  // Optional
  "class_bundle_id": 789,  // Optional
  "add_to_wallet": true  // If true, add directly to wallet
}
```

**Response:**
```json
{
  "bonus_id": 1,
  "writer_id": 123,
  "writer_username": "writer123",
  "amount": 100.00,
  "category": "performance",
  "is_paid": true,
  "added_to_wallet": true,
  "wallet_balance": 250.00
}
```

---

### **Award Class Payment**

**Endpoint:** `POST /api/v1/writer-management/writer-payment-awards/award-class-payment/`

**Request:**
```json
{
  "class_payment_id": 123,
  "amount": 150.00,  // Optional, uses class_payment.writer_compensation_amount if not provided
  "add_to_wallet": true
}
```

**Response:**
```json
{
  "payment_id": 1,
  "bonus_id": 2,
  "class_payment_id": 123,
  "class_bundle_id": 456,
  "writer_id": 789,
  "writer_username": "writer789",
  "amount": 150.00,
  "is_paid": true,
  "added_to_wallet": true,
  "wallet_balance": 400.00
}
```

---

### **Pay Bonus**

**Endpoint:** `POST /api/v1/writer-management/writer-payment-awards/pay-bonus/`

**Request:**
```json
{
  "bonus_id": 1,
  "add_to_wallet": true
}
```

**Response:**
```json
{
  "bonus_id": 1,
  "writer_id": 123,
  "writer_username": "writer123",
  "amount": 100.00,
  "category": "performance",
  "added_to_wallet": true,
  "wallet_balance": 350.00
}
```

---

### **Enhanced WriterBonusViewSet**

**Create Bonus with Wallet:**
```json
POST /api/v1/special-orders/writer-bonuses/
{
  "writer": 123,
  "amount": 100.00,
  "category": "performance",
  "reason": "Great work",
  "add_to_wallet": true
}
```

**Pay Bonus:**
```json
POST /api/v1/special-orders/writer-bonuses/{id}/pay/
{
  "add_to_wallet": true
}
```

---

### **Enhanced ClassPaymentViewSet**

**Award Writer Payment:**
```json
POST /api/v1/class-management/class-payments/{id}/award-writer-payment/
{
  "amount": 150.00,  // Optional
  "add_to_wallet": true
}
```

---

## Privacy Features

### **Writers Cannot See Client Payment Amounts**

1. **Class Payment Serializers:**
   - `ClassPaymentDetailSerializer` - Hides client payment fields for writers
   - `ClassPaymentSummarySerializer` - Hides client payment fields for writers
   - Removed fields for writers:
     - `total_amount` (client payment)
     - `deposit_amount`
     - `balance_remaining`
     - `client_payment_status`
     - `payment_progress`
     - `installments` (client payment details)

2. **Writer Payment View Serializer:**
   - `get_class_bonuses()` - Only shows writer compensation, not client payment
   - Removed `total_amount`, `client_payment_status`, installment details

3. **Result:**
   - Writers see: Their compensation amount, payment status, when they were paid
   - Writers don't see: What client paid, deposit amounts, payment progress, installment details

---

## Workflow Examples

### **Example 1: Award Performance Bonus**

```bash
POST /api/v1/writer-management/writer-payment-awards/award-bonus/
{
  "writer_id": 123,
  "amount": 50.00,
  "category": "performance",
  "reason": "Completed 10 orders this month with 5-star ratings",
  "add_to_wallet": true
}
```

**What Happens:**
1. Creates `WriterBonus` record
2. Adds $50 to writer's wallet
3. Creates `WalletTransaction` record
4. Returns bonus info with wallet balance

---

### **Example 2: Award Class Payment**

```bash
POST /api/v1/writer-management/writer-payment-awards/award-class-payment/
{
  "class_payment_id": 456,
  "amount": 200.00,
  "add_to_wallet": true
}
```

**What Happens:**
1. Creates or updates `ClassWriterPayment` record
2. Creates `WriterBonus` with category `class_payment`
3. Links bonus to class payment
4. Adds $200 to writer's wallet
5. Updates class payment status to `paid`
6. Returns payment info

---

### **Example 3: Pay Existing Bonus**

```bash
POST /api/v1/writer-management/writer-payment-awards/pay-bonus/
{
  "bonus_id": 789,
  "add_to_wallet": true
}
```

**What Happens:**
1. Marks `WriterBonus` as paid
2. Adds amount to writer's wallet
3. Creates `WalletTransaction` record
4. Returns payment confirmation

---

## Benefits

1. **Streamlined Process**: Single service handles all payment awarding
2. **Flexible Payment**: Manual amount or use existing compensation
3. **Direct Wallet Deposit**: Option to add directly to wallet in one step
4. **Privacy**: Writers cannot see client payment amounts
5. **Audit Trail**: All payments tracked via `WriterBonus` and `WalletTransaction`
6. **Backward Compatible**: Existing endpoints still work

---

## Migration Guide

### **For Existing Code**

The streamlined service is **additive** - existing code continues to work. To migrate:

1. **Replace manual bonus creation:**
   ```python
   # Old
   bonus = WriterBonus.objects.create(
       writer=writer,
       amount=100,
       category='performance'
   )
   
   # New (with wallet)
   WriterPaymentAwardService.award_bonus(
       writer_id=writer.id,
       amount=100,
       category='performance',
       add_to_wallet=True,
       website=website,
       admin_user=admin
   )
   ```

2. **Replace class payment scheduling:**
   ```python
   # Old
   ClassPaymentService._schedule_writer_payment(payment)
   
   # New (with wallet)
   WriterPaymentAwardService.award_class_payment(
       class_payment_id=payment.id,
       add_to_wallet=True,
       website=website,
       admin_user=admin
   )
   ```

---

## Security & Permissions

- **Admin Only**: All award/payment endpoints require `IsAdminUser`
- **Writer View**: Writers can view their own bonuses but cannot see client payment amounts
- **Audit Logging**: All payments logged with admin user who awarded them
- **Transaction Safety**: All operations use database transactions

---

## Future Enhancements

1. **Bulk Operations**: Award bonuses to multiple writers at once
2. **Payment Templates**: Pre-configured payment amounts for common scenarios
3. **Automated Payments**: Auto-pay bonuses when certain conditions are met
4. **Payment Scheduling**: Schedule payments for future dates
5. **Payment History**: Enhanced history view for writers

