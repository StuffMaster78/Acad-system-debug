# Order Transition System - Improvements

## ✅ What Was Fixed

### **1. Complete Transition Map**
- ✅ Added all missing statuses to `VALID_TRANSITIONS`
- ✅ Added transitions for: `under_editing`, `disputed`, `reopened`, `refunded`, `on_revision`, `created`
- ✅ Fixed missing transitions between related statuses
- ✅ Added proper terminal states handling

### **2. Enhanced Validation**
- ✅ **Payment Validation**: Checks for completed payment before allowing transitions to payment-required statuses
- ✅ **Writer Assignment Validation**: Ensures writer is assigned before transitioning to writer-required statuses
- ✅ **Better Error Messages**: Now shows allowed transitions when validation fails

### **3. New API Endpoints**

#### **Transition Order Status**
```
POST /api/v1/orders/orders/{id}/transition/
Body: {
    "target_status": "in_progress",
    "reason": "Optional reason",
    "skip_payment_check": false  // Admin only
}
```

#### **Get Available Transitions**
```
GET /api/v1/orders/orders/{id}/available-transitions/
Response: {
    "current_status": "paid",
    "available_transitions": ["available", "pending_writer_assignment", "in_progress", "on_hold", "cancelled"],
    "order_id": 123
}
```

### **4. Improved Service Methods**

#### **StatusTransitionService.transition_order_to_status()**
- ✅ Added `reason` parameter for audit logging
- ✅ Enhanced validation with writer assignment checks
- ✅ Better error messages with allowed transitions list
- ✅ Improved audit logging with old/new status

#### **StatusTransitionService.get_available_transitions()**
- ✅ New method to get available transitions for an order
- ✅ Useful for UI to show available actions

---

## 📋 Complete Transition Map

### **Initial States**
- `created` → `pending`, `unpaid`, `cancelled`
- `pending` → `unpaid`, `cancelled`, `deleted`

### **Payment States**
- `unpaid` → `paid`, `cancelled`, `deleted`, `on_hold`, `pending`
- `paid` → `available`, `pending_writer_assignment`, `in_progress`, `on_hold`, `cancelled`

### **Assignment States**
- `pending_writer_assignment` → `available`, `cancelled`, `on_hold`, `in_progress`
- `available` → `in_progress`, `cancelled`, `on_hold`, `reassigned`

### **Active Work States**
- `in_progress` → `on_hold`, `cancelled`, `submitted`, `reassigned`, `under_editing`
- `on_hold` → `in_progress`, `cancelled`, `available`, `reassigned`
- `reassigned` → `in_progress`, `available`, `on_hold`

### **Submission & Review States**
- `submitted` → `reviewed`, `rated`, `revision_requested`, `disputed`, `cancelled`, `under_editing`
- `reviewed` → `rated`, `revision_requested`, `approved`
- `rated` → `approved`, `revision_requested`, `completed`
- `approved` → `archived`, `completed`
- `completed` → `approved`, `archived`, `closed`

### **Revision States**
- `revision_requested` → `revision_in_progress`, `reassigned`, `on_hold`, `cancelled`
- `revision_in_progress` → `revised`, `submitted`, `cancelled`, `reassigned`, `closed`, `on_hold`
- `revised` → `reviewed`, `rated`, `approved`, `revision_requested`, `cancelled`, `closed`, `under_editing`
- `on_revision` → `revised`, `revision_in_progress`, `cancelled`

### **Editing States**
- `under_editing` → `submitted`, `in_progress`, `revised`, `cancelled`, `on_hold`

### **Dispute States**
- `disputed` → `in_progress`, `revision_requested`, `cancelled`, `closed`, `refunded`

### **Final States**
- `cancelled` → `reopened`, `unpaid`, `refunded`
- `reopened` → `unpaid`, `pending`, `available`
- `refunded` → `closed`, `cancelled`
- `archived` → `closed`
- `closed` → (terminal)
- `deleted` → (terminal)

---

## 🔒 Validation Rules

### **Payment Required Statuses**
- `in_progress`
- `available`
- `pending_writer_assignment`
- `submitted`

### **Writer Assignment Required Statuses**
- `in_progress`
- `submitted`
- `revision_in_progress`
- `revised`

---

## 🎯 Usage Examples

### **Transition Order via API**
```python
POST /api/v1/orders/orders/123/transition/
{
    "target_status": "in_progress",
    "reason": "Writer assigned and ready to start"
}
```

### **Get Available Transitions**
```python
GET /api/v1/orders/orders/123/available-transitions/
# Returns list of valid next statuses
```

### **Using the Service Directly**
```python
from orders.services.status_transition_service import StatusTransitionService

service = StatusTransitionService(user=request.user)
service.transition_order_to_status(
    order,
    "in_progress",
    reason="Starting work on order"
)
```

---

## 🚀 Next Steps (Optional Enhancements)

1. **Role-Based Permissions**: Add role-based transition restrictions
2. **Transition Hooks**: Add pre/post transition hooks for notifications
3. **Bulk Transitions**: Support for transitioning multiple orders
4. **Transition History**: Track all transitions with timestamps
5. **UI Integration**: Update frontend to use new endpoints

---

**Status**: ✅ **Order Transitions Perfected!**

