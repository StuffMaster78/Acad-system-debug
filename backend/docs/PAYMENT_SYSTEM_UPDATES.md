# Payment System Updates

## Summary of Changes

### 1. Classes Contribute to Overall Earnings ✅
- **Updated**: `PaymentBatchingService.get_earnings_for_period()`
- **Change**: Classes are now included in payment batches (fortnightly/monthly)
- **Implementation**: Class bonuses are added to total bonuses and included in total earnings calculation
- **Result**: Classes contribute to writer's overall earnings in payment batches

### 2. Admin Can Adjust Writer Payment Amounts ✅
- **New Endpoint**: `POST /api/v1/writer-payments/payment-management/{payment_id}/adjust-amount/`
- **Purpose**: Admin can adjust payment amounts whether they were set automatically (level-based) or by admin
- **Request Body**:
  ```json
  {
    "adjustment_amount": 25.00,  // Positive to increase, negative to decrease
    "reason": "Additional pages added"  // Required
  }
  ```
- **Features**:
  - Creates `WriterPaymentAdjustment` record for audit trail
  - Updates payment amount
  - Updates wallet if payment was already processed
  - Logs transaction

### 3. Writer Requests for Additional Pages/Slides ✅
- **Updated**: `WriterRequestService._apply_request_changes()`
- **New Method**: `_recalculate_writer_payment_for_additional_pages()`
- **Behavior**: When additional pages/slides are approved:
  - Order page/slide counts are updated
  - Writer payment is recalculated:
    - If admin set custom payment: Adds level-based amount for additional pages
    - If level-based payment: Recalculates total payment with new page/slide counts
  - Uses writer's level to calculate additional earnings

### 4. Payment View Updates ✅
- **Updated**: `WriterPaymentViewSerializer` and `get_payment_info()` endpoint
- **Changes**:
  - Classes shown in `class_bonuses` field
  - Classes contribute to `total_earnings` (not just bonuses)
  - Shows `payment_set_by` field indicating if payment was admin-set or level-calculated

## How It Works

### Payment Batching (Fortnightly/Monthly)
1. System calculates earnings for the period
2. Includes:
   - Order earnings (admin-set or level-based)
   - Special order earnings
   - Tips
   - Bonuses (including class bonuses)
   - Fines (deducted)
3. Classes are included as bonuses but contribute to total earnings

### Admin Payment Adjustments
1. Admin calls adjustment endpoint with payment ID
2. System:
   - Creates adjustment record
   - Updates payment amount
   - Updates wallet if payment was already processed
   - Logs transaction

### Additional Pages/Slides Requests
1. Writer requests additional pages/slides
2. Client/admin approves request
3. System:
   - Updates order page/slide counts
   - Recalculates writer payment:
     - For admin-set payments: Adds level-based amount for additional pages
     - For level-based payments: Recalculates total with new counts
4. Writer sees updated payment amount

## API Endpoints

### Adjust Payment Amount
```http
POST /api/v1/writer-payments/payment-management/{payment_id}/adjust-amount/
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "adjustment_amount": 25.00,
  "reason": "Additional pages added after approval"
}
```

**Response:**
```json
{
  "message": "Payment amount adjusted successfully",
  "payment_id": 123,
  "old_amount": "100.00",
  "new_amount": "125.00",
  "adjustment_amount": "25.00",
  "adjustment_id": 456
}
```

## Testing Checklist

- [ ] Test payment batching includes class bonuses in total earnings
- [ ] Test admin can adjust payment amounts (both admin-set and level-based)
- [ ] Test writer request for additional pages updates writer payment
- [ ] Test writer request for additional slides updates writer payment
- [ ] Verify adjustment records are created and logged
- [ ] Verify wallet is updated when adjusting paid payments
- [ ] Test classes contribute to fortnightly/monthly payment batches

## Notes

- Classes are paid as bonuses but contribute to overall earnings
- Admin adjustments work for both admin-set and level-based payments
- Additional pages/slides automatically recalculate writer payment
- All adjustments are logged for audit trail
