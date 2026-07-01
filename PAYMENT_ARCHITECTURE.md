# Payment Processing Architecture

> Last updated: 2026-07-01 · **Overall completion: ~94%**

---

## Overview

All payments across GradeCrest, EssayManiacs, NurseMyGrade, and ResearchPaperMate
flow through a single intermediary merchant account (OrderBridge) that holds the
Stripe integration. Clients pay via Stripe's hosted checkout and never interact with
OrderBridge directly — it only appears on their bank statement.

The system is **fully configurable per website** — each site can have its own gateway
provider, webhook endpoint, callback URL, and mode (live/test) managed from the admin
panel without touching code or environment variables.

Two providers are registered: **`stripe`** (production) and **`mock`** (local dev/test).

---

## Completion by subsystem

| Subsystem                                    | %        | Status                                                              |
| -------------------------------------------- | -------- | ------------------------------------------------------------------- |
| Payment disclosure                           | **100%** | All three touchpoints done, audit trail in place                    |
| Client wallet + top-up                       | **100%** | Complete including mock-confirm for local dev                       |
| Invoice / PaymentRequest / Receipt lifecycle | **100%** | Public pay page, full invoice pay, PR pay, void receipt all done    |
| Stripe payment collection + webhooks         | **95%**  | `payment_intent.canceled` not yet handled                           |
| Admin financial management                   | **95%**  | Void receipt done; installment schedule UI already existed          |
| Per-website gateway config                   | **100%** | Model, CRUD API, and admin UI complete                              |
| Payment notification email forwarding        | **100%** | Configured from admin, copies fire after every billing.\* email     |
| Client billing frontend                      | **100%** | All checkout flows complete                                         |
| Writer earnings + settlement engine          | **75%**  | Engine complete; automated disbursement deferred by design          |
| Writer payout execution (automated)          | **10%**  | Structure only — no outbound rail (intentional)                     |
| Double-entry ledger                          | **70%**  | Journaling works; reconciliation UI is read-only                    |
| Marketing site pricing / order intake        | **90%**  | Calculator done; flat URLs done across all 5 sites                  |
| Mock payment provider (dev/test)             | **100%** | Full create → confirm → wallet-credit loop without Stripe           |

**Overall: ~94%** — the core money-in path and all client-facing billing flows are
production-ready. The only intentional open area is automated writer payout
disbursement, deferred until volume justifies the integration.

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
│  POST /payments/checkout/                         (authenticated)     │
│  POST /billing/my/invoices/<id>/prepare-payment/  (authenticated)     │
│  POST /billing/pay/invoices/<token>/prepare/      (AllowAny)          │
│  POST /billing/pay/payment-requests/<token>/prepare/ (AllowAny)       │
│                                                                       │
│  PaymentIntentService.create_intent()                                 │
│    → PaymentGatewayConfig.gateway  ← reads per-site config           │
│    → get_provider("stripe" | "mock")                                  │
│    → provider.create_payment()     ← returns checkout_url            │
└───────────────────┬───────────────────────────────────────────────────┘
                    │ checkout_url returned to frontend
                    │
            ┌───────┴──────────────────┐
            │ provider == "stripe"     │ provider == "mock" (dev)
            ▼                         ▼
┌────────────────────────┐  ┌───────────────────────────────────┐
│  STRIPE HOSTED CHECKOUT│  │  POST /payments/checkout/         │
│  checkout.stripe.com   │  │        mock-confirm/              │
│  Card · 3DS · SCA      │  │                                   │
└────────────┬───────────┘  │  1. Mark PaymentIntent SUCCEEDED  │
             │              │  2. PaymentApplicationService      │
             │              │     .apply_payment()               │
             │              │  3. Wallet credited / order        │
             │              │     fulfilled immediately          │
             │              └───────────────────────────────────┘
             │
     ┌───────┴──────────────┐
     │ Webhook (server→server) │ Redirect → /payment/complete
     │ POST /payments/         │ ?status=success&ref={ref}
     │   webhooks/stripe/      │
     │                         │
     │ 1. Verify HMAC sig     │
     │ 2. Deduplicate          │
     │ 3. Update PaymentIntent │
     │ 4. Celery: apply task   │
     └─────────────────────────┘
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
│  wallet_top_up      → ClientWalletService.fund_wallet()            │
│  class_purchase     → Class access granted                          │
│  tip                → Writer wallet credited                        │
│                                                                     │
│  → LedgerService journals every movement (double-entry)             │
│  → NotificationService.notify('billing.receipt.issued')            │
│       → Email receipt to client                                     │
│       → Forward to PaymentNotificationEmail addresses               │
│       → WebSocket push to portal                                    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Payment flows with examples

### Flow 1 — Wallet top-up (client funds their account)

**Who:** Client. **Purpose:** `wallet_top_up`. **No payable linked.**

```
Client → Billing & Wallet tab → Top Up Wallet
  Select preset ($10 / $25 / $50 / $100 / $200) or enter custom amount
  Acknowledge payment disclosure banner (required before checkout)
  Click "Top up"
```

**Request (Stripe):**
```http
POST /api/v1/payments/checkout/
Authorization: Bearer <client_token>
Content-Type: application/json

{
  "provider": "stripe",
  "purpose": "wallet_top_up",
  "amount": "50.00",
  "currency": "USD"
}
```

**Response:**
```json
{
  "payment_intent": {
    "id": 42,
    "reference": "pay_a1b2c3d4e5f6",
    "status": "pending",
    "amount": "50.00",
    "currency": "USD",
    "purpose": "wallet_top_up",
    "client_disclosure_text": "Your payment is securely processed by OrderBridge. Your card or bank statement may show: ORDERBRIDGE.",
    "provider_checkout_url": "https://checkout.stripe.com/pay/cs_test_..."
  },
  "provider_data": {
    "success": true,
    "provider_name": "stripe",
    "provider_reference": "cs_test_a1b2c3d4e5",
    "checkout_url": "https://checkout.stripe.com/pay/cs_test_..."
  }
}
```

Frontend redirects to `checkout_url`. After payment, Stripe webhook fires:

```
POST /api/v1/payments/webhooks/stripe/
  → reference: "pay_a1b2c3d4e5f6"
  → PaymentIntent → SUCCEEDED
  → Celery: apply_payment_intent_task
      → ClientWalletService.fund_wallet(amount=50.00)
      → WalletEntry(type="topup", direction="credit", amount=50.00)
      → billing.receipt.issued notification
```

Client returns to `/payment/complete?status=success&ref=pay_a1b2c3d4e5f6` and sees confirmation.

---

**Request (Mock — dev only):**
```http
POST /api/v1/payments/checkout/
Content-Type: application/json

{ "provider": "mock", "purpose": "wallet_top_up", "amount": "50.00", "currency": "USD" }
```

Frontend receives the intent, then immediately calls:
```http
POST /api/v1/payments/checkout/mock-confirm/
Content-Type: application/json

{ "reference": "pay_a1b2c3d4e5f6" }
```

This marks the intent SUCCEEDED and runs the same `apply_payment()` path as a real webhook — wallet is credited synchronously.

---

### Flow 2 — Order payment (new order wizard, step 3)

**Who:** Client. **Purpose:** `order`. **Payable:** `Order` instance.

```
Client → New Order → Step 1 (topic + instructions)
                   → Step 2 (paper type, academic level, deadline)
                   → Step 3 (price calculation → checkout)
```

**Step 3: Get price quote:**
```http
POST /api/v1/pricing/quotes/paper/start/
Authorization: Bearer <client_token>

{
  "service_code": "academic_writing",
  "pages": 5,
  "deadline_hours": 48,
  "spacing": "double",
  "paper_type_code": "essay",
  "work_type_code": "writing",
  "subject_code": "general",
  "academic_level_code": "undergraduate",
  "topic": "Effects of social media on mental health",
  "instructions": "Analyse the correlation between social media usage and anxiety..."
}
```

**Response:** `{ "calculated_price": "85.00", "snapshot_id": "snap_xyz" }`

**Step 3: Place order:**
```http
POST /api/v1/orders/orders/create/
Authorization: Bearer <client_token>

{
  "topic": "Effects of social media on mental health",
  "order_instructions": "Analyse the correlation...",
  "client_deadline": "2026-07-04T12:00:00Z",
  "number_of_pages": 5,
  "paper_type_id": 1,
  "type_of_work_id": 2,
  "academic_level_id": 3,
  "service_code": "academic_writing",
  "service_family": "paper_order",
  "payment_provider": "stripe",
  "payment_method_code": "card",
  "pricing_snapshot_id": "snap_xyz",
  "total_price": "85.00"
}
```

**Response:**
```json
{
  "order": { "id": 1042, "status": "pending_payment", "topic": "Effects of social media..." },
  "checkout_url": "https://checkout.stripe.com/pay/cs_test_...",
  "payment_intent": { "reference": "pay_order_1042_ab1c" }
}
```

Frontend redirects to Stripe. On completion:
```
Webhook → PaymentIntent SUCCEEDED
  → Order.status = "active"
  → Files unlocked for delivery
  → billing.receipt.issued
  → order.paid notification to client + writer (if assigned)
```

---

### Flow 3 — Invoice payment (admin-issued)

**Who:** Admin creates invoice → Client pays. Two sub-paths.

#### Path A — Authenticated (client already logged in)

```
Admin → Financial Center → Create Invoice
  → Set amount, due date, line items
  → Issue invoice (status: issued)
  → Email sent to client: "Pay Now" button links to /pay/invoice/<token>
  → Portal notification pushed via WebSocket

Client → Billing tab → Invoices → "Pay by card"
  → POST /billing/my/invoices/<id>/prepare-payment/
  → Stripe redirect → webhook → Invoice.status = paid → Receipt issued
```

#### Path B — Email link (no login required)

```
Client opens email → clicks "Pay Now"
  → /pay/invoice/<token>  (PublicPayView — unauthenticated)
  → Page shows: amount, due date, disclosure text
  → Client acknowledges disclosure → clicks Pay
  → POST /billing/pay/invoices/<token>/prepare/
  → Stripe redirect → same webhook fulfillment as Path A
```

**Example invoice pay request:**
```http
POST /api/v1/billing/my/invoices/87/prepare-payment/
Authorization: Bearer <client_token>

{ "provider": "stripe" }
```

**Response:** `{ "checkout_url": "https://checkout.stripe.com/pay/cs_test_..." }`

---

### Flow 4 — Class purchase

**Who:** Client. **Purpose:** `class_purchase`. **Payable:** `ClassPurchase` instance.

```
Client → Classes → New Class → Configure session → Checkout
  → PaymentOrchestrationService.initialize_payment(purpose="class_purchase")
  → Stripe checkout → webhook → Class access granted
```

**After payment:**
- `ClassPurchase.status = active`
- Delivery files unlocked
- `billing.receipt.issued` fires

---

### Flow 5 — Writer tip

**Who:** Client. **Purpose:** `tip`. **Payable:** `Tip` instance.

```
Client → Order detail → Tip writer → Enter amount → Pay
  → PaymentIntent(purpose="tip")
  → Stripe checkout → webhook
  → apply_payment: Writer wallet credited
  → LedgerService: Dr ClientWallet / Cr WriterPayable
  → tip_earning CompensationEvent recorded
```

---

### Flow 6 — Installment payment

**Who:** Client. **Part-payment on an invoice with a schedule.**

```
Admin → Invoice → Set up installment schedule → [amount, due_at] × N
Celery beat:
  → billing.installment.upcoming (3 days before) → reminder email
  → billing.installment.due (on due date) → reminder email

Client → Billing → Invoices → Open invoice → Pay installment
  → POST /billing/my/installments/<id>/prepare-payment/
  → Stripe checkout → InstallmentAllocationService routes partial payment
  → Invoice.status = partially_paid (until all installments settled)
```

---

## Provider registry

Two providers are registered in `payments_processor/providers/`:

| Provider  | Class                    | Use case                      |
|-----------|--------------------------|-------------------------------|
| `stripe`  | `StripePaymentProvider`  | Production + Stripe test mode |
| `mock`    | `MockPaymentProvider`    | Local dev, E2E tests          |

**`mock` provider behaviour:**
- `create_payment()` → returns a fake `checkout_url` (`https://example.com/mock-checkout`)
- No real network call; no card data required
- Confirmation via `POST /payments/checkout/mock-confirm/` — marks intent SUCCEEDED and runs the full `apply_payment()` path synchronously
- Only usable from the paying client's own account; only while intent is `PENDING`

---

## Gateway flexibility diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│               PER-WEBSITE GATEWAY CONFIGURATION                     │
│          Admin UI: /admin/payment-gateway (admin + superadmin)      │
└──────────┬──────────────────────────────────────────────────────────┘
           │ PaymentGatewayConfig model (one row per website)
           │
           ├── gateway           "stripe"
           ├── webhook_endpoint  "/api/v1/payments/webhooks/stripe/"
           ├── callback_base_url "https://app.gradecrest.com"
           ├── mode              live | test
           └── is_active         true | false

Priority chain for Stripe success/cancel URL:
  1. PaymentGatewayConfig.callback_base_url   ← set in admin UI
  2. Website.root_url                         ← fallback
  3. INFOQ_PAYMENT_BASE_URL env var           ← dev-only last resort

Each site routes independently:
  gradecrest.com        → app.gradecrest.com/payment/complete
  nursemygrade.com      → app.nursemygrade.com/payment/complete
  essaymaniacs.com      → app.essaymaniacs.com/payment/complete
  researchpapermate.com → app.researchpapermate.com/payment/complete
  writerscreek.com      → app.writerscreek.com/payment/complete
```

---

## Setup guide

### Local development (mock provider — zero Stripe dependency)

This lets you test the complete checkout + wallet credit loop without a Stripe account
or any payment keys.

**1. Environment (`.env`):**
```env
INFOQ_PAYMENT_BASE_URL=http://localhost:5173
# No Stripe keys needed for mock-only dev
```

**2. Seed gateway config (once, after first migrate):**

In the Django admin or shell, ensure a `PaymentGatewayConfig` row exists for your
dev website with `gateway = "mock"` and `is_active = True`. The seed command below
handles this:
```bash
python manage.py seed_dev_data        # creates website + gateway config rows
python manage.py seed_notification_events
python manage.py seed_templates
```

**3. Wallet top-up with mock (frontend):**

In `ClientWalletView`, the dev UI exposes a "Mock" toggle next to the provider
selector (only shown when `import.meta.env.DEV === true`). Select it, choose an
amount, acknowledge the disclosure, and click Top up. The frontend:
- POSTs to `/payments/checkout/` with `provider: "mock"`
- Receives the `payment_intent.reference`
- Immediately POSTs to `/payments/checkout/mock-confirm/` with that reference
- Reloads the wallet balance — no redirect, no Stripe session needed

**4. Order payment with mock:**

In the order wizard step 3, select **Mock** as the payment method (dev only). The
same `mock-confirm` endpoint is called automatically after order creation.

**5. Via Playwright E2E tests:**

The full suite uses the mock provider automatically. No Stripe keys required:
```bash
cd frontend
npx playwright test          # runs against localhost:5173 + localhost:8000
```

---

### Stripe test mode setup

Use this when you need to simulate real Stripe webhooks, 3DS flows, or decline
scenarios.

**1. Environment (`.env`):**
```env
STRIPE_SECRET_KEY=sk_test_51...
STRIPE_PUBLISHABLE_KEY=pk_test_51...
STRIPE_WEBHOOK_SECRET=whsec_test_...    # from `stripe listen` output
INFOQ_PAYMENT_BASE_URL=http://localhost:5173
```

**2. Start Stripe webhook forwarder:**
```bash
stripe listen --forward-to localhost:8000/api/v1/payments/webhooks/stripe/
# Prints: > Ready! Your webhook signing secret is whsec_test_...
# Copy that value to STRIPE_WEBHOOK_SECRET in .env and restart Django
```

**3. Configure gateway in admin UI:**

Navigate to `/admin/payment-gateway` → Edit the site's gateway config:
- **Gateway:** `stripe`
- **Mode:** `test`
- **Webhook endpoint:** `/api/v1/payments/webhooks/stripe/`
- **Callback base URL:** `http://localhost:5173`
- **Active:** ✓

**4. Test cards:**

| Scenario              | Card number         | Expiry | CVC |
|-----------------------|---------------------|--------|-----|
| Success               | 4242 4242 4242 4242 | Any future | Any |
| 3DS authentication    | 4000 0025 0000 3155 | Any future | Any |
| Decline (card)        | 4000 0000 0000 9995 | Any future | Any |
| Decline (insufficient)| 4000 0000 0000 0341 | Any future | Any |

**5. Test webhook events manually:**
```bash
stripe trigger checkout.session.completed
stripe trigger payment_intent.payment_failed
stripe trigger charge.dispute.created
```

---

### Production setup (live Stripe)

**Step 1 — Stripe Dashboard (OrderBridge account)**

1. In the Stripe Dashboard, go to **Developers → Webhooks → Add endpoint**
2. Add one endpoint per site domain:

   ```
   https://api.gradecrest.com/api/v1/payments/webhooks/stripe/
   https://api.nursemygrade.com/api/v1/payments/webhooks/stripe/
   https://api.essaymaniacs.com/api/v1/payments/webhooks/stripe/
   https://api.researchpapermate.com/api/v1/payments/webhooks/stripe/
   ```
   
   Or use a single endpoint if all sites share one backend:
   ```
   https://api.yourplatform.com/api/v1/payments/webhooks/stripe/<site_slug>/
   ```

3. Subscribe to these events on each endpoint:

   | Event                             | Why                               |
   |-----------------------------------|-----------------------------------|
   | `checkout.session.completed`      | Primary payment confirmation      |
   | `payment_intent.succeeded`        | Fallback confirmation             |
   | `payment_intent.payment_failed`   | Mark intent failed                |
   | `charge.failed`                   | Charge-level failure logging      |
   | `checkout.session.expired`        | Expire the PaymentIntent          |
   | `charge.dispute.created`          | Auto-create PaymentDispute row    |
   | `charge.dispute.updated`          | Update dispute status             |
   | `charge.dispute.closed`           | Close dispute, set resolved_at    |
   | `charge.dispute.funds_reinstated` | Dispute won                       |
   | `charge.dispute.funds_withdrawn`  | Dispute lost                      |

4. Copy the **Signing Secret** (`whsec_live_...`) for each endpoint

**Step 2 — Server environment variables**

```env
STRIPE_SECRET_KEY=sk_live_51...
STRIPE_PUBLISHABLE_KEY=pk_live_51...
STRIPE_WEBHOOK_SECRET=whsec_live_...

# Per-site keys if each site has its own Stripe account (optional)
# Configured in PaymentGatewayConfig model instead of env vars
```

**Step 3 — Admin UI: configure gateway per website**

Log in as superadmin → `/superadmin/payment-gateway` → for each website:

| Field               | Value                                   |
|---------------------|-----------------------------------------|
| Website             | Select the site (e.g. gradecrest.com)   |
| Gateway             | `stripe`                                |
| Mode                | `live`                                  |
| Webhook endpoint    | `/api/v1/payments/webhooks/stripe/`     |
| Callback base URL   | `https://app.gradecrest.com`            |
| Statement descriptor| `ORDERBRIDGE` (max 22 chars)            |
| Active              | ✓                                       |

**Step 4 — Payment notification emails (optional)**

Still in `/superadmin/payment-gateway` → "Payment Notification Emails" tab:

Add each finance/ops address that should receive forwarded copies of every billing
email (receipts, invoices, etc.):

```
finance@yourcompany.com    Label: Finance team
ceo@yourcompany.com        Label: CEO alerts
```

Multiple addresses per site. Pause/resume individually without deleting.

**Step 5 — One-time seeding (run on first deploy)**

```bash
python manage.py seed_notification_events    # registers all event keys in DB
python manage.py seed_templates              # creates email + in-app templates
```

Both commands are idempotent — safe to re-run. Use `--update` to push template
changes after editing `seed_templates.py`.

**Step 6 — Website branding for disclosure**

In Django admin → Websites → Website Branding:
- **Payment processor name:** `OrderBridge`
- **Payment statement descriptor:** `ORDERBRIDGE`

This text is used verbatim in the disclosure banner:
> "Your payment is securely processed by OrderBridge. Your card or bank statement
> may show: ORDERBRIDGE."

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
  → Opens /pay/invoice/<token>   (PublicPayView — no auth required)
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
  → Invoice.status = partially_paid until all installments settled
```

---

## Webhook processing detail

```
POST /api/v1/payments/webhooks/stripe/
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

## API reference

### Checkout

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/api/v1/payments/checkout/` | Client | Create payment intent and get checkout URL |
| `POST` | `/api/v1/payments/checkout/mock-confirm/` | Client | Dev only — instantly confirm a mock intent |
| `POST` | `/api/v1/payments/checkout/cancel-prewarm/` | Client | Cancel an unlinked pre-warmed intent |
| `POST` | `/api/v1/payments/webhooks/stripe/` | None (sig-verified) | Stripe event handler |
| `POST` | `/api/v1/payments/webhooks/stripe/<site_slug>/` | None | Per-site Stripe webhook |
| `POST` | `/api/v1/payments/refunds/` | Admin | Initiate a partial or full refund |

### Billing

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET`  | `/api/v1/billing/my/invoices/` | Client | List client's invoices |
| `POST` | `/api/v1/billing/my/invoices/<id>/prepare-payment/` | Client | Get checkout URL for invoice |
| `GET`  | `/api/v1/billing/my/installments/` | Client | List installments |
| `POST` | `/api/v1/billing/my/installments/<id>/prepare-payment/` | Client | Pay one installment |
| `GET`  | `/api/v1/billing/pay/invoices/<token>/` | None | Public invoice detail |
| `POST` | `/api/v1/billing/pay/invoices/<token>/prepare/` | None | Public invoice checkout |
| `POST` | `/api/v1/billing/pay/payment-requests/<token>/prepare/` | None | Public PR checkout |
| `GET`  | `/api/v1/billing/my/receipts/` | Client | List receipts |
| `GET`  | `/api/v1/billing/my/receipts/<id>/` | Client | Receipt detail |

### Wallet

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET`  | `/api/v1/wallets/me/` | Client | Wallet balance + currency |
| `GET`  | `/api/v1/wallets/me/entries/` | Client | Transaction history |
| `GET`  | `/api/v1/wallets/me/holds/` | Client | Active holds |
| `POST` | `/api/v1/wallets/me/payout-requests/` | Writer | Request payout |

### Gateway config (admin)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET`  | `/api/v1/payments/gateway/status/` | Admin | Gateway connectivity + masked keys |
| `GET/POST` | `/api/v1/payments/gateway/configs/` | Admin/Superadmin | List / create gateway configs |
| `GET/PATCH/DELETE` | `/api/v1/payments/gateway/configs/<id>/` | Admin/Superadmin | Manage one config |
| `GET/POST` | `/api/v1/payments/gateway/notification-emails/` | Admin/Superadmin | Manage notification email addresses |

---

## Key models

### `PaymentGatewayConfig`

| Field               | Purpose                                   |
| ------------------- | ----------------------------------------- |
| `website`           | OneToOneField — one config per site       |
| `gateway`           | Provider name (`"stripe"`, `"mock"`)      |
| `webhook_endpoint`  | Path registered in Stripe dashboard       |
| `callback_base_url` | Base URL for success/cancel redirects     |
| `mode`              | `live` or `test`                          |
| `is_active`         | Inactive → falls back to platform default |

### `PaymentNotificationEmail`

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
| `client_disclosure_text` | Snapshotted at creation — frozen for audit                      |
| `statement_descriptor_snapshot` | What client's statement showed at time of payment        |

### `PaymentDispute`

| Field                       | Purpose                                     |
| --------------------------- | ------------------------------------------- |
| `payment_intent`            | FK to the disputed intent                   |
| `provider_dispute_id`       | Stripe dispute ID (`dp_...`)                |
| `status`                    | `open / under_review / won / lost / closed` |
| `amount` / `currency`       | Disputed amount                             |
| `opened_at` / `resolved_at` | Timeline                                    |
| `raw_payload`               | Full Stripe event stored for audit          |

### `Receipt`

Issued automatically after every settlement. All disclosure and branding fields are
snapshotted at issuance — the receipt always reflects what the client saw at payment
time, not current branding.

---

## Merchant model

| Who                 | Role                                                |
| ------------------- | --------------------------------------------------- |
| OrderBridge         | Stripe account holder — receives all funds          |
| GC / EM / NMG / RPM / WC | Branded portals — clients interact here       |
| Django backend      | Creates sessions, verifies webhooks, fulfils orders |

**Disclosure requirement:** Before every Pay button, `PaymentDisclosureBanner`
(variant="pre") shows the intermediary name and statement descriptor. The Pay button
is disabled until the client acknowledges the disclosure. On return from Stripe,
variant="post" shows confirmation. Both `shown` and `acknowledged` events are
recorded server-side. The disclosure text is snapshotted on every payment model at
creation — receipts always reflect what the client saw, even if branding changes later.

---

## Notification seeding

```bash
# Register event keys from enum → DB
python manage.py seed_notification_events

# Seed email + in-app templates for all billing events
python manage.py seed_templates
```

Both commands are **idempotent** — safe to re-run.
Use `seed_templates --update` to push template edits without destroying existing rows.

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
| `/client/wallet`              | `ClientWalletView.vue`        | Client                    |
| `/admin/payment-gateway`      | `AdminPaymentGatewayView.vue` | Admin + Superadmin        |
| `/superadmin/payment-gateway` | `AdminPaymentGatewayView.vue` | Superadmin                |

`ClientWalletView` — balance, transaction history, holds, top-up (mock in dev, Stripe in prod), payout request form, disclosure gate.

`ClientBillingView` tabs: **Invoices** (installment pay + full pay), **Payment Requests**, **Receipts**.

---

## Refunds

```
POST /api/v1/payments/refunds/
Authorization: Bearer <admin_token>

{
  "payment_intent_reference": "pay_a1b2c3d4e5f6",
  "amount": "25.00",
  "reason": "requested_by_customer"
}
```

`StripePaymentProvider.refund_payment()` retrieves the Checkout Session → charge →
calls `stripe.Refund.create(charge=charge_id, amount=cents)`. Partial refunds
supported. State tracked on `PaymentRefund`, reconciled via `PaymentReconciliationService`.

---

## Decisions log

| Decision                                                           | Reason                                                                                                     |
| ------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------- |
| Single Stripe account (OrderBridge) for all 5 sites                | Simpler compliance, one merchant entity, easier reconciliation                                             |
| Stripe Checkout Sessions (hosted page)                             | PCI compliance out-of-the-box; no card data touches our servers                                            |
| `client_reference_id` + `metadata.reference` both set              | Two lookup paths in webhook — safety net if one field is absent                                            |
| Webhook deduplication via `ProviderWebhookEvent` unique constraint | Prevents double-fulfilment without locks; Stripe retries on non-2xx                                        |
| Fulfilment via Celery async (not inline in webhook handler)        | Webhook must return 200 fast; downstream logic can be slow and retried                                     |
| `/payment/complete` dedicated return page                          | Handles all payment types (order, invoice, wallet, tip); clean separation from billing management          |
| Public `/pay/:type/:token` (no login required)                     | Clients receiving invoice emails often aren't logged in; forcing login causes drop-off                     |
| Token expiry 72h                                                   | Long enough to act on an invoice email; short enough to limit exposure                                     |
| `billing.receipt.issued` fires unconditionally                     | Receipt is a regulatory artifact — must fire regardless of notification preferences                        |
| Dispute webhooks written to DB automatically                       | Admin visibility without polling Stripe dashboard                                                          |
| `PaymentGatewayConfig` per website                                 | Each site can swap provider, endpoint, or callback URL from admin panel without code changes               |
| `PaymentNotificationEmail` per website                             | Finance teams receive forwarded copies without needing portal accounts                                     |
| `website.root_url` drives Stripe callback URLs                     | Each site's return URL is automatically correct; `INFOQ_PAYMENT_BASE_URL` is now dev-only                  |
| `MockPaymentProvider` + `/mock-confirm/` endpoint                  | Complete dev checkout loop without Stripe — same `apply_payment()` code path as production                 |
| `dataclasses.asdict()` on provider response before JSON response   | `ProviderCheckoutResult` is a frozen dataclass; DRF's encoder can't serialize it directly                  |
| Writer payouts: manual ops, no automated rail                      | Volume doesn't justify Wise/Stripe Connect yet; `PayoutRecord` model is ready to attach a rail when needed |
