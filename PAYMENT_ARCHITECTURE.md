# Payment Processing Architecture

## Overview

All payments across GradeCrest, EssayManiacs, NurseMyGrade, and ResearchPaperMate
flow through a single intermediary merchant account (OrderBridge) that holds the
Stripe integration. Clients pay via Stripe's hosted checkout and never interact with
OrderBridge directly — it only appears on their bank statement. Django receives the
webhook, fulfils the order, and the client is redirected back to the portal.

---

## Merchant model

| Who | Role |
|---|---|
| OrderBridge | Stripe account holder — receives funds |
| GC / EM / NMG / RPM | Branded portals — clients interact here |
| Django backend (`api.[site].com`) | Creates sessions, verifies webhooks, fulfils orders |

**Disclosure requirement:** Before reaching the Pay button, the `PaymentDisclosureBanner`
component (variant="pre") shows the intermediary name and statement descriptor. On
post-payment the same component (variant="post") shows a confirmation. Both `shown`
and `acknowledged` events are recorded server-side. The disclosure text snapshot is
stored on every payment model at creation time.

---

## Payment flows

There are seven distinct checkout entry points. All route through
`PaymentOrchestrationService` → Stripe Checkout Session → webhook confirmation.

| Entry point | Purpose code | Who triggers |
|---|---|---|
| Order payment | `order` | Client placing a new order |
| Special order payment | `special_order` | Admin-created bespoke order |
| Class purchase | `class_purchase` | Client buying an academic session |
| Wallet top-up | `wallet_top_up` | Client funding their wallet |
| Tip | `tip` | Client tipping a writer after delivery |
| Invoice payment | `invoice` / `billing_payment_request` | Admin-issued invoice or payment request |
| Extra order charge | `extra_order_charge` | Admin adding a post-creation charge |

---

## Stripe configuration

### Environment variables (`.env`)

```env
STRIPE_SECRET_KEY=sk_live_...          # server-only — never sent to browser
STRIPE_PUBLISHABLE_KEY=pk_live_...     # available to frontend for Stripe.js if needed
STRIPE_WEBHOOK_SECRET=whsec_...        # HMAC key for webhook signature verification
INFOQ_PAYMENT_BASE_URL=https://app.gradecrest.com   # portal base URL for Stripe redirects
```

`INFOQ_PAYMENT_BASE_URL` controls the `success_url` and `cancel_url` sent to Stripe:

```
success_url  →  {INFOQ_PAYMENT_BASE_URL}/payment/complete?status=success&ref={reference}
cancel_url   →  {INFOQ_PAYMENT_BASE_URL}/payment/complete?status=cancelled&ref={reference}
```

In dev use `http://localhost:5173` (the Vite frontend port).
In production use the portal base URL for the primary site (e.g. `https://app.gradecrest.com`).

> **Note:** For multi-site deployments where clients pay from different portals, a future
> improvement is to set `INFOQ_PAYMENT_BASE_URL` dynamically from `payment_intent.website.root_url`.
> Currently it is a single global setting — clients always return to the configured base URL.

### Webhook endpoint

Register **one** endpoint in the OrderBridge Stripe dashboard:

```
POST https://api.[site].com/api/payments/webhooks/stripe/
```

Subscribe to these events:

| Event | Handled by |
|---|---|
| `checkout.session.completed` | `WebhookProcessingService` → payment succeeded |
| `payment_intent.succeeded` | `WebhookProcessingService` → payment succeeded |
| `payment_intent.payment_failed` | `WebhookProcessingService` → payment failed |
| `charge.failed` | `WebhookProcessingService` → payment failed |
| `checkout.session.expired` | `WebhookProcessingService` → session expired |
| `charge.dispute.created` | `WebhookProcessingService` → creates `PaymentDispute` row |
| `charge.dispute.updated` | `WebhookProcessingService` → updates `PaymentDispute.status` |
| `charge.dispute.closed` | `WebhookProcessingService` → closes `PaymentDispute`, sets `resolved_at` |
| `charge.dispute.funds_reinstated` | `WebhookProcessingService` → closes dispute (won) |
| `charge.dispute.funds_withdrawn` | `WebhookProcessingService` → closes dispute (lost) |

---

## Code walkthrough — happy path (order payment)

### Step 1 — Client submits order

**Frontend:** `NewOrderView.vue` → `orders.createPaperOrder()` →

```
POST /api/orders/paper-orders/
  { topic, instructions, deadline, pages, ..., payment_provider: "stripe" }
```

**Backend:** `OrderCreationView`:

1. Validates request, resolves client and website
2. **`OrderCreationService.create_order()`** — creates `Order` row
3. **`OrderPaymentApplicationService.start_checkout(order, provider="stripe")`**:
   - Applies discount codes, calculates outstanding amount
   - **`PaymentIntentService.create_intent()`**:
     - Generates unique `reference` (e.g. `pay_order_42_abc123`)
     - Creates `PaymentIntent` row (`status=CREATED`)
     - Calls **`StripePaymentProvider.create_payment()`** → `stripe.checkout.Session.create()` with:
       - `client_reference_id = reference`
       - `customer_email = client.email`
       - `metadata.reference = reference`
       - `success_url = {INFOQ_PAYMENT_BASE_URL}/payment/complete?status=success&ref={reference}`
       - `cancel_url  = {INFOQ_PAYMENT_BASE_URL}/payment/complete?status=cancelled&ref={reference}`
     - Stores `session.id` → `provider_intent_id`; updates status to `PENDING`
4. Returns `{ checkout_url, reference }` to frontend

**Frontend:** `window.location.href = checkout_url` → browser navigates to Stripe.

### Step 2 — Stripe processes payment

Client enters card on Stripe's hosted page. Stripe:
- Fires signed `POST` to `/api/payments/webhooks/stripe/` (server-to-server)
- Redirects client to `success_url` → `/payment/complete?status=success&ref=...`

### Step 3 — Webhook processing

`WebhookProcessingService.process_webhook()`:

1. Validates provider key and payload shape
2. Verifies HMAC signature via `stripe.Webhook.construct_event()`
3. Parses event into a unified `ProviderWebhookEvent` struct
4. Deduplicates via `ProviderWebhookEvent` unique constraint on `(provider, event_id)`
5. Resolves `PaymentIntent` by `reference`; records `PaymentTransaction`
6. Updates `PaymentIntent.status → SUCCEEDED`
7. On commit: enqueues `apply_payment_intent_task.delay(payment_intent.pk)`

**Dispute events** are intercepted before step 5 and routed to `_handle_dispute_event()`,
which resolves the `PaymentIntent` via `PaymentTransaction.provider_transaction_id`
(the Stripe charge ID) and writes/updates a `PaymentDispute` row.

### Step 4 — Celery fulfils the order

`apply_payment_intent_task` → `PaymentApplicationService.apply_payment()` routes by `purpose`:

| `purpose` | Effect |
|---|---|
| `order` | Order marked paid; files unlocked |
| `wallet_top_up` | Client wallet credited via `WalletService.credit_wallet()` |
| `class_purchase` | Class access granted |
| `invoice` | Invoice/installment marked paid; receipt issued |
| `billing_payment_request` | Payment request marked paid; receipt issued |
| `tip` | Tip marked paid, writer wallet credited |

Sets `application_status = APPLIED` on success. On failure: `APPLICATION_FAILED`; Celery retries up to 3× with exponential backoff.

### Step 5 — Client lands on `/payment/complete`

`PaymentCompleteView.vue` reads `?status=success|cancelled&ref={reference}`:
- `success`: shows green confirmation, links to dashboard and billing
- `cancelled`: shows neutral state, links back to billing

The page waits ~1.8 s before rendering (gives the webhook time to land) then shows
the appropriate state. No polling — the order/invoice status is fresh on next navigation.

---

## Billing flows (invoice and payment request)

Invoices and payment requests are admin-created charges. They have two payment paths:

### Path A — Portal (authenticated client)

```
Client logs in → Billing tab → Invoices / Payment Requests
  → "Pay by card" button
  → POST /billing/my/invoices/<id>/prepare-payment/   (or /my/payment-requests/)
  → Returns { checkout_url }
  → window.location.href = checkout_url
  → Stripe → webhook → InvoiceOrchestrationService.apply_verified_invoice_payment()
  → Receipt issued → billing.receipt.issued notification
```

### Path B — Email link (unauthenticated)

When an invoice or payment request is issued with `send_notification=True`, a
`billing.invoice.issued` notification fires. The email contains a `pay_url`:

```
pay_url = {website.root_url}/pay/invoice/{payment_token}
       or {website.root_url}/pay/payment-request/{payment_token}
```

The client opens this URL without logging in:

```
/pay/:type/:token  →  PublicPayView.vue
  → POST /billing/pay/invoices/<token>/prepare/  (AllowAny)
  → Returns { invoice, checkout_url }
  → Shows invoice summary + disclosure text
  → Client clicks "Pay securely"
  → window.location.href = checkout_url
  → Stripe → webhook → same fulfillment as Path A
```

**Token security:** `payment_token` is a `secrets.token_urlsafe(32)` value generated
by `InvoiceService.ensure_payment_token()`. Tokens expire after 72 hours by default
(configurable via `token_expiry_hours`). Expired tokens return 404.

### Installment schedules

Invoices can be split into installment schedules:

```
POST /billing/invoices/<id>/installments/  { schedule: [{amount, due_at}...] }
```

Each installment is paid independently via:
```
POST /billing/installments/<id>/prepare-payment/  { provider: "stripe" }
```

Celery beat tasks schedule upcoming and overdue installment reminders automatically.

### Receipt issuance

A `Receipt` row is written and `billing.receipt.issued` fires automatically after every
successful invoice or payment request settlement. Receipt emails include:
- Amount and reference
- Disclosure text (processor name + statement descriptor snapshot)
- Support contact

---

## Notification seeding (run once on first deploy)

The notification system requires two management commands to activate billing notifications.
These are **idempotent** — safe to re-run; existing rows are never overwritten.

```bash
# 1. Register event keys in the DB from the enum
docker compose exec web python manage.py seed_notification_events

# 2. Seed default email and in-app templates for all events
docker compose exec web python manage.py seed_templates
```

To update templates after changes:

```bash
docker compose exec web python manage.py seed_templates --update
```

Billing event keys now registered:

| Event key | Channel | Template |
|---|---|---|
| `billing.invoice.issued` | email + in_app | `invoice_issued.html` |
| `billing.invoice.settled` | email + in_app | `payment_received.html` |
| `billing.invoice.reminder` | email + in_app | `payment_reminder.html` |
| `billing.payment_request.issued` | email + in_app | `payment_request_issued.html` |
| `billing.payment_request.settled` | email + in_app | `payment_received.html` |
| `billing.payment_request.reminder` | email + in_app | `payment_reminder.html` |
| `billing.receipt.issued` | email + in_app | `receipt.html` |
| `billing.installment.upcoming` | email + in_app | `payment_reminder.html` |
| `billing.installment.due` | email + in_app | `payment_reminder.html` |
| `billing.installment.overdue` | email + in_app | `payment_reminder.html` |

---

## Per-tenant redirect routing

`Website.root_url` stores the frontend base URL per site:

| Website | `root_url` |
|---|---|
| GradeCrest | `https://app.gradecrest.com` |
| EssayManiacs | `https://app.essaymaniacs.com` |
| NurseMyGrade | `https://app.nursemygrade.com` |
| ResearchPaperMate | `https://app.researchpapermate.com` |

`pay_url` in invoice/payment-request emails uses `website.root_url`:
```
{website.root_url}/pay/invoice/{payment_token}
```

The global `INFOQ_PAYMENT_BASE_URL` setting controls where Stripe redirects after checkout.
These two should match for a given site. In a future improvement they will be unified.

---

## Frontend routes (payment-related)

| Route | View | Auth |
|---|---|---|
| `/payment/complete` | `PaymentCompleteView.vue` | Public |
| `/pay/invoice/:token` | `PublicPayView.vue` | Public (token-gated) |
| `/pay/payment-request/:token` | `PublicPayView.vue` | Public (token-gated) |
| `/client/billing` | `ClientBillingView.vue` | Authenticated client |

`ClientBillingView` has three tabs: **Invoices** (with installment pay buttons and
single-invoice pay button), **Payment Requests** (with Pay now button for `issued` status),
and **Receipts** (read-only list with disclosure details).

---

## Speed profile and the pre-warm optimization

### Current timing

```
Client click → "Placing order…" spinner
    ~50ms   DB write (order creation)
    ~400ms  stripe.checkout.Session.create()   ← bottleneck
    ~50ms   DB save + response
    → browser navigates to Stripe
```

Total perceivable delay: **~500–800ms** before Stripe page appears.

### Pre-warm strategy (removes the delay)

Price is known when the client selects "Pay by card" before clicking Submit.
The Stripe session can be created in the background then.

```
Client selects "Pay by card"  (price quoted)
    │
    ▼  POST /api/payments/checkout/   ← background, no spinner
       Creates PaymentIntent + Stripe session
       Stores { reference, checkout_url } in component state
    │
    Client fills form fields...
    │
    ▼  Client clicks Submit
       POST /api/orders/paper-orders/  { preauth_reference: reference }
       Backend: creates order + links existing PaymentIntent — no Stripe API call
       Returns ~100ms
    │
    ▼  window.location.href = checkout_url   ← INSTANT
```

If price changes after pre-warm (coupon applied): frontend detects mismatch and falls
back to the standard flow. Pre-warm is an optimisation, not a requirement.

**Backend changes still needed:** `OrderPaymentApplicationService.start_checkout()` needs
a `preauth_reference` param to look up and reuse an existing `PaymentIntent` by reference.

---

## Refunds

```
POST /api/payments/refunds/  →  InitiateRefundView
```

`StripePaymentProvider.refund_payment()`:
1. Retrieves Checkout Session (`cs_...`) → gets `payment_intent`
2. Retrieves PaymentIntent → gets `latest_charge`
3. `stripe.Refund.create(charge=charge_id, amount=cents)`

Partial refunds supported. Refund state is tracked on `PaymentRefund` and reconciled
via `PaymentReconciliationService`.

---

## Disputes

`charge.dispute.created` and related events are now handled automatically:

1. Webhook arrives → `WebhookProcessingService._handle_dispute_event()`
2. Resolves linked `PaymentIntent` via `PaymentTransaction.provider_transaction_id`
   (the Stripe charge ID stored when the original payment was processed)
3. `get_or_create` a `PaymentDispute` row
4. Subsequent events update `PaymentDispute.status` and set `resolved_at` on closure

Admin can view open disputes via `AdminFinancialCenterView`. No automated response
is submitted to Stripe — evidence submission is a manual ops step.

---

## Key models

### `PaymentIntent`

| Field | Purpose |
|---|---|
| `website` | Which branded site |
| `client` | The paying user |
| `reference` | Unique internal ID passed as `client_reference_id` to Stripe |
| `purpose` | `order`, `wallet_top_up`, `invoice`, `billing_payment_request`, etc. |
| `provider` | `stripe` (registry supports multiple providers) |
| `status` | `created → pending → succeeded / failed / expired` |
| `application_status` | `not_applied → applying → applied / application_failed` |
| `payable` | GenericFK — Order, Invoice, PaymentRequest, etc. |
| `provider_intent_id` | Stripe Session ID (`cs_...`) |
| `statement_descriptor_snapshot` | What appeared on the client's statement |
| `client_disclosure_text` | Snapshot of the disclosure shown before payment |

### `ProviderWebhookEvent`

Inbox for every raw webhook. Unique constraint on `(provider, event_id)` is the
deduplication mechanism — prevents double-fulfilment even when Stripe retries.

### `PaymentTransaction`

One row per transaction event. Multiple rows possible (charge + refund).
`provider_transaction_id` stores the Stripe charge ID — used to link disputes.

### `PaymentDispute`

| Field | Purpose |
|---|---|
| `payment_intent` | FK to the disputed intent |
| `provider_dispute_id` | Stripe dispute ID (`dp_...`) |
| `status` | `open / under_review / won / lost / closed` |
| `reason` | Stripe dispute reason string |
| `amount` / `currency` | Disputed amount |
| `opened_at` / `resolved_at` | Timeline |
| `raw_payload` | Full Stripe event payload for audit |

### `Invoice` / `PaymentRequest`

Both carry `payment_token` (random URL-safe string, 72h expiry) for unauthenticated
payment via the public `/pay/` routes.

### `Receipt`

Issued automatically after every successful settlement. All disclosure/branding fields
are snapshotted at issuance — the receipt reflects what the client saw at payment time,
not current branding.

---

## Disclosure audit trail

| What | Where |
|---|---|
| Pre-payment notice | `PaymentIntent.client_disclosure_text` (snapshot at creation) |
| When shown | `PaymentIntent.disclosure_shown_at` |
| Acknowledgement | `PaymentDisclosureAcknowledgement` row via `POST /api/websites/payment-disclosure/acknowledge/` |
| Post-payment confirmation | `PaymentDisclosureBanner` variant="post" on billing page |
| Receipt disclosure | `Receipt.client_disclosure_text` (snapshot at receipt issuance) |

The disclosure text reads:
> *"Your payment is securely processed by {processor_name}. Your card or bank statement may show: {statement_descriptor}."*

Both `processor_name` and `statement_descriptor` come from `WebsiteBranding`
(configurable per site from the admin panel).

---

## Local development

```bash
# Forward Stripe webhooks to localhost
stripe listen --forward-to localhost:8000/api/payments/webhooks/stripe/
# CLI prints a whsec_test_... secret — set in .env as STRIPE_WEBHOOK_SECRET

# Test card (any future expiry, any CVC)
4242 4242 4242 4242

# Dev .env additions for payment flows
INFOQ_PAYMENT_BASE_URL=http://localhost:5173
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_test_...   # from stripe listen output
```

After setting up, seed notification templates (once):

```bash
docker compose exec web python manage.py seed_notification_events
docker compose exec web python manage.py seed_templates
```

---

## Adding a second Stripe account

The provider registry (`payments_processor/providers/registry.py`) supports multiple
named providers.

1. Register a new provider class with a different name (e.g. `"stripe-uk"`)
2. Read its own keys from env (`STRIPE_UK_SECRET_KEY`, etc.)
3. Register a second webhook endpoint in that account's Stripe dashboard
4. Set `PaymentIntent.provider = "stripe-uk"` for payments under that account

No changes to the orchestration or application layer — they are provider-agnostic.

---

## Decisions log

| Decision | Reason |
|---|---|
| Single Stripe account (OrderBridge) for all 4 sites | Simpler compliance, one merchant entity, easier reconciliation |
| Stripe Checkout Sessions (hosted page) | PCI compliance out-of-the-box; no card data touches our servers |
| `client_reference_id` + `metadata.reference` both set | Two lookup paths in webhook in case one field is absent from a Stripe event variant |
| Webhook deduplication via `ProviderWebhookEvent` unique constraint | Prevents double-fulfilment without any lock; Stripe retries on non-2xx |
| Fulfilment via Celery async (not inline in webhook handler) | Webhook must return 200 fast; downstream logic can be slow and retried independently |
| `/payment/complete` instead of `/client/billing?payment=success` | Dedicated handler for all payment types (order, invoice, wallet, tip); billing tab is for managing, not confirming |
| Public `/pay/:type/:token` route (no login required) | Clients receiving invoice emails often aren't logged in; forcing login causes drop-off |
| Token expiry 72h | Long enough for a client to act on an invoice email; short enough to limit exposure |
| `billing.receipt.issued` fires on all settlements unconditionally | Receipt is a regulatory artifact — it should always be sent regardless of other notification preferences |
| Dispute webhooks written to DB automatically | Gives admin visibility without manual polling of the Stripe dashboard |
| Writer payouts: manual ops, no automated rail | Volume doesn't justify Wise/Stripe Connect integration yet; PayoutRecord model is ready to attach a rail when needed |
| `INFOQ_PAYMENT_BASE_URL` global setting | Single-site simplicity for now; future improvement is per-website dynamic URL from `website.root_url` |
