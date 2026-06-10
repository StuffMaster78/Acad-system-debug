# Design System

Everything visual about the marketing site flows from a single deliberate decision: **this is an academic credibility brand, not a generic SaaS tool**. Every colour, type choice, and spacing value was chosen to reinforce trust with students who are making a purchase decision that involves their academic future.

---

## Brand colour — why #163e88

The primary brand colour is a deep navy blue: **`#163e88` (brand-700)**.

### Why this specific blue

We studied four direct competitors before choosing:

| Competitor | Primary colour | Feeling |
|---|---|---|
| EssayPro | Rose red `#e74c3c` | Urgent, sales-y |
| EduBirdie | Green `#27ae60` | Friendly, informal |
| EssayPay | Blue-grey `#5b7fa6` | Safe, generic |
| Custom-writing.org | Orange `#f39c12` | Cheap, commodity |

None of them use a deep authoritative blue. We chose `#163e88` because:

1. **Academic association** — deep navy blue is the colour of university regalia, formal publishing (Oxford, Cambridge, Harvard presses), and professional credentials. Students already trust this colour in educational contexts.
2. **High contrast** — `#163e88` on white achieves a contrast ratio of 7.8:1, exceeding WCAG AA (4.5:1) and passing WCAG AAA. Academic credibility requires legibility.
3. **Differentiation** — no direct competitor uses this palette. A student who has visited EssayPro and then arrives here perceives an immediate quality step-up.
4. **Consistency across surfaces** — the same brand scale runs across the marketing site, the client portal, and the writer workspace, so the product feels unified rather than cobbled together.

### The full brand scale

```
brand-50   #eef4ff   — page tint backgrounds, hover fills
brand-100  #dde9ff   — light badges, credential pills
brand-200  #bbd3ff   — borders on tinted surfaces
brand-300  #93b8ff   — icon fills on dark backgrounds
brand-500  #2563c8   — interactive states (focus rings)
brand-600  #1d4fa8   — btn-primary background
brand-700  #163e88   — primary CTA, sidebar, key headings (the core brand colour)
brand-800  #112f6a   — hover state on brand-700 buttons
brand-900  #0d2455   — deep backgrounds, dark nav elements
```

`brand-400` is intentionally absent. The jump from 300 to 500 avoids a muddy mid-tone that reads as neither a background nor a foreground.

---

## Semantic colour tokens

Defined in `tailwind.config.ts` and available across all components:

| Token | Hex | Usage |
|---|---|---|
| `ink` | `#1a1f2e` | All primary body text — slightly warmer than pure black, easier on the eyes for long reading |
| `graphite` | `#4b5563` | Secondary text, metadata, captions |
| `mist` | `#f1f5f9` | Page and panel backgrounds |
| `signal` | `#163e88` | Alias for brand-700 — used in body copy links and inline trust signals |
| `saffron` | `#d97706` | Star ratings, urgency nudges ("3 writers available") |
| `berry` | `#e11d48` | Danger states, form errors, destructive actions — not used for brand CTAs |

### Why `ink` instead of `#000000`

Pure black text on white creates too much optical harshness, particularly for long-form academic content (blog posts, guides). `#1a1f2e` has a slight warm-blue undertone that reads as "dark" while reducing eye strain. This is a standard technique used by Medium, Notion, and every major academic publisher.

### Why `berry` is never used for CTAs

Berry (`#e11d48`) appears only for errors and warnings. Using it for CTAs (as competitors do) trains users to associate your primary action colour with danger. We train users to associate brand-blue with positive actions — placing an order, registering, reading more.

---

## Typography

### Typeface: Plus Jakarta Sans

**Why not Inter?** Inter is the default for SaaS products and is now so ubiquitous it reads as "generic tech tool." A writing services product targeting students needs to feel more considered.

Plus Jakarta Sans was chosen because:

1. **Geometric warmth** — the letterforms are geometric but have humanist details (the double-story `a` and `g`) that make long blog text comfortable to read — critical for a content-heavy site.
2. **Academic weight range** — the 700 weight is genuinely bold without looking aggressive. Academic credibility calls for confident typography, not screaming headlines.
3. **Variable axis** — the font supports a `wght` variable axis which means one file covers all weights (we load 400/600/700 statically for performance).
4. **No licensing cost** — open source via Google Fonts.

### Weight usage

| Weight | Token | Where |
|---|---|---|
| 400 | `font-normal` | Body copy, paragraphs, form inputs |
| 600 | `font-semibold` | Sub-headings, labels, nav items, metadata |
| 700 | `font-bold` | Section headings, card titles, CTA button labels |

We do not load weights 500 or 800. 500 is visually indistinguishable from 400/600 at body sizes and adds payload for no perceptible gain. 800 produces letterforms that are distractingly heavy at display sizes.

### Type scale

The site uses Tailwind's default type scale without modification. Key sizes in practice:

- Hero headline: `text-4xl` / `text-5xl` (36px / 48px) — `font-extrabold` (800, loaded from the 700 weight file with synthetic bold)
- Section heading: `text-3xl` (30px) — `font-bold`
- Card title: `text-base` or `text-lg` (16px / 18px) — `font-bold`
- Body: `text-base` (16px) — `font-normal`, `leading-7` for reading comfort
- Labels / meta: `text-sm` or `text-xs` (14px / 12px) — `font-medium` or `font-semibold`

---

## Spacing

All spacing uses Tailwind's default 4px scale. Key layout conventions:

- Section vertical padding: `py-20` (80px) on desktop, reduces proportionally on mobile
- Max content width: `max-w-7xl` (1280px) for wide sections, `max-w-3xl` (768px) for reading content (blog posts, legal pages)
- Card internal padding: `p-6` (24px) standard, `p-4` (16px) for compact cards
- Between cards in a grid: `gap-6` (24px)

---

## Shadows

Three shadow levels defined in `tailwind.config.ts`:

| Token | CSS | Usage |
|---|---|---|
| `shadow-panel` | `0 1px 3px rgba(26,31,46,0.08), 0 1px 2px rgba(26,31,46,0.04)` | Default card elevation — subtle, not floating |
| `shadow-card` | `0 2px 8px rgba(26,31,46,0.07), 0 1px 2px rgba(26,31,46,0.04)` | Hover state elevation — shows interactivity |
| `shadow-soft` | `0 4px 16px rgba(26,31,46,0.10)` | Modal dialogs, dropdown menus |

Shadow colours use `rgba(26,31,46, ...)` — the same ink base colour — which produces shadows with a warm-blue undertone rather than the flat grey of `rgba(0,0,0, ...)`. This keeps shadows feeling cohesive with the brand rather than generic.

---

## Component primitives

Defined in `assets/css/main.css` via `@layer components`:

```css
.btn-primary    /* Brand blue CTA — used for "Order Now", "Get Started", "Place Order" */
.btn-outline    /* Brand blue outline — secondary actions, "Learn more" */
.section        /* max-w-7xl centred container with responsive padding */
.section-heading /* 3xl/4xl bold serif heading */
.section-sub    /* Lead paragraph beneath a section heading */
.card           /* Rounded white card with subtle border and hover shadow */
```

### Button usage rules

- **One `btn-primary` per visual section** — never two competing primary CTAs side by side.
- `btn-outline` for secondary actions at the same visual level.
- Never use `btn-primary` for navigation — navigation links are plain text with hover states.
- CTA text should be action-oriented: "Get started", "Place my order", "See pricing" — never "Click here" or "Submit".
