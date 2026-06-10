# Content Management

All editorial content — blog posts, service pages, author profiles — is managed through **Wagtail CMS** on the Django backend and consumed by the marketing site via the **Wagtail API v2**.

This means editors never touch the frontend codebase to publish content. They log into the Wagtail admin (`/cms-admin/`) and the site regenerates (or hydrates) automatically.

---

## Content types

### Blog posts (`cms_blog.BlogPostPage`)

Fetched at `/api/v2/pages/?type=cms_blog.BlogPostPage`.

Key fields:

| Field | Description |
|---|---|
| `title` | Article headline |
| `excerpt` | 1–2 sentence summary (used in listing cards and meta description) |
| `featured_image` | Hero image |
| `primary_author` | FK to Author snippet — see Authors below |
| `contributing_authors` | M2M to Author — credited but not primary |
| `reviewer` | FK to Author — the expert who reviewed the article for accuracy |
| `body` | StreamField — see Block library below |
| `category` | Taxonomy grouping |
| `tags` | Many-to-many for cross-cutting topics |
| `citation_mode` | How references are displayed (`sources_list`, `formal_apa7`, `formal_mla9`, `formal_chicago`, `none`) |
| `last_substantive_update` | Manually set when content is meaningfully changed |
| `original_published_at` | **For content migration only** — overrides the display date if the article existed on a previous site |
| `canonical_published_at` | Computed: returns `original_published_at` if set, else `first_published_at` |

#### Content migration

When importing articles from another site, the editor sets `original_published_at` to the article's real first-published date. This field overrides Wagtail's automatic `first_published_at` everywhere it is displayed — in the article header, Schema.org `datePublished`, and the revision history timeline. The `original_source_url` field records where the content came from (internal records only, not displayed publicly).

---

### Service pages (`cms_service_pages.ServicePage`)

Fetched at `/api/v2/pages/?type=cms_service_pages.ServicePage`.

Each service page represents one monetized offering (essays, dissertations, etc.). Key fields beyond title/body:

| Field | Description |
|---|---|
| `service_category` | Grouping for the services listing filter |
| `pricing_from` | Lowest price per page shown in the listing card |
| `turnaround_hours_fastest` | Fastest delivery shown in the listing card |
| `primary_cta_text` / `primary_cta_url` | The sticky bottom bar CTA |
| `reviewer` | Expert who reviewed the page |
| `body` | StreamField with service-page-specific blocks |

---

### Authors (`cms_authors.Author`)

Fetched at `/cms-api/authors/` and `/cms-api/authors/:slug/`.

Authors are Wagtail Snippets (not Pages) — they don't have their own URL in Wagtail, but the marketing site gives them a profile page at `/authors/:slug`.

| Field | Description |
|---|---|
| `name`, `slug` | Identity |
| `profile_photo` | Wagtail image (rendered at `fill-200x200`) |
| `bio` | 2–4 sentence professional biography |
| `credentials` | Degree abbreviations, e.g. "PhD, MA" |
| `degrees` | JSON array: `[{degree, institution, year, verified}]` |
| `licenses` | JSON array: `[{license, state, number, expires}]` |
| `role` | `writer`, `senior_writer`, `editor`, `subject_matter_expert`, `clinical_reviewer` |
| `areas_of_expertise` | Plain text summary |
| `years_experience` | Integer |
| `linkedin_url`, `orcid_id`, `google_scholar_url`, `twitter_handle`, `personal_website` | External profiles |
| `show_publicly` | Whether the author appears in the public `/authors` listing |

ORCID and Google Scholar IDs are treated as **verified credential signals** — they are displayed with distinct coloured pills (ORCID green, Scholar blue) to signal that the author's academic identity is verifiable by a third party.

---

## Blog features

### Author card (on blog posts)

Every blog post renders a full author card after the article body:

- Large avatar with a green verified badge if ORCID or Google Scholar is linked
- Role badge with per-role colour (Senior Writer = brand blue, Editor = violet, Subject Expert = amber, Clinical Reviewer = emerald)
- Credentials + years of experience
- Bio paragraph
- Social links (LinkedIn, Twitter, ORCID, Google Scholar, website)
- "More by [Author]" strip — fetches up to 3 recent articles from `/cms-api/authors/:slug/posts/`

Contributing authors appear in a compact row of linked cards below the primary author.

### Editorial process section

Below the author card, every blog post displays a transparent 5-step editorial timeline:

1. **Topic identified** — from reader requests or keyword research
2. **Research & writing** — by a credentialed author with subject expertise
3. **Editorial review** — by a senior editor; the reviewer's name and credentials are shown if the `reviewer` field is set
4. **Published** — with the canonical publication date
5. **Tracked & updated** — with the last update date

A "Written by humans, not AI" badge appears in the header of this section. The footer contains a plain-language no-AI commitment statement.

### Revision history

A collapsible accordion below the editorial section shows:

- First published date (using `canonical_published_at`)
- Content update date (if `last_substantive_update` is set)
- "Reviewed & verified" entry (if the latest Wagtail revision is significantly newer)
- Editorial save count as a quality signal ("12 editorial saves")

The revision data comes from `GET /cms-api/blog/:id/history/`.

### Engagement

Article engagement is tracked via the `cms_engagement` app:

| Feature | API endpoint |
|---|---|
| View tracking | `POST /cms-api/engagement/track-view/` |
| Reactions (👍 ❤️ 💡 👎) | `POST /cms-api/engagement/react/` |
| Bookmarks | `POST /cms-api/engagement/bookmark/` |
| Share tracking | `POST /cms-api/engagement/share/` |
| Summary (views, reactions, shares) | `GET /cms-api/engagement/page/?page_id=` |

### Social sharing

Share buttons are rendered for: X/Twitter, Facebook, LinkedIn, Reddit, WhatsApp, Telegram, Email, Copy Link. On mobile browsers that support the Web Share API (`navigator.share`), a native "Share" button appears that opens the OS share sheet.

Platform share URLs:

| Platform | URL pattern |
|---|---|
| X/Twitter | `twitter.com/intent/tweet?text={title}&url={url}` |
| Facebook | `facebook.com/sharer/sharer.php?u={url}` |
| LinkedIn | `linkedin.com/sharing/share-offsite/?url={url}` |
| Reddit | `reddit.com/submit?url={url}&title={title}` |
| WhatsApp | `wa.me/?text={title} {url}` |
| Telegram | `t.me/share/url?url={url}&text={title}` |
| Email | `mailto:?subject={title}&body={url}` |

---

## Block library

The blog post and service page `body` fields are Wagtail StreamFields. The frontend renders each block type via `BlockRenderer.vue`. Available block types:

### Shared (blog + service pages)

| Block | Description |
|---|---|
| `heading` | H2/H3/H4 with auto-generated anchor ID for TOC |
| `paragraph` | Rich text |
| `image` | Image with required alt text |
| `list` | Bulleted or numbered |
| `callout` | Info/tip/warning/important box |
| `faq` | Accordion FAQ item (emits FAQPage Schema.org when 3+ present) |
| `cta` | Call-to-action button (primary/secondary/outline) |
| `stats_highlight` | Row of headline stats (e.g. "98% on-time delivery") |
| `checklist` | Action checklist with optional per-item detail |
| `before_after` | Side-by-side writing comparison |
| `key_takeaways` | Highlighted summary box (green, frequently pulled as featured snippet) |
| `toc` | Manual table of contents with anchor links |
| `timeline` | Vertical event timeline |
| `definition` | Inline term definition with Schema.org DefinedTerm |
| `author_review` | Expert review attribution badge |
| `disclaimer` | Academic integrity / medical / copyright notice |
| `table` | Editable data table (Handsontable in Wagtail admin) |
| `chart` | Bar/line/pie/doughnut chart via ECharts |
| `embed` | Sandboxed iframe (Google Sheets/Docs, Tableau, Flourish, Datawrapper, Canva) |
| `calculator` | Inline pricing calculator (live API, Vue component) |
| `divider` | `<hr>` section break |
| `video` | YouTube/Vimeo embed |

### Blog-only

| Block | Description |
|---|---|
| `sources` | "Articles Consulted" / references list |
| `related_posts` | Curated list of related blog posts |
| `code` | Code or citation sample block |
| `sample_excerpt` | Styled paper excerpt with downloadable sample link |

### Service-page-only

| Block | Description |
|---|---|
| `hero` | Full-width hero with CTA |
| `trust_strip` | Rating + reviews + experience bar |
| `feature_grid` | "What You Get" feature highlights |
| `how_it_works` | Numbered process steps |
| `pricing_table` | Service pricing display |
| `comparison_table` | Us vs. competitors |
| `testimonials` | Customer quotes with star ratings |
| `guarantees` | Money-back, on-time, plagiarism-free guarantee cards |
| `benefits_section` | Pre-CTA section: heading + bullet benefits + scrollable trust badge strip |

---

## Adding new content

### Publishing a blog post

1. Log into Wagtail admin (`/cms-admin/`)
2. Navigate to **Pages → Blog**
3. Add a child page of type **Blog Post**
4. Fill in: title, excerpt, featured image, primary author, category
5. Write the body using StreamField blocks
6. Set `reviewer` if an expert reviewed the article
7. If migrating content: set `original_published_at` and `original_source_url`
8. Promote → Publish

The article is live immediately on the SSR portal. For the SSG marketing site, a rebuild (`pnpm build`) is required to bake new posts into static HTML.

### Adding a service page

1. Wagtail admin → **Pages → Services**
2. Add child page of type **Service Page**
3. Fill in service details, pricing, turnaround, CTA text/URL
4. Build the body with StreamField blocks (recommended: Hero → How It Works → Benefits Section → FAQ → CTA)
5. Publish + rebuild

### Adding an author

1. Wagtail admin → **Snippets → Authors**
2. Fill in all fields — name, bio, credentials, degrees, social links
3. Set `show_publicly: true`
4. Save — the author is immediately available in the API and appears on `/authors`
