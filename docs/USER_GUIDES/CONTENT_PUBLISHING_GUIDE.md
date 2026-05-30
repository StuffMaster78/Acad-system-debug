# Content Publishing Guide

**Audience:** Editors, Admins, Support staff  
**Last Updated:** May 2026

---

## Overview

The platform has two publishing systems working in parallel:

| System | Best for | Accessed via |
|---|---|---|
| **Wagtail CMS** | Rich editorial content (blog posts, service pages) with revisions, previews, approval workflows, and media management | `/cms-admin/` |
| **Publishing Desk** | Fast SEO landing pages and static pages managed through the API | `/admin/publishing` and `/admin/content` |

Use the **Publishing Desk** (`/admin/publishing`) as your daily status board — it shows everything across both systems in one place.

---

## Quick Reference — What Lives Where

| Content type | Where to create | Public URL | Who can create |
|---|---|---|---|
| Blog post | Wagtail `/cms-admin/` | `/blog/<slug>` | Editor, Admin |
| Service page | Wagtail `/cms-admin/` | `/services/<slug>` | Editor, Admin |
| SEO landing page | Publishing Desk `/admin/publishing` | `/lp/<slug>` | Admin, Editor, Support |
| Static page (About, Contact, etc.) | Content Management `/admin/content` | `/lp/<slug>` | Admin, Editor, Support |
| Help article | Content Management `/admin/content` | `/help/articles/<slug>` | Admin, Editor, Support |
| Legal document | Content Management `/admin/content` | `/legal/<type>` | Admin, Superadmin |

---

## Part 1 — Blog Posts (Wagtail)

### Prerequisites (one-time setup)

Before publishing the first blog post, create the supporting objects in Wagtail. Go to `/cms-admin/` → **Snippets**:

**Authors** (`Snippets → Authors`)

Create a profile for every writer. Required fields:

- Name, slug, bio
- Credentials (e.g. "MSN, RN — 8 years clinical experience")
- Degrees (JSON array — e.g. `["BSN, University of Nairobi", "MSN, USIU"]`)
- Areas of expertise
- Profile photo
- Optional: ORCID ID, Google Scholar URL, LinkedIn URL

Every blog post must have at least one author. These fields power the **Schema.org Person** markup and the author bio card at the bottom of each post.

**Blog categories** (`Snippets → Blog categories`)

Topic groupings shown as filter badges on the public blog index. Examples:
- Essay Writing
- APA Formatting
- Research Papers
- Nursing Care Plans

**Blog tags** (`Snippets → Blog tags`)

More granular keywords. Tags appear as pill links at the bottom of each post.

**Service categories** (`Snippets → Service categories`)

Categories used on service pages (not blog posts). Create these before building service pages.

---

### Writing a blog post

**Step 1 — Navigate to the Blog page tree**

Go to `/cms-admin/pages/` → find your site's home page (named after your site, e.g. "GradeCrest Home") → click to open it → open the **Blog** page inside it.

**Step 2 — Create the post**

Click **Add child page → Blog Post Page**.

**Core fields:**

| Field | What to fill in |
|---|---|
| **Title** | Becomes the H1 and SERP title. Write for search intent, not cleverness. |
| **Primary author** | Mandatory. Drives Schema.org authorship and the author bio card shown at the bottom of each post. |
| **Featured image** | Displays in the blog index card grid and in Open Graph / Twitter Card previews. |
| **Excerpt** | 1–2 sentence summary used as the meta description. Keep under 160 characters. |
| **Category** | Pick one Blog category. |
| **Tags** | Add relevant tags — readers can filter by these. |

**SEO and funnel fields** (in the Promotions or SEO tab):

| Field | What to fill in |
|---|---|
| **Primary service** | The service page this post should funnel readers toward. Required for Content Graph attribution. |
| **Content pillar** | The topic cluster this post belongs to. Determines which funnel it feeds. |
| **Citation mode** | How references render at the bottom of the post: APA 7 / MLA 9 / Chicago / Simple sources list / None. |
| **Last substantive update** | Date of the last meaningful content refresh (not typo fixes). Used for freshness alerts. |

**Step 3 — Write the body**

The body is a **StreamField** — click the `+` button to add blocks:

| Block | Use it for |
|---|---|
| **Heading** | H2 / H3 / H4 section headings |
| **Paragraph** | Rich text — supports bold, italic, links |
| **Image** | Full-width image with optional caption |
| **Quote** | Pull quote with attribution |
| **Callout** | Info / warning / success / danger highlighted box |
| **FAQ** | Expandable question/answer accordion |
| **CTA** | Call-to-action button with subtext |
| **Sources list** | Simple numbered reference list |
| **Code** | Code block with syntax label |
| **Divider** | Horizontal rule between sections |

> **Paste shortcut:** If you have existing content in a Word doc or web page, copy it and use the **Paste** tool at `/cms-api/paste/` to convert it into StreamField blocks automatically. This strips Office formatting and maps headings, paragraphs, and lists to the correct block types.

**Step 4 — Internal links (important for SEO)**

Every post should link to at least 2 other internal pages. Use the **Link suggestions** tool in the Publishing Desk sidebar — enter the Wagtail page ID and get ranked suggestions based on the content pillar, category, and semantic similarity.

**Step 5 — Pre-publish validation**

Wagtail runs automatic checks before publishing. It will **warn** you if:

- No primary service is linked (post won't contribute to any funnel)
- Fewer than 2 internal links
- No link back to the pillar's hub post

**Blockers** (must be fixed before publishing):
- Missing required fields
- Slug already in use on this site

**Step 6 — Publish**

At the bottom of the editor:

- **Save draft** — saves without publishing (use during writing)
- **Publish** — makes the post live immediately
- **Set schedule → go-live date** — schedules publish for a future date/time

Once live, the post appears at `/blog/<slug>` and is indexed in the blog listing page.

---

## Part 2 — Service Pages (Wagtail)

Service pages follow the same Wagtail flow as blog posts but use different fields and blocks.

**Navigate:** `/cms-admin/pages/` → Your site home → **Services** → **Add child page → Service Page**

**Key fields for service pages:**

| Field | Notes |
|---|---|
| **Service category** | Groups the service in the public listing |
| **Pricing from / to** | Shown on listing cards and in Schema.org structured data |
| **Turnaround hours fastest** | e.g. `3` for "from 3 hours" |
| **Turnaround hours standard** | Standard delivery window |
| **Primary CTA text** | The label on the sticky bottom bar button — e.g. "Order now" |
| **Primary CTA URL** | Where the button goes — typically `/auth/register` or `/client/new-order` |
| **Reviewer** | Expert who reviewed this page. Appears in the reviewer card and Schema.org markup. |
| **Show aggregate rating** | Toggle to display star ratings from the reviews system |

**Service page body blocks:**

| Block | Use it for |
|---|---|
| **Hero** | Full-width banner with heading, subheading, and CTA button |
| **Trust strip** | Row of trust badges/guarantees ("100% original", "On-time delivery") |
| **Feature grid** | Cards explaining key features with icons |
| **How it works** | Numbered step-by-step process |
| **Pricing table** | Pages/prices/turnaround comparison table |
| **Comparison table** | Us vs. competitors feature comparison |
| **Testimonials** | Star-rated quote cards |
| **Guarantees** | Green checkmark guarantee panels |
| Plus all shared blocks | Heading, Paragraph, Image, Quote, Callout, FAQ, CTA, Divider |

Once live, the page appears at `/services/<slug>`.

---

## Part 3 — SEO Landing Pages (Publishing Desk)

SEO landing pages are lightweight structured pages ideal for high-volume keyword targeting. They're managed entirely through the platform admin — no Wagtail access needed.

**Go to:** `/admin/publishing` → click **+ New page** (top-right)

**Step 1 — Select content type**

On the slide-over panel, select **SEO landing page** from the three content type cards.

**Step 2 — Fill in the fields**

| Field | Notes |
|---|---|
| **Title** | Page heading |
| **URL slug** | The `/lp/<slug>` path. Use hyphens, no spaces. |
| **Meta description** | 150–160 chars for search results |
| **Schedule publish** | Optional. Leave blank to publish immediately. |

**Step 3 — Publish**

- **Save as draft** — saves without publishing
- **Publish now** — makes the page live at `/lp/<slug>` immediately

**To unpublish:** find the page in the Publishing Desk table and click **Unpublish** on hover.

> **Note:** SEO pages created here store a simple paragraph body. For richer SEO pages with Hero blocks, FAQ sections, CTAs, and pricing tables, use the **Static pages** tab in Content Management instead (see Part 4).

---

## Part 4 — Static Pages (Content Management)

Static pages are for general informational content — About Us, Contact, Careers, FAQ, custom landing pages. They use the full WYSIWYG editor and publish at `/lp/<slug>`.

**Go to:** `/admin/content` → **Static pages** tab → click **+ New page**

**Fields:**

| Field | Notes |
|---|---|
| **Page title** | Shown as the main heading |
| **URL slug** | `/lp/<slug>` — must be unique |
| **SEO title** | Optional — defaults to page title if blank |
| **Meta description** | 160 chars max |
| **Schedule publish** | Optional datetime picker |
| **Page content** | Full WYSIWYG editor — headings, paragraphs, lists, blockquotes, links, bold/italic |

**Actions:**
- **Save as draft** — invisible to the public
- **Publish now** — live immediately at `/lp/<slug>`
- **Publish / Unpublish toggle** — switch status from the page list

---

## Part 5 — Help Articles (Content Management)

Help articles appear in the public Help Center at `/help`.

**Go to:** `/admin/content` → **Help center** tab

**Step 1 — Create a category (if needed)**

In the left panel, click **+ Add**. Fill in:
- **Title** and **Slug**
- **Icon** — a Lucide icon name (e.g. `credit-card`, `file-text`, `help-circle`)
- **Audience** — All users / Clients / Writers / Staff
- **Order** — controls display order on the Help Center home

**Step 2 — Create an article**

Click **+ New article** in the right panel. Fill in:

| Field | Notes |
|---|---|
| **Title** | Shown as the article heading |
| **Slug** | URL path at `/help/articles/<slug>` |
| **Summary** | One-line description shown in category listings |
| **Audience** | All / Clients / Writers / Staff — controls who sees this article |
| **Featured** | Tick to show on the Help Center home page |
| **Published** | Tick to make the article publicly visible |
| **Content** | Full WYSIWYG editor |

---

## Part 6 — Legal Documents (Content Management)

Legal documents (Terms of Service, Privacy Policy, Refund Policy, etc.) are versioned — each time you update a document, you create a new version and activate it. The previous version is automatically archived.

**Go to:** `/admin/content` → **Legal documents** tab

**Creating a new version:**

1. Select the document type from the left panel (e.g. Terms of Service)
2. Click **+ New version**
3. Fill in:
   - **Title** — e.g. "Terms of Service"
   - **Version** — e.g. "2.1"
   - **Effective date** — when this version takes effect
   - **Require users to re-accept** — tick if users need to accept again on next login
   - **Content** — full WYSIWYG editor
4. Click **Save draft** to save without publishing, or **Save & Activate** to publish

**Activating a version:**

From the version history list, click **Activate** on any draft version. The currently active version is automatically archived.

**Multi-site note:** Superadmins see a site switcher (amber bar at the top). All legal documents are scoped per website — each site maintains its own Terms, Privacy Policy, etc.

---

## Part 7 — Publishing Desk Overview

The Publishing Desk (`/admin/publishing`) is the command centre for all content.

**What it shows:**

- All live and draft blog posts (from Wagtail)
- All live and draft service pages (from Wagtail)
- All SEO landing pages (from the API)
- Status badges: **published** / **draft** / **scheduled**

**Filter and search:**

- Type tabs: All / Blog / Service / SEO pages
- Search by title or slug

**Actions per item:**

- SEO pages: **Publish / Unpublish** toggle inline
- Wagtail pages: **View live** link + **Edit in CMS** link (opens `/cms-admin/`)

**Sidebar tools:**

- **Wagtail quick links** — direct shortcuts to authors, categories, tags, page tree
- **Link suggestions** — enter a Wagtail page ID to get ranked internal link recommendations based on pillar, category, and semantic similarity

**Wagtail publishing guide** (blue button, top-right): opens an 8-step in-app walkthrough of the full Wagtail editorial workflow.

---

## Part 8 — Content Graph and Funnel Attribution

Once posts and service pages are published, connect them to measure revenue attribution.

**Go to:** `/admin/content-graph`

**Step 1 — Create a content pillar**

A pillar groups all content around one service page.

In Wagtail (`/cms-admin/`) → Snippets → Content Pillars → Add:
- **Name** — e.g. "APA Essay Writing"
- **Service page** — the service this pillar funnels traffic toward
- **Hub post** — the flagship comprehensive guide (optional but recommended)
- **Target keywords** — list of keywords to track in GSC

**Step 2 — Assign posts to pillars**

When writing a blog post, set the **Content pillar** field to place it in the right cluster. This makes it a "spoke" post in that pillar.

**Step 3 — View the funnel**

In the Content Graph dashboard → **Funnel tab** → select a pillar to see:

| Stage | What it measures |
|---|---|
| **Top (awareness)** | Blog traffic — total sessions across hub + spoke posts |
| **Middle (consideration)** | Blog → service page clicks and CTR across all conversion links |
| **Bottom (conversion)** | Service page sessions, orders placed, conversion rate, revenue attributed |
| **Efficiency** | Revenue per blog visitor |

**Step 4 — Monitor freshness alerts**

The **Freshness tab** shows alerts for content that needs attention:
- Declining search position (lost rankings)
- Low CTR despite high impressions (rewrite meta title/description)
- No conversion path (add a service CTA)
- Stale content (hasn't been updated in 6+ months)

Click **Acknowledge** to flag you've seen an alert, **Resolve** to mark it fixed.

---

## Frequently Asked Questions

**Q: Should I use Wagtail or the Publishing Desk for a new landing page?**

Use **Wagtail** if the page needs:
- Full StreamField blocks (Hero, FAQ, PricingTable, Testimonials, etc.)
- Author attribution
- Revision history and approval workflows
- Internal linking intelligence

Use the **Publishing Desk / Content Management** if:
- You need the page live in under 5 minutes
- It's a simple text page without rich blocks
- You don't have Wagtail admin access

**Q: What's the difference between an SEO page at /lp/<slug> and a blog post at /blog/<slug>?**

Blog posts are editorial content — they rank for informational queries and feed traffic into service pages. SEO landing pages target transactional or bottom-of-funnel keywords and convert directly. Blog posts require Wagtail; SEO pages are created in the Publishing Desk.

**Q: How do I update an existing blog post?**

Go to `/cms-admin/pages/` → navigate to the Blog → find the post → click to edit. Wagtail keeps full revision history so you can compare or revert to any previous version.

**Q: How does scheduling work?**

- **Wagtail blog/service pages:** in the page editor, use "Set schedule" → enter a go-live date and time.
- **SEO pages and static pages:** in the Publishing Desk or Content Management, use the "Schedule publish" datetime picker.

**Q: Can I preview a page before publishing?**

- **Wagtail pages:** click **Preview** in the editor — opens a live preview in the same browser.
- **SEO / static pages:** navigate to `/lp/<slug>` while logged in — draft pages are visible to authenticated staff.

**Q: The page isn't showing on the site after I published it — what happened?**

1. Check the status in the Publishing Desk — is it showing as "published"?
2. For Wagtail pages: confirm the page is **live** (not just saved) and that you're under the correct site's page tree.
3. For SEO pages: confirm `is_published` is `true` in the API response.
4. Clear your browser cache or try an incognito window.

---

*For technical issues, contact your platform administrator or raise a support ticket.*
