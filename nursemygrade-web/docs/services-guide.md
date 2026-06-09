# Services Guide

NurseMyGrade publishes **22 nursing-specific service landing pages**. Each is a pre-rendered SSG route under `/services/:slug`. This guide explains how they work, what content they carry, and how to add or edit them.

---

## The 22 services

| # | Slug | Title | Price from |
|---|------|-------|-----------|
| 1 | `nursing-essays` | Nursing Essay Writing Service | $24/page |
| 2 | `care-plans` | Nursing Care Plan Writing Service | $26/page |
| 3 | `soap-notes` | SOAP Note Writing Service | $28/page |
| 4 | `capstone-projects` | Nursing Capstone Project Writing Service | $30/page |
| 5 | `nursing-research-papers` | Nursing Research Paper Writing Service | $26/page |
| 6 | `nursing-case-studies` | Nursing Case Study Writing Service | $28/page |
| 7 | `nursing-dissertations` | Nursing Dissertation & Thesis Writing Service | $35/page |
| 8 | `concept-maps` | Nursing Concept Map Writing Service | $25/page |
| 9 | `nursing-coursework` | Nursing Coursework & Assignment Help | $24/page |
| 10 | `online-nursing-classes` | Online Nursing Class Help | $200/course |
| 11 | `shadow-health` | Shadow Health Digital Clinical Experience Help | $45/case |
| 12 | `ihuman-patients` | iHuman Virtual Patient Case Help | $45/case |
| 13 | `buy-nursing-papers` | Buy Nursing Papers Online | $24/page |
| 14 | `nursing-report` | Nursing Report Writing Service | $26/page |
| 15 | `nursing-presentation` | Nursing Presentation (PPT) Writing Service | $35/deck |
| 16 | `bsn-writing` | BSN Nursing Writing Services | $24/page |
| 17 | `msn-help` | MSN Nursing Writing Help | $30/page |
| 18 | `apa-nursing-papers` | APA Nursing Paper Writing Service | $24/page |
| 19 | `medical-paper-writing` | Medical & Health Sciences Paper Writing Service | $26/page |
| 20 | `nursing-homework` | Nursing Homework Help Online | $24/page |
| 21 | `postgrad-nursing` | Postgraduate Nursing Writing Help | $30/page |
| 22 | `health-medical-writers` | Health & Medical Writers for Hire | $28/page |

---

## Data sources — static catalogue vs. CMS

Each service page draws from two sources, merged at render time:

### 1. Static catalogue (`composables/useServices.ts`)

The static catalogue is the primary data source. It contains:

- `slug` — URL key and lookup identifier
- `title` — H1 and meta title seed
- `icon` — Lucide icon name for the service card
- `priceFrom` — starting price (USD)
- `hero` — `{ headline, sub }` — the above-fold section
- `tabs` — array of `{ label, content }` objects (see Tabbed content below)
- `features` — "What's Included" bullets
- `faqs` — service-specific FAQs
- `relatedSlugs` — up to 4 slugs for the "Related Services" strip
- `meta` — `{ title, description }` — SEO meta overrides

The static catalogue exists because:
1. It guarantees content at build time even when the CMS is empty.
2. SEO-critical content (meta titles, descriptions, schema) is version-controlled, not database-dependent.
3. Performance — no API call needed to render the page shell.

### 2. Wagtail CMS (`composables/useServiceCms.ts`)

When a Wagtail `ServicePage` record exists for the same slug, its StreamField body content is fetched at SSG build time and rendered after the static tabs. This allows the content team to add rich editorial content (testimonials, how-it-works steps, pricing tables, benefits sections) without a code deploy.

**Merge priority:** Static catalogue wins for hero, meta, and pricing. Wagtail wins for body blocks.

---

## Page structure

Each service landing page (`pages/services/[slug].vue`) renders in this order:

```
1.  Breadcrumb bar          — Home > Services > [Service Name]
2.  Hero                    — Headline + sub + calculator embed + CTA
3.  Trust strip             — 9,800+ papers · 500+ nurses · 4.98★ · 3 hr delivery
4.  Tabbed content panel    — 6 tabs (see below)
5.  CMS body blocks         — Wagtail StreamField (if present)
6.  Related services strip  — Up to 4 linked service cards
7.  Final CTA banner        — "Ready to get started?" + Order button
```

### Tabbed content

Every static catalogue entry includes 6 content tabs:

| Tab label | What it contains |
|-----------|-----------------|
| **What's Included** | Bullet list of deliverables specific to this service |
| **How It Works** | 4-step process (Brief → Match → Track → Download) |
| **Why NurseMyGrade** | Differentiators specific to this service type |
| **Qualifications** | Writer credential requirements for this service |
| **Pricing** | Price range, page count, deadline tiers |
| **FAQ** | 4–6 service-specific questions |

---

## SEO per service page

Each service page emits three structured data payloads (injected via `useHead`):

1. **`Service` schema** — name, description, provider, price per page
2. **`FAQPage` schema** — 4 universal nursing FAQs (writer credentials, legality, revisions, turnaround)
3. **`BreadcrumbList` schema** — emitted by the `<Breadcrumbs>` component

Meta title format: `[Service Title] — BSN, MSN & DNP Writers | NurseMyGrade`

Canonical URL: `https://nursemygrade.com/services/[slug]`

---

## Adding a new service

### Option A — Static catalogue only (fastest, SEO-ready immediately)

1. Open `composables/useServices.ts`
2. Add a new entry to the `services` array following the existing pattern:

```typescript
{
  slug: 'your-new-slug',
  icon: 'stethoscope',          // Lucide icon name
  priceFrom: 26,
  title: 'Service Title',
  hero: {
    headline: 'Your Headline Here',
    sub: 'Supporting sentence explaining the service.',
  },
  tabs: [
    { label: "What's Included", content: '...' },
    { label: 'How It Works',    content: '...' },
    { label: 'Why NurseMyGrade', content: '...' },
    { label: 'Qualifications',  content: '...' },
    { label: 'Pricing',         content: '...' },
    { label: 'FAQ',             content: '...' },
  ],
  relatedSlugs: ['nursing-essays', 'nursing-research-papers'],
  meta: {
    title: 'Service Title — BSN, MSN & DNP Writers | NurseMyGrade',
    description: '160-char meta description targeting the primary keyword.',
  },
}
```

3. Add the slug to `nitro.prerender.routes` in `nuxt.config.ts` so it is discovered at build time.
4. Run `pnpm build` — the page is immediately live.

### Option B — Wagtail CMS page (for rich editorial content)

1. Complete Option A first (establishes the route and static shell).
2. Log into Wagtail admin → **Pages → Services** → Add child of type **Service Page**.
3. Set the slug to match exactly what you added in `useServices.ts`.
4. Build the body with StreamField blocks — the `[slug].vue` template merges both sources automatically.
5. Publish + `pnpm build`.

---

## Services index page (`/services`)

`pages/services/index.vue` renders:

- A full 4-column grid of all 22 services with icon, title, price, and description
- A simulations section highlighting Shadow Health and iHuman specifically
- An embedded `OrderCalculator` for quote-before-browse conversion
- A nursing subject tags cloud (18 subjects: Med-Surg, Psych, Pediatrics, OB, ICU, etc.)
- A final CTA banner

The services index uses `getAllServices()` from `useServices.ts` — it returns the static catalogue array in definition order.

---

## Price calculator

The `OrderCalculator` and `SidebarCalculator` components both call `GET /api/v1/pricing/calculate/` with:

```
?service=:slug&pages=:n&deadline_hours=:h&level=:l
```

The backend returns a `{ price, deadline_at, writer_tier }` object. In dev, the API proxies to Django on `:8000`. In production, nginx routes this to the Django API.

The calculator is embedded in:
- The hero of `pages/index.vue`
- The hero of each service landing page
- `pages/services/index.vue` (below the grid)
- `pages/pricing.vue`
- `components/marketing/BlogSidebar.vue` (compact version)
