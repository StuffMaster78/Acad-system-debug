# Writer Order Taking Restriction

## Overview

This feature allows admins to restrict writers from taking orders from their profile, even if their writer level would normally allow it. This provides fine-grained control over which writers can self-assign orders.

---

## Key Components

### 1. **New Field: `can_take_orders`**

**Location:** `backend/writer_management/models/profile.py`

Added to `WriterProfile` model:
```python
can_take_orders = models.BooleanField(
    default=True,
    help_text="If disabled, the writer cannot take orders from their profile, even if their level allows it. Admin can override by assigning orders manually."
)
```

**Default:** `True` (all existing writers can take orders by default)

---

## How It Works

### **Restriction Logic**

The `can_take_orders` flag is checked in multiple places to ensure comprehensive restriction:

1. **WriterOrderTakeViewSet.perform_create()** - Main endpoint for taking orders
2. **WriterOrderTake.clean()** - Model-level validation
3. **WriterOrderTakeSerializer.validate()** - Serializer validation
4. **OrderAccessService.can_take()** - Service-level check
5. **assignment_guard.can_writer_take_order()** - Guard function

### **Admin Override**

**Important:** Admins can still assign orders to writers manually, even if `can_take_orders` is `False`. This restriction only applies to writers taking orders themselves from their profile.

---

## Validation Flow

When a writer attempts to take an order:

1. **Check `can_take_orders` flag** - If `False`, reject immediately
2. **Check global config** - `WriterConfig.takes_enabled` must be `True`
3. **Check writer level** - Writer must have a level with `max_orders > 0`
4. **Check current workload** - Writer must not exceed their `max_orders` limit
5. **Check order status** - Order must be available and not assigned

---

## API Behavior

### **Writer Attempts to Take Order**

**Endpoint:** `POST /api/v1/writer-management/writer-order-takes/`

**If `can_take_orders = False`:**
```json
{
  "error": "You are not allowed to take orders. Please contact an administrator."
}
```

**Status Code:** `400 Bad Request`

---

## Admin Management

### **Update via Admin Panel**

Admins can update the `can_take_orders` field through:
- Django Admin interface
- Writer Profile API endpoints (admin only)

### **Update via API**

**Endpoint:** `PATCH /api/v1/writer-management/writers/{id}/`

**Request:**
```json
{
  "can_take_orders": false
}
```

**Response:**
```json
{
  "id": 123,
  "user": 456,
  "registration_id": "Writer #12345",
  "can_take_orders": false,
  ...
}
```

---

## Use Cases

### **1. Temporary Restriction**

Restrict a writer who is:
- On probation
- Under review
- Has quality issues
- Needs training

### **2. Permanent Restriction**

Restrict writers who:
- Should only work on assigned orders
- Are part of a special program
- Have specific workflow requirements

### **3. Selective Control**

Allow some writers to take orders while restricting others, even if they have the same level.

---

## Migration

**File:** `backend/writer_management/migrations/0023_add_can_take_orders_flag.py`

The migration adds the field with `default=True`, so all existing writers will continue to have order-taking enabled.

---

## Code Locations

### **Model**
- `backend/writer_management/models/profile.py` - `WriterProfile.can_take_orders`

### **Views**
- `backend/writer_management/views.py` - `WriterOrderTakeViewSet.perform_create()`
- `backend/writer_management/views/__init__.py` - `WriterOrderTakeViewSet.perform_create()`

### **Serializers**
- `backend/writer_management/serializers.py` - `WriterOrderTakeSerializer.validate()`

### **Services**
- `backend/orders/services/order_access_service.py` - `OrderAccessService.can_take()`
- `backend/orders/services/assignment_guard.py` - `can_writer_take_order()`

### **Models**
- `backend/writer_management/models/requests.py` - `WriterOrderTake.clean()`

---

## Testing

### **Test Cases**

1. **Writer with `can_take_orders = False` cannot take orders**
2. **Writer with `can_take_orders = True` can take orders (if other conditions met)**
3. **Admin can still assign orders to restricted writers**
4. **Default value is `True` for new writers**
5. **Validation error message is clear and helpful**

---

## Benefits

1. **Fine-Grained Control**: Admins can restrict specific writers without changing their level
2. **Flexible Management**: Can be toggled on/off per writer
3. **Admin Override**: Admins can still assign orders manually
4. **Backward Compatible**: All existing writers default to `True`
5. **Clear Error Messages**: Writers understand why they cannot take orders

---

## Future Enhancements

1. **Bulk Update**: Allow admins to restrict multiple writers at once
2. **Reason Tracking**: Store reason for restriction
3. **Automatic Restrictions**: Auto-restrict based on performance metrics
4. **Time-Limited Restrictions**: Restrict for a specific duration
5. **Notification**: Notify writers when restriction is applied/removed

