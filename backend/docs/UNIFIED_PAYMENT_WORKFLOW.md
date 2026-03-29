# Unified Payment Workflow

## Overview

The payment system now supports a unified workflow for all payment types through the `OrderPayment` model. Each payment type is properly identified using `payment_type` and related ForeignKeys, allowing clear distinction between different payment sources.

## Payment Types

### 1. Standard Order Payments
- **payment_type**: `"standard"`
- **Related FK**: `order` → `Order` model
- **Use Case**: Regular writing order payments

### 2. Special Order Payments (Deposit/Full)
- **payment_type**: `"predefined_special"` or `"estimated_special"`
- **Related FK**: `special_order` → `SpecialOrder` model
- **Use Case**: Initial deposit or full payment for special orders

### 3. Special Order Installment Payments
- **payment_type**: `"special_installment"`
- **Related FK**: `special_order` → `SpecialOrder` model
- **Metadata**: `related_object_id` = `installment_payment.id`, `related_object_type` = `"installment_payment"`
- **Use Case**: Individual installment payments for special orders

### 4. Class Bundle Payments
- **payment_type**: `"class_payment"`
- **Related FK**: `class_purchase` → `ClassPurchase` model
- **Use Case**: Class bundle purchase payments

### 5. Wallet Loading/Top-up
- **payment_type**: `"wallet_loading"`
- **No order relationships**: Standalone payment for wallet credit
- **Use Case**: Client adding funds to wallet

## Payment Identification

Each payment can be uniquely identified using:

```python
# Get payment identifier dict
identifier = OrderPaymentService.get_payment_identifier(payment)

# Returns:
{
    'payment_type': 'standard',  # or 'special_installment', etc.
    'payment_id': 123,
    'order_id': 456,  # if standard order
    'special_order_id': None,  # if special order payment
    'class_purchase_id': None,  # if class payment
    'installment_id': 789,  # if installment payment
    'related_object': None,  # or 'wallet_loading'
}
```

## Database Schema

### OrderPayment Model Fields

```python
class OrderPayment(models.Model):
    # Core fields
    payment_type = CharField(choices=PAYMENT_TYPE_CHOICES)
    client = ForeignKey(User)
    website = ForeignKey(Website)
    
    # Relationship FKs (only one set per payment_type)
    order = ForeignKey(Order, null=True)  # for 'standard'
    special_order = ForeignKey(SpecialOrder, null=True)  # for special orders
    class_purchase = ForeignKey(ClassPurchase, null=True)  # for 'class_payment'
    
    # Metadata for installments/wallet
    related_object_id = PositiveIntegerField(null=True)
    related_object_type = CharField(null=True)
    
    # Payment details
    amount = DecimalField()
    original_amount = DecimalField()
    discounted_amount = DecimalField()
    status = CharField(choices=STATUS_CHOICES)
    payment_method = CharField()
    # ... other fields
```

### InstallmentPayment Model

```python
class InstallmentPayment(models.Model):
    special_order = ForeignKey(SpecialOrder)
    amount_due = DecimalField()
    is_paid = BooleanField()
    
    # Link to actual payment transaction
    payment_record = ForeignKey(OrderPayment, null=True)
    
    def mark_paid(self, payment_record=None):
        """Link installment to OrderPayment when paid."""
        self.payment_record = payment_record
        self.is_paid = True
        # ...
```

## API Endpoints

### Standard Order Payment
```http
POST /api/v1/order-payments/orders/{order_id}/initiate/
{
    "payment_method": "wallet",
    "discount_code": "optional"
}
```

### Special Order Installment Payment
```http
POST /api/v1/special-orders/installments/{installment_id}/pay_installment/
{
    "payment_method": "wallet",
    "discount_code": "optional"
}
```

### Query Payments by Type
```http
GET /api/v1/order-payments/?payment_type=standard
GET /api/v1/order-payments/?payment_type=special_installment
GET /api/v1/order-payments/?order_id=123
GET /api/v1/order-payments/?special_order_id=456
GET /api/v1/order-payments/?installment_id=789
GET /api/v1/order-payments/by_type/?payment_type=wallet_loading
```

## Service Layer

### OrderPaymentService
Handles standard order payments with discount application.

```python
payment = OrderPaymentService.create_payment(
    order=order,
    client=user,
    payment_method='wallet',
    discount_code='SAVE10'
)

payment = OrderPaymentService.process_wallet_payment(payment)
```

### SpecialOrderInstallmentPaymentService
Handles installment payments for special orders.

```python
payment = SpecialOrderInstallmentPaymentService.process_installment_payment(
    installment=installment,
    client=user,
    payment_method='wallet'
)
```

### UnifiedPaymentService
General-purpose service for creating any payment type.

```python
# Wallet loading
payment = UnifiedPaymentService.create_wallet_loading_payment(
    client=user,
    website=website,
    amount=Decimal('100.00'),
    payment_method='stripe'
)

# Confirm wallet loading
payment = UnifiedPaymentService.confirm_wallet_loading_payment(
    payment=payment,
    external_id='stripe_pi_xxx'
)
```

## Payment Processing Flow

### 1. Standard Order Payment
```
1. Client initiates payment via API
2. OrderPaymentService.create_payment() creates OrderPayment (payment_type='standard')
3. DiscountEngine applies discounts if discount_code provided
4. If payment_method='wallet': OrderPaymentService.process_wallet_payment()
5. Payment status → 'completed'
6. Order.mark_paid() called automatically
```

### 2. Special Order Installment Payment
```
1. Client initiates installment payment via API
2. SpecialOrderInstallmentPaymentService.process_installment_payment()
3. Creates OrderPayment (payment_type='special_installment', related_object_id=installment.id)
4. Processes payment (wallet/gateway)
5. Links payment to InstallmentPayment via payment_record FK
6. Marks installment as paid
7. Checks if all installments paid → updates special order status
```

### 3. Wallet Loading
```
1. Client initiates wallet top-up via API
2. UnifiedPaymentService.create_wallet_loading_payment()
3. Creates OrderPayment (payment_type='wallet_loading', no order relationships)
4. Processes via gateway (Stripe/PayPal)
5. On confirmation: UnifiedPaymentService.confirm_wallet_loading_payment()
6. Credits wallet balance
7. Payment status → 'completed'
```

## Validation Rules

The `OrderPayment.clean()` method enforces:

1. **Payment Type Matching**: Each `payment_type` must have the correct related FK set:
   - `standard` → requires `order_id`
   - `predefined_special` / `estimated_special` → requires `special_order_id`
   - `special_installment` → requires `related_object_id` (installment.id)
   - `class_payment` → requires `class_purchase_id`
   - `wallet_loading` → no order relationships allowed

2. **Duplicate Payment Prevention**: Standard orders cannot have multiple completed payments

3. **Status Transitions**: Payments can only transition through valid states

## Database Indexes

Optimized indexes for efficient querying:

```python
class Meta:
    indexes = [
        models.Index(fields=['payment_type', 'order_id']),
        models.Index(fields=['payment_type', 'special_order_id']),
        models.Index(fields=['payment_type', 'class_purchase_id']),
        models.Index(fields=['client', 'status']),
        models.Index(fields=['related_object_type', 'related_object_id']),
    ]
```

## Benefits of Unified Workflow

1. **Single Source of Truth**: All payments tracked in `OrderPayment`
2. **Consistent Processing**: Same payment methods (wallet/gateway) for all types
3. **Easy Filtering**: Query by `payment_type` and related IDs
4. **Clear Identification**: Each payment type has distinct identification
5. **Unified Refunds**: Same refund process for all payment types
6. **Audit Trail**: All payments in one place for reporting
7. **Gateway Integration**: Single integration point for all payment types

## Migration Notes

When migrating existing data:

1. **Special Order Installments**: Update existing `InstallmentPayment` records to link to `OrderPayment` via `payment_record` FK
2. **Class Purchases**: Create `OrderPayment` records for existing class purchases with `payment_type='class_payment'`
3. **Wallet Transactions**: Consider creating `OrderPayment` records for historical wallet loads

## Future Enhancements

1. Payment gateway integration (Stripe/PayPal) for all payment types
2. Payment analytics dashboard showing breakdown by type
3. Automated refund processing for all payment types
4. Payment reconciliation reports by payment_type

