# Payment Processing Architecture

> Last updated: 2026-06-29 · **Overall completion: ~91%**

---

## Overview

All payments across GradeCrest, EssayManiacs, NurseMyGrade, and ResearchPaperMate
flow through a single intermediary merchant account (OrderBridge) that holds the
Stripe integration. Clients pay via Stripe's hosted checkout and never interact with
OrderBridge directly — it only appears on their bank statement.

The system is **fully configurable per website** — each site can have its own gateway
provider, webhook endpoint, callback URL, and mode (live/test) managed from the admin
panel without touching code or environment variables.

---

## Completion by subsystem

| Subsystem                                    | %        | Status                                                                       |
| -------------------------------------------- | -------- | ---------------------------------------------------------------------------- |
| Payment disclosure                           | **100%** | All three touchpoints done, audit trail in place                             |
| Client wallet + top-up                       | **100%** | Complete including receipt view                                              |
| Invoice / PaymentRequest / Receipt lifecycle | **100%** | Public pay page, full invoice pay, PR pay, void receipt all done             |
| Stripe payment collection + webhooks         | **95%**  | Dispute webhook auto-writes to DB; `payment_intent.canceled` not yet handled |
| Admin financial management                   | **95%**  | Void receipt done; installment schedule UI already existed                   |
| Per-website gateway config                   | **100%** | Model, CRUD API, and admin UI complete                                       |
| Payment notification email forwarding        | **100%** | Configured from admin, copies fire after every billing.\* email              |
| Client billing frontend                      | **100%** | All 5 missing flows now complete                                             |
| Writer earnings + settlement engine          | **75%**  | Engine complete; automated disbursement deferred by design                   |
| Writer payout execution (automated)          | **10%**  | Structure only — no outbound rail (intentional)                              |
| Double-entry ledger                          | **70%**  | Journaling works; reconciliation UI is read-only                             |
| Marketing site pricing / order intake        | **90%**  | Calculator done; flat URLs done across all 5 sites                           |

**Overall: ~91%** — the core money-in path, all client-facing billing flows, and the
gateway management layer are production-ready. The only intentional open area is
automated writer payout disbursement, deferred until volume justifies the integration.

---

## Architecture diagram

```
┌────────────────────────────────────────────────────────────────────────┐
│                         CLIENT BROWSER                                 │
│                                                                        │
│  Logged-in portal             OR         Email link (no login)         │
│  app.[site].com/client/billing           [site].com/pay/invoice/<tok> │
└───────────┬────────────────────────────────────────┬───────────────────┘
            │ Pay button                             │ PublicPayView
            │                                        │
            ▼                                        ▼
┌───────────────────────────────────────────────────────────────────────┐
│                          DJANGO BACKEND                               │
│                                                                       │
│  /billing/my/invoices/<id>/prepare-payment/  (authenticated)         │
│  /billing/my/payment-requests/<id>/prepare-payment/ (authenticated)  │
│  /billing/pay/invoices/<token>/prepare/  (AllowAny — token-gated)   │
│  /billing/pay/payment-requests/<token>/prepare/ (AllowAny)          │
│                                                                       │
│  PaymentOrchestrationService.initialize_payment()                    │
│    → PaymentGatewayConfig.gateway   ← reads per-site config         │
│    → PaymentGatewayConfig.mode      ← live or test key set          │
│    → StripePaymentProvider.create_payment()                          │
│         success_url = PaymentGatewayConfig.callback_base_url         │
│                     ??  Website.root_url                              │
│                     ??  INFOQ_PAYMENT_BASE_URL (dev fallback)        │
│         + /payment/complete?status=success&ref={reference}           │
└───────────────────┬───────────────────────────────────────────────────┘
                    │ checkout_url returned to frontend
                    │ window.location.href = checkout_url
                    ▼
┌───────────────────────────────────────────────────────────────────────┐
│                     STRIPE HOSTED CHECKOUT                            │
│                   checkout.stripe.com/pay/cs_...                     │
│                                                                       │
│  Card entry · 3DS auth · Strong Customer Authentication               │
└─────────────┬──────────────────────────────────┬─────────────────────┘
              │ POST (server-to-server)           │ 302 redirect
              │ Signed webhook                    │ to success_url
              ▼                                   ▼
┌─────────────────────────────┐    ┌──────────────────────────────────┐
│  /payments/webhooks/stripe/ │    │  /payment/complete               │
│                             │    │  ?status=success&ref={reference} │
│  WebhookProcessingService   │    │                                  │
│  1. Verify HMAC signature   │    │  PaymentCompleteView.vue         │
│  2. Deduplicate (DB unique) │    │  Shows ✓ confirmation            │
│  3. Update PaymentIntent    │    │  Links to dashboard + billing    │
│  4. If dispute event →      │    └──────────────────────────────────┘
│     write PaymentDispute    │
│  5. On commit: enqueue      │
│     Celery task             │
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    CELERY — apply_payment_intent_task               │
│                                                                     │
│  PaymentApplicationService.apply_payment() routes by purpose:      │
│                                                                     │
│  order              → order fulfilled, files unlocked               │
│  invoice            → Invoice.status = paid, Receipt issued         │
│  billing_payment_request → PaymentRequest.status = paid, Receipt   │
│  wallet_top_up      → Client wallet credited                        │
│  class_purchase     → Class access granted                          │
│  tip                → Writer wallet credited                        │
│                                                                     │
│  → LedgerService journals every movement (double-entry)             │
│  → NotificationService.notify('billing.receipt.issued')            │
│       → EmailBackend sends receipt email to client                  │
│       → EmailBackend forwards copy to PaymentNotificationEmail(s)  │
│       → InAppBackend pushes WebSocket notification to portal       │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Gateway flexibility diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│               PER-WEBSITE GATEWAY CONFIGURATION                     │
│          Admin UI: /admin/payment-gateway (admin + superadmin)      │
└──────────┬──────────────────────────────────────────────────────────┘
           │ PaymentGatewayConfig model (one row per website)
           │
           ├── gateway          "stripe"          (extensible to PayPal etc.)
           ├── webhook_endpoint "/api/payments/webhooks/stripe/"
           ├── callback_base_url "https://app.gradecrest.com"
           ├── mode             live | test
           └── is_active        true | false

Priority chain for Stripe success/cancel URL:
  1. PaymentGatewayConfig.callback_base_url   ← set in admin UI
  2. Website.root_url                         ← fallback
  3. INFOQ_PAYMENT_BASE_URL env var           ← dev-only fallback

Each site routes independently:
  gradecrest.com      → app.gradecrest.com/payment/complete
  nursemygrade.com    → app.nursemygrade.com/payment/complete
  essaymaniacs.com    → app.essaymaniacs.com/payment/complete
  researchpapermate.com → app.researchpapermate.com/payment/complete
```

---

## Billing flows (invoice and payment request)

### Path A — Authenticated portal

```
Admin creates invoice / payment request
  → issues it (status: issued)
  → billing.invoice.issued notification fires
      → Email to client: invoice_issued.html with "Pay Now" button
          pay_url = {website.root_url}/pay/invoice/{payment_token}
      → In-app notification pushed via WebSocket
      → Forward copy to PaymentNotificationEmail addresses

Client (logged in) → Billing tab → Invoices
  → "Pay by card" button
  → POST /billing/my/invoices/<id>/prepare-payment/
  → checkout_url returned → Stripe redirect
  → Webhook → InvoiceOrchestrationService.apply_verified_invoice_payment()
  → Receipt issued → billing.receipt.issued fires
```

### Path B — Email link (no login required)

```
Client receives email with pay_url link
  → Opens /pay/invoice/<token>   (PublicPayView — no auth)
  → Page shows: invoice title, amount, due date, disclosure text
  → POST /billing/pay/invoices/<token>/prepare/   (AllowAny)
  → checkout_url returned → Stripe redirect
  → Same webhook fulfillment as Path A
  → Token expires after 72h (configurable)
```

### Installment flow

```
Admin creates installment schedule on an invoice
  → POST /billing/invoices/<id>/installments/  [{amount, due_at}...]

Celery beat (every hour):
  → schedule_upcoming_installment_reminders()  → billing.installment.upcoming
  → schedule_due_installment_reminders()       → billing.installment.due
  → dispatch_due_billing_reminders()

Client pays individual installment:
  → POST /billing/installments/<id>/prepare-payment/
  → InstallmentAllocationService allocates partial payment
```

---

## Notification email forwarding

```
Any billing.* email sent
  └── EmailBackend.send() succeeds
      └── _forward_to_payment_notification_emails()
            └── PaymentNotificationEmail.objects.filter(
                  website=website, is_active=True)
                  → provider.send(to=each_email,
                                  subject="[FWD] " + original_subject)
```

Configure addresses at `/admin/payment-gateway` → "Payment Notification Emails" tab.
Multiple addresses per website supported (e.g. finance team + CEO).
Pause/resume per address without deleting.

---

## Merchant model

| Who                 | Role                                                |
| ------------------- | --------------------------------------------------- |
| OrderBridge         | Stripe account holder — receives funds              |
| GC / EM / NMG / RPM | Branded portals — clients interact here             |
| Django backend      | Creates sessions, verifies webhooks, fulfils orders |

**Disclosure requirement:** Before the Pay button, `PaymentDisclosureBanner` (variant="pre")
shows the intermediary name and statement descriptor. On post-payment, variant="post"
shows confirmation. Both `shown` and `acknowledged` events are recorded server-side.
The disclosure text is snapshotted on every payment model at creation time — receipts
always reflect what the client saw, even if branding changes later.

---

## Stripe configuration

### Environment variables

```env
STRIPE_SECRET_KEY=sk_live_...           # server-only
STRIPE_PUBLISHABLE_KEY=pk_live_...      # frontend (Stripe.js if needed)
STRIPE_WEBHOOK_SECRET=whsec_...         # HMAC verification
INFOQ_PAYMENT_BASE_URL=http://localhost:5173   # dev-only fallback
```

> In production `INFOQ_PAYMENT_BASE_URL` is only used if `PaymentGatewayConfig.callback_base_url`
> and `Website.root_url` are both blank. Set `root_url` per site in the admin and this
> env var becomes irrelevant.

### Webhook endpoint

Register in the OrderBridge Stripe dashboard:

```
POST https://api.[site].com/api/payments/webhooks/stripe/
```

Subscribe to:

| Event                             | Handler                            |
| --------------------------------- | ---------------------------------- |
| `checkout.session.completed`      | Payment succeeded                  |
| `payment_intent.succeeded`        | Payment succeeded                  |
| `payment_intent.payment_failed`   | Payment failed                     |
| `charge.failed`                   | Charge-level failure               |
| `checkout.session.expired`        | Session expired                    |
| `charge.dispute.created`          | Creates `PaymentDispute` row       |
| `charge.dispute.updated`          | Updates `PaymentDispute.status`    |
| `charge.dispute.closed`           | Closes dispute, sets `resolved_at` |
| `charge.dispute.funds_reinstated` | Dispute won                        |
| `charge.dispute.funds_withdrawn`  | Dispute lost                       |

---

## Webhook processing detail

```
POST /api/payments/webhooks/stripe/
  │
  ├── Signature verification (HMAC via STRIPE_WEBHOOK_SECRET)
  │     400 on failure → Stripe auto-retries
  │
  ├── Is this a dispute event? (charge.dispute.*)
  │     YES → _handle_dispute_event()
  │             Resolve PaymentIntent via PaymentTransaction.provider_transaction_id
  │             get_or_create PaymentDispute
  │             Update status / resolved_at on subsequent events
  │             Return 200
  │
  └── Payment event path:
        Deduplication: ProviderWebhookEvent unique(provider, event_id)
        Resolve PaymentIntent by reference
        Record PaymentTransaction
        Update PaymentIntent.status
        If SUCCEEDED → on_commit: apply_payment_intent_task.delay()
        Return 200 always (500 only on transient errors → Stripe retries)
```

---

## Key models

### `PaymentGatewayConfig` _(new)_

| Field               | Purpose                                   |
| ------------------- | ----------------------------------------- |
| `website`           | OneToOneField — one config per site       |
| `gateway`           | Provider name (`"stripe"`)                |
| `webhook_endpoint`  | Path registered in Stripe dashboard       |
| `callback_base_url` | Base URL for success/cancel redirects     |
| `mode`              | `live` or `test`                          |
| `is_active`         | Inactive → falls back to platform default |

### `PaymentNotificationEmail` _(new)_

| Field       | Purpose                                     |
| ----------- | ------------------------------------------- |
| `website`   | ForeignKey — multiple rows per site allowed |
| `email`     | Forwarding address                          |
| `label`     | Optional label (e.g. "Finance team")        |
| `is_active` | Pause/resume without deleting               |

### `PaymentIntent`

| Field                | Purpose                                                              |
| -------------------- | -------------------------------------------------------------------- |
| `website`            | Which branded site                                                   |
| `client`             | The paying user                                                      |
| `reference`          | Unique ID passed as `client_reference_id` to Stripe                  |
| `purpose`            | `order`, `wallet_top_up`, `invoice`, `billing_payment_request`, etc. |
| `status`             | `created → pending → succeeded / failed / expired`                   |
| `application_status` | `not_applied → applying → applied / application_failed`              |
| `payable`            | GenericFK — Order, Invoice, PaymentRequest, etc.                     |

### `PaymentDispute`

| Field                       | Purpose                                     |
| --------------------------- | ------------------------------------------- |
| `payment_intent`            | FK to the disputed intent                   |
| `provider_dispute_id`       | Stripe dispute ID (`dp_...`)                |
| `status`                    | `open / under_review / won / lost / closed` |
| `amount` / `currency`       | Disputed amount                             |
| `opened_at` / `resolved_at` | Timeline                                    |
| `raw_payload`               | Full Stripe event stored for audit          |

### `Invoice` / `PaymentRequest`

Both carry `payment_token` (random URL-safe 32-char string, 72h expiry) enabling
unauthenticated payment via `/pay/invoice/<token>` or `/pay/payment-request/<token>`.

### `Receipt`

Issued automatically after every settlement. All disclosure and branding fields are
snapshotted at issuance — the receipt always reflects what the client saw at payment
time, not current branding.

---

## Notification seeding (run once on first deploy)

```bash
# Register event keys from enum → DB
docker compose exec web python manage.py seed_notification_events

# Seed email + in-app templates for all billing events
docker compose exec web python manage.py seed_templates
```

Both commands are **idempotent** — safe to re-run, existing rows are never overwritten.
Use `seed_templates --update` to push template changes after editing `seed_templates.py`.

Billing events now registered and templated:

| Event key                          | Email template                                      |
| ---------------------------------- | --------------------------------------------------- |
| `billing.invoice.issued`           | `invoice_issued.html` (with "Pay Now" link)         |
| `billing.invoice.settled`          | `payment_received.html`                             |
| `billing.invoice.reminder`         | `payment_reminder.html`                             |
| `billing.payment_request.issued`   | `payment_request_issued.html` (with "Pay Now" link) |
| `billing.payment_request.settled`  | `payment_received.html`                             |
| `billing.payment_request.reminder` | `payment_reminder.html`                             |
| `billing.receipt.issued`           | `receipt.html` (with disclosure block)              |
| `billing.installment.upcoming`     | `payment_reminder.html`                             |
| `billing.installment.due`          | `payment_reminder.html`                             |
| `billing.installment.overdue`      | `payment_reminder.html`                             |

---

## Frontend routes

| Route                         | View                          | Auth                      |
| ----------------------------- | ----------------------------- | ------------------------- |
| `/payment/complete`           | `PaymentCompleteView.vue`     | Public                    |
| `/pay/invoice/:token`         | `PublicPayView.vue`           | Public (token-gated, 72h) |
| `/pay/payment-request/:token` | `PublicPayView.vue`           | Public (token-gated, 72h) |
| `/client/billing`             | `ClientBillingView.vue`       | Client                    |
| `/admin/payment-gateway`      | `AdminPaymentGatewayView.vue` | Admin + Superadmin        |
| `/superadmin/payment-gateway` | `AdminPaymentGatewayView.vue` | Superadmin                |

`ClientBillingView` tabs: **Invoices** (installment pay + full invoice pay), **Payment Requests** (Pay now button for issued status), **Receipts** (read-only with disclosure details).

---

## Local development

```bash
# Forward Stripe webhooks to localhost
stripe listen --forward-to localhost:8000/api/payments/webhooks/stripe/
# CLI prints a whsec_test_... secret — set in .env as STRIPE_WEBHOOK_SECRET

# Test card (any future expiry, any CVC)
4242 4242 4242 4242

# Dev .env
INFOQ_PAYMENT_BASE_URL=http://localhost:5173
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_test_...

# One-time seeding (after first migrate)
docker compose exec web python manage.py seed_notification_events
docker compose exec web python manage.py seed_templates
```

---

## Refunds

```
POST /api/payments/refunds/  →  InitiateRefundView
```

`StripePaymentProvider.refund_payment()` retrieves the Checkout Session → charge → calls
`stripe.Refund.create(charge=charge_id, amount=cents)`. Partial refunds supported.
Refund state tracked on `PaymentRefund`, reconciled via `PaymentReconciliationService`.

---

## Decisions log

| Decision                                                           | Reason                                                                                                     |
| ------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------- |
| Single Stripe account (OrderBridge) for all 4 sites                | Simpler compliance, one merchant entity, easier reconciliation                                             |
| Stripe Checkout Sessions (hosted page)                             | PCI compliance out-of-the-box; no card data touches our servers                                            |
| `client_reference_id` + `metadata.reference` both set              | Two lookup paths in webhook — safety net if one field is absent                                            |
| Webhook deduplication via `ProviderWebhookEvent` unique constraint | Prevents double-fulfilment without locks; Stripe retries on non-2xx                                        |
| Fulfilment via Celery async (not inline in webhook handler)        | Webhook must return 200 fast; downstream logic can be slow and retried                                     |
| `/payment/complete` dedicated return page                          | Handles all payment types (order, invoice, wallet, tip); clean separation from billing management          |
| Public `/pay/:type/:token` (no login required)                     | Clients receiving invoice emails often aren't logged in; forcing login causes drop-off                     |
| Token expiry 72h                                                   | Long enough to act on an invoice email; short enough to limit exposure                                     |
| `billing.receipt.issued` fires unconditionally                     | Receipt is a regulatory artifact — must fire regardless of notification preferences                        |
| Dispute webhooks written to DB automatically                       | Admin visibility without polling Stripe dashboard                                                          |
| `PaymentGatewayConfig` per website                                 | Each site can swap provider, endpoint, or callback URL from the admin panel without code changes           |
| `PaymentNotificationEmail` per website                             | Finance teams receive forwarded copies without needing portal accounts                                     |
| `website.root_url` drives Stripe callback URLs                     | Each site's return URL is automatically correct; `INFOQ_PAYMENT_BASE_URL` is now dev-only                  |
| Writer payouts: manual ops, no automated rail                      | Volume doesn't justify Wise/Stripe Connect yet; `PayoutRecord` model is ready to attach a rail when needed |
