# Order Action Streamlining

## Overview

This document describes the streamlined order action system that ensures only valid actions are available based on order status and user role.

---

## Key Principles

1. **Status-Based Actions**: Actions are determined by the current order status
2. **Role-Based Permissions**: Actions are filtered by user role (admin, superadmin, support, writer, client)
3. **Business Logic Validation**: Additional rules prevent invalid actions (e.g., completed orders cannot be reassigned)
4. **Automatic Transitions**: Actions automatically trigger appropriate status transitions

---

## Action Availability by Status

### **Pending**
- ✅ Mark as Paid (admin, superadmin, support)
- ✅ Assign Writer (admin, superadmin, support)
- ✅ Cancel Order (admin, superadmin, client)
- ✅ Edit Order Details (admin, superadmin, support)
- ✅ Update Order (admin, superadmin, support)

### **Unpaid**
- ✅ Mark as Paid (admin, superadmin, support, client)
- ✅ Cancel Order (admin, superadmin, client)
- ✅ Put on Hold (admin, superadmin, support)
- ✅ Edit Order Details (admin, superadmin, support)
- ✅ Update Order (admin, superadmin, support)

### **Paid**
- ✅ Assign Writer (admin, superadmin, support)
- ✅ Make Available (admin, superadmin, support)
- ✅ Cancel Order (admin, superadmin)
- ✅ Put on Hold (admin, superadmin, support)
- ✅ Edit Order Details (admin, superadmin, support)
- ✅ Update Order (admin, superadmin, support)

### **Available**
- ✅ Assign Writer (admin, superadmin, support, writer)
- ✅ Start Order (writer)
- ✅ Cancel Order (admin, superadmin)
- ✅ Put on Hold (admin, superadmin, support)
- ✅ Edit Order Details (admin, superadmin, support)
- ✅ Update Order (admin, superadmin, support)

### **In Progress**
- ✅ Submit Order (writer)
- ✅ Put on Hold (writer, admin, superadmin, support)
- ✅ **Reassign Order** (admin, superadmin, support) ⚠️
- ✅ Move to Editing (admin, superadmin, editor)
- ✅ Cancel Order (admin, superadmin)
- ✅ Edit Order Details (admin, superadmin, support)
- ✅ Update Order (admin, superadmin, support)

### **Submitted**
- ✅ Review Order (admin, superadmin, support, editor)
- ✅ Rate Order (admin, superadmin)
- ✅ Request Revision (admin, superadmin, client, support)
- ✅ Move to Editing (admin, superadmin, editor)
- ✅ Dispute Order (client, admin, superadmin)
- ✅ Cancel Order (admin, superadmin)
- ✅ Edit Order Details (admin, superadmin, support)
- ✅ Update Order (admin, superadmin, support)

### **Under Editing**
- ✅ Submit After Editing (editor, admin, superadmin)
- ✅ Return to Writer (editor, admin, superadmin)
- ✅ Put on Hold (admin, superadmin, support)
- ✅ Edit Order Details (admin, superadmin, support)
- ✅ Update Order (admin, superadmin, support)

### **Reviewed**
- ✅ Rate Order (admin, superadmin)
- ✅ Request Revision (admin, superadmin, client)
- ✅ Approve Order (admin, superadmin)

### **Rated**
- ✅ Approve Order (admin, superadmin)
- ✅ Complete Order (admin, superadmin)
- ✅ Request Revision (admin, superadmin, client)

### **Approved**
- ✅ Complete Order (admin, superadmin)
- ✅ Archive Order (admin, superadmin)

### **Completed** ⚠️
- ✅ Approve Order (admin, superadmin)
- ✅ Archive Order (admin, superadmin)
- ✅ Close Order (admin, superadmin)
- ✅ Request Revision (admin, superadmin, client, support)
- ✅ Edit Order Details (admin, superadmin, support) - for corrections
- ❌ **Reassign Order** - NOT AVAILABLE (business rule)

### **Revision Requested**
- ✅ Start Revision (writer, admin, superadmin)
- ✅ **Reassign Order** (admin, superadmin, support) ⚠️
- ✅ Put on Hold (admin, superadmin, support)
- ✅ Cancel Order (admin, superadmin)
- ✅ Edit Order Details (admin, superadmin, support)
- ✅ Update Order (admin, superadmin, support)

### **Revision In Progress**
- ✅ Submit Revision (writer)
- ✅ Submit Order (writer)
- ✅ **Reassign Order** (admin, superadmin, support) ⚠️
- ✅ Put on Hold (admin, superadmin, support)
- ✅ Cancel Order (admin, superadmin)
- ✅ Edit Order Details (admin, superadmin, support)
- ✅ Update Order (admin, superadmin, support)

### **Revised**
- ✅ Review Revision (admin, superadmin, support, editor)
- ✅ Rate Order (admin, superadmin)
- ✅ Approve Order (admin, superadmin)
- ✅ Request Another Revision (admin, superadmin, client)
- ✅ Move to Editing (admin, superadmin, editor)
- ✅ Close Order (admin, superadmin)
- ✅ Edit Order Details (admin, superadmin, support)
- ✅ Update Order (admin, superadmin, support)

### **On Hold**
- ✅ Resume Order (admin, superadmin, support, writer)
- ✅ Cancel Order (admin, superadmin)
- ✅ Edit Order Details (admin, superadmin, support)
- ✅ Update Order (admin, superadmin, support)

### **Reassigned**
- ✅ Start Order (writer)

### **Disputed**
- ✅ Resolve Dispute (admin, superadmin, support)
- ✅ Request Revision (admin, superadmin)
- ✅ Refund Order (admin, superadmin)

### **Cancelled**
- ✅ Reopen Order (admin, superadmin)
- ✅ Refund Order (admin, superadmin)

### **Archived**
- ✅ Close Order (admin, superadmin)

### **Closed**
- ❌ No actions available (final state)

### **Refunded**
- ✅ Close Order (admin, superadmin)

---

## Business Rules

### **1. Completed Orders Cannot Be Reassigned**
- **Rule**: Orders in `completed`, `closed`, or `archived` status cannot be reassigned
- **Reason**: Work is finished, reassignment doesn't make sense
- **Implementation**: Filtered out in `get_available_actions()`

### **2. Final States Have Limited Actions**
- **Rule**: `closed`, `archived`, `refunded` orders have very limited actions
- **Reason**: These are final states, most actions are no longer applicable
- **Implementation**: Only specific actions allowed (close, edit for corrections)

### **3. Edit/Update Actions Available for Admin/Support**
- **Rule**: `edit_order` and `update_order` are available in most states for admin/support
- **Reason**: Admins need to make corrections and updates
- **Implementation**: Added to most statuses with `target_status: None` (no status change)

### **4. Cancelled Orders Have Limited Actions**
- **Rule**: Cancelled orders can only be reopened, refunded, or edited
- **Reason**: Order is cancelled, most actions don't apply
- **Implementation**: Filtered in `get_available_actions()`

---

## API Endpoints

### **Get Available Actions**
```http
GET /api/v1/orders/orders/{id}/action/
```

**Response:**
```json
{
  "status": "success",
  "order_id": 123,
  "current_status": "in_progress",
  "available_actions": [
    {
      "action": "submit_order",
      "label": "Submit Order",
      "target_status": "submitted",
      "roles": ["writer"],
      "available": true,
      "can_transition": true,
      "current_status": "in_progress"
    },
    {
      "action": "reassign_order",
      "label": "Reassign Order",
      "target_status": "reassigned",
      "roles": ["admin", "superadmin", "support"],
      "available": true,
      "can_transition": true,
      "current_status": "in_progress"
    },
    {
      "action": "edit_order",
      "label": "Edit Order Details",
      "target_status": null,
      "roles": ["admin", "superadmin", "support"],
      "available": true,
      "can_transition": true,
      "current_status": "in_progress"
    }
  ],
  "user_role": "admin"
}
```

### **Execute Action**
```http
POST /api/v1/orders/orders/{id}/action/
Content-Type: application/json

{
  "action": "reassign_order",
  "writer_id": 456,
  "reason": "Writer requested reassignment"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Order #123 reassigned successfully. Status changed from 'in_progress' to 'reassigned'.",
  "action": "reassign_order",
  "action_label": "Reassign Order",
  "order_id": 123,
  "old_status": "in_progress",
  "new_status": "reassigned",
  "status_changed": true,
  "order": { ... },
  "reason": "Writer requested reassignment"
}
```

---

## Frontend Integration

### **Using Available Actions**

The frontend should:
1. Call `GET /api/v1/orders/orders/{id}/action/` to get available actions
2. Filter actions by user role
3. Display only actions that are available
4. Disable/hide actions that are not available

### **Example Vue Component**

```vue
<template>
  <div v-if="availableActions.length > 0">
    <button
      v-for="action in availableActions"
      :key="action.action"
      :disabled="!action.can_transition"
      @click="executeAction(action.action)"
      class="action-button"
    >
      {{ action.label }}
    </button>
  </div>
</template>

<script>
export default {
  data() {
    return {
      availableActions: []
    }
  },
  async mounted() {
    await this.loadAvailableActions()
  },
  methods: {
    async loadAvailableActions() {
      const response = await ordersAPI.getAvailableActions(this.orderId)
      this.availableActions = response.data.available_actions.filter(
        action => action.available && action.can_transition
      )
    },
    async executeAction(actionName) {
      await ordersAPI.executeAction(this.orderId, actionName)
      await this.loadAvailableActions() // Refresh
    }
  }
}
</script>
```

---

## Status Transition Flow

```
Pending → Paid → Available → In Progress → Submitted → Reviewed → Rated → Completed
                                                              ↓
                                                         Revision Requested
                                                              ↓
                                                         Revision In Progress
                                                              ↓
                                                         Revised → (back to Reviewed)
```

**Key Transitions:**
- ✅ `in_progress` → `submitted` (writer submits)
- ✅ `submitted` → `revision_requested` (client/admin requests revision)
- ✅ `revision_requested` → `revision_in_progress` (writer starts revision)
- ✅ `revision_in_progress` → `revised` (writer submits revision)
- ✅ `revised` → `reviewed` (admin reviews)
- ✅ `reviewed` → `rated` → `completed` (final approval)
- ❌ `completed` → `reassigned` (NOT ALLOWED)

---

## Benefits

1. **Clear Action Visibility**: Users only see actions they can perform
2. **Prevents Invalid Actions**: Business rules prevent impossible actions
3. **Automatic Transitions**: Actions trigger appropriate status changes
4. **Role-Based Security**: Actions filtered by user permissions
5. **Better UX**: Frontend can show/hide buttons based on availability
6. **Audit Trail**: All actions are logged with reasons

---

## Future Enhancements

1. **Action Groups**: Group related actions (e.g., "Order Management", "Status Changes")
2. **Action Conditions**: Add conditional logic (e.g., "Reassign only if order is not paid")
3. **Bulk Actions**: Support bulk action execution
4. **Action History**: Show history of actions performed
5. **Action Templates**: Pre-configured action sets for common workflows

