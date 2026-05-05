# Discounts Frontend Handoff

## Core Principle

A client may use one discount per payable item.

No stacking.

A discount can come from:

1. First order discount
2. Manual entered code
3. Holiday discount
4. Campaign discount
5. Loyalty discount
6. Spend tier discount

The backend decides eligibility and final amount.

Frontend should never calculate the final payable amount as the source of
truth.

## Client Checkout UX

At checkout, frontend should:

1. Load available discounts
2. Allow client to enter a code
3. Preview selected discount
4. Show discount amount and final amount
5. Submit selected code during checkout/payment
6. Display applied discount receipt after payment

## Client Endpoints

### Available Discounts

POST `/discounts/client/available/`

Request:

```json
{
  "subtotal": "120.00",
  "payable_type": "order",
  "has_prior_paid_purchase": true,
  "lifetime_spend": "850.00"
}

Response:
```json
{
  "discounts": [
    {
      "discount_code": "HOLIDAY20",
      "name": "Holiday 20",
      "discount_amount": "24.00",
      "final_amount": "96.00",
      "frontend_label": "Holiday offer",
      "frontend_badge": "Limited time",
      "cta_label": "Use HOLIDAY20"
    }
  ]
}

Preview Discount

POST /discounts/client/preview/

Request:
```json
{
  "subtotal": "120.00",
  "payable_type": "order",
  "entered_code": "HOLIDAY20",
  "has_prior_paid_purchase": true,
  "lifetime_spend": "850.00"
}

Response:
```json
{
  "discount": {
    "discount_code": "HOLIDAY20",
    "discount_amount": "24.00",
    "final_amount": "96.00",
    "origin": "holiday",
    "source": "entered_code"
  }
}

Apply Discount

Usually called by checkout/order/payment flow, not directly by simple UI.

POST /discounts/client/apply/

Request:

{
  "subtotal": "120.00",
  "payable_type": "order",
  "payable_id": "123",
  "entered_code": "HOLIDAY20",
  "has_prior_paid_purchase": true,
  "lifetime_spend": "850.00"
}

Response:

{
  "discount_code": "HOLIDAY20",
  "discount_amount": "24.00",
  "final_amount": "96.00",
  "origin": "holiday"
}

Frontend Ideas

Show discount cards with:

- discount code
- savings amount
- final amount
- expiry date
- reason client qualifies
- copy button
- apply button

Example copy:

“You qualify for this tier reward because your lifetime spend has unlocked
Gold savings.”

# Admin Discount Dashboard Handoff

## Admin Capabilities

Admins can:

1. Create discounts
2. Generate discount codes with prefixes
3. Attach discounts to campaigns
4. Create spend tiers
5. Clone campaigns and discounts
6. Archive or restore discounts
7. View dashboard analytics
8. Manage first order discount settings
9. Manage global discount settings

## Useful Dashboard Widgets

### Summary Cards

- Total discounts
- Working discounts
- Scheduled discounts
- Expired discounts
- Archived discounts
- Total redemptions
- Distinct clients
- Total discount given

### Working Discounts Table

Columns:

- Code
- Name
- Origin
- Campaign
- Status
- Usage count
- Distinct clients
- Total discount given
- Starts at
- Ends at

### Abuse Detection

Useful indicators:

- High usage count
- Low distinct clients
- High discount amount
- No per-client usage limit

Example:

If usage count is 100 and distinct clients is 2, admin should review the code.

### Campaign Performance

Show:

- Campaign name
- Discount count
- Usage count
- Distinct clients
- Total discount given
- Status
- Date window

# Client Checkout Discount UX

## Client User Stories

### View Available Discounts

As a client, I want to see discounts I qualify for so that I can choose the
best one before paying.

### Enter Discount Code

As a client, I want to enter a discount code so that I can reduce my payable
amount if the code is valid.

### Understand Why a Discount Failed

As a client, I want a clear message if my discount fails so that I know what
to do next.

Examples:

- This discount has expired.
- You are not eligible for this discount.
- This discount requires a higher subtotal.
- This discount has already been used.

## UX Rules

1. Never show multiple discounts as stacked.
2. Always show one selected discount.
3. Show “best saving” clearly.
4. If first order discount is automatic, show it as automatic.
5. If entered code beats automatic discount, show the chosen winner.
6. Display final amount from backend only.

## Checkout Display Example

Subtotal: `$120.00`

Discount:

`HOLIDAY20 - $24.00`

Final amount:

`$96.00`

CTA:

`Proceed to secure payment`

# Campaign Calendar Handoff

## Purpose

The campaign calendar lets clients see upcoming and active promotions.

## Endpoint

GET `/discounts/client/campaign-calendar/`

Response:

```json
{
  "campaigns": [
    {
      "id": 12,
      "title": "Back to School Promo",
      "description": "Save on essays and class help.",
      "starts_at": "2026-09-01T00:00:00Z",
      "ends_at": "2026-09-15T23:59:59Z",
      "status": "scheduled",
      "badge": "Coming soon",
      "discounts": [
        {
          "code": "SCHOOL15",
          "name": "School 15",
          "discount_type": "percentage",
          "discount_value": "15.00",
          "cta_label": "Use SCHOOL15"
        }
      ]
    }
  ]
}

UX Ideas

Calendar views:

Monthly calendar
Upcoming promotions list
Active campaign banner
Countdown timer
“Copy code” CTA
“Apply at checkout” CTA
Client Display Examples
Scheduled

“Back to School Promo starts September 1.”

Active

“Black Friday is live. Use BLACKFRIDAY20 today.”

Expiring Soon

“Ends in 2 days.”

# Discount Domain Integration Handoff

## Domain Apps

The following apps should integrate with discounts:

1. orders
2. special_orders
3. classes
4. invoices/billing
5. payments_processor

## Integration Boundary

Domain apps should use:

```python
DiscountDomainAdapter
DiscountPayableContext


Domain apps should not directly create DiscountUsage.

Preview Flow

Use preview when:

client is editing checkout
admin is quoting an order
invoice amount is being shown before payment
Apply Flow

Use apply when:

payable is confirmed
invoice is created/finalized
payment intent is initialized
checkout is locked
Orders

Payable type:

order

Metadata:

{
  "source": "orders",
  "order_id": 123
}
Special Orders

Payable type:

special_order

Metadata:

{
  "source": "special_orders",
  "special_order_id": 55
}
Classes

Payable type:

class_order

Metadata:

{
  "source": "classes",
  "class_order_id": 88
}
Payment Safety Rule

The payable final amount must be calculated server-side.

Frontend may show preview values, but backend must reapply or confirm discount
before creating payment intent.
