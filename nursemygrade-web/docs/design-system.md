# Design System

Everything visual about NurseMyGrade flows from one deliberate decision: **this is a clinical credibility brand, not a generic academic service**. Every colour, typeface choice, and icon was chosen to reinforce trust with nursing students — people making a purchase decision about their professional future in healthcare.

---

## Brand colour — why teal

The primary brand colour family is **teal**: `#0d9488` (brand-600) through `#0f766e` (brand-700).

### Why teal specifically

We studied four direct competitors before choosing:

| Competitor | Primary colour | Feeling |
|---|---|---|
| EssayPro | Rose red `#e74c3c` | Urgent, sales-y |
| EduBirdie | Bright green `#27ae60` | Friendly, generic |
| NursingPaperHelp | Royal blue `#1a56db` | Corporate, cold |
| CustomNursingPapers | Orange/red `#e05328` | Cheap, commodity |

None of them use teal. We chose it because:

1. **Clinical association** — teal is the colour of scrubs, surgical drapes, medical equipment packaging, and nursing uniform accents. Nursing students already associate it with their profession. The brand colour signals "we understand your world" before a word is read.
2. **Differentiation** — no nursing writing service competitor uses this palette. The instant brand recognition it creates is valuable when students tab-compare services.
3. **Warmth without aggression** — teal sits between the cold authority of navy and the informal warmth of green. It reads as both trustworthy and approachable — the right register for a service students confide personal academic struggles to.
4. **High contrast** — `#0d9488` on white achieves sufficient contrast for interactive elements; `#0f766e` (brand-700) passes WCAG AA at 4.8:1 on white backgrounds.

### The full brand scale

Defined in `tailwind.config.ts` under `theme.extend.colors.brand`:

```
brand-50   #f0fdfa   — page tint backgrounds, light section fills
brand-100  #ccfbf1   — badge backgrounds, light chips
brand-200  #99f6e4   — borders on tinted surfaces, icon fills
brand-300  #5eead4   — decorative accents, footer icon highlights
brand-400  #2dd4bf   — footer wordmark accent, secondary icon fills
brand-500  #14b8a6   — interactive states, focus rings
brand-600  #0d9488   — primary CTA buttons, key headings, header logo mark
brand-700  #0f766e   — hover state on brand-600, sidebar panels
brand-800  #115e59   — deep teal, gradient endpoint (logo vertical bar)
brand-900  #134e4a   — dark backgrounds, deep accent panels
```

---

## Logo — the medical cross mark

The logo is an inline SVG medical cross (two overlapping rounded-rect bars at 90°) with teal gradient fills, plus the "NurseMyGrade" wordmark.

### Header logo
```
SVG size: 32×32px
Vertical bar:  rect(x=12, y=2, w=8, h=28, rx=4) — filled with linear gradient #0d9488 → #115e59 (top to bottom)
Horizontal bar: rect(x=2, y=12, w=28, h=8, rx=4) — filled with linear gradient #2dd4bf → #0d9488 (left to right), opacity 0.9
```

Wordmark: `font-bold tracking-tight` — `Nurse` in `text-slate-900`, `MyGrade` in `text-brand-600`.

The gradient IDs (`nmg-v`, `nmg-h`) are scoped to the header SVG. The footer uses separate IDs (`nmg-vf`, `nmg-hf`) to avoid conflicts when both render on the same page.

### Footer logo
Footer version is 28×28px. Gradient stops use lighter teal (`#5eead4 → #0d9488` vertical, `#99f6e4 → #2dd4bf` horizontal) so the mark reads clearly on the dark slate footer background.

Wordmark: `Nurse` in `text-white`, `MyGrade` in `text-brand-400`.

---

## Semantic colour tokens

Defined in `tailwind.config.ts` alongside the brand scale:

| Token | Hex | Usage |
|---|---|---|
| `ink` | `#1a1f2e` | All primary body text — slightly warm, reduces eye strain on clinical reading |
| `graphite` | `#4b5563` | Secondary text, timestamps, metadata |
| `mist` | `#f1f5f9` | Page and panel backgrounds |
| `saffron` | `#d97706` | Star ratings, urgency nudges ("3 writers available tonight") |
| `berry` | `#e11d48` | Form errors, danger states — never used for CTAs |

### Why `berry` is never used for CTAs

Berry (`#e11d48`) appears only for errors and warnings. Competitors (EssayPro, EduBirdie) use red/rose for primary CTAs — this trains users to associate the order action with danger. We associate brand-teal with positive actions, creating a cleaner emotional signal for nursing students who are already anxious about their coursework.

---

## Typography

### Typeface: Plus Jakarta Sans (body) + system serif (headings)

**Plus Jakarta Sans** is loaded for all body text, labels, and navigation. It was chosen because:

1. **Geometric warmth** — humanist details (double-story `a`, `g`) make clinical text comfortable to read at length.
2. **Professional weight range** — 700 bold is confident without aggression. This is the right tone for a service credentialed nurses work with.
3. **Variable axis** — one file covers all weights via `wght` axis; we load 400/600/700 statically for performance.
4. **No licensing cost** — open source (Google Fonts).

Section headings use `font-serif` (the browser's serif fallback stack: Georgia, Times New Roman, serif). This creates a small but meaningful editorial register shift between body copy and structural headings — typical of medical and academic publishing.

### Weight usage

| Weight | Token | Where |
|---|---|---|
| 400 | `font-normal` | Body copy, paragraphs, descriptions |
| 600 | `font-semibold` | Sub-headings, nav items, badge labels |
| 700 | `font-bold` | CTA buttons, card titles, metadata callouts |

### Type scale

- Hero headline: `text-4xl md:text-5xl font-extrabold` (36–48px)
- Section heading: `text-3xl font-bold font-serif`
- Card title: `text-lg font-bold`
- Body: `text-base leading-7`
- Labels / meta: `text-sm font-semibold` or `text-xs font-medium`

---

## Spacing

Tailwind's default 4px scale. Key layout conventions:

- Section vertical padding: `py-20` (80px) on desktop
- Max content width: `max-w-7xl` (1280px) wide sections, `max-w-3xl` (768px) reading content
- Card internal padding: `p-6` standard, `p-4` compact cards
- Grid gap: `gap-6` between cards

---

## Shadows

Three shadow levels:

| Token | Usage |
|---|---|
| `shadow-panel` | Default card elevation — barely perceptible lift |
| `shadow-card` | Hover state — signals interactivity |
| `shadow-soft` | Modals, dropdowns |

All shadow colours use `rgba(26,31,46, ...)` (the ink base) — produces shadows with a warm undertone rather than flat grey.

---

## Component primitives

Defined in `assets/css/main.css` via `@layer components`:

```css
.btn-primary    /* Teal CTA — "Order Now", "Get Started", "Place Order" */
.btn-outline    /* Teal outline — secondary actions */
.section        /* max-w-7xl centred container with responsive padding */
.section-heading /* 3xl/4xl bold serif heading */
.section-sub    /* Lead paragraph beneath a section heading */
.card           /* Rounded white card with border and hover shadow */
```

### Button rules

- **One `btn-primary` per visual section** — no competing primary CTAs.
- `btn-outline` for secondary actions at the same visual level.
- Never use `btn-primary` for navigation.
- CTA copy should be action-oriented and nursing-specific: "Order my care plan", "Get started", "See nursing prices" — never "Click here" or "Submit".

---

## Announcement bar

`components/marketing/AnnouncementBar.vue` renders a dismissible teal banner above the header. Used for promotions (e.g., `NURSE15` discount code). Dismissed state is persisted in `localStorage` keyed by message hash, so a new message auto-shows even if a previous one was dismissed.

---

## WhatsApp button

`components/marketing/WhatsAppButton.vue` renders a fixed floating button (bottom-right, `z-50`) linking to the NurseMyGrade WhatsApp contact. The button is intentionally teal (`bg-[#25D366]` is the WhatsApp brand green, kept for recognition) on desktop and collapses on very small screens.

WhatsApp is the primary contact channel for international nursing students — this button is a direct conversion tool, not decoration.
