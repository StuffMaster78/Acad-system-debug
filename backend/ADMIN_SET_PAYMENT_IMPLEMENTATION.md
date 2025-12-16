# Admin-Set Payment Implementation

## Overview
Updated the payment system so that admins can set payment amounts/percentages when assigning writers, and classes are paid as bonuses.

## Changes Made

### 1. SpecialOrder Model (`backend/special_orders/models.py`)
**Added fields:**
- `writer_payment_amount` (DecimalField): Fixed payment amount set by admin when assigning writer
- `writer_payment_percentage` (DecimalField): Payment percentage of order total set by admin when assigning writer

**Migration Required:**
```python
# Run: python manage.py makemigrations special_orders --name add_writer_payment_fields
# Or create manually:
class Migration(migrations.Migration):
    dependencies = [...]
    
    operations = [
        migrations.AddField(
            model_name='specialorder',
            name='writer_payment_amount',
            field=models.DecimalField(
                max_digits=10,
                decimal_places=2,
                null=True,
                blank=True,
                help_text="Fixed payment amount for the writer (set by admin when assigning)."
            ),
        ),
        migrations.AddField(
            model_name='specialorder',
            name='writer_payment_percentage',
            field=models.DecimalField(
                max_digits=5,
                decimal_places=2,
                null=True,
                blank=True,
                help_text="Payment percentage of order total for the writer (set by admin when assigning)."
            ),
        ),
    ]
```

### 2. Order Assignment Service (`backend/orders/services/assignment.py`)
**Updated:**
- `assign_writer()` now accepts `writer_payment_amount` parameter
- Sets `order.writer_compensation` if payment amount provided by admin

### 3. Special Order Assignment Service (`backend/special_orders/services/writer_assignment.py`)
**Updated:**
- `assign_writer()` now accepts `payment_amount` and `payment_percentage` parameters
- Validates that only one is provided (not both)
- Sets the appropriate field on SpecialOrder

### 4. Assignment Views Updated

#### Regular Orders:
- **`WriterOrderRequestViewSet.assign_from_request`**: Accepts `writer_payment_amount` in request
- **`AdminOrderManagementViewSet.bulk_assign`**: Accepts `writer_payment_amount` or `writer_payment_amounts` (per-order dict)
- **`WriterOrderRequestViewSet.approve`**: Accepts `writer_payment_amount` in request

#### Special Orders:
- **`SpecialOrderViewSet.assign_writer`** (NEW): Admin endpoint to assign writer with payment
  - Accepts `writer_id`, `payment_amount` OR `payment_percentage`, `admin_notes`
  - Endpoint: `POST /api/v1/special-orders/{id}/assign_writer/`

#### Classes:
- **`ExpressClassViewSet.assign_writer`**: Updated to accept `bonus_amount`
  - Creates `WriterBonus` with category `'class_payment'`
  - Classes are paid as bonuses, not regular earnings

### 5. Writer Payment View (`backend/writer_management/views_dashboard.py`)
**Updated:**
- `get_payment_info()` endpoint shows:
  - Admin-set payment amounts (from `order.writer_compensation` or `special_order.writer_payment_amount/percentage`)
  - Falls back to level-based calculation if admin hasn't set payment
  - Classes shown as bonuses in `class_bonuses` field
  - Total bonuses includes class bonuses

### 6. Payment Calculation (`backend/writer_payments_management/models.py`)
**Updated `WriterPayment.process_payment()`:**
- For regular orders: Uses `order.writer_compensation` if set, otherwise calculates from level
- For special orders: Uses `special_order.writer_payment_amount` or `writer_payment_percentage` if set, otherwise calculates from level

### 7. Writer Payment View Serializer (`backend/writer_management/serializers.py`)
**Updated `WriterPaymentViewSerializer`:**
- `get_order_earnings()`: Uses admin-set `order.writer_compensation` if available
- `get_special_order_earnings()`: Uses admin-set payment amount/percentage if available
- `get_class_bonuses()`: Returns class payments as bonuses (not regular earnings)
- Shows `payment_set_by` field indicating whether payment was set by admin or calculated from level

## How It Works

### Regular Orders:
1. Admin assigns writer via any assignment endpoint
2. Admin can optionally provide `writer_payment_amount` in request
3. If provided, `order.writer_compensation` is set
4. Writer sees this amount in their payment view (not calculated from level)
5. If not provided, payment is calculated from writer's level (fallback)

### Special Orders:
1. Admin assigns writer via `POST /api/v1/special-orders/{id}/assign_writer/`
2. Admin provides either:
   - `payment_amount`: Fixed dollar amount
   - `payment_percentage`: Percentage of order total
3. Writer sees this amount in their payment view
4. If not provided, payment is calculated from writer's level (fallback)

### Classes:
1. Admin assigns writer via `POST /api/v1/express-classes/{id}/assign_writer/`
2. Admin provides `bonus_amount` (required)
3. System creates a `WriterBonus` with category `'class_payment'`
4. Writer sees this in their `class_bonuses` list (not in regular earnings)
5. Included in `total_bonuses` calculation

## API Examples

### Assign Writer to Regular Order with Payment:
```http
POST /api/v1/writer-order-requests/{id}/assign/
{
  "writer_payment_amount": 75.00,
  "reason": "Assigned by admin"
}
```

### Assign Writer to Special Order with Fixed Amount:
```http
POST /api/v1/special-orders/{id}/assign_writer/
{
  "writer_id": 123,
  "payment_amount": 200.00,
  "admin_notes": "Special handling required"
}
```

### Assign Writer to Special Order with Percentage:
```http
POST /api/v1/special-orders/{id}/assign_writer/
{
  "writer_id": 123,
  "payment_percentage": 15.5,
  "admin_notes": "15.5% of order total"
}
```

### Assign Writer to Class (as Bonus):
```http
POST /api/v1/express-classes/{id}/assign_writer/
{
  "writer_id": 123,
  "bonus_amount": 150.00,
  "admin_notes": "Class payment"
}
```

## Writer Payment View Response

```json
{
  "cost_per_page": "5.00",
  "cost_per_slide": "3.00",
  "cost_per_class": null,
  "level_name": "Intermediate",
  "earning_mode": "fixed_per_page",
  "order_earnings": [
    {
      "order_id": 123,
      "order_topic": "Essay on History",
      "pages": 5,
      "slides": 0,
      "amount": 75.00,
      "payment_set_by": "admin",  // or "level"
      "completed_at": "2025-01-15T10:30:00Z"
    }
  ],
  "special_order_earnings": [
    {
      "special_order_id": 456,
      "order_title": "Custom Research Project",
      "amount": 200.00,
      "bonus": 0.00,
      "total": 200.00,
      "payment_set_by": "admin_amount",  // or "admin_percentage" or "level"
      "completed_at": "2025-01-20T14:00:00Z"
    }
  ],
  "class_bonuses": [
    {
      "class_id": null,
      "class_title": "Class Bonus - Payment for class: Advanced Writing",
      "amount": 150.00,
      "bonus_type": "class_payment",
      "granted_at": "2025-01-18T09:00:00Z"
    }
  ],
  "total_earnings": "275.00",  // Orders + Special Orders (classes not included)
  "total_bonuses": "150.00",  // Includes class bonuses
  "total_tips": "0.00"
}
```

## Key Points

1. **Admin Control**: Admins can set custom payment amounts when assigning, overriding level-based calculations
2. **Fallback**: If admin doesn't set payment, system uses level-based calculation
3. **Classes as Bonuses**: Classes are always paid as bonuses, never as regular earnings
4. **Installments Hidden**: Writers never see installment information
5. **Transparency**: Writers can see if payment was set by admin or calculated from level

## Testing Checklist

- [ ] Test assigning regular order with payment amount
- [ ] Test assigning regular order without payment (should use level calculation)
- [ ] Test assigning special order with fixed amount
- [ ] Test assigning special order with percentage
- [ ] Test assigning special order without payment (should use level calculation)
- [ ] Test assigning class with bonus amount
- [ ] Verify classes appear in bonuses, not regular earnings
- [ ] Verify installments are excluded from writer views
- [ ] Verify payment_set_by field shows correct source
- [ ] Test bulk assignment with payment amounts

## Migration Command

```bash
cd backend
python manage.py makemigrations special_orders --name add_writer_payment_fields
python manage.py migrate
```
