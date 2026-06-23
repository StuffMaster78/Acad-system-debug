# Image Handling & Signals Playbook
### SEO · GEO · AEO · Social · Schema.org
> Covers all four sites: **NurseMyGrade**, **GradeCrest**, **EssayManiacs**, **ResearchPaperMate**

---

## 1 · How images flow (the pipeline)

```
Editor uploads in Wagtail admin
         │
         ▼
  Wagtail Image model (original stored in MEDIA_ROOT or S3)
         │
         ├─► get_rendition("fill-800x450|format-webp")  → .url  (WebP)
         └─► get_rendition("fill-800x450")              → .url  (JPEG/PNG fallback)
         │
         ▼
  Serializer returns { url, url_fallback, width, height, alt }
         │
         ▼
  BlockRenderer.vue / blog [slug].vue
         │
         ▼
  <picture>
    <source type="image/webp" :srcset="img.url" />
    <img :src="img.url_fallback" :width="img.width"
         :height="img.height" :alt="img.alt"
         decoding="async" loading="lazy" />
  </picture>
```

### Where renditions are requested (backend)

| File | Rendition spec | Used for |
|---|---|---|
| `cms_blog/serializers.py` | `fill-800x450\|format-webp` + fallback | Blog post featured image (list + detail) |
| `cms_blog/serializers.py` | `fill-1200x630\|format-webp` + fallback | `og:image` for blog post detail |
| `cms_service_pages/serializers.py` | `fill-800x600\|format-webp` + fallback | Service hero / thumbnail |
| `cms_core/blocks.py` | `fill-1200x630\|format-webp` + fallback | CMS image blocks inside body |
| `cms_authors/serializers.py` | `fill-200x200\|format-webp` + fallback | Author profile photo |
| `cms_authors/serializers.py` | `fill-400x400` | Author `schema:image` in JSON-LD |

### Frontend `<picture>` element (all four BlockRenderer.vue files)

- WebP `<source>` is first — modern browsers pick it.
- `<img>` fallback is JPEG/original — Safari <16, older Android.
- `width` and `height` are always set → prevents CLS (Cumulative Layout Shift).
- `decoding="async"` offloads decode from the main thread.
- `loading="lazy"` is set on body images; **hero images must NOT have lazy** (they are LCP candidates).

### Static / OG default images

Each site has a branded SVG at `public/og-default.svg` (1200×630) used when no
`featured_image` is attached to a page. It is served as a static asset and
should be converted to a real PNG for production — **SVGs are not reliably
rendered by all social crawlers and LLM scrapers**.

---

## 2 · Getting images onto the live sites

This is the main gap right now. The code is wired; the data is missing.

### 2a — For CMS blog posts & service pages moved from static to Wagtail

Every blog post and service page that was previously static (hardcoded in
`useBlog()` / `useServices()`) and has now been ported to Wagtail needs its
featured image uploaded manually in the Wagtail admin:

1. Go to **Wagtail admin → Images → Add an image**.
2. Upload the original full-resolution image (JPEG or PNG, ≥ 1200px wide).
3. Open the blog post / service page in the Wagtail page editor.
4. Set the **Featured image** field (or **Hero image** for service pages).
5. Publish.

Wagtail will auto-generate WebP renditions on first request and cache them.

### 2b — Media file storage on the live server

Wagtail images are stored under `MEDIA_ROOT` (default: `backend/media/`).
On a production server this must be one of:

| Option | When to use |
|---|---|
| **Local disk** with Nginx `location /media/` | Single-server, low traffic |
| **S3 + django-storages** (`DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'`) | Multi-server or CDN-backed |
| **DigitalOcean Spaces / Cloudflare R2** | Same as S3, different endpoint |

If you deployed and the images return 404, check:
- `MEDIA_URL` is set correctly in `.env.production`.
- Nginx has `location /media/ { alias /path/to/media/; }`.
- Or `AWS_S3_*` env vars are wired if using object storage.

### 2c — Author photos

Author photos follow the same path. After creating an Author record in
Wagtail admin, upload a headshot (≥ 400×400 px, square crop). The serializer
returns `fill-200x200|format-webp` for display and `fill-400x400` for
`schema:image` in JSON-LD.

### 2d — OG default SVG → PNG

The `og-default.svg` files in each site's `public/` folder are used as
fallback `og:image`. Convert each to a 1200×630 PNG before launch:

```bash
# requires librsvg or Inkscape on the server
rsvg-convert -w 1200 -h 630 public/og-default.svg -o public/og-default.png
# then update the ogImage path in the page composable from .svg → .png
```

Or use a design tool (Figma export, ImageMagick) — just replace the file and
update the reference.

---

## 3 · SEO signals — current state

### Meta tags

All four sites emit via `useSeoMeta()`:

| Signal | Set? | Notes |
|---|---|---|
| `<title>` | ✅ | Unique per page, ≤ 60 chars on key pages |
| `meta description` | ✅ | 150–160 chars on key pages |
| `og:title` | ✅ | Slightly punchier than title tag |
| `og:description` | ✅ | |
| `og:image` | ✅ | Falls back to `og-default.svg` if no hero |
| `og:image:width/height` | ⚠️ | Not set explicitly — add `ogImageWidth: 1200, ogImageHeight: 630` |
| `twitter:card` | ⚠️ | Not set — add `twitterCard: 'summary_large_image'` |
| `robots` | ✅ | Auth/login pages get `noindex, nofollow` |

### Canonical

Set via `useHead({ link: [{ rel: 'canonical', href: '...' }] })` on homepages
and service pages. Blog posts derive canonical from `page.url` returned by
Wagtail. **Verify every page has a canonical** — missing canonicals let
paginated or filtered URLs split PageRank.

### robots.txt — fixed this session

All four sites now have correct per-site `Sitemap:` lines. Previously NMG,
EM, and RPM all pointed to `researchpapermate.com/sitemap.xml`.

```
# Correct (each site)
Sitemap: https://<site-domain>/sitemap.xml
Disallow: /auth/
Disallow: /login
Disallow: /register
```

GradeCrest had no `robots.txt` at all — file created this session.

### Sitemap

Each Nuxt site should serve `/sitemap.xml`. Verify the sitemap module is
configured and includes:
- Homepage
- All `/services/[slug]` pages (dynamic → pre-rendered or SSR)
- All `/blog/[slug]` pages (dynamic → pre-rendered or SSR)
- Author pages (if public)

If using `@nuxtjs/sitemap`, the CMS pages need to be added via
`sitemaps.sources` fetching from the Wagtail API at build/SSR time.

---

## 4 · Schema.org JSON-LD — current state

### Homepage (NMG, EM, RPM — added this session; GradeCrest already had)

```json
Organization  @id: https://<site>/#org
  sameAs: [Trustpilot profile URL]
  contactPoint: { contactType: "customer support" }

WebSite  @id: https://<site>/#website
  publisher: { @id: .../#org }
  potentialAction: SearchAction (site search)

ProfessionalService  @id: https://<site>/#service
  aggregateRating: { ratingValue, reviewCount }
  priceRange
```

### Blog post pages (all four sites)

```json
Article / BlogPosting
  headline, description, datePublished, dateModified
  author: { @type: Person, ... }
  publisher: { @id: .../#org }
  image: { @type: ImageObject, url, width, height }
  speakable: { @type: SpeakableSpecification,
               cssSelector: [".post-excerpt", ".key-takeaways", "h1"] }
```

The `speakable` node is the primary **AEO signal** — it tells Google's voice
assistant and LLM-based engines which parts of the page to read aloud or
surface in audio summaries.

### Service pages

```json
BreadcrumbList  (NMG added this session; GradeCrest already had)
  Home → Services → [Service Name]
```

### Definition blocks (all four BlockRenderer.vue)

HTML microdata added to every `definition` block:

```html
<div itemscope itemtype="https://schema.org/DefinedTerm">
  <span itemprop="name">{{ term }}</span>
  <span itemprop="description">{{ definition }}</span>
  <span itemprop="disambiguatingDescription">{{ example }}</span>
</div>
```

---

## 5 · GEO signals (Generative Engine Optimization)

GEO targets LLM-based search surfaces (ChatGPT Search, Perplexity, Gemini,
Bing Copilot) that retrieve and cite web pages.

### What we have

| Signal | Status | Where |
|---|---|---|
| **E-E-A-T author markup** | ✅ | `AuthorSchemaOrgSerializer` emits credentials, degrees, sameAs (LinkedIn, ORCID, Google Scholar) |
| **Organization sameAs** | ✅ | Homepage JSON-LD `sameAs: [Trustpilot URL]` |
| **DefinedTerm microdata** | ✅ | Every definition block |
| **BreadcrumbList** | ✅ NMG + GradeCrest | EM + RPM still need it on service pages |
| **Speakable** | ✅ | Blog Article JSON-LD |
| **WebSite SearchAction** | ✅ | Homepage JSON-LD |
| **Aggregate rating** | ✅ | ProfessionalService on homepage |

### What's still missing (GEO gaps)

- **FAQ schema on service pages** — LLMs pull directly from FAQPage JSON-LD.
  Add a `FAQPage` node to each service page that has an accordion/FAQ section.
- **HowTo schema** — If a blog post describes a step-by-step process, wrap it
  in `HowTo` JSON-LD. Perplexity and ChatGPT Search surface these directly.
- **Cite-ready statistics** — LLMs prefer citing pages with specific numbers.
  The homepage stats (9,800+ papers, 4.98/5 rating) are good; add date context
  (`"as of [year]"`) so citations stay accurate.
- **EM + RPM BreadcrumbList on service pages** — missing (NMG added this
  session, GradeCrest had it).
- **`dateModified` on service pages** — GEO engines favour freshness; emit
  `dateModified` in the service page JSON-LD.

---

## 6 · AEO signals (Answer Engine Optimization)

AEO targets featured snippets, People Also Ask boxes, and voice answers.

### What we have

| Signal | Status |
|---|---|
| **Speakable** on blog posts | ✅ targets `.post-excerpt`, `.key-takeaways`, `h1` |
| **DefinedTerm** on definition blocks | ✅ |
| **Structured headings** (H2/H3 hierarchy) | ✅ enforced via BlockRenderer |
| **Table of contents** with anchor IDs | ✅ (`extractToc` + `slugifyHeading`) |

### What's still missing (AEO gaps)

- **FAQPage JSON-LD** on service pages — the single biggest AEO win.
  Add a `FAQPage` block type in Wagtail + render as JSON-LD. Google uses
  this for PAA boxes; Bing Copilot uses it for direct answers.
- **Q&A structured content** in blog posts — posts that answer a question
  should open with a direct 40–60 word answer immediately below H1 (the
  "position zero" paragraph). This is editorial, not a code change.
- **`@type: QAPage`** — for blog posts formatted as "What is X?" / "How
  do I Y?" pages, change the Article type to QAPage to get PAA eligibility.
- **Speakable on service pages** — currently only on blog posts. Add
  `SpeakableSpecification` targeting the hero description and key benefit
  bullets on service pages too.

---

## 7 · Social / OGP signals

### Open Graph

All four sites emit `og:title`, `og:description`, `og:image` via
`useSeoMeta()`. Gaps:

```ts
// Add to every page's useSeoMeta call:
ogImageWidth: 1200,
ogImageHeight: 630,
ogType: 'website',       // or 'article' on blog posts
twitterCard: 'summary_large_image',
twitterSite: '@<handle>',  // if you have brand Twitter accounts
```

### WhatsApp / Telegram / iMessage

These use OGP. The `og:image` must be an absolute URL (not root-relative).
Currently the fallback is `/og-default.svg` — it must be
`https://<site>/og-default.png`. Fix: use `useHead` with the full URL:

```ts
useHead({
  meta: [
    { property: 'og:image', content: `https://${host}/og-default.png` },
  ],
})
```

---

## 8 · Quick-reference checklist for each new page

- [ ] `useSeoMeta` with `title`, `description`, `ogTitle`, `ogDescription`, `ogImage` (absolute URL), `ogImageWidth: 1200`, `ogImageHeight: 630`, `twitterCard: 'summary_large_image'`
- [ ] `canonical` in `useHead`
- [ ] At least one JSON-LD node (Article for blog, ProfessionalService or FAQPage for service)
- [ ] Featured image uploaded in Wagtail (≥ 1200px wide)
- [ ] Hero `<img>` does **not** have `loading="lazy"` (it's LCP)
- [ ] All body images have explicit `width` + `height` (CLS prevention)
- [ ] Page is included in `sitemap.xml`
- [ ] Page is **not** blocked by `robots.txt` (unless it should be)

---

## 9 · Open tasks (priority order)

| # | Task | Who | Effort |
|---|---|---|---|
| 1 | Convert `og-default.svg` → `og-default.png` on all four sites | Dev | 30 min |
| 2 | Add `ogImageWidth`, `ogImageHeight`, `twitterCard` to all `useSeoMeta` calls | Dev | 1 hr |
| 3 | Upload featured images for all ported blog posts + service pages in Wagtail admin | Content | Per post |
| 4 | Add `FAQPage` JSON-LD to service pages that have FAQ sections | Dev | 2 hr |
| 5 | Add BreadcrumbList to EM + RPM service pages (NMG done, GradeCrest done) | Dev | 1 hr |
| 6 | Add `speakable` to service pages (currently only on blog posts) | Dev | 1 hr |
| 7 | Configure Wagtail sitemap module to pull CMS pages dynamically | Dev | 2 hr |
| 8 | Configure media storage (S3/Spaces) and `MEDIA_URL` on production | DevOps | Half-day |
| 9 | Add `HowTo` JSON-LD to step-by-step blog posts | Dev | 2 hr |
| 10 | Add `dateModified` to service page JSON-LD | Dev | 30 min |
