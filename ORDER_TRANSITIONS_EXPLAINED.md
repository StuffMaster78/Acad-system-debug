# Order Transitions System - Complete Guide

**Question:** Are order transitions event-driven, automatic, and can they be overridden?

**Answer:** ✅ **YES to all three!**

---

## 📋 Overview

The order transition system is a **hybrid system** that supports:
1. ✅ **Event-driven transitions** (Django signals)
2. ✅ **Automatic transitions** (scheduled tasks, conditional logic)
3. ✅ **Manual overrides** (admin actions with bypass options)

---

## 1. ✅ Event-Driven Transitions

### Django Signals

Order transitions can be triggered automatically by Django signals when certain events occur:

**File:** `backend/orders/signals.py`

#### Example: Payment Received → Auto Transition
```python
@receiver(pre_save, sender=Order)
def update_order_status(sender, instance, **kwargs):
    """
    Automatically update the order's status based on payment.
    """
    if instance.is_paid and instance.status == 'unpaid':
        instance.status = 'pending'  # Auto-update status when payment is received
```

**Event:** Payment received (`is_paid` becomes `True`)  
**Automatic Transition:** `unpaid` → `pending`

#### Example: Dispute Created → Flag Order
```python
@receiver(post_save, sender=Dispute)
def handle_dispute_creation(sender, instance, created, **kwargs):
    """
    When a dispute is created, flag the order.
    """
    if created:
        order = instance.order
        order.flag = True  # Mark the order as disputed
        order.save()
```

**Event:** Dispute created  
**Action:** Order flagged automatically

#### Example: Writer Request Approved → Update Cost
```python
@receiver(post_save, sender=WriterRequest)
def on_writer_request_approved(sender, instance, created, **kwargs):
    if instance.admin_approval and instance.client_approval:
        # Automatically update total cost after approval
        instance.order.calculate_total_cost()
```

**Event:** Writer request approved by both admin and client  
**Action:** Order cost recalculated automatically

---

## 2. ✅ Automatic Transitions

### A. Scheduled Tasks (Celery)

Automatic transitions can be triggered by scheduled Celery tasks:

**File:** `backend/orders/tasks.py`

#### Example: Auto-Archive Service
```python
@shared_task
def auto_archive_orders():
    """
    Automatically archive orders older than cutoff date.
    """
    from orders.services.auto_archive_service import AutoArchiveService
    from datetime import datetime, timedelta
    
    cutoff_date = datetime.now() - timedelta(days=90)
    AutoArchiveService.archive_orders_older_than(
        cutoff_date=cutoff_date,
        status="approved"
    )
```

**Trigger:** Scheduled task (e.g., daily cron)  
**Action:** Automatically transitions `approved` → `archived` for old orders

#### Example: Status Transition Service
```python
@staticmethod
def move_complete_orders_to_approved_older_than(cutoff_date: datetime) -> None:
    """
    Promote 'complete' orders to 'approved' if older than a given date.
    """
    orders = get_orders_by_status_older_than("complete", cutoff_date)
    for order in orders:
        order.status = "approved"
        save_order(order)
```

**Trigger:** Scheduled task  
**Action:** Automatically transitions `completed` → `approved` for old orders

### B. Conditional Automatic Transitions

#### Example: Submit Order → Auto Move to Editing
**File:** `backend/orders/services/submit_order_service.py`

```python
class SubmitOrderService:
    def execute(self, order_id, user):
        order = Order.objects.get(id=order_id)
        order.status = OrderStatus.SUBMITTED.value
        order.save()

        # Fire editing transition (checks if editing should occur)
        MoveOrderToEditingService.execute(order=order, user=user)
        
        # Auto-issue fine if late
        auto_issue_late_fine(order)
        
        return order
```

**Trigger:** Writer submits order  
**Automatic Actions:**
1. Status changes to `submitted`
2. Automatically moves to `under_editing` if eligible
3. Automatically issues late fine if deadline passed

### C. State Machine with Automatic Flag

**File:** `backend/orders/services/state_machine.py`

```python
def transition_to(
    self, new_state: str, actor=None, action="manual",
    is_automatic=False, meta=None
) -> Order:
    """
    Transition with is_automatic flag to track automatic transitions.
    """
    # ... validation and transition logic ...
    
    # Log the transition
    OrderTransitionLog.objects.create(
        order=self.order,
        user=actor if actor and actor.is_authenticated else None,
        old_status=old_state,
        new_status=new_state,
        action=action,
        is_automatic=is_automatic,  # ✅ Tracks if transition was automatic
        meta=meta or {}
    )
```

**Key Feature:** All transitions are logged with `is_automatic` flag for audit trail.

---

## 3. ✅ Manual Overrides

### A. Admin Override with `skip_payment_check`

**File:** `backend/orders/services/status_transition_service.py`

```python
def transition_order_to_status(
    self,
    order: Order,
    target_status: str,
    *,
    metadata: Optional[dict] = None,
    log_action: bool = True,
    skip_payment_check: bool = False,  # ✅ Admin override flag
    reason: Optional[str] = None
) -> Order:
    """
    Transition an order to a new status if valid.
    
    Args:
        skip_payment_check (bool): Skip payment validation (for admin overrides).
    """
    # Validate payment requirement for statuses that require payment
    payment_required_statuses = ['in_progress', 'available', 'pending_writer_assignment', 'submitted']
    if not skip_payment_check and target_status in payment_required_statuses:
        self._validate_payment_completed(order, target_status)
    
    # ... rest of transition logic ...
```

**Usage:** Admin can bypass payment checks:
```python
service = StatusTransitionService(user=admin_user)
service.transition_order_to_status(
    order=order,
    target_status='in_progress',
    skip_payment_check=True,  # ✅ Override payment requirement
    reason="Admin override - payment pending"
)
```

### B. Manual Transitions via Action System

**File:** `backend/orders/views/orders/actions.py`

```python
class OrderActionView(views.APIView):
    """
    Handles transitions on an order using the action dispatcher.
    Actions automatically trigger appropriate status transitions.
    """
    
    def post(self, request, pk: int):
        """
        Executes an action on a specific order.
        Actions automatically trigger appropriate status transitions.
        """
        action = request.data.get("action")
        # ... action execution ...
```

**Usage:** Manual transitions via API:
```json
POST /api/v1/orders/orders/{id}/action/
{
    "action": "transition_to_status",
    "target_status": "in_progress",
    "reason": "Manual override by admin",
    "skip_payment_check": true
}
```

### C. Reopen Cancelled Orders

**File:** `backend/orders/services/status_transition_service.py`

```python
@staticmethod
def reopen_cancelled_order_to_unpaid(order_id: int) -> Optional[Order]:
    """
    Restore a cancelled order to 'unpaid' status.
    Useful when the client wants to reprocess a cancelled order.
    """
    order = Order.objects.filter(
        id=order_id, status="cancelled"
    ).first()
    if not order:
        return None
    order.status = "unpaid"
    order.save(update_fields=["status"])
    return order
```

**Usage:** Override cancellation and restore order:
```python
StatusTransitionService.reopen_cancelled_order_to_unpaid(order_id=123)
# Transitions: cancelled → unpaid
```

---

## 📊 Transition Validation

### Valid Transitions Map

**File:** `backend/orders/services/status_transition_service.py`

```python
VALID_TRANSITIONS: Dict[str, List[str]] = {
    # Initial states
    "pending": ["unpaid", "cancelled", "deleted"],
    "created": ["pending", "unpaid", "cancelled"],
    
    # Payment states
    "unpaid": ["paid", "cancelled", "deleted", "on_hold", "pending"],
    "paid": ["available", "pending_writer_assignment", "in_progress", "on_hold", "cancelled"],
    
    # Assignment states
    "pending_writer_assignment": ["available", "cancelled", "on_hold", "in_progress"],
    "available": ["in_progress", "cancelled", "on_hold", "reassigned"],
    
    # Active work states
    "in_progress": ["on_hold", "cancelled", "submitted", "reassigned", "under_editing"],
    "on_hold": ["in_progress", "cancelled", "available", "reassigned"],
    
    # ... more transitions ...
}
```

**Key Points:**
- ✅ All transitions are validated against this map
- ✅ Invalid transitions raise `InvalidTransitionError`
- ✅ Overrides can bypass validation (with `skip_payment_check`)

---

## 📝 Transition Logging

### OrderTransitionLog Model

**File:** `backend/orders/models.py`

```python
class OrderTransitionLog(models.Model):
    """
    Logs all status transitions for an order.
    This is useful for auditing and tracking changes in order status.
    """
    order = models.ForeignKey("orders.Order", on_delete=models.CASCADE)
    user = models.ForeignKey('users.User', null=True, blank=True)
    old_status = models.CharField(max_length=32)
    new_status = models.CharField(max_length=32)
    action = models.CharField(max_length=64)  # e.g. "mark_paid", "auto_expire"
    is_automatic = models.BooleanField(default=False)  # ✅ Tracks automatic vs manual
    timestamp = models.DateTimeField(auto_now_add=True)
    meta = models.JSONField(null=True, blank=True)  # Optional context
```

**Features:**
- ✅ Tracks all transitions (automatic and manual)
- ✅ Records `is_automatic` flag
- ✅ Stores actor (user who triggered, or None for automatic)
- ✅ Stores metadata (reason, notes, etc.)

---

## 🎯 Summary

### ✅ Event-Driven: YES
- Django signals trigger transitions on events (payment, dispute, etc.)
- Example: `unpaid` → `pending` when payment received

### ✅ Automatic: YES
- Scheduled Celery tasks (auto-archive, status promotions)
- Conditional logic (submit → auto move to editing)
- `is_automatic` flag tracks automatic transitions

### ✅ Can Be Overridden: YES
- `skip_payment_check=True` for admin overrides
- Manual transitions via action system
- Reopen cancelled orders
- All overrides are logged with reason

---

## 🔧 Usage Examples

### 1. Automatic Transition (Event-Driven)
```python
# Payment received → automatically transitions
order.is_paid = True
order.save()  # Signal triggers: unpaid → pending
```

### 2. Automatic Transition (Scheduled)
```python
# Scheduled task runs daily
AutoArchiveService.archive_orders_older_than(
    cutoff_date=datetime.now() - timedelta(days=90),
    status="approved"
)
# Transitions: approved → archived
```

### 3. Manual Override (Admin)
```python
service = StatusTransitionService(user=admin_user)
service.transition_order_to_status(
    order=order,
    target_status='in_progress',
    skip_payment_check=True,  # Override payment requirement
    reason="Admin override - payment processing"
)
```

### 4. Manual Transition (API)
```json
POST /api/v1/orders/orders/123/action/
{
    "action": "transition_to_status",
    "target_status": "in_progress",
    "reason": "Manual transition by admin"
}
```

---

## 📚 Related Files

- `backend/orders/services/status_transition_service.py` - Main transition service
- `backend/orders/services/state_machine.py` - State machine with hooks
- `backend/orders/signals.py` - Event-driven transitions
- `backend/orders/tasks.py` - Scheduled automatic transitions
- `backend/orders/models.py` - OrderTransitionLog model
- `backend/orders/views/orders/actions.py` - Manual transition API

---

**Conclusion:** The order transition system is **fully event-driven, supports automatic transitions, and allows manual overrides** with proper logging and audit trails.

