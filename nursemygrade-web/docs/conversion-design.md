# Conversion Design

## Research approach

Before building a single component, we studied four direct competitors in detail to understand what conversion patterns the market uses and where gaps exist:

| Site | What we studied |
|---|---|
| essaypro.com | Service page structure, author presentation, trust signals, pre-CTA sections |
| edubirdie.com | Blog engagement (likes, stats), article listing, author cards |
| custom-writing.org | Content structure, testimonials placement, pricing display |
| essaypay.com | Author bio format, reading time display, social sharing placement |

---

## What competitors do (their ceiling)

### Author presentation

All four competitors show a small circular avatar + 2–3 sentence bio at the **bottom** of articles. None of them:
- Display role badges (Senior Writer vs. Editor vs. Subject Expert)
- Surface verified credentials (ORCID, Google Scholar) as trust signals
- Show the author's post count or link to their other articles
- Attribute the article to a specific reviewing editor

### Stats and engagement

- EduBirdie shows "30 likes" on some articles — the only competitor with any social proof on individual posts
- None show view counts, share counts, or reaction counts
- None have a "was this helpful?" mechanism

### Editorial transparency

None of the four competitors explain how articles are written or reviewed. No editorial process is disclosed. This is a significant trust gap — students are evaluating whether to pay for a service based on whether they trust the brand's expertise, and none of these sites tell the story of how content is produced.

### Sharing

All sites have 2–3 share icons (Twitter, Facebook, LinkedIn). None have:
- WhatsApp sharing (major gap for the student demographic)
- Telegram sharing
- Native Web Share API (mobile system share sheet)
- Copy-link button

### Revision history

All sites show a single "Last updated: [date]" timestamp. None show:
- Original publication date vs. update date as separate signals
- Number of editorial revisions as a quality indicator
- A timeline of the article's editorial history

---

## What we built differently

### Trust differentiation

Our core positioning is: **we are the most transparent writing service**. Where competitors hide their operations behind generic claims, we show:

1. **Named, credentialed authors** with verifiable external profiles (ORCID, Google Scholar IDs link out to real academic profiles). A student can verify our writer actually has a PhD in the subject they're writing about.

2. **Role hierarchy** (Writer → Senior Writer → Editor → Subject Expert → Clinical Reviewer) displayed as coloured badges. This shows there's a professional structure behind the content, not just random freelancers.

3. **The reviewing editor** is named on every article. This is unique in the market and models the standard used by medical and academic publishers.

4. **Editorial process made visible** — the 5-step timeline (Topic → Research → Editorial Review → Published → Tracked) tells the complete story of how a piece comes to exist. The "Written by humans, not AI" badge directly addresses the market's current anxiety about AI-generated content.

5. **Revision history** — showing that an article has been saved and refined 12 times is a quality signal. It tells the reader this wasn't dashed off; it was worked.

### Benefits section (pre-CTA pattern)

From studying essaypro.com/custom-essay, we adopted the pattern of placing a **benefits section directly above the final CTA** on service pages. The pattern works because:

- By the time a reader reaches the bottom of a service page, they've consumed the information but may still need one final affirmation before clicking "Order"
- A compact list of benefits (with checkmarks) + a badge strip of trust signals acts as that final reassurance
- It converts the reader's last question ("but is this actually good?") into a "yes" before presenting the action

We implemented this as an editor-configurable Wagtail block (`benefits_section`) so each service page can have a benefits section tailored to that specific service.

### Mobile-first sharing

The student demographic uses WhatsApp and Telegram extensively (particularly international students). By adding both platforms and the native Web Share API:

- WhatsApp is the most likely platform a student uses to share an article with a classmate ("read this, it explains APA format perfectly")
- Telegram group chats are common in university cohorts
- The native Web Share API means mobile users don't even need to know our share buttons exist — the OS share sheet they already use appears

### Content migration transparency

When migrating existing content from another site, editors can set the `original_published_at` date so articles don't falsely appear to have been "published today." This preserves the article's real publication history and maintains Schema.org accuracy for SEO.

---

## Conversion funnel

The site is designed as a funnel with a single ultimate goal: a logged-in order being placed.

```
Blog post / Service page
        ↓
  Inline CTA ("Get started", "Order now")
        ↓
  /register  (account creation)
        ↓
  /order or portal /client/new-order
        ↓
  Order placed
```

Every page element is evaluated against whether it moves a visitor toward this outcome. Navigation items are ordered by conversion proximity: Services (closest to order) → Blog (content, trust building) → Help (objection handling) → Become a writer (separate funnel).

### CTA placement rules

1. **Above the fold** — every page has a primary CTA visible without scrolling
2. **Mid-article** — long blog posts and service pages have at least one CTA in the middle third of the content
3. **End of article** — the closing CTA block ("Need help with your assignment?") appears before the author card
4. **Sticky pricing bar** — service pages have a sticky bottom bar showing price + delivery + CTA that persists as the user scrolls

### Trust signals — layered

We layer trust signals at multiple points rather than clustering them all in one place:

- **Header**: brand name + professional colour
- **Hero**: headline claim + primary CTA
- **Trust strip**: aggregate stats (orders completed, rating, years operating)
- **In-content**: author credentials, ORCID/Scholar links, reviewer attribution
- **Pre-CTA**: benefits section + trust badges
- **Footer**: legal links (terms, privacy, refund policy) — signals that there's a real, accountable company behind the service
