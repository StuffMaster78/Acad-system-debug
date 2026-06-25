# Payment Processing Architecture

## Overview

All payments across GradeCrest, EssayManiacs, NurseMyGrade, and ResearchPaperMate
flow through a single intermediary merchant account (OrderBridge) that holds the
Stripe integration. Clients pay via Stripe's hosted checkout and never interact with
OrderBridge directly — it only appears on their bank statement. Django receives the
webhook, fulfils the order, and the client is redirected back to their portal.

```
Client (portal — app.[site].com)
    │  clicks Submit Order
    ▼
POST /api/orders/paper-orders/           ← one request does everything
    │
    ├── OrderCreationService.create_order()          ~50ms   DB write
    │
    └── OrderPaymentApplicationService.start_checkout()
            │
            └── stripe.checkout.Session.create()     ~400ms  Stripe API
                    returns checkout_url
    │
    ▼  window.location.href = checkout_url

checkout.stripe.com/pay/cs_...           ← client sees Stripe branded page
    │
    ├── Stripe → POST /api/payments/webhooks/stripe/   server-to-server
    │               └── Celery → order fulfilled async
    │
    └── Stripe → redirect → app.[site].com/client/billing?payment=success
```

---

## Merchant model

| Who | Role |
|---|---|
| OrderBridge | Stripe account holder — receives funds |
| GC / EM / NMG / RPM | Branded portals — clients interact here |
| Django backend (`api.[site].com`) | Creates sessions, verifies webhooks, fulfils orders |

**Why clients do not see OrderBridge during checkout:** The redirect goes to
`checkout.stripe.com` (Stripe's own hosted page). OrderBridge only appears on
the bank statement.

**Disclosure requirement:** Before the client reaches the Pay button, the
`PaymentDisclosureBanner` component (variant="pre") shows the intermediary name
and statement descriptor. On post-payment the same component (variant="post") shows
a confirmation. Both `shown` and `acknowledged` events are recorded server-side on
`PaymentDisclosure` records. The disclosure text snapshot is stored on
`PaymentIntent.client_disclosure_text` at session creation time.

---

## Stripe configuration

Three environment variables in `.env`:

```env
STRIPE_SECRET_KEY=sk_live_...         # server-only — never sent to browser
STRIPE_PUBLISHABLE_KEY=pk_live_...    # returned to frontend for Stripe.js if needed
STRIPE_WEBHOOK_SECRET=whsec_...       # HMAC key for webhook signature verification
```

All three come from the **OrderBridge** Stripe dashboard.

### Webhook endpoint

Register in Stripe dashboard under OrderBridge's account:

```
POST https://api.[site].com/api/payments/webhooks/stripe/
```

Subscribe to these events:

| Event | Meaning |
|---|---|
| `checkout.session.completed` | Payment succeeded via hosted checkout |
| `payment_intent.succeeded` | Payment succeeded via Payment Intents API |
| `payment_intent.payment_failed` | Card declined |
| `charge.failed` | Charge-level failure |
| `checkout.session.expired` | Client abandoned checkout |

---

## Code walkthrough — happy path

### Step 1 — Client submits order

**Frontend:** `NewOrderView.vue` → `orders.createPaperOrder()` →

```
POST /api/orders/paper-orders/
  { topic, instructions, deadline, pages, ..., payment_provider: "stripe" }
```

**Backend:** `OrderCreationView` (order_creation_views.py):

1. Validates request, resolves client and website
2. **`OrderCreationService.create_order()`** — creates `Order` row in DB
3. **`OrderPaymentApplicationService.start_checkout(order, provider="stripe")`**:
   - Applies any discount codes
   - Calculates outstanding amount
   - Calls **`PaymentIntentService.create_intent()`** which:
     - Generates unique `reference` (e.g. `pay_order_42_abc123`)
     - Creates `PaymentIntent` DB row (`status=CREATED`)
     - Calls **`StripePaymentProvider.create_payment(payment_intent)`** which calls
       `stripe.checkout.Session.create()` with:
       - `client_reference_id = reference`
       - `customer_email = client.email`  ← Stripe pre-fills the form
       - `metadata.reference = reference`  ← second lookup path
       - `success_url = {portal_url}/client/billing?payment=success&ref={reference}`
       - `cancel_url  = {portal_url}/client/billing?payment=cancelled&ref={reference}`
     - Stores `session.id` as `provider_intent_id`, updates status to `PENDING`
   - Sets `order.status = PENDING_PAYMENT`
4. Returns `{ checkout_url, reference }` to frontend

**Frontend:** `window.location.href = checkout_url` → browser navigates to Stripe.

---

### Step 2 — Stripe processes payment

Client enters card details on Stripe's hosted page. Stripe:

- **Fires a signed POST** to `/api/payments/webhooks/stripe/` (server-to-server)
- **Redirects client** to the `success_url` (portal)

Both happen simultaneously. The redirect is faster; the webhook may arrive seconds later.

---

### Step 3 — Webhook processing

**`PaymentWebhookView`** (`webhook_views.py`):
- Reads raw body bytes, stores them in `headers["_raw_body"]` for HMAC verification
- Calls `WebhookProcessingService.process_webhook()`

**`WebhookProcessingService.process_webhook()`** (`webhook_processing_service.py`):

1. **Validate** — checks provider key and payload shape
2. **Verify signature** — `stripe.Webhook.construct_event(raw_body, sig_header, STRIPE_WEBHOOK_SECRET)`
   Returns 400 on failure; Stripe retries automatically
3. **Parse** — `StripePaymentProvider.parse_webhook()` normalises both
   `checkout.session.completed` and `payment_intent.succeeded` event shapes into a
   unified `ProviderWebhookEvent` with `reference`, `amount`, `status`
4. **Deduplicate** — inserts `ProviderWebhookEvent` row with unique constraint on
   `(provider, event_id)`. If duplicate, returns 200 immediately so Stripe stops retrying
5. **Resolve** the `PaymentIntent` by `reference`
6. **Record** a `PaymentTransaction` row
7. **Update** `PaymentIntent.status → SUCCEEDED`
8. **On commit** — enqueues Celery task: `apply_payment_intent_task.delay(payment_intent.pk)`

Returns 200 in all processed cases. Returns 500 only on transient errors so Stripe retries those.

---

### Step 4 — Celery fulfils the order

**`apply_payment_intent_task`** (`payment_application_tasks.py`):

- Idempotency guard: skips if `application_status == APPLIED`
- Sets `application_status = APPLYING`
- Calls `PaymentApplicationService.apply_payment()`

**`PaymentApplicationService.apply_payment()`** (`payment_application_service.py`):

1. Validates eligibility
2. `PaymentAllocationApplicationService.apply_successful_external_payment()` — handles wallet holds and allocation
3. Routes to the correct domain handler by `PaymentIntent.purpose`:

| `purpose` | Handler | Effect |
|---|---|---|
| `ORDER` | `OrderPaymentApplicationService.apply_confirmed_payment()` | Order marked paid; files unlocked |
| `WALLET_TOP_UP` | `ClientWalletService.fund_wallet()` | Client wallet credited |
| `CLASS_PURCHASE` | class access service | Class access granted |
| `INVOICE` | billing domain | Invoice marked paid |
| `TIP` | tip domain | Tip marked paid |

4. Sets `application_status = APPLIED`
5. On failure: sets `APPLICATION_FAILED`, re-raises for Celery retry (max 3 × exponential backoff)

---

### Step 5 — Client lands on success page

The portal at `/client/billing?payment=success&ref={reference}` reads the query params
and shows a confirmation banner. The order's `payment_status` is updated asynchronously
by the webhook; the page polls or uses the existing order detail endpoint to confirm.

---

## Per-tenant redirect routing

`PaymentIntent.website` → `Website.portal_url` stores the client portal base URL per site:

| Website | `portal_url` |
|---|---|
| GradeCrest | `https://app.gradecrest.com` |
| EssayManiacs | `https://app.essaymaniacs.com` |
| NurseMyGrade | `https://app.nursemygrade.com` |
| ResearchPaperMate | `https://app.researchpapermate.com` |

`StripePaymentProvider.create_payment()` reads `payment_intent.website.portal_url`
and falls back to `settings.FRONTEND_URL` if blank (dev / unregistered sites).

---

## Speed profile and the pre-warm optimization

### Current timing

```
Client click → "Placing order…" spinner
    ~50ms   DB write (order creation)
    ~400ms  stripe.checkout.Session.create()   ← the bottleneck
    ~50ms   DB save + response
"Redirecting to payment…"
    → browser navigates to Stripe
```

Total perceivable delay: **~500–800ms** before the Stripe page appears.

The loading states ("Placing order…" → "Redirecting to payment…") are already in place
so this is perceived as progress, not a freeze.

### Pre-warm strategy (removes the delay entirely)

**Key insight:** the price is known when the client selects "Pay by card" and the quote
is displayed — before they click Submit. The Stripe session can be created then.

**Flow with pre-warm:**

```
Client selects "Pay by card"  (price already quoted)
    │
    ▼ POST /api/payments/checkout/   ← background, no spinner
      { provider: "stripe", purpose: "ORDER", amount: quotedPrice }
      Creates PaymentIntent (no order yet) + Stripe session
      Returns { reference, checkout_url }    ← stored in component state
    │
    Client fills form fields...
    │
    ▼ Client clicks Submit
      POST /api/orders/paper-orders/ with { preauth_reference: reference }
      Backend: create order + link existing PaymentIntent (no Stripe API call)
      Returns immediately ~100ms
    │
    ▼ window.location.href = checkout_url   ← INSTANT, URL was pre-fetched
```

**Edge case — price changes** (coupon applied after pre-warm):
Stripe Checkout Sessions are immutable; the amount cannot be changed. The frontend
detects the mismatch (`quotedPrice ≠ orderTotal`) and falls back to the standard flow
(creates a new session during submit). Pre-warm cache is invalidated.

### Backend changes needed for pre-warm

1. `OrderPaymentApplicationService.start_checkout()` — add `preauth_reference: str | None = None` param:
   - If provided and amounts match: look up existing `PaymentIntent`, link it to the order, skip Stripe call
   - If amounts mismatch or pre-auth expired: fall back to creating a new session

2. `OrderCreationView` — pass `preauth_reference` from request data to `start_checkout()`

3. Frontend `NewOrderView.vue` — `watch(paymentMethod)`: when method becomes `"stripe"`
   and `latestQuote` exists, call `POST /api/payments/checkout/` in the background.
   Store `{ reference, checkout_url, forAmount }`. On submit, pass `preauth_reference`.
   If `order.total_price ≠ forAmount`, ignore the pre-auth and use the `checkout_url`
   returned from the order creation response instead.

---

## Refunds

```
POST /api/payments/refunds/  →  InitiateRefundView
```

`StripePaymentProvider.refund_payment()`:
1. If `provider_reference` starts with `cs_`: retrieve Checkout Session → get `payment_intent`
2. Retrieve PaymentIntent → get `latest_charge`
3. `stripe.Refund.create(charge=charge_id, amount=cents)`

Partial refunds supported via the `amount` parameter.

---

## Key models

### `PaymentIntent`

| Field | Purpose |
|---|---|
| `website` | Which branded site |
| `client` | The paying user |
| `reference` | Unique internal ID — passed as `client_reference_id` to Stripe |
| `purpose` | `ORDER`, `WALLET_TOP_UP`, `CLASS_PURCHASE`, `TIP`, etc. |
| `provider` | `stripe` (registry supports multiple providers) |
| `status` | `CREATED → PENDING → SUCCEEDED / FAILED / EXPIRED` |
| `application_status` | `NOT_APPLIED → APPLYING → APPLIED / APPLICATION_FAILED` |
| `payable` | GenericFK — Order, Invoice, SpecialOrder, etc. (nullable for pre-warm) |
| `provider_intent_id` | Stripe Session ID (`cs_...`) or PaymentIntent ID (`pi_...`) |
| `provider_checkout_url` | `checkout.stripe.com/...` URL |
| `statement_descriptor_snapshot` | What appeared on the client's statement |
| `client_disclosure_text` | Snapshot of the disclosure shown before payment |
| `disclosure_shown_at` | When the disclosure was presented |

### `ProviderWebhookEvent`

Inbox table for every raw webhook received. Unique constraint on `(provider, event_id)`
is the deduplication mechanism — prevents double-fulfilment even if Stripe retries.

### `PaymentTransaction`

One row per transaction event on a `PaymentIntent`. Multiple rows possible (charge + refund).

---

## Disclosure audit trail

| What | Where |
|---|---|
| Pre-payment notice text | `PaymentIntent.client_disclosure_text` (snapshot at creation) |
| When shown to client | `PaymentIntent.disclosure_shown_at` |
| Acknowledgement event | `PaymentDisclosure` row via `websitesApi.acknowledgePaymentDisclosure()` |
| Post-payment confirmation | `PaymentDisclosureBanner` variant="post" on billing page |

The disclosure text reads: *"Your payment is securely processed by {processor_name}.
Your card or bank statement may show: {statement_descriptor}."*

Both `processor_name` and `statement_descriptor` come from `Website.public_branding`
so they are configurable per site from the Wagtail/admin panel.

---

## Adding a second Stripe account

The provider registry (`payments_processor/providers/registry.py`) supports multiple
named providers.

1. Register a new provider class with a different `provider_name` (e.g. `"stripe-uk"`)
2. Read its own keys from env (`STRIPE_UK_SECRET_KEY`, etc.)
3. Register a second webhook endpoint in that account's Stripe dashboard
4. Set `PaymentIntent.provider = "stripe-uk"` when creating payments for that account's sites

No changes to the orchestration or application layer — they are provider-agnostic.

---

## Local development

```bash
# Forward Stripe webhooks to localhost
stripe listen --forward-to localhost:8000/api/payments/webhooks/stripe/
# CLI prints a whsec_test_... secret — put it in .env as STRIPE_WEBHOOK_SECRET

# Test card (any future expiry, any CVC)
4242 4242 4242 4242
```

---

## Decisions log

| Decision | Reason |
|---|---|
| Single Stripe account (OrderBridge) for all 4 sites | Simpler compliance, one merchant entity, easier reconciliation |
| Stripe Checkout Sessions (hosted page) not Payment Elements | PCI compliance out-of-the-box; no card data touches our servers |
| `client_reference_id` + `metadata.reference` both set | Two lookup paths in webhook in case one field is absent from a Stripe event variant |
| Webhook deduplication via `ProviderWebhookEvent` unique constraint | Stripe retries webhooks on non-2xx; constraint prevents double-fulfilment without any lock |
| Fulfilment via Celery async task (not inline in webhook) | Webhook must return 200 fast; downstream domain logic can be slow and retried independently |
| Success URL → portal, not marketing site | Order management lives in the portal; client is already authenticated there |
| `client_disclosure_text` snapshot stored on `PaymentIntent` | Regulatory audit trail — the exact text shown to the client is preserved even if branding changes later |
| Pre-warm optional, falls back on price mismatch | Stripe sessions are immutable; coupon codes applied after pre-warm require a fresh session anyway |
