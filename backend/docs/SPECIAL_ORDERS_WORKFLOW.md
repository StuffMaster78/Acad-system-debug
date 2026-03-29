# Special Orders Workflow

## Overview

Special orders handle custom/customized writing services with two pricing models:
1. **Predefined Cost** - Fixed pricing based on predefined order types (e.g., "Shadow Health" assignments)
2. **Estimated Cost** - Custom pricing determined by admin after review

---

## Key Models

### **SpecialOrder**
- Two order types: `predefined` or `estimated`
- Four statuses: `inquiry` → `awaiting_approval` → `in_progress` → `completed`
- Supports installment payments (deposit + balance)
- Can have writer assigned
- Admin override controls for special cases

### **InstallmentPayment**
- Tracks installment payments (typically 2: deposit + balance)
- Each installment has `due_date`, `amount_due`, `is_paid` status

### **PredefinedSpecialOrderConfig**
- Configuration for predefined order types (e.g., "Shadow Health")
- Has multiple duration options with fixed prices

### **EstimatedSpecialOrderSettings**
- Website-level settings for deposit percentages
- Default deposit percentage (typically 50%)

---

## Complete Workflow

### **Phase 1: Order Creation**

**Endpoint:** `POST /api/special-orders/`

**Service:** `create_special_order(data, user)` or `SpecialOrderService.create_special_order()`

**Process:**
1. Client submits order:
   ```python
   {
       "order_type": "predefined" | "estimated",
       "predefined_type": <id>,  # If predefined
       "duration_days": 3,
       "inquiry_details": "Description of what client needs",
       "website": <website_id>
   }
   ```

2. **For Predefined Orders:**
   - Lookup `PredefinedSpecialOrderConfig` by `predefined_type`
   - Find matching `PredefinedSpecialOrderDuration` for `duration_days`
   - Set `total_cost = duration_price.price`
   - Set `deposit_required = total_cost` (full payment upfront for predefined)

3. **For Estimated Orders:**
   - `total_cost = 0` initially
   - Admin determines cost later
   - Deposit calculated when cost is set: `deposit_required = total_cost * (deposit_percentage / 100)`
   - Default deposit percentage from `EstimatedSpecialOrderSettings` (typically 50%)

4. **Generate Installments:**
   - `InstallmentPaymentService.generate_installments(order)`
   - Creates 2 installments:
     - Installment 1: 50% of total, due immediately
     - Installment 2: 50% of total, due in 7 days

5. **Initial Status:**
   - Status: `inquiry`
   - `is_approved = False`

**Signal:** `handle_new_special_order` → Sends notification to admins

---

### **Phase 2: Admin Review & Approval**

**For Estimated Orders:**
1. Admin reviews inquiry
2. Admin sets:
   - `total_cost` (or uses `price_per_day * duration_days`)
   - `admin_approved_cost`
   - Updates `admin_notes`

3. Admin approves order:
   ```python
   OrderApprovalService.approve_special_order(order, admin_user)
   # Sets:
   # - is_approved = True
   # - status = 'approved' (NOTE: This conflicts with STATUS_CHOICES - should be 'awaiting_approval' or 'in_progress')
   ```

4. Status transition: `inquiry` → `awaiting_approval` → `in_progress`

**For Predefined Orders:**
- Approval may be automatic or require admin confirmation
- Pricing already set during creation

---

### **Phase 3: Payment Processing**

**Installment Payments:**

1. **Client pays deposit (Installment 1):**
   - Client initiates payment for first installment
   - Payment processed via `InstallmentPaymentViewSet`
   - `InstallmentPayment.mark_paid()` sets `is_paid = True`, `paid_at = timestamp`

2. **After deposit payment:**
   - Order can proceed to `in_progress`
   - Writer can be assigned
   - Work can begin

3. **Client pays balance (Installment 2):**
   - Due in 7 days (or as configured)
   - Same payment process
   - Both installments must be paid for full completion

**Payment Methods:**
- Wallet deduction (immediate)
- External payment (Stripe/PayPal) - pending gateway integration
- Admin override: `admin_marked_paid = True` (manual payment tracking)

**Admin Override:**
```python
SpecialOrderService.override_payment(order)
# Sets admin_marked_paid = True
# Allows order to proceed even without payment confirmation
```

---

### **Phase 4: Writer Assignment & Work**

1. **Writer Assignment:**
   - Admin assigns writer: `order.writer = <writer_user>`
   - Writer receives notification

2. **Work Progress:**
   - Status remains `in_progress`
   - Writer uploads files (if applicable)
   - Writer can mark complete with or without files

3. **Writer Completion:**
   - Writer marks order complete
   - If no files: `writer_completed_no_files = True`
   - Status: `in_progress` → `completed`

---

### **Phase 5: Completion & File Access**

**Completion Scenarios:**

1. **Normal Completion:**
   - Writer uploads files
   - Writer marks complete
   - Status → `completed`
   - Files available to client

2. **Completion Without Files:**
   - `writer_completed_no_files = True`
   - Admin must unlock file access: `admin_unlocked_files = True`

3. **Admin Override Completion:**
   ```python
   CompletionService.complete_special_order(order, admin_user, 'manual', 'justification')
   # Logs to OrderCompletionLog
   # Sets status = 'completed'
   ```

**File Access Control:**
- Files locked until:
  - All installments paid, OR
  - `admin_unlocked_files = True`, OR
  - `admin_marked_paid = True`

**Completion Logging:**
- All completions logged to `OrderCompletionLog`:
  - Who completed (`completed_by`)
  - Method (`completion_steps`)
  - Justification/reason

---

## Status Flow Diagram

```
[Client Submits] 
    ↓
inquiry
    ↓
[Admin Reviews]
    ↓
awaiting_approval
    ↓
[Admin Approves]
    ↓
in_progress ← [Writer Assigned]
    ↓
[Writer Works]
    ↓
[Writer/Admin Completes]
    ↓
completed
```

---

## Payment Flow

### **Installment Structure:**
```
Order Total: $100
├─ Installment 1 (Deposit): $50.00 (due: order.created_at)
│  └─ is_paid: True/False
│
└─ Installment 2 (Balance): $50.00 (due: order.created_at + 7 days)
   └─ is_paid: True/False
```

### **Payment Processing:**
1. Client initiates payment for installment
2. Payment processed (wallet/external/manual)
3. `InstallmentPayment.mark_paid()` updates status
4. Signal/notification sent
5. Order proceeds if deposit paid

---

## Admin Controls & Overrides

### **Payment Override:**
- `admin_marked_paid = True`
- Allows order to proceed without payment confirmation
- Use case: External payment, manual processing

### **File Access Override:**
- `admin_unlocked_files = True`
- Unlocks file downloads regardless of payment status
- Use case: Order completed without files, special circumstances

### **Cost Approval:**
- `admin_approved_cost`
- Admin-set cost for estimated orders
- Separate from `total_cost` (tracks what admin approved vs. what was charged)

---

## Key Services

### **1. SpecialOrderService**
- `create_special_order()` - Creates new order
- `update_special_order()` - Updates order status/approval
- `validate_special_order()` - Validates order data
- `approve_special_order()` - Approves order (status issue noted)
- `complete_special_order()` - Marks order complete

### **2. InstallmentPaymentService**
- `generate_installments()` - Creates 2 installments (50/50 split)
- `create_installment()` - Creates single installment
- `mark_installment_as_paid()` - Marks installment paid
- `get_user_installments()` - Filters installments by user role

### **3. OrderApprovalService**
- `approve_special_order()` - Handles approval logic
- Validates status is `awaiting_approval`
- Updates `is_approved` and status

### **4. CompletionService**
- `complete_special_order()` - Marks order complete
- Logs completion to `OrderCompletionLog`
- Tracks who, how, and why

---

## Differences from Standard Orders

| Aspect | Standard Orders | Special Orders |
|--------|----------------|----------------|
| **Pricing** | Auto-calculated from pages/services | Predefined config OR admin-estimated |
| **Payment** | Single payment upfront | Installment payments (deposit + balance) |
| **Status Flow** | More complex (CREATED → IN_PROGRESS → SUBMITTED → etc.) | Simpler (inquiry → awaiting_approval → in_progress → completed) |
| **Approval** | Automatic (payment = approval) | Requires admin approval (especially estimated) |
| **Payment Model** | `OrderPayment` | `InstallmentPayment` |
| **File Access** | Automatic after payment | Controlled by admin overrides |

---

## API Endpoints

### **Special Orders:**
- `GET/POST /api/special-orders/` - List/create orders
- `GET/PUT/PATCH /api/special-orders/{id}/` - Retrieve/update order
- `POST /api/special-orders/{id}/approve/` - Approve order (admin)
- `POST /api/special-orders/{id}/override_payment/` - Override payment (admin)
- `POST /api/special-orders/{id}/complete_order/` - Complete order

### **Installments:**
- `GET/POST /api/installment-payments/` - List/create installments
- `GET/PUT/PATCH /api/installment-payments/{id}/` - Manage installments

### **Configuration:**
- `GET/POST /api/predefined-special-order-configs/` - Manage predefined types (admin)
- `GET/POST /api/predefined-special-order-durations/` - Manage duration pricing (admin)
- `GET/POST /api/estimated-special-order-settings/` - Manage deposit settings (admin)

---

## Potential Issues & Notes

### ✅ **FIXED ISSUES:**

### **1. ✅ Status Mismatch in Approval - FIXED**
**Previous Issue:**
```python
order.status = 'approved'  # ❌ Not in STATUS_CHOICES
```

**Fix Applied:**
- Now sets status to `'in_progress'` if deposit is paid
- Otherwise keeps as `'awaiting_approval'` until payment
- Validates status before approval (must be 'inquiry' or 'awaiting_approval')

### **2. ✅ Duplicate save() in SpecialOrder - FIXED**
**Previous Issue:**
- Two `save()` methods defined (lines 195-217 and 236-240)
- Second would override first

**Fix Applied:**
- Merged both `save()` methods into one
- Calculates estimated cost first, then pricing/deposit
- Proper order of operations maintained

### **3. ✅ Installment Generation Logic - FIXED**
**Previous Issue:**
- Always generated 2 installments (50/50 split)
- Didn't respect predefined vs estimated order differences

**Fix Applied:**
- **Predefined orders:** Single installment for full amount (100%)
- **Estimated orders:** Two installments (deposit + balance) based on deposit_required
- Added duplicate check to prevent regenerating installments
- Handles cases where balance might be zero

### **4. Payment Integration:**
- Installments don't integrate with `OrderPayment` model
- Payment gateway integration needed for external payments
- Manual admin override available as workaround

---

## Summary

Special orders provide a flexible system for handling custom writing services with:
- ✅ Two pricing models (predefined vs. estimated)
- ✅ Installment payment support
- ✅ Admin approval workflow
- ✅ Writer assignment and completion tracking
- ✅ Admin override controls
- ✅ Completion logging for audit trail

The workflow is well-structured but has some minor issues around status management and installment payment structure that should be addressed.

