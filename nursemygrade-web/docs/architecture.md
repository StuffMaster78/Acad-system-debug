# Architecture

## Why Nuxt 3 + SSG

The marketing site is built with **Nuxt 3** compiled to a **static site** (SSG). The choice of SSG over SSR or CSR was deliberate:

| Concern | SSG answer |
|---|---|
| SEO | Pages are pre-rendered HTML at build time — crawlers get full content instantly, no JavaScript required |
| Performance | Zero server compute per request; pages served directly from nginx/CDN with sub-20ms TTFB |
| Academic content indexing | Blog posts and service pages need to rank for competitive keywords. SSG guarantees they are fully crawlable |
| Cost | Static hosting is free or near-free at any scale |
| Reliability | No application server to fail — a static directory survives traffic spikes without configuration |

The portal (`frontend/`) uses CSR (Vue 3 SPA) because it's authenticated, personalized, and never indexed by search engines. The marketing site has the opposite requirements.

---

## Nuxt 3 setup

```
nuxt.config.ts
├── modules: @nuxtjs/tailwindcss, @pinia/nuxt
├── nitro.prerender.routes  — explicit route list for SSG crawl
├── nitro.devProxy          — /api/v1 and /api/v2 → localhost:8000 in dev
└── runtimeConfig.public    — apiBase, appUrl, siteUrl
```

### Pre-rendered routes

`nuxt.config.ts` lists every route explicitly in `nitro.prerender.routes`. This is required for routes that are not linked from the homepage (e.g., individual service pages). At build time Nuxt visits each route, renders it to HTML, and writes the file.

Dynamic routes (blog post slugs, individual service pages) are discovered via `crawlLinks: true` — Nuxt follows all `<a>` tags from the pre-rendered pages to find additional routes.

### API proxy in dev

In development the Nuxt dev server proxies `/api/v1/*` and `/api/v2/*` to Django on `:8000` **without** rewriting the `Host` header. This is critical: Django's multi-tenant resolver reads `Host: localhost:3000` to identify the `Website` record (seeded for local dev). If the proxy rewrites the host, Django would return 404 or the wrong tenant's data.

In production this proxy is not used — nginx routes API requests directly:

```
researchpapermate.com/api/v1/*  →  api.researchpapermate.com (Django)
researchpapermate.com/api/v2/*  →  api.researchpapermate.com (Wagtail)
researchpapermate.com/*         →  .output/public/ (static files)
```

---

## Routing

Nuxt file-based routing maps the `pages/` directory:

```
pages/
├── index.vue                     GET /
├── services/
│   ├── index.vue                 GET /services
│   ├── [slug].vue                GET /services/:slug  (dynamic, SSG via crawl)
├── blog/
│   ├── index.vue                 GET /blog
│   └── [slug].vue                GET /blog/:slug
├── pricing.vue                   GET /pricing
├── order.vue                     GET /order
├── quote.vue                     GET /quote
├── class-support.vue             GET /class-support
├── about.vue                     GET /about
├── contact.vue                   GET /contact
├── apply.vue                     GET /apply
├── auth/
│   ├── magic-link.vue            GET /auth/magic-link
├── login.vue                     GET /login
├── register.vue                  GET /register
├── privacy.vue                   GET /privacy
├── terms.vue                     GET /terms
└── refunds.vue                   GET /refunds
```

---

## Layouts

```
layouts/
├── default.vue   — Header + main + footer (used by all marketing pages)
└── minimal.vue   — Header only (used for auth pages: login, register)
```

---

## Data fetching

All API calls use `useFetch` or `useAsyncData` (Nuxt composables that run during SSG, so the data is baked into the HTML):

```typescript
// Service page — data fetched at build time
const { data } = await useFetch(`/api/v2/pages/`, {
  params: { type: 'cms_service_pages.ServicePage', slug: route.params.slug, fields: '...' }
})
```

At runtime in the browser, Nuxt hydrates the page using the already-rendered HTML — API calls are not repeated on first load. This is the core SSG performance advantage.

For interactive features that need live data (pricing calculator, writer availability), `$fetch` is used on the client side after hydration.

---

## Component organisation

```
components/
├── layout/     Header.vue, Footer.vue, MobileNav.vue
├── marketing/  Page-section components
│   ├── AnnouncementBar.vue   — Top-of-page promotional banner
│   ├── BlogSidebar.vue       — Sidebar for blog posts (related, tags)
│   ├── HomeFaq.vue           — Accordion FAQ on the home page
│   ├── OrderCalculator.vue   — Inline pricing calculator (home, pricing pages)
│   ├── SidebarCalculator.vue — Sticky sidebar calculator on service pages
│   ├── TestimonialsSection.vue
│   ├── TrustBadges.vue       — "50,000+ orders", "4.9★", "On-time" badges
│   ├── WhatsAppButton.vue    — Floating WhatsApp CTA
│   └── WriterShowcase.vue    — Sample writer profiles for social proof
├── cms/        Wagtail StreamField block renderers (see content-management.md)
└── ui/
    └── Icon.vue              — Thin wrapper around the icon system
```

---

## Stores

Pinia stores (`stores/`) handle client-side state:

| Store | Purpose |
|---|---|
| `auth` | JWT tokens, user profile, login/logout |
| `ui` | Mobile menu open/closed, modal state |
| `cart` / `order` | Order configuration state across the quote → order flow |

Stores that contain sensitive state (auth tokens) are hydrated from `localStorage` on mount, not from SSG — this prevents the server from baking user-specific state into static files.

---

## Build output

```bash
pnpm build
```

Outputs to `.output/public/` — a directory of static HTML, CSS, JS, and assets. The nginx config in `nginx/` serves this directory.

Key nginx behaviours:
- All `.html` files served with `Cache-Control: no-cache` (so deploys are picked up immediately)
- Static assets (`_nuxt/`, `public/`) served with `Cache-Control: max-age=31536000, immutable` (content-hashed filenames)
- `try_files $uri $uri.html $uri/ =404` — handles clean URLs without `.html` extension
- API proxy in production handled by a separate upstream block to `api.researchpapermate.com`
