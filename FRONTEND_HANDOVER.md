# Frontend Engineer Handoff

**Platform:** Multi-tenant writing services platform  
**Backend:** Django 5.2 REST · Wagtail 7 CMS · Django Channels (WebSocket)  
**Reference implementation:** `frontend/` — Vue 3 + Pinia + TypeScript + Tailwind  
**Updated:** June 2026

> This document is for engineers building or customising **client portals** and the **writer portal**. For the staff portal, see the reference implementation directly.

---

## Table of Contents

**Shared foundations**
1. [Portal Bootstrap (read this first)](#1-portal-bootstrap-read-this-first)
2. [Branding & Theming](#2-branding--theming)
3. [Authentication](#3-authentication)
4. [Real-time Notifications](#4-real-time-notifications)
5. [Rate Limits & Pagination](#5-rate-limits--pagination)

**Client portal**
6. [Pricing Calculator](#6-pricing-calculator)
7. [Order Config Dropdowns](#7-order-config-dropdowns)
8. [Discount / Coupon Codes](#8-discount--coupon-codes)
9. [Order Placement & Tracking](#9-order-placement--tracking)
10. [Payment & Wallet](#10-payment--wallet)
11. [Payment Disclosure (legal requirement)](#11-payment-disclosure-legal-requirement)
12. [Loyalty & Rewards](#12-loyalty--rewards)
13. [Disputes](#13-disputes)
14. [CMS Content](#14-cms-content)
15. [Legal Documents & Help Center](#15-legal-documents--help-center)
16. [SEO & Analytics](#16-seo--analytics)
17. [Writer Applications (public form)](#17-writer-applications-public-form)
18. [Multi-Niche Configuration](#18-multi-niche-configuration)

**Writer portal**
19. [Writer Portal Overview](#19-writer-portal-overview)
20. [Writer Profile & Availability](#20-writer-profile--availability)
21. [Order Pool & Assignments](#21-order-pool--assignments)
22. [Earnings & Payouts](#22-earnings--payouts)
23. [Vetting & Quizzes](#23-vetting--quizzes)
24. [Writer Public Profile](#24-writer-public-profile)

**Operations**
25. [Multi-Tenant Setup Per Client Site](#25-multi-tenant-setup-per-client-site)
26. [Environment Variables](#26-environment-variables)
27. [New Client Site Checklist](#27-new-client-site-checklist)

---

## 1. Portal Bootstrap (read this first)

**First call on every page load — before any auth or routing.**

```
GET /api/v1/portal-context/
```

No authentication. No rate limit. Tenant resolved automatically from the `Host` header.

### Response

```json
{
  "surface": "client",
  "portal": { "code": "client_portal", "name": "EssayBrand" },
  "website": {
    "id": 3,
    "name": "EssayBrand",
    "slug": "essaybrand",
    "domain": "essaybrand.com"
  },
  "branding": {
    "brand_name": "EssayBrand",
    "tagline": "Expert writing, delivered on time.",
    "logo_url": "https://cdn.essaybrand.com/logo.png",
    "favicon_url": "https://cdn.essaybrand.com/favicon.ico",
    "primary_color": "#4f46e5",
    "secondary_color": "#0f172a",
    "accent_color": "#14b8a6"
  },
  "payment_disclosure": {
    "processor_name": "OrderBridge Payments",
    "statement_descriptor": "ORDERBRIDGE PAYMENTS",
    "text": "...",
    "pre_payment_notice": "..."
  },
  "allowed_roles": ["client"],
  "ga4_measurement_id": "G-XXXXXXXXXX"
}
```

### What to do with it

| Field | Action |
|-------|--------|
| `surface` | Gate routing — redirect writers/staff away from client domain |
| `branding.*` | Apply as CSS vars; set `document.title`, favicon |
| `payment_disclosure` | Store — display before and after every payment |
| `allowed_roles` | Only users with matching role may access this surface |
| `ga4_measurement_id` | Initialize GA4 with this ID if present |

### Surface → allowed roles

| Portal code | Surface | Roles |
|---|---|---|
| `client_portal` | `client` | client |
| `writer_portal` | `writer` | writer |
| `internal_admin` | `staff` | admin, superadmin, editor, support |

---

## 2. Branding & Theming

```typescript
const ctx = await fetch('/api/v1/portal-context/').then(r => r.json());
const root = document.documentElement;
root.style.setProperty('--color-primary',   ctx.branding.primary_color);
root.style.setProperty('--color-secondary', ctx.branding.secondary_color);
root.style.setProperty('--color-accent',    ctx.branding.accent_color);
document.title = ctx.branding.brand_name;
```

### Extended website config

```
GET /api/v1/websites/current/
```

Returns everything in portal context plus:
- `support_email`, `support_phone`
- `branding.homepage_headline`, `branding.homepage_subheadline`
- `branding.trust_claims[]` — bullet points for trust sections
- `branding.footer_disclaimer`
- `niche.service_catalog[]` — service codes active on this site
- `niche.subject_catalog[]` — subject areas for this site
- `niche.order_form_defaults` — pre-filled form values
- `niche.seo_defaults` — meta title/description templates

---

## 3. Authentication

All auth endpoints: `/api/v1/auth/`

Store `access` token in memory (not localStorage). Store `refresh` in an httpOnly cookie where possible.

### Login

```
POST /api/v1/auth/login/
Body: { email, password }
Returns: { access, refresh, user: { id, email, role, full_name } }
```

Rate limited: **10/minute**.

### Registration

```
POST /api/v1/auth/register/
Body: { email, password, first_name, last_name }

POST /api/v1/auth/register/confirm/
Body: { token }    ← from email link
```

### Magic link (passwordless)

```
POST /api/v1/auth/magic-link/request/   Body: { email }
POST /api/v1/auth/magic-link/confirm/   Body: { token }
```

Rate limited: **5/minute**.

### Token refresh

```
POST /api/v1/auth/token/refresh/
Body: { refresh }
Returns: { access }
```

### Other auth endpoints

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/auth/logout/` | End session |
| POST | `/auth/password/change/` | Change password (authenticated) |
| POST | `/auth/password/reset/request/` | Password reset email |
| POST | `/auth/password/reset/confirm/` | Confirm reset with token |
| GET | `/auth/sessions/current/` | Session info |
| POST | `/auth/mfa/challenge/` | Send MFA code |
| POST | `/auth/mfa/verify/` | Verify MFA code |
| POST | `/auth/account-deletion/request/` | Schedule deletion |

---

## 4. Real-time Notifications

The backend pushes in-app notifications via WebSocket. Polling is the fallback.

### WebSocket (primary)

Connect after login using the JWT access token:

```javascript
const ws = new WebSocket(
  `wss://app.writerscreek.com/ws/notifications/?token=${accessToken}`
);

ws.onmessage = (evt) => {
  const notification = JSON.parse(evt.data);
  // { id, event_key, title, message, category, priority,
  //   is_read, is_critical, created_at }
  showNotificationBadge(notification);
};

ws.onclose = () => setTimeout(reconnect, 5000); // auto-reconnect
```

The server closes the connection with code `4001` if the token is invalid or expired. Refresh the token and reconnect.

### Polling fallback

If WebSocket is unavailable:

```
GET /api/v1/notifications/poll/
Returns: { unread_count: 3, latest: NotificationItem | null }
```

Throttled at **4/minute** — safe to call every 30 s.

### Notification feed

```
GET /api/v1/notifications/feed/
Query: ?is_read=false, ?category=info|warning|error|success, ?priority=high

PATCH /api/v1/notifications/feed/{id}/mark-read/
PATCH /api/v1/notifications/feed/mark-all-read/
```

---

## 5. Rate Limits & Pagination

### Rate limits

| Scope | Limit |
|-------|-------|
| Portal context | No limit |
| Authenticated requests | 10,000 / hour |
| Anonymous requests | 2,000 / hour |
| Login | 10 / min |
| Magic link | 5 / min |
| Password reset | 5 / 10 min |
| Notification poll | 4 / min |

### Pagination

All list endpoints:

```json
{ "count": 142, "next": "?page=3", "previous": "?page=1", "results": [...] }
```

Use `?page=N` or `?limit=N&offset=N`. Default page size is **25**.

Wagtail API:

```json
{ "meta": { "total_count": 142 }, "items": [...] }
```

Uses `?limit=N&offset=N`.

---

## 6. Pricing Calculator

Fully anonymous — no auth required for start/update steps.

### Flow

```
POST /api/v1/pricing/quotes/paper/start/        ← fast estimate, debounce on input
POST /api/v1/pricing/quotes/paper/{id}/update/  ← exact price + line items
POST /api/v1/pricing/quotes/{id}/snapshot/      ← lock price before placing order
```

### Start (live preview)

```
POST /api/v1/pricing/quotes/paper/start/
Body:
{
  "service_code":        "standard_paper",
  "pages":               2,
  "deadline_hours":      48,
  "spacing":             "double",
  "paper_type_code":     "essay",
  "work_type_code":      "writing",
  "subject_code":        "nursing",
  "academic_level_code": "undergraduate",
  "writer_level_code":   "standard"
}

Returns:
{
  "session_id": "a1b2c3d4-...",
  "status": "estimate",
  "estimated_min_price": "18.00",
  "estimated_max_price": "24.00",
  "currency": "USD"
}
```

### Update (exact price + breakdown)

```
POST /api/v1/pricing/quotes/paper/{session_id}/update/
Body: same fields (pass changed values only)

Returns:
{
  "session_id": "...",
  "status": "final",
  "calculated_price": "21.00",
  "currency": "USD",
  "lines": [
    { "line_type": "base",     "label": "Base price (2 pages)", "amount": "18.00" },
    { "line_type": "deadline", "label": "48h deadline",         "amount": "2.00"  },
    { "line_type": "level",    "label": "Undergraduate",        "amount": "1.00"  }
  ]
}
```

### Other order types

| Type | Start | Update |
|------|-------|--------|
| Design (slides) | `POST /pricing/quotes/design/start/` | `.../design/{id}/update/` |
| Diagrams | `POST /pricing/quotes/diagram/start/` | `.../diagram/{id}/update/` |
| Multi-service | `POST /pricing/quotes/composite/create/` | `.../composite/{id}/update/` |

### Snapshot (before placing order)

```
POST /api/v1/pricing/quotes/{session_id}/snapshot/
Returns: { snapshot_id, price, currency, expires_at }
```

Pass `snapshot_id` to the order creation endpoint.

---

## 7. Order Config Dropdowns

Public endpoints — no auth, cache at boot.

```
GET /api/v1/order-configs/academic-levels/
GET /api/v1/order-configs/paper-types/
GET /api/v1/order-configs/formatting-styles/
GET /api/v1/order-configs/subjects/
GET /api/v1/order-configs/types-of-work/
GET /api/v1/order-configs/english-types/
GET /api/v1/order-configs/writer-deadline-configs/
GET /api/v1/pricing/public/addons/?service_code=standard_paper
```

All return `[{ id, name, code, is_active, display_order, ... }]`. Use `code` for API calls, `name` for display. Only show `is_active: true` items.

The **subject catalog** and **service catalog** for a specific tenant are pre-filtered by the backend based on the `Host` header — you get only what that site offers.

---

## 8. Discount / Coupon Codes

### Preview (show discount before ordering)

```
POST /api/v1/discounts/client/preview/
Authorization: Bearer <token>
Body:
{
  "subtotal": "21.00",
  "payable_type": "order",
  "entered_code": "SUMMER15",
  "has_prior_paid_purchase": false
}

Returns:
{
  "discount": {
    "discount_code": "SUMMER15",
    "discount_amount": "3.15",
    "final_amount": "17.85",
    "origin": "manual"
  }
}
```

`discount` is `null` if the code is invalid, expired, or not eligible for this order.

### Apply at order creation

Pass `discount_code_used` (or `entered_code`) in the order creation payload — the backend applies the discount and records usage automatically. No separate apply step needed.

### List available discounts

```
POST /api/v1/discounts/client/
Body: { "subtotal": "21.00", "payable_type": "order" }
Returns: [{ discount_code, name, discount_type, discount_value, origin, ends_at }]
```

Use this to show "available promotions" or auto-apply the best discount.

---

## 9. Order Placement & Tracking

### Place an order

```
POST /api/v1/orders/create/
Authorization: Bearer <token>
Body:
{
  "topic":               "Nursing leadership reflection",
  "paper_type_id":       4,
  "academic_level_id":   2,
  "formatting_style_id": 1,
  "subject_id":          7,
  "type_of_work_id":     1,
  "deadline_hours":      48,
  "pages":               2,
  "spacing":             "double",
  "instructions":        "...",
  "pricing_snapshot_id": "snap_abc123",
  "discount_code_used":  "SUMMER15"
}

Returns: { order: { id, status, total_price, currency, client_deadline, ... } }
```

### Client order list

```
GET /api/v1/orders/
Query: ?status=active|completed|cancelled, ?page=1, ?sort_by=created_at
```

### Order detail

```
GET /api/v1/orders/{id}/
```

Returns full order including assigned writer (pen name only), files, messages.

### Order lifecycle (available actions)

```
GET /api/v1/orders/{id}/lifecycle/
Returns: {
  status, available_actions, has_active_dispute, current_writer_id, ...
}
```

`available_actions` tells the UI exactly which buttons to show. Possible client actions:
- `approve_order` — client approves completed order
- `request_revision` — within revision window
- `raise_dispute` — when order is in_progress/submitted/completed
- `cancel_order` — before assignment

### Actions

```
POST /api/v1/orders/{id}/approve/
POST /api/v1/orders/{id}/request-revision/   Body: { reason }
POST /api/v1/orders/{id}/disputes/           Body: { reason, summary }
POST /api/v1/orders/{id}/cancel/             Body: { reason }
```

### Order status values

| Status | Meaning for client |
|--------|--------------------|
| `created` / `unpaid` | Payment pending |
| `paid` | Paid, awaiting assignment |
| `assigned` / `in_progress` | Writer working |
| `qa_review` / `submitted` | In final review — download available |
| `completed` | Approved |
| `revision_requested` | Revision in progress |
| `disputed` | Under review by support |
| `cancelled` | Cancelled |

---

## 10. Payment & Wallet

### Wallet balance

```
GET /api/v1/wallets/balance/
Returns: { available_balance, pending_balance, currency }
```

### Wallet top-up (Stripe)

```
POST /api/v1/payments/wallet/top-up/
Body: { amount: "50.00", payment_method_id: "pm_..." }
Returns: { client_secret }   ← pass to Stripe.js to confirm
```

### Wallet transaction history

```
GET /api/v1/wallets/entries/
Returns: [{ id, direction, amount, description, entry_type, created_at, balance_after }]
```

### Pay order from wallet

```
POST /api/v1/orders/{id}/pay-from-wallet/
```

### Pay order with Stripe card

```
POST /api/v1/payments/order/{id}/pay/
Body: { payment_method_id }
Returns: { client_secret, status }
```

Pass `client_secret` to `stripe.confirmCardPayment()`.

---

## 11. Payment Disclosure (legal requirement)

**Mandatory on all client sites. Do not skip.**

From portal context:

```javascript
const { pre_payment_notice, text, statement_descriptor } = ctx.payment_disclosure;
```

**Before payment confirmation:** show `pre_payment_notice`.

**After payment / on receipt:** show `text` and `statement_descriptor`.

Example:
> "You are placing this order with EssayBrand. Payments are securely processed by OrderBridge Payments. Your card statement may show: ORDERBRIDGE PAYMENTS."

If `payment_disclosure` is `null`, the tenant is misconfigured — surface a warning in dev, generic notice in prod.

---

## 12. Loyalty & Rewards

```
GET /api/v1/loyalty/status/
Returns: { points_balance, tier, next_tier, points_to_next_tier, lifetime_points }

GET /api/v1/loyalty/history/
Returns paginated points transactions

POST /api/v1/loyalty/redeem/
Body: { reward_id, points_to_spend }

GET /api/v1/loyalty/rewards/
Returns available rewards catalog
```

Loyalty tier badge and points are typically shown in the client dashboard header.

---

## 13. Disputes

```
POST /api/v1/orders/{order_id}/disputes/
Body: { reason: "quality_issue|late_delivery|wrong_file|...", summary }
Returns: { dispute_id, status: "open" }

GET /api/v1/disputes/my/
Returns client's own disputes

POST /api/v1/disputes/{id}/withdraw/
```

Show raise-dispute UI only when `available_actions` includes `raise_dispute`.

---

## 14. CMS Content

### Wagtail Page API

```
GET /api/v2/pages/?type=<PageType>&live=true&fields=...
```

### Blog posts

```
# List
GET /api/v2/pages/?type=cms_blog.BlogPostPage&live=true&order=-first_published_at
  &fields=title,slug,excerpt,featured_image,category,primary_author,first_published_at

# Single
GET /api/v2/pages/?type=cms_blog.BlogPostPage&slug=<slug>
  &fields=title,excerpt,body,primary_author,category,tags,citation_mode
```

### Service pages

```
# List
GET /api/v2/pages/?type=cms_service_pages.ServicePage&live=true&order=title
  &fields=title,slug,service_category,pricing_from,pricing_to,turnaround_hours_fastest

# Single
GET /api/v2/pages/?type=cms_service_pages.ServicePage&slug=<slug>
  &fields=title,body,pricing_from,pricing_to,primary_cta_text,show_aggregate_rating
```

### Services hero content

```
GET /api/v2/pages/?type=cms_service_pages.ServiceIndexPage&live=true&limit=1
  &fields=title,intro
```

### Authors

```
GET /cms-api/authors/
GET /cms-api/authors/<slug>/
GET /cms-api/authors/<slug>/posts/
```

### Content graph (topic clusters)

```
GET /cms-api/content-graph/pillars/
GET /cms-api/content-graph/pillars/<slug>/spokes/
```

### Attachments (gated downloads)

```
GET /cms-api/attachments/                         List
GET /cms-api/attachments/<slug>/
GET /cms-api/attachments/<slug>/check_access/     { access_level, has_access, requires_email }
POST /cms-api/attachments/<slug>/download/
  Body: { email, consent_marketing, consent_newsletter }
  Returns: { download_url, expires_at }
```

### Newsletter

```
POST /cms-api/newsletters/subscribe/
Body: { email, frequency: "weekly|monthly|instant", consent_marketing, source }

POST /cms-api/newsletters/unsubscribe/
Body: { email, reason }
```

### SEO landing pages

```
GET /api/v1/seo-pages/public/seo-pages/<slug>/
Returns: { title, meta_title, meta_description, blocks, publish_date }
```

### StreamField block types

All `body` fields arrive as `[{ type, value }]`. Implement a block renderer for:

`heading`, `paragraph`, `image`, `list`, `checklist`, `quote`, `callout`, `stats_highlight`, `before_after`, `definition`, `timeline`, `faq`, `cta`, `table`, `chart`, `embed`, `video`, `key_takeaways`, `toc`, `author_review`, `disclaimer`, `sample_excerpt`

Service page extras: `hero`, `trust_strip`, `feature_grid`, `how_it_works`, `pricing_table`, `comparison_table`, `testimonials`, `guarantees`

Blog extras: `sources`, `related_posts`, `code`

---

## 15. Legal Documents & Help Center

```
GET  /api/v1/legal/                       List active documents
GET  /api/v1/legal/<doc_type>/            Single document (HTML content)
POST /api/v1/legal/<doc_type>/agree/      Record acceptance (auth required)
```

`doc_type`: `terms_of_service`, `privacy_policy`, `refund_policy`, `cookie_policy`, `acceptable_use_policy`

```
GET /api/v1/legal/help/categories/        Role-scoped categories
GET /api/v1/legal/help/articles/          Role-scoped articles
GET /api/v1/legal/help/articles/<slug>/   Single article
```

---

## 16. SEO & Analytics

### GA4

```javascript
const ga4Id = ctx.ga4_measurement_id; // from portal context
if (ga4Id) {
  // initialise gtag with ga4Id
  gtag('config', ga4Id);
}
```

### Structured data

```
GET /api/v1/seo/schema/<page_type>/?url=<canonical_url>
Returns: JSON-LD schema (Organization, FAQPage, Article, etc.)
```

### Canonical URLs

Build canonicals from the `website.domain` in portal context. The CMS uses Wagtail's built-in `seo_title` and `search_description` fields — access via `?fields=seo_title,search_description` in page queries.

### Sitemap

```
GET /sitemap.xml    ← auto-generated, tenant-scoped
```

---

## 17. Writer Applications (public form)

```
POST /api/v1/writer-management/applications/submit/
Content-Type: multipart/form-data

Fields:
  full_name, email, phone_number (opt), country (opt),
  education_level, years_of_experience, subjects (multi),
  application_text, resume (file), sample_work (file)
```

No authentication. Returns `201 Created`. Do **not** set `Content-Type` manually — let the browser set the boundary.

---

## 18. Multi-Niche Configuration

Each tenant (`Website` record) can have a completely different order form, subject catalog, and pricing profile. The backend enforces this automatically via the `Host` header.

### What differs per niche

| Feature | How it's configured | Where you see it |
|---------|---------------------|-----------------|
| Subject catalog | `WebsiteNicheConfig.subject_catalog` | `/api/v1/order-configs/subjects/` filtered by site |
| Service catalog | `WebsiteNicheConfig.service_catalog` | `/api/v1/websites/current/` → `niche.service_catalog` |
| Order form defaults | `WebsiteNicheConfig.order_form_defaults` | Pre-fill deadline, pages, academic level |
| Branding | `WebsiteBranding` | Portal context |
| Pricing profile | Per-service pricing rules attached to the website | Pricing API |
| Writer levels | `WriterLevel` records scoped to website | Shown on order form as writer tier selection |
| CMS content | Wagtail pages under the tenant's root page | Standard Wagtail API, auto-filtered |
| Legal docs | Scoped to website | `/api/v1/legal/` |

### Niche vs general sites

A **niche** site (e.g. `nursingressays.com`) typically:
- Has `subject_catalog = ["nursing", "pharmacology", "healthcare_management"]`
- Pre-fills academic level to "Undergraduate" or "Masters"
- Has service pages specific to nursing
- May have higher pricing for specialised subjects

A **general** site (e.g. `writepro.com`) has the full catalog.

**Your frontend doesn't need to handle this differently** — just read the catalogs from the API and present what's returned. The backend serves the right subset per tenant.

### Order form default values

```
GET /api/v1/websites/current/
→ niche.order_form_defaults: {
    deadline_hours: 72,
    pages: 2,
    academic_level_code: "undergraduate",
    spacing: "double"
  }
```

Pre-fill the order form with these values on mount.

---

## 19. Writer Portal Overview

The writer portal lives at `app.writerscreek.com` — a single shared domain for all writers across all tenants. Portal context returns `surface: "writer"`.

Writers sign in at **writerscreek.com/login** (the single login entry point) and are automatically routed to `app.writerscreek.com/auth/adopt` via a JWT hash redirect. The `/auth/adopt` route is already implemented in the reference SPA (`AdoptTokenView.vue`).

### Key writer endpoints

All writer-specific endpoints are under `/api/v1/writer-management/me/` (authenticated as writer role).

```
GET  /writer-management/me/profile/              Own profile (registration_id, bio, etc.)
PATCH /writer-management/me/profile/             Update bio, qualifications, timezone
GET  /writer-management/me/availability/         Availability windows
POST /writer-management/me/availability/toggle/  Toggle accepting orders on/off
GET  /writer-management/me/performance/          Stats: rating, on-time %, completion %
```

---

## 20. Writer Profile & Availability

### Own profile

```
GET /api/v1/writer-management/me/profile/
Returns:
{
  registration_id, pen_name, bio, qualifications, years_of_experience,
  timezone, writer_level: { name, is_active }, is_accepting_orders,
  is_verified, joined_at
}
```

### Update profile

```
PATCH /api/v1/writer-management/me/profile/
Body: { bio, qualifications, timezone }
```

### Availability

```
GET  /writer-management/me/availability/
POST /writer-management/me/availability/declare/    Body: { from_date, to_date, reason }
POST /writer-management/me/availability/toggle/     Body: { accepting: true|false }
```

### Performance stats

```
GET /api/v1/writer-management/me/performance/
Returns:
{
  total_orders, completed_orders, cancelled_orders,
  on_time_deliveries, late_deliveries,
  average_rating, total_ratings, revision_count,
  total_earnings, total_tips_received
}
```

Derive computed stats:
- `on_time_rate = on_time_deliveries / completed_orders`
- `completion_rate = completed_orders / total_orders`

---

## 21. Order Pool & Assignments

### Available orders (pool)

```
GET /api/v1/orders/?status=ready_for_staffing
Returns writer-safe order subset (no client identity, no total_price)
```

Writers see: `topic`, `deadline`, `writer_deadline`, `pages`, `subject`, `academic_level`, `writer_compensation` (their share), `preferred_writer_id` (if invited).

### Express interest / take order

```
POST /api/v1/orders/{id}/bid/           Express interest
POST /api/v1/orders/{id}/take/          Immediate take (if pool allows direct take)
POST /api/v1/orders/{id}/acknowledge/   Acknowledge after assignment
```

### Current assignments

```
GET /api/v1/orders/?status=assigned,in_progress,revision_requested
Returns writer's active assignments
```

### Submit work

```
POST /api/v1/orders/{id}/submit/
Body: { delivery_notes }    ← files attached via /orders/{id}/files/
```

### Files

```
GET  /api/v1/orders/{id}/files/
POST /api/v1/orders/{id}/files/        Upload file (multipart)
```

### Writer-visible order fields

Writers **never** see:
- `client_deadline` (they see `writer_deadline` only)
- Client contact information
- `total_price` (they see `writer_compensation` only)
- Payment status

---

## 22. Earnings & Payouts

### Earnings summary

```
GET /api/v1/writer-compensation/writer/compensation/summary/
Returns:
{ total_earned, completed_orders, pending_amount, available_for_advance }
```

### Current payment window

```
GET /api/v1/writer-compensation/writer/compensation/current-window/
Returns:
{ window_id, net, event_count, cycle_type, start_date, end_date, status }
```

### Wallet balance

```
GET /api/v1/writer-compensation/writer/compensation/balance/
Returns: { pending, available, lifetime }
```

### Earnings events (order-by-order history)

```
GET /api/v1/writer-compensation/writer/compensation/events/
Query: ?event_type=ORDER_EARNING|TIP|BONUS, ?status=matured|paid
Returns paginated CompensationEvent list
```

### Payout history

```
GET /api/v1/writer-compensation/writer/compensation/payouts/
Returns: [{ id, total_amount, status, window_label, paid_at }]
```

### Earnings trend chart

```
GET /api/v1/analytics/charts/writer-earnings/?months=12
Returns: { labels, series: [{name, type, data}], summary: {change_pct, current, previous} }
```

---

## 23. Vetting & Quizzes

Writers must pass required quizzes before their application can be approved.

### Available quizzes

```
GET /api/v1/vetting/quizzes/
Returns quizzes for this website (grammar, subject, essay)
```

### Start an attempt

```
POST /api/v1/vetting/quizzes/{quiz_id}/start/
Returns: { attempt_id, questions: [{ id, text, type, choices }] }
```

### Submit answers

```
POST /api/v1/vetting/attempts/{attempt_id}/submit/
Body:
{
  "answers": [
    { "question_id": 1, "selected_choice_id": 3 },
    { "question_id": 2, "essay_response": "..." }
  ]
}
Returns: { status: "passed|failed|pending_review", score }
```

### Attempt status

```
GET /api/v1/vetting/attempts/my/
Returns writer's own attempts with status and scores
```

---

## 24. Writer Public Profile

Client-visible writer card — shown during assignment selection or as a standalone profile page.

```
GET /api/v1/writer-management/writers/{public_uuid}/card/
Authorization: Bearer <client token>
Returns:
{
  public_uuid, registration_id, pen_name, bio, qualifications,
  years_of_experience, timezone, level_name, is_verified, joined_at,
  rating_average, review_count, completed_orders_count
}
```

### Writer reviews

```
GET /api/v1/writer-management/writers/{registration_id}/reviews/
GET /api/v1/writer-management/writers/{registration_id}/reviews/summary/
Returns: { average_rating, total_reviews, rating_distribution }
```

Note: the card endpoint uses `public_uuid`; review endpoints use `registration_id`. Both are returned in the card response.

---

## 25. Multi-Tenant Setup Per Client Site

When onboarding a new client website:

### Backend (admin panel or Django shell)

```python
# 1. Create Website record
website = Website.objects.create(
    name="NursingEssays Pro",
    slug="nursingressays",
    domain="nursingressays.com",
    is_active=True,
)

# 2. Create WebsiteBranding
WebsiteBranding.objects.create(
    website=website,
    brand_name="NursingEssays Pro",
    primary_color="#0ea5e9",
    tagline="Written by qualified nurses.",
    payment_processor_name="OrderBridge Payments",
    statement_descriptor="ORDERBRIDGE PAYMENTS",
)

# 3. Create PortalDefinition
PortalDefinition.objects.create(
    code="client_portal",
    name="NursingEssays Pro Client Portal",
    domain="nursingressays.com",
    is_active=True,
)

# 4. Create niche config
WebsiteNicheConfig.objects.create(
    website=website,
    subject_catalog=["nursing", "healthcare_management", "pharmacology"],
    service_catalog=["standard_paper", "editing"],
    order_form_defaults={
        "academic_level_code": "undergraduate",
        "deadline_hours": 72,
    },
)

# 5. Create writer levels for this site
WriterLevel.objects.create(website=website, name="Standard", is_default=True, display_order=1)
WriterLevel.objects.create(website=website, name="Advanced", display_order=2)
```

### nginx

Add the new domain to the `server_name` directive or create a separate server block. Both proxy to the same Django backend — the middleware handles the rest.

### CORS

Add the new domain to `CORS_ALLOWED_ORIGINS` in `.env`:

```
CORS_ALLOWED_ORIGINS=https://essaybrand.com,https://nursingressays.com
```

### Wagtail CMS

1. In the Wagtail admin, create a new `TenantHomePage` under the root
2. Set it as the root page for `nursingressays.com`
3. Create a `ServiceIndexPage` and publish service pages under it
4. Create help articles scoped to `audience=client`

---

## 26. Environment Variables

```env
# Frontend build
VITE_API_BASE_URL=https://api.yourplatform.com    # or http://localhost:8000 in dev
VITE_API_PREFIX=/api/v1

# Backend
SECRET_KEY=<long random>
DEBUG=False
ALLOWED_HOSTS=writerscreek.com,app.writerscreek.com,admin.writerscreek.com,gradecrest.com
CORS_ALLOWED_ORIGINS=https://app.writerscreek.com,https://writerscreek.com,https://admin.writerscreek.com,https://gradecrest.com
SESSION_COOKIE_DOMAIN=.writerscreek.com
CSRF_COOKIE_DOMAIN=.writerscreek.com
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
SENDGRID_API_KEY=SG....
CHANNEL_REDIS_URL=redis://:password@redis:6379/3   # for WebSocket channel layer
```

---

## 27. New Client Site Checklist

- [ ] DNS A record → server IP
- [ ] nginx server_name added to the appropriate server block in `nginx/nginx.conf`
- [ ] New domain in `CORS_ALLOWED_ORIGINS` + `CSRF_TRUSTED_ORIGINS`
- [ ] SSL cert issued: `docker compose run --rm certbot certonly --webroot -w /var/www/certbot -d {domain}`
- [ ] `Website` record created in admin
- [ ] `WebsiteBranding` record configured (colors, brand name, payment disclosure)
- [ ] `PortalDefinition` record created (`code=client_portal`, domain set)
- [ ] `WebsiteNicheConfig` configured (subject catalog, order form defaults)
- [ ] `WriterLevel` records created for this website (at least one default)
- [ ] Tip policy configured (`TipPolicy`) — required for order flow
- [ ] Wagtail: root page created and set for the domain
- [ ] Wagtail: at least one `ServiceIndexPage` and service pages published
- [ ] Help articles published for `audience=client`
- [ ] Legal documents published (terms, privacy, refund policy)
- [ ] `ga4_measurement_id` set on `WebsiteBranding` if using GA4
- [ ] Test: `GET /api/v1/portal-context/` returns correct branding from the domain
- [ ] Test: pricing calculator returns prices
- [ ] Test: order placement end-to-end with test account
- [ ] Test: payment disclosure shown before and after payment
- [ ] Test: magic link login flow

---

*Architecture diagrams: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)*  
*Backend URL tree: `backend/writing_system/urls.py`*  
*Domain resolution: `backend/core/middleware/portal_tenant_resolver.py`*
