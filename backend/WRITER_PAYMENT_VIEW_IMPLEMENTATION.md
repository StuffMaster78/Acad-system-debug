# Writer Payment View Implementation

## Overview
Implemented a writer-specific payment view system that shows only level-based payment information (cost per page, per slide, per class) and excludes installments and internal payment details.

## Changes Made

### 1. WriterPaymentViewSerializer (`backend/writer_management/serializers.py`)
- **Purpose**: Serializer for writers to view their payment information
- **Features**:
  - Shows level-based payment rates (cost per page, per slide, per class)
  - Excludes installments from payment calculations
  - Provides breakdown of earnings by order type (regular orders, special orders, classes)
  - Calculates totals for bonuses and tips (excluding installments)

### 2. Payment Info Endpoint (`backend/writer_management/views_dashboard.py`)
- **Endpoint**: `GET /api/v1/writer-dashboard/payment-info/`
- **Purpose**: Returns writer's payment information based on their level
- **Response includes**:
  - `cost_per_page`: Base pay per page from writer level
  - `cost_per_slide`: Base pay per slide from writer level
  - `cost_per_class`: Base pay per class (if configured)
  - `level_name`: Current writer level name
  - `earning_mode`: How earnings are calculated (fixed_per_page, percentage_of_order_cost, etc.)
  - `order_earnings`: List of earnings from regular orders (excluding installments)
  - `special_order_earnings`: List of earnings from special orders
  - `class_earnings`: List of earnings from classes
  - `total_earnings`: Sum of all earnings
  - `total_bonuses`: Total bonuses received
  - `total_tips`: Total tips received

### 3. Updated Earnings Endpoint
- **Endpoint**: `GET /api/v1/writer-dashboard/earnings/`
- **Changes**: Now excludes payments related to installments from calculations

### 4. Extended Earnings Calculator (`backend/writer_management/services/earnings_calculator.py`)
- **New Methods**:
  - `calculate_class_earnings()`: Calculates earnings for class purchases
  - `calculate_special_order_earnings()`: Calculates earnings for special orders (excluding installments)

## How It Works

### For Regular Orders
- Writers see payment based on their level's `base_pay_per_page` and `base_pay_per_slide`
- Or percentage-based if their level uses percentage earning mode
- Installments are automatically excluded

### For Special Orders
- Uses the same calculation logic as regular orders
- Adds special order bonus if available
- Excludes installment payment details

### For Classes
- Uses `base_pay_per_class` if configured in writer level
- Falls back to percentage-based calculation if class rate not set
- **Note**: Class-writer relationship needs to be defined in your models

## What Still Needs to Be Done

### 1. Class Payment Structure
- **Issue**: Class-writer relationship needs to be defined
- **Action Required**: 
  - Determine how classes are assigned to writers
  - Update `get_class_earnings()` method in `WriterPaymentViewSerializer` to filter classes correctly
  - Add `base_pay_per_class` field to `WriterLevel` model if not already present

### 2. WriterLevel Model Enhancement
- **Check**: Does `WriterLevel` have `base_pay_per_class` field?
- **If not**: Add migration to add this field:
  ```python
  base_pay_per_class = models.DecimalField(
      max_digits=10,
      decimal_places=2,
      default=0.00,
      help_text="Base pay per class (for class-based orders)."
  )
  ```

### 3. Special Order Payment Calculation
- **Current**: Uses standard order calculation + bonus
- **Consider**: Should special orders have different payment rates?
- **Action**: Review if special orders need unique payment calculation logic

### 4. Installment Exclusion
- **Current**: Excludes payments with "installment" in description
- **Consider**: May need more robust filtering if installments are tracked differently
- **Action**: Review how installments are stored and adjust exclusion logic if needed

## API Usage

### Get Payment Info
```http
GET /api/v1/writer-dashboard/payment-info/
Authorization: Bearer <writer_token>
```

**Response:**
```json
{
  "cost_per_page": "5.00",
  "cost_per_slide": "3.00",
  "cost_per_class": null,
  "level_name": "Intermediate",
  "earning_mode": "fixed_per_page",
  "order_earnings": [
    {
      "order_id": 123,
      "order_topic": "Essay on History",
      "pages": 5,
      "slides": 0,
      "amount": 25.00,
      "completed_at": "2025-01-15T10:30:00Z"
    }
  ],
  "special_order_earnings": [],
  "class_earnings": [],
  "total_earnings": "25.00",
  "total_bonuses": "0.00",
  "total_tips": "0.00"
}
```

## Testing Checklist

- [ ] Test payment info endpoint with different writer levels
- [ ] Verify installments are excluded from calculations
- [ ] Test with special orders
- [ ] Test with classes (once class-writer relationship is defined)
- [ ] Verify percentage-based earning modes work correctly
- [ ] Test urgency and technical bonuses are included
- [ ] Verify bonuses and tips are calculated correctly

## Notes

- Writers will only see their level-based payment rates, not the full payment breakdown
- Installments are completely hidden from writer views
- Payment calculations respect the writer's level configuration
- Special orders and classes use the same level-based calculation as regular orders
