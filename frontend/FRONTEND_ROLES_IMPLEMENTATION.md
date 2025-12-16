# Frontend Roles Implementation

## Summary

Built necessary frontend components for role-based payment management features:

## Components Created

### 1. Admin Payment Adjustment Modal
**File**: `frontend/src/components/admin/PaymentAdjustmentModal.vue`

**Purpose**: Allows admins to adjust writer payment amounts (increase or decrease)

**Features**:
- Shows current payment information
- Input for adjustment amount (positive/negative)
- Required reason field for audit trail
- Preview of new payment amount
- Color-coded display (green for increase, red for decrease)

**Usage**:
```vue
<PaymentAdjustmentModal
  :is-open="showModal"
  :payment="paymentData"
  @close="closeModal"
  @success="handleSuccess"
/>
```

### 2. Writer Request Additional Pages/Slides Modal
**File**: `frontend/src/components/writer/RequestAdditionalPagesModal.vue`

**Purpose**: Allows writers to request additional pages or slides for an order

**Features**:
- Radio buttons for request type (pages or slides)
- Input for number of additional pages/slides
- Required reason field
- Shows new total after addition
- Estimated cost display (if available)

**Usage**:
```vue
<RequestAdditionalPagesModal
  :is-open="showModal"
  :order="orderData"
  @close="closeModal"
  @success="handleSuccess"
/>
```

## API Updates

### 1. Writer Payments API
**File**: `frontend/src/api/writer-payments.js`

**Added**:
- `adjustPaymentAmount(paymentId, data)` - Adjust payment amount endpoint

### 2. Orders API
**File**: `frontend/src/api/orders.js`

**Added**:
- `createWriterRequest(orderId, data)` - Create writer request for additional pages/slides
- `getWriterRequests(orderId)` - Get writer requests for an order
- `approveWriterRequest(orderId, requestId, data)` - Approve writer request

### 3. Writer Dashboard API
**File**: `frontend/src/api/writer-dashboard.js`

**Added**:
- `getPaymentInfo()` - Get payment information from dashboard endpoint

## View Updates

### 1. All Writer Payments (Admin)
**File**: `frontend/src/views/admin/AllWriterPayments.vue`

**Changes**:
- Added "Adjust" button in actions column
- Integrated PaymentAdjustmentModal component
- Added handlers for opening/closing adjust modal
- Added success handler to reload payments after adjustment

**Features**:
- Admins can adjust any payment amount
- Shows payment details in modal
- Updates payment list after successful adjustment

## Role-Based Access

### Admin/Superadmin
- Can adjust writer payment amounts
- Can view all writer payments
- Can approve writer requests for additional pages/slides

### Writer
- Can request additional pages/slides for assigned orders
- Can view their own payment information
- Can see payment breakdowns

## Next Steps

1. **Admin Order Assignment**: Update order assignment component to include payment amount input
2. **Writer Payment View**: Update writer payment view to use new payment-info endpoint
3. **Writer Request Approval**: Create admin component to approve/decline writer requests
4. **Special Order Assignment**: Add payment amount/percentage input for special orders
5. **Class Assignment**: Add bonus amount input for class assignments

## Testing Checklist

- [ ] Admin can open payment adjustment modal
- [ ] Admin can adjust payment amounts (positive and negative)
- [ ] Adjustment requires reason
- [ ] Payment list updates after adjustment
- [ ] Writer can request additional pages/slides
- [ ] Writer request shows estimated cost
- [ ] Writer request requires reason
- [ ] API endpoints are correctly called
- [ ] Error handling works correctly
- [ ] Loading states display properly
