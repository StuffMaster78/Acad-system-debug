# Tipping Workflow Implementation

## Overview

Complete tipping workflow implementation supporting:
- **Direct tips**: Clients can tip writers directly
- **Order-based tips**: Clients can tip writers for specific orders
- **Class/task-based tips**: Clients can tip writers for class bundles or tasks
- **Writer privacy**: Writers only see their share, not platform profit or full tip amount
- **Admin configuration**: Admins set tip percentages per writer level
- **Payment processing**: Integrated with payment system

## Implementation Status

### ✅ Completed

1. **Tip Model** (`writer_management/models/tipping.py`)
   - Supports optional order (for direct tips)
   - Supports class/task-based tips via `related_entity_type` and `related_entity_id`
   - Tracks payment status and payment record
   - Stores writer percentage and split amounts

2. **TipService** (`writer_management/services/tip_service.py`)
   - `create_tip()`: Creates tips with automatic split calculation
   - `process_tip_payment()`: Processes payment for tips
   - `compute_split()`: Calculates writer share based on writer level
   - `get_writer_level()`: Fetches writer's current level

3. **Serializers** (`writer_management/serializers.py`)
   - `TipCreateSerializer`: Supports all tip types (direct, order-based, class-based)
   - `TipListSerializer`: Writer-safe (writers only see their share)
   - `TipDetailSerializer`: Detailed view with role-based field visibility

4. **Views** (`writer_management/views/tips.py`)
   - `TipViewSet`: Full CRUD with filtering
   - `process_payment` action: Process payment for pending tips
   - Filtering by tip_type, order_id, related_entity

5. **Payment Integration**
   - Added 'tip' to `PAYMENT_TYPE_CHOICES`
   - `UnifiedPaymentService.create_tip_payment()`: Creates tip payment records

### ⚠️ Requires Migration

The Tip model has been updated with new fields. **A migration must be created and applied:**

```bash
python manage.py makemigrations writer_management
python manage.py migrate
```

### 📋 Remaining Tasks

1. **Admin Endpoints for Tip Percentage Management**
   - Writer levels already have `tip_percentage` field
   - Admins can manage via `WriterLevelConfigViewSet` at `/api/v1/writer-management/writer-level-configs/`
   - Consider adding dedicated tip percentage management endpoint if needed

2. **Frontend Integration**
   - Update frontend API to support new tip endpoints
   - Create UI for:
     - Direct tipping
     - Order-based tipping
     - Class/task-based tipping
     - Tip history (writer-safe view)

3. **Testing**
   - Test direct tips
   - Test order-based tips
   - Test class-based tips
   - Test payment processing
   - Test writer privacy (writers don't see platform profit)

## API Endpoints

### Create Tip
```http
POST /api/v1/writer-management/tips/
Content-Type: application/json

{
  "writer_id": 123,
  "tip_amount": "50.00",
  "tip_reason": "Great work!",
  "payment_method": "wallet",
  
  // For order-based tip:
  "order_id": 456,
  
  // OR for class/task-based tip:
  "related_entity_type": "class_bundle",
  "related_entity_id": 789,
  
  // OR omit both for direct tip
}
```

### List Tips
```http
GET /api/v1/writer-management/tips/
GET /api/v1/writer-management/tips/?tip_type=direct
GET /api/v1/writer-management/tips/?order_id=456
GET /api/v1/writer-management/tips/?related_entity_type=class_bundle&related_entity_id=789
```

### Get Tip Details
```http
GET /api/v1/writer-management/tips/{id}/
```

### Process Tip Payment
```http
POST /api/v1/writer-management/tips/{id}/process_payment/
{
  "payment_method": "wallet",
  "discount_code": "optional"
}
```

## Writer Privacy

**Writers only see:**
- `amount_received`: Their share (writer_earning)
- Tip reason
- Client name
- Related order/class info

**Writers do NOT see:**
- `tip_amount`: Full tip amount
- `platform_profit`: Platform's share
- `writer_percentage`: Percentage split

**Clients and Admins see:**
- Full tip amount
- All details

## Admin Configuration

Admins can set tip percentages per writer level via:
```http
GET /api/v1/writer-management/writer-level-configs/
POST /api/v1/writer-management/writer-level-configs/
PUT /api/v1/writer-management/writer-level-configs/{id}/
```

The `tip_percentage` field on `WriterLevel` determines what percentage of tips writers receive.

## Payment Flow

1. Client creates tip → Tip created with `payment_status='pending'`
2. Payment processed → `TipService.process_tip_payment()` creates `OrderPayment`
3. Payment linked → Tip's `payment` FK set to `OrderPayment`
4. Status updated → Tip's `payment_status` updated based on payment result

## Example Usage

### Direct Tip
```python
from writer_management.services.tip_service import TipService

tip = TipService.create_tip(
    client=client_user,
    writer=writer_user,
    amount=Decimal('50.00'),
    reason='Thank you for your excellent work!',
    website=website
)

# Process payment
TipService.process_tip_payment(tip, payment_method='wallet')
```

### Order-Based Tip
```python
tip = TipService.create_tip(
    client=client_user,
    writer=writer_user,
    amount=Decimal('25.00'),
    order=order_instance,
    reason='Great job on this order!',
    website=website
)
```

### Class-Based Tip
```python
tip = TipService.create_tip(
    client=client_user,
    writer=writer_user,
    amount=Decimal('100.00'),
    related_entity_type='class_bundle',
    related_entity_id=class_bundle.id,
    reason='Excellent class work!',
    website=website
)
```

## Notes

- Default writer percentage is 30% if writer level doesn't have `tip_percentage` set
- Tips are website-scoped (multitenancy support)
- Payment processing supports wallet, stripe, and manual methods
- Discount codes on tips may not be fully supported (check with business requirements)

