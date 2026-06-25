# Payment Processing Architecture

## Overview

All payments across GradeCrest, EssayManiacs, NurseMyGrade, and ResearchPaperMate
flow through a single intermediary merchant account (OrderBridge) that holds the
Stripe integration. Clients pay on a branded site and never see OrderBridge — their
bank statement shows `ORDERBRIDGE PAYMENTS`. The Django backend receives a webhook
from Stripe, confirms the payment, and triggers all downstream events automatically.

```
Client (GC / EM / NMG / RPM)
        │
        │  clicks Pay
        ▼
Django backend  ──── creates Stripe Checkout Session ────▶  Stripe (OrderBridge account)
        │                                                           │
        │  returns checkout_url                                     │  client enters card
        ▼                                                           │
Client redirected to checkout.stripe.com                           │  payment processed
                                                                    │
        ┌──────────────────────────────────────────────────────────┘
        │
        ├──▶  POST /api/payments/webhooks/stripe/   (server-to-server, async)
        │
        └──▶  Client redirected to app.[site].com/client/billing?payment=success
```

---

## Merchant model

| Who | Role |
|---|---|
| OrderBridge (xyz.com) | Stripe account holder — the entity that receives funds |
| GC / EM / NMG / RPM | Branded checkout surfaces — clients interact with these |
| Django backend | Verifies webhook, records the payment, dispatches domain events |

**Why clients don't see OrderBridge during checkout:** The redirect goes to
`checkout.stripe.com` (Stripe's own hosted page), not to any OrderBridge URL.
OrderBridge only appears on the client's bank statement.

**Payment disclosure:** Before the client hits Pay, the frontend renders a
`PaymentDisclosureBanner` showing the intermediary name and statement descriptor.
This snapshot is stored on `PaymentIntent.client_disclosure_text` at payment
creation time for audit purposes.

---

## Stripe configuration

Three environment variables in `.env`:

```env
STRIPE_SECRET_KEY=sk_live_...        # server-only — never exposed to browser
STRIPE_PUBLISHABLE_KEY=pk_live_...   # returned to client for Stripe.js if needed
STRIPE_WEBHOOK_SECRET=whsec_...      # signs all webhook payloads from Stripe
```

All three come from the **OrderBridge Stripe dashboard**.

### Webhook endpoint

Register this URL in the Stripe dashboard under OrderBridge's account:

```
POST https://[django-domain]/api/payments/webhooks/stripe/
```

Events to subscribe to:

| Event | Meaning |
|---|---|
| `checkout.session.completed` | Payment succeeded via hosted checkout |
| `payment_intent.succeeded` | Payment succeeded via Payment Intents API |
| `payment_intent.payment_failed` | Card declined or payment failed |
| `charge.failed` | Charge-level failure |
| `checkout.session.expired` | Client abandoned the checkout page |

---

## Code walkthrough — happy path

### Step 1 — Client initiates checkout

The client portal calls:

```
POST /api/payments/checkout/
```

`PaymentCheckoutView` → `PaymentOrchestrationService.initialize_payment(payment_intent)`.

`PaymentOrchestrationService` calls `PaymentProviderService.create_payment()` which
routes to **`StripePaymentProvider.create_payment()`**
(`payments_processor/providers/stripe.py`).

Stripe creates a **Checkout Session** with:
- `line_items` — the order amount and description
- `client_reference_id` — the internal order reference (used to match the webhook)
- `metadata.reference` — same reference, second lookup path
- `success_url` — `{website.portal_url}/client/billing?payment=success&ref={reference}`
- `cancel_url` — `{website.portal_url}/client/billing?payment=cancelled&ref={reference}`

The `success_url` uses `Website.portal_url` (e.g. `https://app.gradecrest.com`) so
the redirect lands on the correct branded portal for whichever site the client paid on.

The Checkout Session URL (`checkout.stripe.com/pay/cs_live_...`) is returned to the
frontend, which redirects the client there.

### Step 2 — Webhook arrives

After the client pays, Stripe fires a signed POST to
`/api/payments/webhooks/stripe/`.

**`PaymentWebhookView`** (`payments_processor/api/views/webhook_views.py`):
- Reads raw body bytes and passes them through untouched
  (`headers["_raw_body"] = request.body`) for signature verification
- Calls `WebhookProcessingService.process_webhook()`

**`WebhookProcessingService.process_webhook()`** (`payments_processor/services/webhook_processing_service.py`):

1. **Validates** provider key, payload shape
2. **Verifies signature** — `StripePaymentProvider.verify_webhook()` calls
   `stripe.Webhook.construct_event(raw_body, sig_header, STRIPE_WEBHOOK_SECRET)`.
   If the signature fails the request gets a 400; Stripe will retry.
3. **Parses** the event — `StripePaymentProvider.parse_webhook()` normalises both
   `checkout.session.completed` and `payment_intent.succeeded` shapes into a
   unified `ProviderWebhookEvent` with `reference`, `amount`, `status`, and
   `provider_transaction_id`.
4. **Deduplicates** — creates a `ProviderWebhookEvent` DB record. The unique
   constraint on `(provider, event_id)` prevents double-processing. If the
   insert raises `IntegrityError` a 200 is returned with `duplicate: true`
   so Stripe stops retrying.
5. **Resolves** the `PaymentIntent` by the `reference` extracted from the event.
6. **Records** a `PaymentTransaction` row (amount, currency, kind, status).
7. **Updates** `PaymentIntent.status` → `SUCCEEDED`.
8. **On commit** — enqueues a Celery task:
   `apply_payment_intent_task.delay(payment_intent.pk)`

Returns 200 in all processed cases (including ignored events) so Stripe never
retries on business-logic errors. Returns 500 only on transient failures so
Stripe *does* retry those.

### Step 3 — Celery applies the payment

**`apply_payment_intent_task`** (`payments_processor/tasks/payment_application_tasks.py`):

- Idempotency guard: skips if `application_status == APPLIED`
- Resolves the payable total amount
- Sets `application_status = APPLYING`
- Calls `PaymentApplicationService.apply_payment()`

**`PaymentApplicationService.apply_payment()`** (`payments_processor/services/payment_application_service.py`):

1. Validates eligibility
2. Calls `PaymentAllocationApplicationService.apply_successful_external_payment()`
   to handle wallet holds and allocation
3. If **fully settled**, routes to the correct domain handler by `purpose`:

| `PaymentIntent.purpose` | Handler | What happens |
|---|---|---|
| `ORDER` | `OrderPaymentApplicationService.apply_confirmed_payment()` | Order marked paid, files unlocked via `FileDeliveryGuardService.unlock_after_payment()` |
| `SPECIAL_ORDER` | `SpecialOrderPaymentsProcessorBridge.apply_successful_transaction()` | Special order payment applied via ledger reference |
| `WALLET_TOP_UP` | `ClientWalletService.fund_wallet()` | Client wallet credited |
| `CLASS_PURCHASE` | returns `grant_access` | Class access granted |
| `INVOICE` | billing domain | Invoice marked paid |
| `BILLING_PAYMENT_REQUEST` | billing domain | Payment request settled |
| `TIP` | tip domain | Tip marked paid |

4. On success, sets `application_status = APPLIED`
5. On exception, sets `application_status = APPLICATION_FAILED`, records error,
   and re-raises so Celery retries (max 3 times with exponential backoff)

### Step 4 — Client lands on success page

While the webhook is being processed server-side, Stripe simultaneously redirects
the client to the `success_url`. The portal's `/client/billing` page reads the
`?payment=success&ref=` query params and shows a confirmation. The order's actual
`payment_status` field is updated asynchronously by the webhook; the frontend polls
or uses the existing order detail view to confirm.

---

## Per-tenant redirect routing

`PaymentIntent` has a `website` FK to the `Website` model.
`Website.portal_url` stores the client portal base URL per site:

| Website | `portal_url` |
|---|---|
| GradeCrest | `https://app.gradecrest.com` |
| EssayManiacs | `https://app.essaymaniacs.com` |
| NurseMyGrade | `https://app.nursemygrade.com` |
| ResearchPaperMate | `https://app.researchpapermate.com` |

`StripePaymentProvider.create_payment()` reads
`payment_intent.website.portal_url` and falls back to
`settings.FRONTEND_URL` if the field is blank (dev / unregistered sites).

---

## Key models

### `PaymentIntent` (`payments_processor/models/payment_intent.py`)

The central record for every external payment attempt.

| Field | Purpose |
|---|---|
| `website` | Which branded site this payment belongs to |
| `client` | The paying user |
| `reference` | Unique internal reference — passed to Stripe as `client_reference_id` |
| `purpose` | What this payment is for (`ORDER`, `WALLET_TOP_UP`, etc.) |
| `provider` | Always `stripe` for now |
| `status` | `CREATED → PENDING → SUCCEEDED / FAILED` |
| `application_status` | `NOT_APPLIED → APPLYING → APPLIED / APPLICATION_FAILED` |
| `payable` | GenericFK — the Order, Invoice, SpecialOrder, etc. being paid for |
| `provider_intent_id` | Stripe Session or PaymentIntent ID |
| `provider_checkout_url` | The `checkout.stripe.com/...` URL |
| `statement_descriptor_snapshot` | Snapshot of what appeared on the client's statement |
| `client_disclosure_text` | Snapshot of the disclosure shown before payment |
| `disclosure_accepted_at` | Timestamped when payment confirmed |

### `ProviderWebhookEvent` (`payments_processor/models/`)

Inbox record for every webhook received. The unique constraint on
`(provider, event_id)` is the deduplication mechanism.

### `PaymentTransaction` (`payments_processor/models/`)

One row per transaction event on a `PaymentIntent`. Multiple rows are possible
(e.g. charge + refund).

---

## Refunds

`POST /api/payments/refunds/` → `InitiateRefundView`

`StripePaymentProvider.refund_payment()`:
1. Retrieves the Stripe PaymentIntent from `provider_reference`
2. Gets `latest_charge` from the PaymentIntent
3. Calls `stripe.Refund.create(charge=charge_id, amount=cents)`

Partial refunds are supported via the `amount` parameter.

---

## Adding a second Stripe account (future)

The provider registry (`payments_processor/providers/registry.py`) supports
multiple named providers. To add a second account:

1. Register a new provider class (e.g. `StripeUKPaymentProvider`) with a
   different `provider_name`
2. Read its own key set from env (e.g. `STRIPE_UK_SECRET_KEY`)
3. Register a second webhook endpoint in that account's Stripe dashboard pointing
   to the same `/api/payments/webhooks/stripe-uk/` URL pattern
4. Set `PaymentIntent.provider = "stripe-uk"` when creating payments for that
   account's sites

No changes to the orchestration or application layer are needed — they are
provider-agnostic.

---

## Local development

In dev the Stripe keys are absent, so checkout creation will fail unless you use
Stripe test keys. Use the [Stripe CLI](https://stripe.com/docs/stripe-cli) to
forward webhooks to localhost:

```bash
stripe listen --forward-to localhost:8000/api/payments/webhooks/stripe/
```

The CLI prints a `whsec_test_...` secret — put that in your `.env` as
`STRIPE_WEBHOOK_SECRET` for dev.

Use test card `4242 4242 4242 4242` (any future expiry, any CVC) on the Stripe
hosted checkout page to trigger a successful payment end-to-end.
