# Referral Program Eligibility Update

## Overview

Updated the referral program so that clients only become eligible for referral rewards after ordering and approving their first order. This prevents abuse of the referral system.

---

## Changes Made

### 1. Updated Referral Service (`backend/referrals/services/referral_service.py`)

#### `_get_qualifying_order()` Method
- **Before**: Checked for `status='completed'` and `is_paid=True`
- **After**: Checks for `status='approved'` only
- **Reason**: A client must approve their first order to become eligible

#### `apply_discount()` Method
- **Before**: Checked for previous orders with `status='completed'`
- **After**: Checks for previous orders with `status='approved'`
- **Reason**: Only the first approved order qualifies for referral discount

#### `get_referral_discount()` Method
- **Before**: Checked for previous orders with `status='completed'`
- **After**: Checks for previous orders with `status='approved'`
- **Reason**: Consistent with eligibility requirement

### 2. Updated Approve Order Service (`backend/orders/services/approve_order_service.py`)

#### Added `_award_referral_bonus()` Method
- Awards referral bonus when an order is approved
- Checks if this is the first approved order for the client
- Only awards bonus if no previous approved orders exist
- Prevents duplicate bonus awards

#### Updated `approve_order()` Method
- Now calls `_award_referral_bonus()` after approving the order
- Ensures referral bonus is awarded at the right time

### 3. Updated Complete Order Service (`backend/orders/services/complete_order_service.py`)

#### Updated `_award_referral_bonus()` Method
- **Before**: Awarded bonus when order was completed
- **After**: Does nothing (bonus now awarded on approval)
- **Reason**: Bonuses should be awarded when order is approved, not completed

### 4. Updated Referral Model (`backend/referrals/models.py`)

#### `apply_referral_discount()` Method
- **Before**: Checked if order count == 1
- **After**: Checks for previous approved orders
- **Reason**: Only first approved order should get discount

### 5. Updated Referral Admin (`backend/referrals/admin.py`)

#### `award_loyalty_bonus()` Method
- **Before**: Checked for `status='completed'` and `payment_status='paid'`
- **After**: Checks for `status='approved'`
- **Reason**: Consistent with new eligibility requirement

---

## Eligibility Flow

### Before (Old Flow)
1. Client signs up with referral code
2. Referral is recorded
3. Client places first order
4. Order is completed and paid
5. **Referral bonus awarded** ❌ (Too early - abuse risk)

### After (New Flow)
1. Client signs up with referral code
2. Referral is recorded
3. Client places first order
4. Order is completed
5. Client reviews and rates the order
6. Order is approved by client
7. **Referral bonus awarded** ✅ (After approval - prevents abuse)

---

## Benefits

1. **Prevents Abuse**: Clients must actually approve their first order, proving they're a real customer
2. **Quality Control**: Ensures the referred client is satisfied with the service
3. **Fair System**: Only rewards referrals when the client has approved their first order
4. **Reduces Fraud**: Makes it harder to game the system with fake accounts

---

## Technical Details

### Order Status Flow
- `completed` → Order is finished by writer
- `reviewed` → Client has reviewed the order
- `rated` → Client has rated the order
- `approved` → **Client has approved the order** ← Eligibility trigger

### Referral Bonus Award
- Triggered when order status changes to `approved`
- Only for the first approved order
- Checks for previous approved orders to prevent duplicates
- Uses transaction to ensure atomicity

---

## Testing Recommendations

1. **Test First Approved Order**:
   - Create referral
   - Place first order
   - Complete order
   - Review and rate
   - Approve order
   - Verify bonus is awarded

2. **Test Subsequent Orders**:
   - Approve second order
   - Verify bonus is NOT awarded again

3. **Test Multiple Referrals**:
   - Create multiple referrals
   - Approve first order for each
   - Verify each gets bonus only once

4. **Test Edge Cases**:
   - Order cancelled before approval
   - Order rejected
   - Multiple orders before approval

---

## Migration Notes

- No database migration required
- Existing referrals will work with new logic
- Bonuses will only be awarded when orders are approved going forward
- Previously awarded bonuses are not affected

---

*Updated: December 3, 2025*

