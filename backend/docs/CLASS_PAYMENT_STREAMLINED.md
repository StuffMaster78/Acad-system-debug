# Streamlined Class Payment and Installment System

## Overview

This document describes the streamlined class payment and installment tracking system that provides a unified view of class payments, installments, and writer compensation.

## Architecture

### Models

#### 1. ClassPayment
Central model that tracks:
- **Client Payments**: Total amount, deposit, balance, payment status
- **Writer Compensation**: Compensation amount, paid amount, payment status
- **Installment Tracking**: Number of installments, paid installments
- **Status Management**: Automatic status updates based on payments

#### 2. ClassPaymentInstallment
Links `ClassInstallment` to `ClassPayment` for streamlined tracking:
- Tracks installment payment status
- Links to `OrderPayment` records
- Provides unified view of all installments

#### 3. ClassWriterPayment
Tracks individual writer payments:
- Links to `WriterBonus` records
- Supports full, partial, and installment-based payments
- Tracks payment status and timing

### Service Layer

#### ClassPaymentService
Provides unified methods for:
- Creating payment records for bundles
- Recording installment payments
- Updating payment statuses
- Scheduling writer payments
- Retrieving payment details

## Key Features

### 1. Unified Payment Tracking
- Single source of truth for class payments
- Links client payments, installments, and writer compensation
- Automatic status updates

### 2. Installment Management
- Tracks all installments in one place
- Shows payment progress
- Links to actual payment transactions

### 3. Writer Compensation
- Automatic calculation based on bundle pricing
- Supports installment-based writer payments
- Links to WriterBonus records

### 4. Streamlined API
- `/api/v1/class-management/class-payments/` - List all payments
- `/api/v1/class-management/class-payments/bundle/{id}/` - Get bundle payment details
- `/api/v1/class-management/class-payments/writer/{id}/` - Get writer's class payments

## Usage

### Creating Payment Record

```python
from class_management.services.class_payment_service import ClassPaymentService

# When bundle is created or writer assigned
payment = ClassPaymentService.create_payment_for_bundle(bundle, writer)
```

### Recording Installment Payment

```python
# When installment is paid
ClassPaymentService.record_installment_payment(installment, payment_record)
```

### Getting Payment Details

```python
# Get comprehensive payment details
details = ClassPaymentService.get_payment_details(bundle_id)
```

### Getting Writer Payments

```python
# Get all class payments for a writer
payments = ClassPaymentService.get_writer_class_payments(writer)
```

## Integration Points

### 1. Class Bundle Assignment
When a writer is assigned to a class bundle:
- `ClassPayment` record is created/updated
- Writer compensation is calculated
- Payment status is initialized

### 2. Installment Payment Processing
When an installment is paid:
- `ClassPaymentInstallment` is created/updated
- `ClassPayment` status is updated
- Writer payment is scheduled if bundle is fully paid

### 3. Writer Dashboard
The writer dashboard now shows:
- Class payments with installment details
- Payment progress
- Writer payment status
- Installment breakdown

## Benefits

1. **Streamlined Tracking**: All payment information in one place
2. **Clear Installment Details**: Easy to see which installments are paid
3. **Automatic Status Updates**: Payment statuses update automatically
4. **Writer Visibility**: Writers can see their class payment status
5. **Admin Control**: Admins can view and manage all payments

## Migration Path

1. Run migrations to create new models
2. Existing bundles will get `ClassPayment` records when accessed
3. Existing installments will be linked automatically
4. Writer bonuses are preserved for backward compatibility

## API Endpoints

### List Payments
```
GET /api/v1/class-management/class-payments/
```

### Get Bundle Payment Details
```
GET /api/v1/class-management/class-payments/bundle/{bundle_id}/
```

### Get Writer Payments
```
GET /api/v1/class-management/class-payments/writer/{writer_id}/
```

### Refresh Payment Status (Admin)
```
POST /api/v1/class-management/class-payments/{id}/refresh_status/
```

### Schedule Writer Payment (Admin)
```
POST /api/v1/class-management/class-payments/{id}/schedule_writer_payment/
```

## Response Format

### Payment Details Response
```json
{
  "id": 1,
  "bundle_id": 123,
  "bundle_status": "in_progress",
  "number_of_classes": 10,
  "assigned_writer_username": "writer1",
  "total_amount": "1000.00",
  "deposit_amount": "200.00",
  "deposit_paid": "200.00",
  "balance_remaining": "600.00",
  "client_payment_status": "partial",
  "payment_progress": 40.0,
  "writer_compensation_amount": "600.00",
  "writer_paid_amount": "0.00",
  "writer_payment_status": "pending",
  "uses_installments": true,
  "total_installments": 4,
  "paid_installments": 1,
  "installments": [
    {
      "id": 1,
      "installment_number": 1,
      "amount": "200.00",
      "is_paid": true,
      "paid_at": "2024-01-15T10:00:00Z",
      "due_date": "2024-01-15"
    }
  ],
  "writer_payments": []
}
```

## Future Enhancements

1. Installment-based writer payments (pay writer as installments are paid)
2. Payment reminders and notifications
3. Payment analytics and reporting
4. Automated payment scheduling

