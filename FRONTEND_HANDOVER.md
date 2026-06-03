# Frontend Handover — Client Website Integration Guide

**Platform:** Multi-tenant academic writing services platform  
**Stack:** Django REST + Wagtail CMS · Vue 3 + Pinia + TypeScript (reference impl)  
**Date:** 2026-06-03  

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Portal Context — Bootstrap Entry Point](#2-portal-context--bootstrap-entry-point)
3. [Branding & Theming](#3-branding--theming)
4. [Authentication Flows](#4-authentication-flows)
5. [Pricing Calculator API](#5-pricing-calculator-api)
6. [Order Config Dropdowns](#6-order-config-dropdowns)
7. [Order Placement](#7-order-placement)
8. [CMS Content](#8-cms-content)
9. [Legal Documents & Help Center](#9-legal-documents--help-center)
10. [Newsletter Subscription](#10-newsletter-subscription)
11. [Attachments & Resources](#11-attachments--resources)
12. [Writer Applications (Public Form)](#12-writer-applications-public-form)
13. [Payment Disclosure Requirements](#13-payment-disclosure-requirements)
14. [Rate Limits & Pagination](#14-rate-limits--pagination)
15. [Multi-Tenant Domain Resolution](#15-multi-tenant-domain-resolution)
16. [Calculator Readiness Assessment](#16-calculator-readiness-assessment)
17. [Established Frontend Patterns](#17-established-frontend-patterns)
18. [Quick-Start Checklist](#18-quick-start-checklist)

---

## 1. Architecture Overview

Each client website is a **tenant** — a `Website` record with its own domain, branding, and content. The same backend serves all tenants; requests are routed to the correct tenant by the `PortalTenantResolverMiddleware`, which reads the request `Host` header and sets `request.website` and `request.portal` on every request.

```
essaybrand.com  ──►  Django middleware ──►  request.website = Website(id=3)
                                        ──►  request.portal  = PortalDefinition(code="client_portal")

writers.platform.com  ──►  Django middleware ──►  request.website = None
                                              ──►  request.portal  = PortalDefinition(code="writer_portal")
```

**Three portal surfaces:**

| Code | Domain type | Allowed roles | Surface |
|------|-------------|---------------|---------|
| `client_portal` | Client brand domain (e.g. essaybrand.com) | client | client |
| `writer_portal` | Shared writer domain | writer | writer |
| `internal_admin` | Staff domain | admin, superadmin, editor, support | staff |

A FE team building a **client website** works on the `client` surface only.

---

## 2. Portal Context — Bootstrap Entry Point

**This is the first call your app must make on every page load.**

```
GET /api/v1/portal-context/
```

- No authentication required
- No rate limit (explicitly disabled — safe to call on every request)
- Response is tenant-scoped automatically by the `Host` header

### Response shape

```json
{
  "surface": "client",
  "portal": { "code": "client_portal", "name": "Client Portal" },
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
    "text": "Your payment is securely processed by OrderBridge Payments. Your card statement may show: ORDERBRIDGE PAYMENTS.",
    "pre_payment_notice": "You are placing this order with EssayBrand. Payments are securely processed by OrderBridge Payments, our billing partner. Your card statement may show ORDERBRIDGE PAYMENTS."
  },
  "allowed_roles": ["client"]
}
```

### Usage

1. Apply `branding.primary_color`, `secondary_color`, `accent_color` as CSS custom properties on `<html>`.
2. Set `document.title` from `branding.brand_name`.
3. Set favicon from `branding.favicon_url`.
4. Store `payment_disclosure` — you **must** display it before and after every payment (legal requirement).
5. Check `allowed_roles` — only `client` users may use this surface; redirect others.

---

## 3. Branding & Theming

All tenant branding comes from the portal context. Apply it at boot:

```typescript
const ctx = await fetch('/api/v1/portal-context/').then(r => r.json());
const root = document.documentElement;
root.style.setProperty('--color-primary',   ctx.branding.primary_color);
root.style.setProperty('--color-secondary', ctx.branding.secondary_color);
root.style.setProperty('--color-accent',    ctx.branding.accent_color);
```

### Additional public config

```
GET /api/v1/websites/current/
```

Returns extended config including:
- `website` — id, name, slug, domain, support_email
- `branding` — same fields as portal context plus homepage headline/subheadline, trust claims, footer disclaimer
- `niche.service_catalog` — list of service codes available on this site
- `niche.subject_catalog` — list of subject areas
- `niche.order_form_defaults` — default values for the order form
- `niche.seo_defaults` — default meta title/description patterns

---

## 4. Authentication Flows

All auth endpoints are under `/api/v1/auth/`. The backend returns JWT tokens.

### Standard login

```
POST /api/v1/auth/login/
Body: { email, password }
Returns: { access, refresh, user: { id, email, role, full_name } }
```

Store `access` in memory (not localStorage for XSS safety), `refresh` in an httpOnly cookie if possible.

### Magic link (passwordless)

```
POST /api/v1/auth/magic-link/request/
Body: { email }

POST /api/v1/auth/magic-link/confirm/
Body: { token }
Returns: { access, refresh, user }
```

Rate limited to **5 requests per minute**.

### Registration

```
POST /api/v1/auth/register/
Body: { email, password, first_name, last_name }

POST /api/v1/auth/register/confirm/
Body: { token }       ← from email link
```

### Token refresh

```
POST /api/v1/auth/token/refresh/
Body: { refresh }
Returns: { access }
```

### Password reset

```
POST /api/v1/auth/password/reset/request/
Body: { email }

POST /api/v1/auth/password/reset/confirm/
Body: { token, password }
```

### All other auth routes

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/auth/logout/` | End current session |
| POST | `/auth/password/change/` | Change password (auth required) |
| GET | `/auth/sessions/current/` | Current session info |
| POST | `/auth/mfa/challenge/` | Send MFA code |
| POST | `/auth/mfa/verify/` | Verify MFA code |
| POST | `/auth/account-deletion/request/` | Schedule account deletion |
| POST | `/auth/account-deletion/cancel/` | Cancel deletion |

---

## 5. Pricing Calculator API

**The pricing API is fully built and ready for on-the-fly calculators.**

The flow is: **start session → update with user selections → display price breakdown**.  
Sessions are anonymous — no authentication required for the start/update steps.

### Step 1: Start a quote session

```
POST /api/v1/pricing/quotes/paper/start/
Body (all required unless marked optional):
{
  "service_code":        "standard_paper",
  "pages":               2,
  "deadline_hours":      48,
  "spacing":             "double",
  "paper_type_code":     "essay",
  "work_type_code":      "writing",
  "subject_code":        "nursing",
  "academic_level_code": "undergraduate",
  "writer_level_code":   "standard"  // optional
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

Use this for **live preview as users type** — no session persistence needed, fast.

### Step 2: Get final breakdown

```
POST /api/v1/pricing/quotes/paper/{session_id}/update/
Body: same fields as start (any changed values)

Returns:
{
  "session_id": "a1b2c3d4-...",
  "status": "final",
  "calculated_price": "21.00",
  "currency": "USD",
  "lines": [
    { "line_type": "base",     "label": "Base price (2 pages)",    "amount": "18.00" },
    { "line_type": "deadline", "label": "48h deadline",            "amount": "2.00"  },
    { "line_type": "level",    "label": "Undergraduate level",     "amount": "1.00"  }
  ]
}
```

### Other quote types

| Service | Start | Update |
|---------|-------|--------|
| Design (slides/PPT) | `POST /pricing/quotes/design/start/` | `POST /pricing/quotes/design/{id}/update/` |
| Diagrams | `POST /pricing/quotes/diagram/start/` | `POST /pricing/quotes/diagram/{id}/update/` |
| Multi-service order | `POST /pricing/quotes/composite/create/` | `POST /pricing/quotes/composite/{id}/update/` |

### Step 3: Snapshot (before placing order)

Once the user is ready to order, convert the session to a locked-in price:

```
POST /api/v1/pricing/quotes/{session_id}/snapshot/
Returns: { snapshot_id, price, currency, expires_at }
```

Pass `snapshot_id` to the order creation endpoint.

### Calculator inputs — where to get them

All dropdown values come from:

```
GET /api/v1/order-configs/academic-levels/
GET /api/v1/order-configs/paper-types/
GET /api/v1/order-configs/formatting-styles/
GET /api/v1/order-configs/subjects/
GET /api/v1/order-configs/types-of-work/
GET /api/v1/order-configs/english-types/
GET /api/v1/order-configs/writer-deadline-configs/
```

Each returns `[{ id, name, code, is_active, display_order, ... }]`. Use `code` as the key for pricing calls, `name` for display.

---

## 6. Order Config Dropdowns

Populate all order form selects from these endpoints (public, no auth):

```
GET /api/v1/order-configs/<collection>/
```

| Collection | Contents |
|---|---|
| `academic-levels` | High school, Undergraduate, Master's, PhD |
| `paper-types` | Essay, Research paper, Dissertation, Case study… |
| `formatting-styles` | APA, MLA, Chicago, Harvard… |
| `subjects` | Nursing, Business, Psychology… |
| `types-of-work` | Writing, Editing, Rewriting, Proofreading… |
| `english-types` | US English, UK English… |
| `writer-deadline-configs` | Available deadlines (hours), mapped to urgency tier |

Results are already ordered by `display_order`. Only return `is_active: true` items.

---

## 7. Order Placement

Order creation requires authentication. The flow:

1. User builds order form → call pricing API to preview price
2. User confirms → `POST /pricing/quotes/{session_id}/snapshot/` to lock price
3. Call order creation:

```
POST /api/v1/orders/create/
Authorization: Bearer <access_token>
Body:
{
  "topic":                "Nursing leadership reflection",
  "paper_type_id":        4,
  "academic_level_id":    2,
  "formatting_style_id":  1,
  "subject_id":           7,
  "type_of_work_id":      1,
  "pricing_snapshot_id":  "snap_abc123",
  "discount_code_used":   "SUMMER15"    // optional
}
```

Returns the new order object with `id`, `status: "pending"`, and payment context.

### Payment disclosure — mandatory display

Before the user confirms payment, display `payment_disclosure.pre_payment_notice` from portal context.
After payment confirmation, display `payment_disclosure.text`.  
This is a **legal requirement** — do not skip it.

---

## 8. CMS Content

Content is managed in Wagtail and served via two APIs:

### Wagtail Page API (primary)

```
GET /api/v2/pages/
Query params:
  type       cms_blog.BlogPostPage | cms_service_pages.ServicePage | ...
  slug       filter by slug
  live=true  only published
  order      -first_published_at | title | ...
  fields     comma-separated field names to include
  limit      default 25
  offset     pagination
```

### Blog posts

```
GET /api/v2/pages/?type=cms_blog.BlogPostPage&live=true&order=-first_published_at&fields=title,slug,excerpt,featured_image,category,primary_author,first_published_at,last_substantive_update

// Single post by slug:
GET /api/v2/pages/?type=cms_blog.BlogPostPage&slug=how-to-write-a-nursing-essay&fields=title,excerpt,body,primary_author,category,tags,citation_mode,primary_service
```

**BlogPostPage exposed fields:** title, slug, excerpt, featured_image, body (StreamField), primary_author, contributing_authors, category, tags, citation_mode, primary_service, pillar, last_substantive_update

### Service pages

```
GET /api/v2/pages/?type=cms_service_pages.ServicePage&live=true&order=title&fields=title,slug,service_category,pricing_from,pricing_to,turnaround_hours_fastest,primary_cta_text,primary_cta_url

// Single service page:
GET /api/v2/pages/?type=cms_service_pages.ServicePage&slug=nursing-essay&fields=title,body,service_category,pricing_from,pricing_to,primary_cta_text,primary_cta_url,reviewer,show_aggregate_rating
```

**ServicePage exposed fields:** title, slug, service_category, pricing_from, pricing_to, turnaround_hours_fastest, turnaround_hours_standard, primary_cta_text, primary_cta_url, show_aggregate_rating, reviewer, body (StreamField), last_substantive_update

### Service index (hero content)

```
GET /api/v2/pages/?type=cms_service_pages.ServiceIndexPage&live=true&fields=title,intro&limit=1
```

Use `title` as the services page headline and `intro` (RichTextField HTML) as the sub-paragraph.

### Available CMS Block Types

All blocks arrive in the `body` StreamField as `[{ type: string, value: object }]`.

**Both blog posts and service pages:**
`heading`, `paragraph`, `image`, `list`, `checklist`, `quote`, `callout`, `stats_highlight`, `before_after`, `definition`, `timeline`, `faq`, `cta`, `internal_link`, `attachment`, `table`, `chart`, `embed`, `divider`, `video`, `key_takeaways`, `toc`, `author_review`, `disclaimer`, `sample_excerpt`

**Blog only:** `sources`, `related_posts`, `code`

**Service pages only:** `hero`, `trust_strip`, `feature_grid`, `how_it_works`, `pricing_table`, `comparison_table`, `testimonials`, `guarantees`

### Custom CMS endpoints

```
GET /cms-api/authors/                       List all published authors
GET /cms-api/authors/<slug>/                Single author profile
GET /cms-api/authors/<slug>/posts/          Posts by this author
GET /cms-api/content-graph/pillars/         Topic cluster pillars
GET /cms-api/content-graph/pillars/<slug>/spokes/  Related posts in cluster
GET /cms-api/citations/?blog_post=<id>      Academic citations for a post
```

### SEO Landing Pages

Dynamic, database-driven landing pages (not Wagtail pages):

```
GET /api/v1/seo-pages/public/seo-pages/<slug>/
Returns: { title, meta_title, meta_description, blocks, publish_date }
```

---

## 9. Legal Documents & Help Center

### Legal documents

```
GET /api/v1/legal/                          List all active documents
GET /api/v1/legal/<doc_type>/               Single document

doc_type values:
  terms_of_service
  privacy_policy
  refund_policy
  cookie_policy
  acceptable_use_policy
  writer_agreement
  copyright_policy

POST /api/v1/legal/<doc_type>/agree/        Record user acceptance (auth required)
```

Returns: `{ title, content (HTML), version, effective_date }`

### Help center articles

```
GET /api/v1/legal/help/categories/         Categories for the current user's role
GET /api/v1/legal/help/articles/           Articles (filtered by role automatically)
GET /api/v1/legal/help/articles/<slug>/    Single article

Query params for articles:
  category    <slug>    filter by category
  featured    true      only featured articles
```

Articles are **automatically audience-filtered** by the backend based on the authenticated user's role. Anonymous requests return `audience=all` articles only.

---

## 10. Newsletter Subscription

```
POST /cms-api/newsletters/subscribe/
Body:
{
  "email": "user@example.com",
  "frequency": "weekly",      // weekly | monthly | instant
  "consent_marketing": true,
  "source": "blog_form",      // blog_form | attachment_gate | order_optin
  "source_detail": "slug-of-post"  // optional attribution
}

POST /cms-api/newsletters/unsubscribe/
Body: { "email": "user@example.com", "reason": "not_relevant" }
// reason: too_frequent | not_relevant | never_subscribed | other
```

---

## 11. Attachments & Resources

Email-gated downloadable resources (sample essays, templates, guides):

```
GET /cms-api/attachments/                   List all public attachments
  Query: type, category, level, style, featured

GET /cms-api/attachments/<slug>/            Single attachment detail

GET /cms-api/attachments/<slug>/check_access/
Returns:
{
  "access_level": "free" | "email" | "account" | "customer" | "paid",
  "has_access": true | false,
  "requires_email": true,
  "requires_account": false,
  "requires_purchase": false
}

POST /cms-api/attachments/<slug>/download/
Body: { "email": "...", "consent_marketing": false, "consent_newsletter": false }
Returns: { "download_url": "...", "expires_at": "..." }

POST /cms-api/attachments/<slug>/rate/
Body: { "rating": 4 }    // 1–5
```

---

## 12. Writer Applications (Public Form)

```
POST /api/v1/writer-management/applications/submit/
Content-Type: multipart/form-data
Body:
  full_name         string (required)
  email             string (required)
  phone_number      string
  country           string
  education_level   string
  years_of_experience  integer
  subjects          string[] (repeated field or JSON)
  application_text  string (min 10 chars)
  resume            file (.pdf, .doc, .docx)
  sample_work       file (.pdf, .doc, .docx)
```

No authentication required. Returns `201 Created` on success.

**Important:** Do **not** set `Content-Type: multipart/form-data` manually — let the browser/axios set it with the correct boundary string.

---

## 13. Payment Disclosure Requirements

**Legal requirement — must be displayed on all client sites.**

1. **Before payment confirmation:** display `payment_disclosure.pre_payment_notice`
2. **After payment / on receipt:** display `payment_disclosure.text` and `payment_disclosure.statement_descriptor`

Both strings come from the portal context response. If `payment_disclosure` is `null`, the tenant has not configured payment disclosure — surface a generic notice and flag this to the tenant admin.

Example pre-payment notice:
> "You are placing this order with EssayBrand. Payments are securely processed by OrderBridge Payments, our billing partner. Your card statement may show ORDERBRIDGE PAYMENTS."

---

## 14. Rate Limits & Pagination

### Rate limits

| Scope | Limit |
|-------|-------|
| Portal context | **No limit** |
| Authenticated users | 10,000 / hour |
| Anonymous | 2,000 / hour |
| Login endpoint | 10 / minute |
| Magic link request | 5 / minute |
| Password reset | 5 / 10 minutes |

### Pagination

Default: **25 items per page**. Use `?limit=N&offset=N` or `?page=N` depending on the endpoint. All paginated responses wrap in:

```json
{ "count": 142, "next": "...", "previous": "...", "results": [...] }
```

Wagtail API uses `?limit=N&offset=N` and wraps in `{ "meta": { "total_count": 142 }, "items": [...] }`.

---

## 15. Multi-Tenant Domain Resolution

The backend resolves the tenant **automatically from the `Host` header**. You don't need to pass a website ID in requests — just ensure the `Host` header matches the configured tenant domain.

In development:
- Run the backend with `DEBUG=True`
- Run `python manage.py seed_dev_data` once to create a dev tenant with `domain=localhost`
- All API calls from `localhost` will resolve to the dev tenant automatically

In production:
- Configure your DNS and nginx to proxy to the Django backend
- Set the `Host` header to the client domain (e.g., `essaybrand.com`)
- The middleware does the rest

**CORS:** The backend has CORS configured. Add your client domain to `CORS_ALLOWED_ORIGINS` in the environment or settings.

---

## 16. Calculator Readiness Assessment

### Verdict: Ready. No new backend work needed.

The pricing API supports fully anonymous, real-time price calculations. Here's exactly what to build:

### Inline page calculator (homepage / service page)

```
User selects: paper type, pages, deadline, academic level
    ↓ debounce 300ms
POST /api/v1/pricing/quotes/paper/start/
    { service_code, paper_type_code, pages, deadline_hours, academic_level_code, spacing }
    ↓
Display: estimated_min_price – estimated_max_price (e.g., "$18 – $24")
    ↓ user clicks "Get exact price" or fills more fields
POST /api/v1/pricing/quotes/paper/{session_id}/update/
    ↓
Display: calculated_price + line items breakdown
```

### Sidebar calculator (persistent, route-aware)

Same API flow — the sidebar component holds a `session_id` in local state and calls `update/` on every change. Since sessions are anonymous, no auth is needed until the user clicks "Place Order".

### CMS calculator block — not yet built

Currently no `PricingCalculatorBlock` in the block library. To embed a calculator inside a blog post or service page body, you'd need to:

1. Add a `CalculatorBlock` to `backend/cms_core/blocks.py` SERVICE_PAGE_BLOCKS (a simple struct with `service_code` and `default_deadline_hours` fields)
2. Render it as a Vue `<PricingCalculator>` component client-side when the block type is `calculator`

This is a one-day addition — the API is ready, only the block definition and frontend component are missing.

### Data needed to populate calculators

All dropdown options are live from the API:

```javascript
const [levels, paperTypes, deadlines, subjects] = await Promise.all([
  fetch('/api/v1/order-configs/academic-levels/').then(r => r.json()),
  fetch('/api/v1/order-configs/paper-types/').then(r => r.json()),
  fetch('/api/v1/order-configs/writer-deadline-configs/').then(r => r.json()),
  fetch('/api/v1/order-configs/subjects/').then(r => r.json()),
]);
```

Cache these at app boot — they change infrequently.

---

## 17. Established Frontend Patterns

The reference implementation (`frontend/`) uses Vue 3 + Pinia + TypeScript. Key patterns:

### Boot sequence

```typescript
// main.ts / App.vue
const portalCtx = usePortalContextStore();
await portalCtx.init();  // calls /api/v1/portal-context/, applies CSS vars
```

### API client

```typescript
// src/api/client.ts
// Axios instance with:
//   - JWT Authorization header injection
//   - 401 → auto refresh token
//   - Base URL configurable via VITE_API_BASE_URL env var
import { api, apiPath } from '@/api/client';

const { data } = await api.get(apiPath('/order-configs/academic-levels/'));
```

### CMS API wrapper

```typescript
import { cmsApi } from '@/api/cms';

const { data } = await cmsApi.servicePages({ category: 'nursing' });
// data.items: ServicePageSummary[]
```

### Public views already built

| View | Route | Notes |
|------|-------|-------|
| `HomeView.vue` | `/` | Minimal sign-in portal |
| `ServicesView.vue` | `/services` | CMS-driven hero + service cards |
| `ServicePageView.vue` | `/services/:slug` | Full StreamField block renderer |
| `BlogIndexView.vue` | `/blog` | Paginated blog listing |
| `BlogPostView.vue` | `/blog/:slug` | Full post with TOC, citations |
| `AuthorsView.vue` | `/authors` | Author directory |
| `AuthorView.vue` | `/authors/:slug` | Author profile + posts |
| `ResourcesView.vue` | `/resources` | Downloadable resources listing |
| `ResourceView.vue` | `/resources/:slug` | Resource detail + access gate |
| `HelpCenterView.vue` | `/help` | Help center + legal links |
| `HelpArticleView.vue` | `/help/articles/:slug` | Article reader |
| `LegalView.vue` | `/legal/:docType` | Legal document viewer |
| `WriterApplyView.vue` | `/apply` | Writer application form |
| `LandingPageView.vue` | `/:slug` | Dynamic SEO landing pages |

### Environment variables

```env
VITE_API_BASE_URL=https://api.essaybrand.com     # or http://localhost:8000 in dev
VITE_API_PREFIX=/api/v1
```

---

## 18. Quick-Start Checklist

For each new client website:

- [ ] Configure DNS — point domain to load balancer / nginx
- [ ] Add domain to `CORS_ALLOWED_ORIGINS` in backend env
- [ ] Run `python manage.py seed_dev_data` (dev) or create `Website` record (prod)
- [ ] Create `WebsiteBranding` record — brand_name, colors, payment_processor_name, statement_descriptor
- [ ] Create `PortalDefinition` for the domain with `code="client_portal"`
- [ ] Publish at least one `TenantHomePage` in Wagtail under Root (required for CMS to work)
- [ ] Create `ServiceIndexPage` under TenantHomePage and publish service pages
- [ ] Create help categories and articles scoped to `audience=client`
- [ ] Set up legal documents (terms, privacy, refund) via admin panel
- [ ] Configure `WriterLevel` records + `TipPolicy` (required for order flow)
- [ ] Set `VITE_API_BASE_URL` in the FE build to the backend URL
- [ ] Call `GET /api/v1/portal-context/` at app boot and apply branding
- [ ] Display payment disclosure on all checkout flows
- [ ] Test magic link flow end-to-end
- [ ] Test order placement with a test account

---

*For backend architecture questions, see `backend/writing_system/urls.py` for the full URL tree and `backend/core/middleware/portal_tenant_resolver.py` for domain resolution logic.*
