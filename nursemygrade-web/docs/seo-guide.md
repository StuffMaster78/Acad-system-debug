# SEO Guide

NurseMyGrade competes for high-value commercial keywords in a competitive niche (nursing writing services). SEO is not an afterthought — every page is structured to be fully crawlable, schema-annotated, and canonicalised at build time.

---

## Core approach: SSG = SEO foundation

The entire marketing site is statically generated. When Googlebot fetches any page, it receives complete HTML — no JavaScript required, no client-side rendering to wait for. This means:

- Content in `<h1>`, `<p>`, `<li>`, and structured data is immediately readable.
- Lighthouse Performance scores of 95+ are achievable on every page, which feeds into Core Web Vitals.
- Time-to-first-byte is under 20ms (static file from nginx/CDN) — well inside Google's threshold.

---

## Meta tags

Every page sets meta tags using Nuxt's `useSeoMeta` composable:

```typescript
useSeoMeta({
  title: 'Page Title — Brand | NurseMyGrade',
  description: '155–165 character meta description targeting the primary keyword.',
  ogTitle: 'Open Graph title (can differ from page title)',
  ogDescription: 'Open Graph description for social previews',
})
```

### Title format conventions

| Page type | Title pattern |
|-----------|--------------|
| Homepage | `Nursing Paper Writing Service — BSN, MSN & DNP Writers \| NurseMyGrade` |
| Service page | `[Service Name] — BSN, MSN & DNP Writers \| NurseMyGrade` |
| Blog post | `[Post Title] \| NurseMyGrade Blog` |
| Utility pages | `[Page Name] \| NurseMyGrade` |

The `— BSN, MSN & DNP Writers` qualifier appears on service pages because it targets the modifier students use to distinguish a credentialed service from generic mills. It also communicates the quality differentiator in the SERP snippet.

---

## Canonical URLs

Every page declares its canonical URL via `useHead`:

```typescript
useHead({
  link: [{ rel: 'canonical', href: 'https://nursemygrade.com/services/nursing-essays' }],
})
```

**Why this matters:** Nuxt SSG can generate a page at both `/services/nursing-essays` and `/services/nursing-essays/` (trailing slash variant). Without a canonical, Google may split ranking signals between both URLs. Every page locks its canonical to the non-trailing-slash form.

Service pages derive their canonical dynamically using `useRuntimeConfig().public.siteUrl`:

```typescript
const siteUrl = config.public.siteUrl || 'https://nursemygrade.com'
const canonicalUrl = `${siteUrl}/services/${route.params.slug}`
```

---

## Structured data (JSON-LD)

Structured data is injected via `useHead` script blocks. Each page type emits different schema payloads.

### Homepage — `ProfessionalService` + `Organization` + `AggregateRating`

```json
{
  "@context": "https://schema.org",
  "@type": ["ProfessionalService", "Organization"],
  "name": "NurseMyGrade",
  "description": "Nursing paper writing service staffed by BSN, MSN, and DNP credentialed nurses.",
  "url": "https://nursemygrade.com",
  "priceRange": "$24–$50 per page",
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.98",
    "reviewCount": "9800",
    "bestRating": "5"
  }
}
```

The `ProfessionalService` type (rather than just `Organization`) causes Google to show the star rating and price range in rich results for brand searches.

The homepage also emits an `FAQPage` schema for the nursing-specific FAQ accordion, and an `Organization` schema with social profile links.

### Service pages — `Service` + `FAQPage` + `BreadcrumbList`

```json
{
  "@context": "https://schema.org",
  "@type": "Service",
  "name": "Nursing Care Plan Writing Service",
  "provider": { "@type": "Organization", "name": "NurseMyGrade" },
  "offers": {
    "@type": "Offer",
    "price": 26,
    "priceCurrency": "USD",
    "priceSpecification": {
      "@type": "UnitPriceSpecification",
      "unitText": "page"
    }
  }
}
```

The `FAQPage` schema on service pages contains 4 universal nursing FAQs:
- How fast can you deliver?
- Are your writers real nurses?
- What if I need revisions?
- Is using a nursing writing service legal?

These target featured snippet slots for questions students type verbatim into Google.

### Blog posts — `Article` + `BreadcrumbList` (+ `FAQPage` when FAQ blocks present)

Blog posts emit `Article` schema with:
- `headline`, `description`, `image`, `datePublished`, `dateModified`
- `author` → `Person` with `jobTitle` and credentials
- `publisher` → `Organization` (NurseMyGrade)

When a blog post body contains 3 or more `faq` StreamField blocks, the frontend automatically emits a `FAQPage` schema alongside the `Article` schema.

---

## Breadcrumbs

The `<Breadcrumbs>` component (`components/ui/Breadcrumbs.vue`) renders two things simultaneously:

1. **Visual breadcrumb nav** — `Home > Services > Nursing Care Plan Writing Service`
2. **`BreadcrumbList` JSON-LD** — emitted inline within the component, not via `useHead`

```vue
<Breadcrumbs :items="[
  { label: 'Services', href: '/services' },
  { label: 'Nursing Care Plan Writing Service' },
]" />
```

`items` is an array of `{ label, href? }`. The last item (current page) has no `href`.

The component automatically prepends the Home crumb (`/`) so callers don't need to include it.

### JSON-LD output

```json
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    { "@type": "ListItem", "position": 1, "name": "Home", "item": "https://nursemygrade.com/" },
    { "@type": "ListItem", "position": 2, "name": "Services", "item": "https://nursemygrade.com/services" },
    { "@type": "ListItem", "position": 3, "name": "Nursing Care Plan Writing Service" }
  ]
}
```

Note: The last item intentionally omits `item` — Google accepts this and it prevents the current page from being treated as a link to itself.

---

## Sitemap

The sitemap is generated by `@nuxtjs/sitemap` (configured in `nuxt.config.ts`). It combines:

1. **Static routes** — all routes in the `pages/` directory
2. **Dynamic routes** — service slugs and blog slugs discovered via `server/api/_sitemap-urls.ts`

`server/api/_sitemap-urls.ts` calls the Wagtail API at build time to enumerate all published service pages and blog posts that have a URL and are not excluded from indexing:

```typescript
// Fetches slugs from Wagtail and returns them as sitemap URL objects
const [servicePages, blogPosts] = await Promise.all([
  $fetch('/api/v2/pages/?type=cms_service_pages.ServicePage&fields=slug'),
  $fetch('/api/v2/pages/?type=cms_blog.BlogPostPage&fields=slug,last_published_at'),
])
```

Each URL in the sitemap includes:
- `loc` — the full URL
- `lastmod` — ISO date from Wagtail `last_published_at` (blog) or today's date (services)
- `changefreq` — `monthly` for services, `weekly` for blog posts
- `priority` — `0.8` for services, `0.6` for blog posts

---

## Robots

`public/robots.txt` allows all crawlers on all paths. The portal routes (authenticated `/client/`, `/writer/`, `/staff/`) live on a separate domain and are not present in the marketing site's nginx config — so there is nothing to block here.

---

## Keyword strategy

The site targets three tiers of keywords:

### Tier 1 — High-intent transactional (service pages)

These are the money keywords. Each service page owns one:

| Keyword | Page |
|---------|------|
| nursing essay writing service | `/services/nursing-essays` |
| nursing care plan writing service | `/services/care-plans` |
| SOAP note writing service | `/services/soap-notes` |
| nursing capstone project help | `/services/capstone-projects` |
| buy nursing papers online | `/services/buy-nursing-papers` |
| Shadow Health DCE help | `/services/shadow-health` |
| iHuman virtual patient help | `/services/ihuman-patients` |

### Tier 2 — Informational (blog)

Blog posts target "how to write a SOAP note", "NANDA nursing diagnoses examples", "nursing capstone project ideas" — queries from students early in the research phase. These posts drive top-of-funnel traffic and feed into the order conversion path.

### Tier 3 — Brand + credential modifiers

Searches like "BSN nursing writers", "nurse-written essays", "DNP expert nursing papers" are targeted by the credential-heavy copy throughout the site (trust strip, writer showcase, writer cards, hero headlines).

---

## Performance and Core Web Vitals targets

| Metric | Target | Mechanism |
|--------|--------|-----------|
| LCP | < 1.8s | Static HTML, images with `loading="eager"` + `fetchpriority="high"` on hero |
| CLS | < 0.1 | Image dimensions explicit in `<img>` and Wagtail image wrappers |
| INP | < 200ms | Minimal JS on first paint; Vue hydration deferred for below-fold components |
| TTFB | < 200ms | Static nginx / CDN, no application server |

---

## Checking SEO health

```bash
# Run a Lighthouse audit against the local dev server
pnpm dev --port 3001
# In Chrome DevTools → Lighthouse → SEO + Performance

# Validate structured data
# Paste any page URL into: https://validator.schema.org/

# Inspect sitemap
curl http://localhost:3001/sitemap.xml
```
