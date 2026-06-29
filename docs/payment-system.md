# Payment System — Architecture & Completion Status

> Last updated: 2026-06-29

---

## Overview

Payments on this platform flow through a single intermediary merchant entity (e.g. *OrderBridge Payments*), not directly through each client-brand website. The card statement descriptor shows the intermediary name — not the brand name. All payment-related code lives across six backend apps and one frontend SPA.

**Backend apps involved**

| App | Responsibility |
|---|---|
| `billing` | Invoice, PaymentRequest, Receipt, Installment, Reminder, SupportingDocument lifecycles |
| `payments_processor` | PaymentIntent, Stripe adapter, webhooks, refunds, disputes |
| `wallets` | Client & writer wallets, holds, writer payout requests |
| `writer_compensation` | Earnings events, settlement periods, payout batches, bonuses |
| `ledger` | Double-entry accounting journal across all money movement |
| `writer_management` | Legacy writer payment preference + payment history records |

---

## 1. Money-In (Client Payments)

### 1.1 Checkout Flows

There are five distinct checkout entry points. All route through `PaymentOrchestrationService` → Stripe Checkout Session → webhook confirmation.

| Entry point | Trigger | Purpose code |
|---|---|---|
| Order payment | Order placed, client pays for service | `order` |
| Special order payment | Admin creates bespoke order | `special_order` |
| Class purchase | Client buys academic assistance session | `class_purchase` |
| Wallet top-up | Client manually funds their wallet | `wallet_top_up` |
| Tip | Client tips a writer after delivery | `tip` |
| Invoice payment | Admin-issued invoice, installment-level | `invoice` |
| Payment request | Admin-created ad-hoc charge | `billing_payment_request` |

### 1.2 PaymentIntent Lifecycle

```
created → pending → authorized → captured → applied
                             └──→ failed
                 └──→ expired
```

`PaymentApplicationService.apply_payment()` routes the `applied` step to the correct downstream handler per `purpose` — crediting the wallet, fulfilling the order, granting class access, etc.

### 1.3 Stripe Integration

- Provider: `StripePaymentProvider` in `payments_processor/providers/stripe.py`
- Method: Stripe Checkout Sessions (hosted page redirect)
- Webhook endpoint: `POST /payments/webhooks/stripe/` (unauthenticated, signature-verified)
- Handled events: `checkout.session.completed`, `payment_intent.succeeded`, `payment_intent.payment_failed`, `charge.failed`, `checkout.session.expired`
- Not yet handled: `charge.dispute.created`, `charge.dispute.closed`, `payment_intent.canceled`, `refund.updated`, `radar.early_fraud_warning`

### 1.4 Invoice & Installment System

- `Invoice` model: full lifecycle (draft → issued → partially_paid → paid → cancelled/expired)
- `PaymentInstallment`: schedules split payment dates; `InstallmentAllocationService` routes partial payments
- `PaymentRequest`: lightweight ad-hoc charge (no installments), mirrors Invoice structure
- `Receipt`: immutable snapshot issued on successful payment; fields snapshot all disclosure/branding state at issuance time
- `Reminder`: scheduled notifications (email) for due/overdue invoices and payment requests; runs via Celery beat

**Public (unauthenticated) pay flow**

Backend exposes token-based endpoints:
- `GET /billing/pay/invoices/<token>/`
- `POST /billing/pay/invoices/<token>/prepare/`
- `POST /billing/pay/payment-requests/<token>/prepare/`

These allow a client to pay an invoice via a link in their email without being logged in. **No frontend page exists for this yet.**

### 1.5 Discount Integration

Discounts can be applied to invoices via `InvoiceDiscountIntegrationService`. **Not yet wired for PaymentRequests.**

---

## 2. Payment Disclosure

Regulatory/chargeback mitigation: clients must see and acknowledge the statement descriptor before payment is processed.

**Source of truth:** `WebsiteBranding.payment_processor_name` + `payment_statement_descriptor`

Disclosure text rendered as:
> "Your payment is securely processed by {processor}. Your card or bank statement may show: {descriptor}."

**Three disclosure touchpoints — all implemented:**

| Point | Implementation |
|---|---|
| Before payment | `PaymentDisclosureBanner` (pre variant), submit button disabled until `paymentDisclosureAccepted = true` |
| Payment confirmation | `PaymentDisclosureBanner` (post variant) shown on success state |
| Receipt / email | `ReceiptService` copies snapshot from `PaymentIntent` or `PaymentRequest` at issuance |

**Audit trail:** `PaymentDisclosureAcknowledgement` model + `POST /api/websites/payment-disclosure/acknowledge/`

**Models with snapshotted disclosure fields:**

| Model | Fields snapshotted |
|---|---|
| `PaymentIntent` | 5 fields at `create_intent()` |
| `Invoice` | 5 fields at `create_invoice()` |
| `PaymentRequest` | 5 fields at `create_payment_request()` |
| `Receipt` | Copied from intent/request at `issue_receipt()` |
| `WalletEntry` | 5 fields (wallet top-up flow) |

---

## 3. Client Wallet

- Each client has one `Wallet` per website (currency-specific)
- Top-up: client initiates → Stripe Checkout → webhook → `WalletService.credit_wallet()` → `WalletEntry` posted
- Order payment from wallet: `WalletService.debit_wallet()` → hold created → released on order acceptance or returned on cancellation
- `WalletHold`: reserved balance mechanism — amount is locked but not yet debited; captured on event or released on cancellation
- Loyalty points can be converted to wallet credit (`loyalty_conversion` entry type)

**Frontend:** `ClientWalletView` — balance, entry history, holds, top-up button, payout request form, disclosure gate before top-up.

---

## 4. Money-Out (Writer Payouts)

### 4.1 Compensation Events

Every earning-generating action produces a `CompensationEvent`:

| Source | Event types |
|---|---|
| Order delivery | `order_earning` |
| Special order milestone | `special_order_earning` |
| Class session | `class_session_earning` |
| Tip | `tip_earning` |
| Admin bonus | `bonus` |
| Fine / deduction | `fine`, `deduction`, `penalty` |

### 4.2 Settlement Engine

```
CompensationEvents
  → SettlementPeriod (per writer, per window)
    → SettlementItems (line-by-line breakdown)
      → SettlementPeriod.finalize()
        → PayoutBatch → PayoutRecord (per writer)
          → mark_record_paid(method, external_reference)
```

`SettlementEngineService.run_settlement_pipeline()` is the single orchestration entry point. Settlement periods can be weekly, biweekly, or monthly per `WriterPayoutPreference.cycle_type`.

### 4.3 Payout Execution

Writer payouts are **manually executed by admins**. The flow:

1. Admin runs settlement → `PayoutRecord` created with status `pending`
2. Admin pays the writer outside the system (bank transfer, PayPal, Wise, etc.)
3. Admin calls `mark_record_paid(method='bank_transfer', external_reference='TXN-123')` → `PayoutRecord.status = paid`
4. `WalletSyncService.settle_payout_record()` credits the writer's wallet

**No automated disbursement rail exists.** Stripe Connect, PayPal Payouts, Wise API — none are integrated.

### 4.4 Writer Payout Requests (Ad-hoc)

Writers can request an early/ad-hoc payout via `WriterPayoutRequestService.request_payout()`. Admin approves/rejects/processes in `AdminWalletsView`. This is separate from the settlement engine cycle.

---

## 5. Double-Entry Ledger

Every material money movement is journaled via `FinancialOrchestrationService`:

| Event | Journal entries |
|---|---|
| Client pays (Stripe capture) | Dr: Gateway receivable / Cr: Revenue |
| Order fulfilled → writer earns | Dr: Writer expense / Cr: Writer payable |
| Tip paid | Dr: Client wallet / Cr: Writer payable |
| Refund issued | Dr: Revenue / Cr: Gateway payable |
| Writer payout | Dr: Writer payable / Cr: Bank |
| Admin wallet credit | Dr: Adjustment expense / Cr: Client wallet |

`JournalEntry` + `JournalLine` (double-entry). `AccountBalanceSnapshot` for period-end auditing. `ReconciliationRecord` for cross-checking against Stripe/bank statements.

---

## 6. Frontend Payment UX — Flows

### Client

| Flow | Status |
|---|---|
| Top up wallet | Done |
| Pay order from wallet (portal) | Done |
| Pay order via Stripe (portal) | Done |
| View invoices + pay installments | Done |
| View payment requests | Done (no pay button yet) |
| View receipts | **Missing** |
| Pay full invoice in one shot | **Missing** |
| Pay payment request | **Missing** |
| Pay invoice from email link (public) | **Missing** |
| Post-Stripe return/confirmation page | **Missing** |

### Admin

| View | Status |
|---|---|
| Create/issue invoices & payment requests | Done |
| View receipts | Done (read-only) |
| Void receipts | **Missing** |
| Create installment schedules (UI) | **Missing** |
| Manage payment disclosure config | Done |
| Fund/debit wallets | Done |
| Approve writer payout requests | Done |
| Run compensation settlement | Done |
| Mark payout records paid | Done |
| View ledger / journal | Done |
| Configure payment reminders | Done |

### Writer

| View | Status |
|---|---|
| View earnings events | Done |
| View payout history | Done |
| Set payout preference / cycle | Done |
| Request early payout | Done |
| View advance payments | Done |

---

## 7. Known Gaps & Decisions Pending

### Technical gaps

1. **Public invoice pay page** — backend token endpoints exist; no frontend page. Every invoiced client who gets an email link has nowhere to land.
2. **Post-Stripe success page** — no dedicated return URL handler; app currently relies on whatever page was open when checkout was initiated.
3. **Client receipt view** — `GET /billing/receipts/` exists; no frontend route or component.
4. **Dispute webhook handling** — `charge.dispute.created` / `charge.dispute.closed` not routed through the webhook handler; `PaymentDispute` model exists but is never written to automatically.
5. **Automated payout disbursement** — entire writer payout flow is manual. No Stripe Connect, no PayPal Payouts, no Wise.
6. **PaymentRequest discounts** — `InvoiceDiscountIntegrationService` wired only for `Invoice`; `PaymentRequest` has no discount path.
7. **Duplicate models** — `WriterPayoutPreference` and `CurrencyConversion` each exist in both `writer_management` and `writer_compensation`. Ownership unclear; migration risk.

### Architectural decisions still open

- **Stripe Connect vs. manual payouts forever** — current manual approach works at low volume; Connect adds complexity but removes the ops bottleneck as scale grows.
- **Marketing site → portal checkout handoff** — currently marketing sites collect the order then portal handles payment. A "pay now" flow directly from the marketing site order form has never been scoped.
- **Multi-currency** — `CurrencyConversionRate` and `CurrencyConversion` models exist but are unused in any live service path.

---

## 8. Completion by Subsystem

| Subsystem | % Done | Notes |
|---|---|---|
| Invoice / PaymentRequest / Receipt lifecycle | **85%** | Missing: public pay page, void receipt UI, PR discounts |
| Stripe payment collection + webhooks | **80%** | Missing: dispute events, post-Stripe success page |
| Client wallet + top-up | **90%** | Very complete; minor gap: no receipt view |
| Client billing frontend | **55%** | 5 frontend flows still missing |
| Admin financial management | **80%** | Missing: receipt void, installment schedule UI |
| Writer earnings + settlement engine | **75%** | Engine complete; automated disbursement at 0% |
| Writer payout execution (automated) | **10%** | Structure only — no actual outbound payment rail |
| Double-entry ledger | **70%** | Journaling works; reconciliation UI is admin-only and basic |
| Payment disclosure | **100%** | All three touchpoints done, audit trail in place |
| Marketing site pricing / order intake | **75%** | Calculator done; no portal checkout handoff |

**Overall: ~73% complete**

The core money-in path (client pays → order fulfilled) is production-ready. The main open area is automated writer payouts — the settlement engine is built but the actual disbursement to a writer's bank/PayPal is 100% manual ops work today.

---

## 9. What Ships Next (Recommended Sequence)

1. **Public invoice pay page** — highest business value, unblocks the invoicing feature entirely
2. **Stripe return / success confirmation page** — closes the checkout loop for all flows
3. **Client "Pay payment request" button** — one missing button in `ClientBillingView`
4. **Client receipt view** — read-only, backend already done
5. **Dispute webhook routing** — low risk, closes a financial integrity gap
6. **Automated payout rail** (Wise API or Stripe Connect) — ops-reducing, deferred to when volume justifies it
