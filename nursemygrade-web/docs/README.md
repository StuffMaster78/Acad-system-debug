# NurseMyGrade — Marketing Site Documentation

This directory documents the public-facing marketing website at **nursemygrade.com**. The site is a Nuxt 3 SSG application living in `nursemygrade-web/` — separate from the authenticated portal (client, writer, and staff dashboards) which lives in `frontend/`.

---

## Contents

| File | What it covers |
|------|---------------|
| [design-system.md](./design-system.md) | Teal brand palette, typography, spacing, Tailwind config, component primitives |
| [architecture.md](./architecture.md) | Nuxt 3 SSG setup, routing, composables, API proxy, build & deploy |
| [content-management.md](./content-management.md) | Wagtail CMS integration — how staff add service page content, blog posts, authors |
| [services-guide.md](./services-guide.md) | The 24 service landing pages — how they work, how to add new ones |
| [seo-guide.md](./seo-guide.md) | Breadcrumbs, canonical URLs, JSON-LD schemas, sitemap configuration |
| [conversion-design.md](./conversion-design.md) | Competitor research, conversion patterns adopted, homepage architecture |

---

## Project at a glance

```
nursemygrade-web/
├── pages/
│   ├── index.vue              # Homepage — hero, service strip, pillars, tabs, FAQ, CTA
│   ├── services/
│   │   ├── index.vue          # All 24 services + simulations + calculator
│   │   └── [slug].vue         # Individual service landing page (tabbed + editorial)
│   ├── blog/
│   │   ├── index.vue          # Blog listing with sidebar
│   │   └── [slug].vue         # Blog article with inline CTA
│   ├── order.vue              # 3-step nursing paper order form
│   ├── quote.vue              # Custom quote form (Shadow Health, iHuman, special)
│   ├── class-support.vue      # Full online class help form
│   ├── pricing.vue
│   ├── about.vue
│   ├── apply.vue              # Writer application (BSN/MSN/DNP)
│   ├── contact.vue
│   └── auth/
├── components/
│   ├── marketing/
│   │   ├── AnnouncementBar.vue    # Dismissible promo bar (NURSE15 code)
│   │   ├── TrustBadges.vue        # 4.98★ · 500+ nurses · 9,800+ papers
│   │   ├── WriterShowcase.vue     # 6 nurse writer cards (BSN/MSN/DNP)
│   │   ├── HomeFaq.vue            # Nursing-specific FAQ accordion
│   │   ├── NursingContentTabs.vue # 6-tab deep content (Leading Service, Why Us…)
│   │   ├── WritingServicesGrid.vue# 24 service links + calculator + CTA
│   │   ├── OrderCalculator.vue    # Full price calculator (hero embed)
│   │   ├── SidebarCalculator.vue  # Compact sidebar calculator
│   │   ├── BlogSidebar.vue        # Blog sidebar (calc + service links)
│   │   ├── TestimonialsSection.vue
│   │   └── WhatsAppButton.vue     # Floating WhatsApp CTA
│   ├── cms/                       # Wagtail StreamField block renderers
│   ├── ui/
│   │   ├── Icon.vue               # Inline SVG icon library (Lucide paths)
│   │   └── Breadcrumbs.vue        # Breadcrumb nav + BreadcrumbList JSON-LD
│   └── layout/
│       ├── SiteHeader.vue         # Sticky header + mega-menu (4-col nursing services)
│       └── SiteFooter.vue         # 8-col sectioned footer
├── composables/
│   ├── useServices.ts             # 22 nursing service definitions (static + CMS merge)
│   ├── useBlog.ts                 # Blog posts + 4 nursing author profiles
│   ├── useOrderForm.ts            # Nursing-specific order form data
│   ├── useApi.ts                  # Authenticated API client
│   ├── useAppUrl.ts               # Portal URL builder
│   ├── useToc.ts                  # Blog article TOC generator
│   └── useServiceCms.ts           # Wagtail service page fetcher
├── server/api/
│   └── _sitemap-urls.ts           # Dynamic sitemap URL source
├── assets/css/main.css            # Global styles + animations
└── tailwind.config.ts             # Teal brand palette
```

---

## Running locally

```bash
cd nursemygrade-web
pnpm install
pnpm dev --port 3001   # http://localhost:3001
                        # Proxies /api/v1, /api/v2, /cms-api → Django on :8000
```

> **Note:** In dev the Django backend returns the dev-seeded tenant ("WritePro Dev").  
> The logo and brand colours are hardcoded in the frontend so the site looks correct regardless.  
> Connect the nursemygrade.com Website record in Django admin to fully activate the portal store.

## Building for production

```bash
pnpm build    # SSG → .output/public/
```

All 22 service slugs, blog posts, and author pages are pre-rendered at build time. Dynamic routes (new Wagtail pages) are discovered via `crawlLinks: true` and the `/api/_sitemap-urls` server route.
