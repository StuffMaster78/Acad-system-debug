# Payment Reference Streamlining

## Overview

This document describes the streamlined payment reference system that allows admins to track external payment references (MPESA, PayPal, Stripe, bank transfers, etc.) when marking orders as paid or paying writers.

---

## Features

### 1. **Order Payment Reference Tracking**

When marking orders as paid for client payments that were not captured correctly, admins can now provide:
- **Optional `reference_id`**: External payment reference (MPESA message, PayPal transaction ID, etc.)
- **Optional `payment_method`**: Payment method used (MPESA, PayPal, Stripe, bank_transfer, etc.)

**API Usage:**
```http
POST /api/v1/orders/orders/{id}/action/
Content-Type: application/json

{
  "action": "mark_paid",
  "reference_id": "MPESA_REF_123456789",
  "payment_method": "MPESA"
}
```

**Backend Behavior:**
- If no payment record exists and `reference_id` is provided, creates a new `OrderPayment` record
- Stores `reference_id` in both `transaction_id` and `reference_id` fields
- Stores `payment_method` for tracking
- Marks payment as `completed` and confirms it

### 2. **Writer Payment Reference Tracking**

When paying writers, admins can now provide:
- **Optional `payment_reference_id`**: External payment reference from payment system

**API Usage:**
```http
POST /api/v1/writer-payments-management/writer-payments/clear-pending/
Content-Type: application/json

{
  "payment_ids": [1, 2, 3],
  "payment_reference_id": "MPESA_REF_987654321",
  "mark_as_paid": true
}
```

**Backend Behavior:**
- Stores `payment_reference_id` in `WriterPayment.payment_reference_id`
- Also stores in `transaction_reference` if not already set
- Includes reference in wallet transaction description
- Logs reference in transaction metadata

---

## Database Changes

### **OrderPayment Model**
- Already has `reference_id` and `transaction_id` fields
- Uses `reference_id` when provided for manual payments

### **WriterPayment Model**
- **New field**: `payment_reference_id` (CharField, max_length=255, optional)
- Stores external payment system references
- Used alongside existing `transaction_reference` field

**Migration:**
```python
# backend/writer_payments_management/migrations/0001_add_payment_reference_id.py
migrations.AddField(
    model_name='writerpayment',
    name='payment_reference_id',
    field=models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text='Payment system reference ID (MPESA, PayPal, Stripe, bank transfer, etc.)'
    ),
)
```

---

## Service Updates

### **MarkOrderPaidService**

**Updated Method:**
```python
def mark_paid(
    self, 
    order_id: int, 
    reference_id: str = None, 
    payment_method: str = None
) -> Order:
    """
    Mark an order as paid.
    
    If no payment exists and reference_id is provided, creates payment record.
    """
```

**Key Changes:**
- Accepts optional `reference_id` and `payment_method`
- Creates `OrderPayment` if missing and `reference_id` provided
- Uses `reference_id` as `transaction_id` and `reference_id`
- Sets `payment_method` for tracking

### **WriterPayment.mark_as_paid()**

**Updated Method:**
```python
def mark_as_paid(
    self, 
    admin_user, 
    payment_reference_id: str = None
):
    """
    Mark payment as paid with optional external reference.
    """
```

**Key Changes:**
- Accepts optional `payment_reference_id`
- Stores in `payment_reference_id` field
- Also stores in `transaction_reference` if not set
- Includes reference in transaction description and metadata

---

## Frontend Integration

### **Mark Order as Paid**

When admins mark orders as paid, they can optionally provide:
- Payment reference ID (e.g., MPESA message, PayPal transaction ID)
- Payment method (MPESA, PayPal, Stripe, bank_transfer, etc.)

**Example Form:**
```vue
<template>
  <form @submit.prevent="markOrderPaid">
    <input 
      v-model="referenceId" 
      placeholder="Payment Reference (Optional)"
      type="text"
    />
    <select v-model="paymentMethod">
      <option value="">Select Payment Method</option>
      <option value="MPESA">MPESA</option>
      <option value="PayPal">PayPal</option>
      <option value="Stripe">Stripe</option>
      <option value="bank_transfer">Bank Transfer</option>
    </select>
    <button type="submit">Mark as Paid</button>
  </form>
</template>

<script>
const markOrderPaid = async () => {
  await ordersAPI.executeAction(orderId, {
    action: 'mark_paid',
    reference_id: referenceId.value,
    payment_method: paymentMethod.value
  })
}
</script>
```

### **Pay Writers**

When admins pay writers, they can optionally provide:
- Payment reference ID from the payment system

**Example Form:**
```vue
<template>
  <form @submit.prevent="payWriters">
    <input 
      v-model="paymentReferenceId" 
      placeholder="Payment Reference (Optional)"
      type="text"
    />
    <button type="submit">Mark as Paid</button>
  </form>
</template>

<script>
const payWriters = async () => {
  await writerPaymentsAPI.clearPending({
    payment_ids: selectedPaymentIds.value,
    payment_reference_id: paymentReferenceId.value,
    mark_as_paid: true
  })
}
</script>
```

---

## Benefits

1. **Better Tracking**: External payment references are now tracked for audit purposes
2. **Flexibility**: Optional fields allow gradual adoption
3. **Audit Trail**: All payment references are logged in audit logs
4. **Reconciliation**: Easier to reconcile payments with external systems
5. **Support**: Support team can verify payments using external references

---

## Use Cases

### **Use Case 1: MPESA Payment Not Captured**

**Scenario:** Client paid via MPESA but payment wasn't captured automatically.

**Solution:**
1. Admin receives MPESA confirmation message: "QH7X8K9L - You have received KES 5,000.00 from John Doe"
2. Admin marks order as paid with:
   - `reference_id`: "QH7X8K9L"
   - `payment_method`: "MPESA"
3. System creates `OrderPayment` record with reference
4. Order is marked as paid and moves to `in_progress`

### **Use Case 2: PayPal Payment Reference**

**Scenario:** Client paid via PayPal but webhook failed.

**Solution:**
1. Admin finds PayPal transaction ID: "PAYPAL-TXN-123456789"
2. Admin marks order as paid with:
   - `reference_id`: "PAYPAL-TXN-123456789"
   - `payment_method`: "PayPal"
3. System creates payment record and marks order as paid

### **Use Case 3: Writer Payment via MPESA**

**Scenario:** Admin pays writer via MPESA and wants to track the reference.

**Solution:**
1. Admin receives MPESA confirmation: "QH7X8K9L - You have sent KES 2,000.00 to Writer Name"
2. Admin marks writer payment as paid with:
   - `payment_reference_id`: "QH7X8K9L"
3. System stores reference in `WriterPayment.payment_reference_id`
4. Reference is included in wallet transaction description

---

## Future Enhancements

1. **Payment Method Validation**: Validate payment methods against allowed list
2. **Reference Format Validation**: Validate reference formats per payment method
3. **Duplicate Detection**: Check for duplicate references to prevent double payments
4. **Payment Reconciliation**: Automated reconciliation with external payment systems
5. **Reference Search**: Search orders/payments by external reference ID

