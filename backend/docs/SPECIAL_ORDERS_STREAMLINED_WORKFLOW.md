# Streamlined Special Orders Workflow

## Overview

The streamlined special order workflow provides a unified, efficient process for:
1. **Placing orders** (client)
2. **Negotiating and setting prices** (admin)
3. **Approving and assigning writers** (admin)
4. **Completing orders** (writer/admin)

This replaces the previous fragmented workflow with a single service that handles all operations atomically and provides clear status tracking.

---

## Key Components

### 1. **StreamlinedSpecialOrderService**
Located in: `backend/special_orders/services/streamlined_order_service.py`

Provides unified methods:
- `place_order()` - Create new order
- `set_price()` - Set/negotiate price (can be called multiple times)
- `approve_and_assign()` - Approve order and optionally assign writer in one action
- `complete_order()` - Complete order with notes
- `get_order_workflow_status()` - Get current status and available actions

### 2. **StreamlinedSpecialOrderViewSet**
Located in: `backend/special_orders/views/streamlined_views.py`

Provides REST API endpoints:
- `POST /api/streamlined-orders/place-order/` - Place new order
- `POST /api/streamlined-orders/{id}/set-price/` - Set/negotiate price
- `POST /api/streamlined-orders/{id}/approve-and-assign/` - Approve and assign writer
- `POST /api/streamlined-orders/{id}/complete/` - Complete order
- `GET /api/streamlined-orders/{id}/workflow-status/` - Get workflow status
- `POST /api/streamlined-orders/{id}/quick-approve/` - Quick approve (price + approve + assign)

### 3. **Enhanced Existing ViewSet**
The existing `SpecialOrderViewSet` now includes streamlined actions:
- `POST /api/special-orders/{id}/set-price/` - Set price (streamlined)
- `POST /api/special-orders/{id}/complete/` - Complete order (streamlined)
- `GET /api/special-orders/{id}/workflow-status/` - Get workflow status

---

## Workflow Steps

### **Step 1: Client Places Order**

**Endpoint:** `POST /api/streamlined-orders/place-order/`

**Request:**
```json
{
  "order_type": "estimated",
  "duration_days": 5,
  "inquiry_details": "I need help with a complex research paper",
  "website_id": 1,
  "price_per_day": 50.00  // Optional, for estimated orders
}
```

**For Predefined Orders:**
```json
{
  "order_type": "predefined",
  "predefined_type_id": 1,
  "duration_days": 3,
  "inquiry_details": "Shadow Health assignment",
  "website_id": 1
}
```

**Response:** Order created with status `inquiry`

---

### **Step 2: Admin Sets/Negotiates Price** (Estimated Orders Only)

**Endpoint:** `POST /api/streamlined-orders/{id}/set-price/`

**Request:**
```json
{
  "total_cost": 500.00,  // OR
  "price_per_day": 50.00,
  "admin_notes": "Price negotiated based on complexity"
}
```

**What Happens:**
- Sets `total_cost` and `admin_approved_cost`
- Calculates `deposit_required` based on website settings (default 50%)
- Regenerates installments
- Updates status to `awaiting_approval`
- Notifies client

**Note:** Can be called multiple times for negotiation.

---

### **Step 3: Admin Approves and Assigns Writer**

**Endpoint:** `POST /api/streamlined-orders/{id}/approve-and-assign/`

**Request:**
```json
{
  "writer_id": 123,
  "writer_payment_amount": 100.00,  // OR
  "writer_payment_percentage": 15.5,
  "auto_assign": false
}
```

**What Happens:**
- Approves order (`is_approved = True`)
- Assigns writer (if provided)
- Sets writer payment (amount or percentage)
- Updates status:
  - `in_progress` if deposit paid and writer assigned
  - `awaiting_approval` if waiting for payment or writer
- Notifies client and writer

**Quick Approve (All-in-One):**
**Endpoint:** `POST /api/streamlined-orders/{id}/quick-approve/`

```json
{
  "total_cost": 500.00,
  "writer_id": 123,
  "writer_payment_percentage": 15.5,
  "admin_notes": "Quick approval"
}
```

This combines Step 2 and Step 3 in one action.

---

### **Step 4: Writer Completes Order**

**Endpoint:** `POST /api/streamlined-orders/{id}/complete/`

**Request:**
```json
{
  "files_uploaded": true,
  "completion_notes": "Order completed successfully"
}
```

**What Happens:**
- Updates status to `completed`
- Records completion notes
- Notifies client

---

## Workflow Status Tracking

**Endpoint:** `GET /api/streamlined-orders/{id}/workflow-status/`

**Response:**
```json
{
  "current_status": "awaiting_approval",
  "is_approved": true,
  "has_price": true,
  "has_writer": true,
  "deposit_paid": true,
  "all_payments_paid": false,
  "available_actions": {
    "client": ["pay_deposit"],
    "admin": ["assign_writer", "mark_payment_paid"],
    "writer": []
  }
}
```

---

## Status Flow

```
inquiry
  ↓ (admin sets price)
awaiting_approval
  ↓ (admin approves + assigns writer + deposit paid)
in_progress
  ↓ (writer completes)
completed
```

---

## Benefits

1. **Unified Service**: All operations in one service class
2. **Atomic Operations**: Database transactions ensure consistency
3. **Clear Status Tracking**: `get_order_workflow_status()` shows what's next
4. **Flexible Negotiation**: `set_price()` can be called multiple times
5. **Quick Actions**: `quick_approve()` combines multiple steps
6. **Backward Compatible**: Existing endpoints still work
7. **Notifications**: Automatic notifications at each step
8. **Error Handling**: Comprehensive validation and error messages

---

## Migration Guide

### For Existing Code

The streamlined service is **additive** - existing code continues to work. To migrate:

1. **Replace manual price setting:**
   ```python
   # Old
   order.total_cost = 500
   order.save()
   
   # New
   StreamlinedSpecialOrderService.set_price(order, admin_user, total_cost=500)
   ```

2. **Replace approval + assignment:**
   ```python
   # Old
   OrderApprovalService.approve_special_order(order, admin)
   assign_writer(order, writer, payment_amount=100)
   
   # New
   StreamlinedSpecialOrderService.approve_and_assign(
       order, admin, writer_id=writer.id, writer_payment_amount=100
   )
   ```

3. **Use workflow status:**
   ```python
   # New
   status = StreamlinedSpecialOrderService.get_order_workflow_status(order, user)
   # Check status['available_actions'][user.role]
   ```

---

## API Examples

### Complete Flow Example

```bash
# 1. Client places order
POST /api/streamlined-orders/place-order/
{
  "order_type": "estimated",
  "duration_days": 5,
  "inquiry_details": "Research paper",
  "website_id": 1
}

# 2. Admin sets price
POST /api/streamlined-orders/1/set-price/
{
  "total_cost": 500.00,
  "admin_notes": "Based on complexity"
}

# 3. Admin approves and assigns
POST /api/streamlined-orders/1/approve-and-assign/
{
  "writer_id": 123,
  "writer_payment_percentage": 15.5
}

# 4. Writer completes
POST /api/streamlined-orders/1/complete/
{
  "files_uploaded": true,
  "completion_notes": "Done"
}
```

---

## Error Handling

All methods raise `ValidationError` with descriptive messages:
- Order status validation
- Required field validation
- Business rule validation (e.g., writer can only complete their orders)

Errors are returned as:
```json
{
  "error": "Order must have a price set before approval"
}
```

---

## Future Enhancements

1. **Auto-assign writer**: Smart matching based on writer skills/availability
2. **Price suggestions**: AI-powered price recommendations
3. **Bulk operations**: Approve/assign multiple orders at once
4. **Workflow templates**: Pre-configured workflows for common scenarios
5. **Negotiation history**: Track all price negotiations with timestamps

