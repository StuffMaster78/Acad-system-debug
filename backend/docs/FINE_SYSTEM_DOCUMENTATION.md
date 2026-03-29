# Writer Fine System - Complete Documentation

## Overview

A comprehensive fine system for writers with progressive hourly lateness fines, admin-configurable rules, dispute workflow, and escalation handling.

---

## Features

### 1. Progressive Hourly Lateness Fines
- **Cumulative Mode** (Default): Fines accumulate per hour
  - 1st hour: 5%
  - 2nd hour: +10% (total: 15%)
  - 3rd hour: +15% (total: 30%)
  - Hours 4-24: +5% per hour
  - After 24 hours: +20% per day
  
- **Progressive Mode**: Use percentage for the hour range
  - 0-1 hour: 5%
  - 1-2 hours: 10%
  - 2-3 hours: 15%
  - etc.

### 2. Admin-Configurable Fine Rules
- Website-specific fine rules via `LatenessFineRule`
- Configurable percentages per hour
- Choice of calculation mode (cumulative/progressive)
- Base amount selection (writer compensation or order total)
- Maximum fine cap
- Date-based activation/deactivation

### 3. Automatic Fine Application
- Fines automatically issued when writer submits late order
- Uses `order.submitted_at` timestamp
- Checks against `order.client_deadline` or `order.writer_deadline`
- Immediately adjusts writer compensation

### 4. Admin Controls
- **Waive Fine**: Restores compensation, marks fine as waived
- **Void/Revoke Fine**: Completely removes fine, restores compensation
- **Bulk Actions**: Waive/void multiple fines at once (Django Admin)

### 5. Writer Dispute Workflow
- Writers can dispute fines on their orders
- Dispute creates `FineAppeal` record
- Fine status changes to `DISPUTED`
- Escalation to admin/superadmin for resolution

### 6. Dispute Resolution
- Admin/superadmin can review disputes
- Accept dispute → Fine waived, compensation restored
- Reject dispute → Fine upheld, compensation remains reduced
- Escalation support for complex cases

---

## Models

### LatenessFineRule

Admin-configurable fine rules per website.

**Key Fields:**
- `website`: ForeignKey to Website
- `first_hour_percentage`: Fine % for first hour (default: 5%)
- `second_hour_percentage`: Fine % for second hour (default: 10%)
- `third_hour_percentage`: Fine % for third hour (default: 15%)
- `subsequent_hours_percentage`: Fine % per hour after 3 hours (default: 5%)
- `daily_rate_percentage`: Fine % per day after 24 hours (default: 20%)
- `max_fine_percentage`: Maximum fine cap (optional)
- `calculation_mode`: 'cumulative' or 'progressive'
- `base_amount`: 'writer_compensation' or 'total_price'
- `active`: Boolean
- `start_date`, `end_date`: Activation period

### Fine

Represents a fine issued to an order.

**Status Flow:**
1. `ISSUED` - Fine automatically issued
2. `DISPUTED` - Writer disputes the fine
3. `ESCALATED` - Dispute escalated for resolution
4. `RESOLVED` - Dispute reviewed, fine upheld
5. `WAIVED` - Fine waived (compensation restored)
6. `VOIDED` - Fine voided/revoked by admin

### FineAppeal

Represents a dispute/appeal against a fine.

**Key Fields:**
- `fine`: OneToOne to Fine
- `reason`: Writer's justification
- `appealed_by`: Writer who disputed
- `reviewed_by`: Admin who reviewed
- `accepted`: Boolean (True = waived, False = upheld)
- `escalated`: Boolean
- `escalated_to`: Admin handling escalation
- `resolution_notes`: Reviewer notes

---

## Calculation Examples

### Example 1: Cumulative Mode (2.5 hours late)
```
Base: Writer Compensation = $100

Calculation:
- Hour 1: 5% = $5
- Hour 2: 10% = $10
- Hour 2.5: Additional 0% (still in hour 2)

Total Fine: $15 (15% of $100)
```

### Example 2: Cumulative Mode (5 hours late)
```
Base: Writer Compensation = $200

Calculation:
- Hour 1: 5% = $10
- Hour 2: 10% = $20
- Hour 3: 15% = $30
- Hours 4-5: 2 × 5% = 2 × $10 = $20

Total Fine: $80 (40% of $200)
```

### Example 3: With Max Cap (24 hours late)
```
Base: Writer Compensation = $100
Max Cap: 50%

Without cap: Would be ~120% (capped)
Total Fine: $50 (50% of $100, max cap applied)
```

---

## API Endpoints

### Fine Management

#### List Fines
**GET** `/api/v1/fines/api/fines/`

**Response:** List of fines (filtered by user role)

#### Get Fine
**GET** `/api/v1/fines/api/fines/{id}/`

#### Dispute Fine (Writer)
**POST** `/api/v1/fines/api/fines/{id}/dispute/`

**Request Body:**
```json
{
  "reason": "I submitted on time but deadline was extended. Please review."
}
```

**Response:**
```json
{
  "id": 1,
  "fine": 123,
  "fine_amount": "15.00",
  "reason": "...",
  "status": "disputed",
  ...
}
```

#### Waive Fine (Admin)
**POST** `/api/v1/fines/api/fines/{id}/waive/`

**Request Body:**
```json
{
  "reason": "Deadline extension approved, fine waived"
}
```

#### Void Fine (Admin)
**POST** `/api/v1/fines/api/fines/{id}/void/`

**Request Body:**
```json
{
  "reason": "Fine issued incorrectly"
}
```

### Dispute Management

#### List Disputes
**GET** `/api/v1/fines/api/fine-appeals/`

#### Get Dispute
**GET** `/api/v1/fines/api/fine-appeals/{id}/`

#### Review Dispute (Admin)
**POST** `/api/v1/fines/api/fine-appeals/{id}/review/`

**Request Body:**
```json
{
  "accept": true,
  "review_notes": "Deadline extension verified. Fine waived."
}
```

**Response:**
- If `accept: true` → Fine waived, compensation restored
- If `accept: false` → Fine upheld, compensation remains reduced

#### Escalate Dispute (Admin)
**POST** `/api/v1/fines/api/fine-appeals/{id}/escalate/`

**Request Body:**
```json
{
  "escalated_to_id": 5,
  "escalation_reason": "Requires senior admin review"
}
```

### Fine Rule Configuration (Admin)

#### List Rules
**GET** `/api/v1/fines/api/lateness-rules/`

#### Get Active Rule
**GET** `/api/v1/fines/api/lateness-rules/active_rule/`

**Response:** Current active rule or defaults

#### Create Rule
**POST** `/api/v1/fines/api/lateness-rules/`

**Request Body:**
```json
{
  "first_hour_percentage": "5.00",
  "second_hour_percentage": "10.00",
  "third_hour_percentage": "15.00",
  "subsequent_hours_percentage": "5.00",
  "daily_rate_percentage": "20.00",
  "calculation_mode": "cumulative",
  "base_amount": "writer_compensation",
  "max_fine_percentage": "50.00",
  "active": true,
  "description": "Standard lateness fine policy"
}
```

#### Update Rule
**PUT/PATCH** `/api/v1/fines/api/lateness-rules/{id}/`

---

## Workflow

### 1. Automatic Fine Issuance

```
Writer submits order → SubmitOrderService.execute()
  ↓
Order.submitted_at = now()
  ↓
auto_issue_late_fine(order)
  ↓
LateFineCalculationService.calculate_late_fine()
  ↓
If late:
  - Calculate fine amount (progressive hourly)
  - Create Fine record
  - Adjust writer compensation (-fine_amount)
  - Status: ISSUED
```

### 2. Writer Disputes Fine

```
Writer calls POST /fines/{id}/dispute/
  ↓
FineAppealService.submit_appeal()
  ↓
Create FineAppeal record
  ↓
Fine.status = DISPUTED
  ↓
Status: DISPUTED (awaiting review)
```

### 3. Admin Reviews Dispute

```
Admin calls POST /fine-appeals/{id}/review/
  {
    "accept": true/false,
    "review_notes": "..."
  }
  ↓
FineAppealService.review_appeal()
  ↓
If accept = true:
  - FineService.waive_fine()
  - Fine.status = WAIVED
  - Restore compensation
If accept = false:
  - Fine.status = RESOLVED
  - Fine upheld
```

### 4. Admin Waives/Voids Fine

```
Admin calls POST /fines/{id}/waive/ or /void/
  ↓
FineService.waive_fine() or void_fine()
  ↓
- Fine.status = WAIVED/VOIDED
- Restore writer compensation
- Fine resolved
```

### 5. Escalation (Optional)

```
Support/Admin calls POST /fine-appeals/{id}/escalate/
  ↓
FineAppealService.escalate_dispute()
  ↓
- appeal.escalated = True
- appeal.escalated_to = admin
- Fine.status = ESCALATED
- Senior admin reviews
```

---

## Permissions

### Writers
- ✅ View their own fines
- ✅ Dispute their own fines
- ❌ Cannot waive/void fines
- ❌ Cannot review disputes

### Admins/Superadmins
- ✅ View all fines
- ✅ Waive fines
- ✅ Void/revoke fines
- ✅ Review disputes
- ✅ Escalate disputes
- ✅ Configure fine rules

### Support
- ✅ View all fines
- ✅ Review disputes
- ✅ Escalate disputes
- ❌ Cannot waive/void fines (unless escalated)

---

## Django Admin

### Fine Admin
- List display: id, order, fine_type, amount, status, imposed_at
- Filters: fine_type, status, imposed_at, resolved
- Actions: `waive_selected_fines`, `void_selected_fines`

### FineAppeal Admin
- List display: id, fine, appealed_by, created_at, reviewed_by, accepted, escalated
- Filters: accepted, escalated, created_at

### LatenessFineRule Admin
- Full CRUD interface
- Fieldsets organized by category
- Tracks created_by admin

---

## Configuration Best Practices

### Default Progressive Rates
```python
{
    "first_hour_percentage": 5.00,
    "second_hour_percentage": 10.00,
    "third_hour_percentage": 15.00,
    "subsequent_hours_percentage": 5.00,
    "daily_rate_percentage": 20.00,
    "calculation_mode": "cumulative",
    "base_amount": "writer_compensation",
    "max_fine_percentage": 50.00  # Cap at 50%
}
```

### Recommendations
1. **Start Conservative**: Lower percentages for first few hours
2. **Set Max Cap**: Prevent excessive fines (recommend 50-100%)
3. **Use Cumulative Mode**: More intuitive for writers
4. **Base on Writer Compensation**: Fairer than total price
5. **Review Regularly**: Adjust percentages based on data

---

## Integration Points

### With Order Submission
- `SubmitOrderService` automatically calls `auto_issue_late_fine()`
- Fine issued immediately upon late submission

### With Writer Compensation
- Fine amount deducted from `order.writer_compensation`
- Compensation restored if fine waived/voided

### With Audit Logging
- All fine actions logged
- Includes waiver, void, dispute, review actions

### With Notifications (Future)
- Notify writer when fine issued
- Notify writer when dispute reviewed
- Notify admin when dispute submitted

---

## Error Handling

### Common Errors

1. **Fine Already Issued**
   - Error: Fine already exists for this order
   - Solution: Check for existing fine before issuing

2. **Cannot Dispute**
   - Error: "Only 'issued' fines can be disputed"
   - Solution: Writer can only dispute fines in `ISSUED` status

3. **Permission Denied**
   - Error: "Only admins can waive fines"
   - Solution: Use admin/superadmin account

4. **Dispute Already Reviewed**
   - Error: "This appeal has already been reviewed"
   - Solution: Cannot review same dispute twice

---

## Testing Scenarios

### Test Case 1: On-Time Submission
- Writer submits order 1 hour before deadline
- Expected: No fine issued

### Test Case 2: 1.5 Hours Late
- Writer submits 1.5 hours after deadline
- Expected: Fine = 5% of writer compensation (first hour only)

### Test Case 3: 3 Hours Late
- Writer submits 3 hours after deadline
- Expected: Fine = 30% cumulative (5% + 10% + 15%)

### Test Case 4: Writer Disputes
- Writer disputes fine with reason
- Expected: Fine status = DISPUTED, FineAppeal created

### Test Case 5: Admin Waives
- Admin waives fine with reason
- Expected: Fine status = WAIVED, compensation restored

### Test Case 6: Admin Voids
- Admin voids fine
- Expected: Fine status = VOIDED, compensation restored

### Test Case 7: Dispute Accepted
- Admin reviews dispute, accepts
- Expected: Fine waived, compensation restored

### Test Case 8: Dispute Rejected
- Admin reviews dispute, rejects
- Expected: Fine upheld, compensation remains reduced

---

## Migration Notes

1. **Order Model**: Added `submitted_at` field (null=True)
   - Existing orders will have `submitted_at = None`
   - Fine calculation skips if `submitted_at` is None

2. **Fine Status**: Added new statuses
   - `DISPUTED`, `ESCALATED`, `VOIDED`
   - Existing fines remain with current status

3. **FineAppeal Model**: Enhanced with escalation fields
   - Existing appeals have `escalated = False`

---

## Future Enhancements

1. **Notification Integration**: Notify users of fine actions
2. **Fine Analytics**: Dashboard showing fine trends
3. **Writer Fine History**: Track writer fine patterns
4. **Automated Warnings**: Warn writers before fine thresholds
5. **Fine Payment Plans**: Allow installment payment of large fines
6. **Fine Exemptions**: Exempt certain writers or order types
7. **Fine Appeals Time Limit**: Set deadline for disputing fines
8. **Fine Policy History**: Track changes to fine rules over time

