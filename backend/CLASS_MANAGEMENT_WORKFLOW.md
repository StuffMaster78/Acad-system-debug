# Class Management Workflow

## Overview

The class management system supports two ways to create and purchase class bundles:
1. **Bundle Config Purchase**: Client selects a predefined bundle from admin-configured pricing
2. **Admin Manual Entry**: Admin creates a custom bundle with manual pricing, deposits, and installments

All payments are integrated with the unified `OrderPayment` workflow for consistent payment processing.

## Models

### ClassBundle
Represents a bundle of classes purchased by a client.

**Key Fields:**
- `pricing_source`: `'config'` (from bundle config) or `'manual'` (admin-created)
- `total_price`: Total price for the bundle
- `deposit_required`: Deposit amount required (set by admin)
- `deposit_paid`: Amount of deposit already paid
- `balance_remaining`: Remaining balance after deposit (excludes deposit from balance)
- `installments_enabled`: Whether installments are enabled
- `installment_count`: Number of installments (if enabled)
- `created_by_admin`: Admin who created (if manual)

### ClassInstallment
Represents a scheduled installment payment for a class bundle.

**Key Fields:**
- `class_bundle`: Link to ClassBundle
- `amount`: Amount due for this installment
- `due_date`: Date when installment is due
- `is_paid`: Whether installment has been paid
- `payment_record`: Link to `OrderPayment` (unified payment workflow)
- `installment_number`: Sequence number (1, 2, 3, ...)

### ClassPurchase
Represents a payment record for deposits or full payments.

**Key Fields:**
- `bundle`: Link to ClassBundle
- `payment_type`: `'deposit'`, `'full'`, or `'installment'`
- `payment_record`: Link to `OrderPayment` (unified payment workflow)
- `price_locked`: Price at time of payment

## Workflows

### 1. Client Selects Bundle from Config

**Flow:**
1. Client browses available `ClassBundleConfig` options
2. Client selects a bundle (level, duration, bundle_size)
3. System creates `ClassBundle` with `pricing_source='config'`
4. Client pays full amount or deposit (if enabled)
5. If installments enabled, system generates `ClassInstallment` records
6. Client pays installments as they become due

**API Endpoints:**
- `GET /api/v1/class-management/class-bundle-configs/` - Browse available bundles
- `GET /api/v1/class-management/class-bundle-configs/get_class_price/` - Get price
- `POST /api/v1/class-management/class-bundles/` - Create bundle from config
- `POST /api/v1/class-management/class-bundles/{id}/pay_deposit/` - Pay deposit
- `POST /api/v1/class-management/class-installments/{id}/pay_installment/` - Pay installment

### 2. Admin Creates Manual Bundle

**Flow:**
1. Admin creates bundle with custom pricing via `POST /api/v1/class-management/class-bundles/create_manual/`
2. Admin sets:
   - Total price
   - Number of classes
   - Deposit required
   - Whether installments are enabled
   - Number of installments (if enabled)
3. System creates `ClassBundle` with `pricing_source='manual'`
4. If installments enabled, admin can configure them:
   - `POST /api/v1/class-management/class-bundles/{id}/configure_installments/`
   - Set installment count, interval, and optionally specific amounts
5. Client pays deposit and installments as scheduled

**API Endpoints:**
- `POST /api/v1/class-management/class-bundles/create_manual/` - Create manual bundle (admin only)
- `POST /api/v1/class-management/class-bundles/{id}/configure_installments/` - Configure installments (admin only)

## Payment Processing

### Deposit Payment

```python
# Via API
POST /api/v1/class-management/class-bundles/{id}/pay_deposit/
{
    "payment_method": "wallet",  # or "stripe", "manual"
    "discount_code": "optional"
}

# Via Service
payment = ClassPaymentProcessor.process_deposit_payment(
    bundle=bundle,
    client=client,
    payment_method='wallet'
)
```

**Process:**
1. Validates deposit not already paid
2. Creates `OrderPayment` with `payment_type='class_payment'`
3. Creates `ClassPurchase` record linked to payment
4. Processes payment (wallet/gateway)
5. Updates `bundle.deposit_paid` on completion

### Installment Payment

```python
# Via API
POST /api/v1/class-management/class-installments/{id}/pay_installment/
{
    "payment_method": "wallet",
    "discount_code": "optional"
}

# Via Service
payment = ClassPaymentProcessor.process_installment_payment(
    installment=installment,
    client=client,
    payment_method='wallet'
)
```

**Process:**
1. Validates installment not already paid
2. Validates deposit is paid first
3. Creates `OrderPayment` with `payment_type='class_payment'` and `related_object_id=installment.id`
4. Processes payment (wallet/gateway)
5. Links payment to `ClassInstallment.payment_record`
6. Marks installment as paid
7. Updates bundle balance

### Full Payment (No Installments)

For bundles without installments, client can pay full amount:

```python
payment = ClassPaymentProcessor.process_full_payment(
    bundle=bundle,
    client=client,
    payment_method='wallet'
)
```

## Admin Services

### Create Manual Bundle

```python
from class_management.services.class_bundle_admin import ClassBundleAdminService

bundle = ClassBundleAdminService.create_manual_bundle(
    client=client,
    website=website,
    admin_user=admin,
    total_price=Decimal('500.00'),
    number_of_classes=5,
    deposit_required=Decimal('100.00'),
    installments_enabled=True,
    installment_count=4,
    duration='15-16',
    level='grad'
)
```

### Configure Installments

```python
bundle = ClassBundleAdminService.configure_installments(
    bundle=bundle,
    admin_user=admin,
    installment_count=4,
    interval_weeks=2,
    amounts=None  # Optional: [100, 100, 100, 100] for custom amounts
)
```

### Update Pricing

```python
bundle = ClassBundleAdminService.update_bundle_pricing(
    bundle=bundle,
    admin_user=admin,
    total_price=Decimal('600.00'),
    deposit_required=Decimal('150.00')
)
# Note: Can only update if no payments have been made
```

## Payment Identification

All class payments are tracked via `OrderPayment` with:

- **payment_type**: `'class_payment'`
- **class_purchase**: FK to `ClassPurchase` (for deposits/full payments)
- **related_object_id**: 
  - `bundle.id` for deposits/full payments
  - `installment.id` for installment payments
- **related_object_type**: 
  - `'class_bundle_deposit'` for deposits
  - `'class_bundle_full'` for full payments
  - `'class_installment'` for installments

Query payments by type:
```python
# Get all class payments
payments = OrderPayment.objects.filter(payment_type='class_payment')

# Get payments for a specific bundle
payments = OrderPayment.objects.filter(
    class_purchase__bundle_id=bundle.id
)

# Get installment payments
payments = OrderPayment.objects.filter(
    related_object_type='class_installment',
    related_object_id=installment.id
)
```

## Bundle Status Flow

1. **Created** → `status='in_progress'`
2. **Deposit Paid** → `has_deposit_paid=True` (if deposit required)
3. **Installments Paid** → `is_fully_paid=True` (if installments enabled)
4. **Completed** → `status='completed'` (all classes done)

## Key Features

### Deposit System
- Admin sets `deposit_required` for each bundle
- Deposit must be paid before installments can be paid
- Deposit is separate from installment balance
- `balance_remaining = total_price - deposit_required - installments_paid`

### Installment System
- Admin configures installments with:
  - Count (number of installments)
  - Interval (weeks between installments)
  - Optional custom amounts per installment
- Installments have due dates
- Installments can be paid individually
- System tracks which installments are overdue

### Manual Pricing
- Admin can set any price (not limited to config)
- Useful for custom classes or special pricing
- Still supports deposits and installments
- Tracked via `pricing_source='manual'` and `created_by_admin`

## Validation Rules

1. **Deposit**: Cannot exceed total price
2. **Installments**: Can only be enabled if `total_price > deposit_required`
3. **Installment Amounts**: Must sum to `total_price - deposit_required`
4. **Payment Order**: Deposit must be paid before installments
5. **Pricing Updates**: Cannot update pricing after payments are made
6. **Installment Reconfiguration**: Cannot reconfigure after installments are paid

## Integration with Unified Payment Workflow

All class payments use `OrderPayment` for:
- Consistent payment processing (wallet/gateway)
- Unified refund handling
- Payment analytics and reporting
- Gateway integration (when implemented)

Class-specific tracking via:
- `ClassPurchase` for deposit/full payment records
- `ClassInstallment.payment_record` for installment payments
- Both link to `OrderPayment` for unified workflow

