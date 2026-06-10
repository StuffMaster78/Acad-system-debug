# ResearchPaperMate — Marketing Site Documentation

This directory documents the public-facing marketing website at **researchpapermate.com**. The site is a Nuxt 3 static-site-generation (SSG) application that lives in `researchpapermate-web/` — separate from the portal (`frontend/`), which handles authenticated client, writer, and staff dashboards.

---

## Contents

| File | What it covers |
|------|---------------|
| [design-system.md](./design-system.md) | Brand colour rationale, full palette, typography, spacing, component primitives |
| [architecture.md](./architecture.md) | Nuxt 3 SSG setup, routing, data fetching, API proxy, build & deploy |
| [content-management.md](./content-management.md) | Wagtail CMS integration — blog posts, service pages, authors |
| [conversion-design.md](./conversion-design.md) | Competitor research findings, conversion patterns we adopted and improved on |

---

## Quick reference

```
researchpapermate-web/
├── pages/              # File-based routing (Nuxt)
│   ├── index.vue       # Home — hero, trust strip, services overview, CTA
│   ├── services/       # Service detail pages
│   ├── blog/           # Blog index + post detail
│   ├── pricing.vue
│   ├── order.vue
│   ├── about.vue
│   ├── apply.vue       # Writer application form
│   └── auth/           # Login, register, magic-link
├── components/
│   ├── marketing/      # Page-section components (hero, FAQ, testimonials…)
│   ├── cms/            # Wagtail block renderers
│   ├── ui/             # Design system primitives (Button, Icon…)
│   └── layout/         # Header, footer, nav
├── layouts/            # Default + minimal layouts
├── stores/             # Pinia stores (auth, cart, UI state)
├── composables/        # useApi, useMeta, useAnalytics…
├── assets/css/main.css # Global styles + @layer components
└── tailwind.config.ts  # Design tokens
```

## Running locally

```bash
cd researchpapermate-web
pnpm install
pnpm dev          # http://localhost:3000 — proxies /api/v1 and /api/v2 to Django on :8000
```

## Building for production

```bash
pnpm build        # SSG → .output/public/
```

The output is a fully static directory served by nginx. See [architecture.md](./architecture.md) for the nginx config and deployment pipeline.
