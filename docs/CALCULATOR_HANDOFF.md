# Calculator Design Handoff

**For**: Frontend designer / developer  
**Last updated**: June 2026  
**Status**: Paper, Design, and Diagram calculators are implemented. The CMS calculator block routes to the correct widget by `service_code`.

---

## Contents

1. [Design Tokens](#1-design-tokens)
2. [Anatomy of a Calculator](#2-anatomy-of-a-calculator)
3. [Calculator 1 — Paper Orders](#3-calculator-1--paper-orders)
4. [Calculator 2 — Design Orders](#4-calculator-2--design-orders)
5. [Calculator 3 — Diagram Orders](#5-calculator-3--diagram-orders)
6. [All States](#6-all-states)
7. [Price Breakdown Lines](#7-price-breakdown-lines)
8. [Add-Ons Panel](#8-add-ons-panel)
9. [Tight Deadline Warning](#9-tight-deadline-warning)
10. [Mobile Layout](#10-mobile-layout)
11. [Shared Composable](#11-shared-composable)
12. [API Quick Reference](#12-api-quick-reference)

---

## 1. Design Tokens

These are the only custom colours in the design system. Everything else uses Tailwind's default slate/emerald/amber/rose palette.

| Token | Hex | Usage |
|---|---|---|
| `ink` | `#17202a` | Primary text, headings, primary buttons, stepper buttons |
| `graphite` | `#2f3a45` | Secondary text, field labels, muted values |
| `mist` | `#eef3f6` | Subtle backgrounds, hover states |
| `signal` | `#0f766e` | Brand green — active states, focus rings, links |
| `saffron` | `#b7791f` | Warnings — tight deadline notice, urgent label |
| `berry` | `#9f1239` | Primary CTA button ("Place Order") |

### Typography scale used in calculators

| Role | Class | Size / Weight |
|---|---|---|
| Widget heading | `text-lg font-bold` | 18px bold |
| Widget subtitle | `text-sm` | 14px regular |
| Field label | `text-xs font-semibold uppercase tracking-wide` | 12px semibold caps |
| Input value | `text-sm` | 14px regular |
| Page count hint | `text-xs` | 12px regular |
| Price — range | `text-3xl font-extrabold` | 30px 900 weight |
| Price — exact | `text-3xl font-extrabold` | 30px 900 weight |
| Currency code | `text-sm` | 14px regular |
| Breakdown line | `text-sm` | 14px regular |
| Disclaimer | `text-xs text-slate-400` | 12px muted |

### Spacing

All internal spacing uses 4px increments. Key values:
- Widget outer padding: `px-6 py-5` (24px / 20px)
- Input grid gap: `gap-4` (16px)
- Price section top border: `border-t border-slate-100`
- Breakdown list items: `px-4 py-2` (16px / 8px)

### Border radius

- Widget container: `rounded-2xl` (16px)
- Inputs and selects: `rounded-lg` (8px)
- Stepper buttons: `rounded-lg` (8px)
- Breakdown list: `rounded-lg` (8px)
- CTA button: `rounded-xl` (12px)

---

## 2. Anatomy of a Calculator

Every calculator variant shares this four-zone layout:

```
┌──────────────────────────────────────────────┐
│  ZONE A — Header                              │  bg: ink → slate-700 gradient
│  Icon  Title                                  │  text: white
│        Subtitle                               │
├──────────────────────────────────────────────┤
│  ZONE B — Inputs                              │  bg: white, px-6 py-5
│  Two-column grid (collapses to 1 on mobile)   │
│                                               │
├──────────────────────────────────────────────┤
│  ZONE C — Price Display                       │  bg: white, border-t slate-100
│  Estimate range  OR  Exact price + breakdown  │
│  Error / loading / deadline warning           │
│                                               │
│  [ Secondary CTA ]   [ Primary CTA → ]        │
│  No credit card required · 100% confidential  │
└──────────────────────────────────────────────┘
```

Zone A height: fixed (`py-5` = 20px top/bottom).  
Zone B height: grows with content.  
Zone C height: grows with breakdown lines.  
Widget min-width: works from 280px upward.

---

## 3. Calculator 1 — Paper Orders

**File**: `frontend/src/components/cms/PricingCalculator.vue`

### Input grid (2 columns, collapses at `sm`)

```
┌─────────────────────┬─────────────────────┐
│  ACADEMIC LEVEL     │  TYPE OF PAPER       │
│  ┌───────────────┐  │  ┌───────────────┐  │
│  │ Undergraduate ▾│  │  │ Essay         ▾│  │
│  └───────────────┘  │  └───────────────┘  │
├─────────────────────┼─────────────────────┤
│  PAGES              │  DEADLINE            │
│  ┌───┐  ┌───────┐  ┌───┐  │  ┌───────────────┐  │
│  │ − │  │   3   │  │ + │  │  │ 2 days        ▾│  │
│  └───┘  └───────┘  └───┘  │  └───────────────┘  │
│  ≈ 825 words · double spaced   │                  │
└─────────────────────┴─────────────────────┘
```

**Stepper buttons (−/+)**:
- Size: 40×40px (`size-10`)
- Border: `border border-slate-200`
- Background: white, hover: `slate-50`
- Disabled (− at 1 page): `opacity-40`
- Font: `text-lg font-bold text-ink`

**Page count hint** below the stepper: `≈ {pages × 275} words · {spacing} spaced`  
Updates live as pages change. `double` spacing = 275 words/page, `single` = 550 words/page.

**Deadline options** — items with `is_urgent: true` show ⚡ suffix in the option label.

### Payload sent on every change (debounced 350ms)

```json
{
  "service_code": "standard_paper",
  "pages": 3,
  "deadline_hours": 48,
  "spacing": "double",
  "paper_type_code": "essay",
  "work_type_code": "writing",
  "subject_code": "general",
  "academic_level_code": "undergraduate"
}
```

`work_type_code` defaults to `"writing"`, `subject_code` defaults to `"general"` unless a subject selector is shown.

---

## 4. Calculator 2 — Design Orders

**File**: `frontend/src/components/cms/DesignCalculator.vue`  
**Backend endpoints**: live at `/api/pricing/quotes/design/start/` and `.../update/`

### Input grid

```
┌─────────────────────┬─────────────────────┐
│  NUMBER OF SLIDES   │  DEADLINE            │
│  ┌───┐  ┌───────┐  ┌───┐  │  ┌───────────────┐  │
│  │ − │  │  10   │  │ + │  │  │ 2 days        ▾│  │
│  └───┘  └───────┘  └───┘  │  └───────────────┘  │
│  Presentation slides       │                      │
└─────────────────────┴─────────────────────┘
```

Below the grid, if addons are available for this service, show the add-ons panel (see Section 8).

### Payload

```json
{
  "service_code": "presentation_design",
  "quantity": 10,
  "deadline_hours": 48,
  "selected_addon_codes": ["source_file_included"]
}
```

**`service_code`** is passed in as a prop from the CMS block — the admin sets it to match whichever design service is being priced on that page.

**No academic level, no paper type** — these selectors are not shown for design orders.

---

## 5. Calculator 3 — Diagram Orders

**File**: `frontend/src/components/cms/DiagramCalculator.vue`  
**Backend endpoints**: live at `/api/pricing/quotes/diagram/start/` and `.../update/`

### Input grid

```
┌─────────────────────┬─────────────────────┐
│  NUMBER OF DIAGRAMS │  DEADLINE            │
│  ┌───┐  ┌───────┐  ┌───┐  │  ┌───────────────┐  │
│  │ − │  │   3   │  │ + │  │  │ 3 days        ▾│  │
│  └───┘  └───────┘  └───┘  │  └───────────────┘  │
└─────────────────────┴─────────────────────┘

COMPLEXITY
┌──────────────────────────────────────────────┐
│  ○ Simple      ● Moderate      ○ Complex      │
│  Basic bar chart  Annotated flow  Multi-layer │
│  or flowchart     with branches   systems map │
└──────────────────────────────────────────────┘
```

**Complexity selector** — three options, always all three shown (values are fixed: `simple`, `moderate`, `complex`). Use radio buttons styled as a segmented control or a card picker. Include a one-line description below each label.

| Value | Label | Description hint |
|---|---|---|
| `simple` | Simple | Basic chart, table, or single-step flow |
| `moderate` | Moderate | Multi-step flow, annotated diagram |
| `complex` | Complex | Multi-layer system map, large org chart |

### Payload

```json
{
  "service_code": "diagram_design",
  "quantity": 3,
  "diagram_complexity": "moderate",
  "deadline_hours": 72,
  "selected_addon_codes": []
}
```

---

## 6. All States

Every calculator passes through these states. Design and implement all of them.

### State 1 — Loading config (on mount)

Zone B shows a spinner instead of inputs. Zone C is empty.

```
┌──────────────────────────────────────┐
│  ▓ Get your instant price            │
│    No account needed…                │
├──────────────────────────────────────┤
│                                      │
│      ↻ Loading options…              │
│                                      │
└──────────────────────────────────────┘
```

Icon: `RefreshCw` from lucide-vue, `animate-spin`. Text: `text-graphite`.

---

### State 2 — Calculating (after first input change)

Inputs remain interactive. Price zone shows spinner inline next to a dash.

```
├──────────────────────────────────────┤
│  ESTIMATED PRICE                      │
│  —   ↻                               │
│  Calculating…                        │
│                                      │
│                    [ Place Order → ] │
└──────────────────────────────────────┘
```

---

### State 3 — Estimate shown (default active state)

The range updates live on every debounced input change. The spinner appears inline to the right of the price while a re-fetch is in flight.

```
├──────────────────────────────────────┤
│  ESTIMATED PRICE                      │
│  $22.00 – $35.00  USD  ↻             │  ← spinner only while fetching
│  Final price may vary by subject      │
│  and writer level.                   │
│                                      │
│  [ Get exact price ]  [ Place Order → ]│
│                                      │
│  No credit card required · 100% confidential │
└──────────────────────────────────────┘
```

- Range: `text-3xl font-extrabold text-ink`
- Currency: `text-sm text-graphite` inline after the range
- Spinner: `size-4 animate-spin text-graphite`, only visible while `quoteLoading`
- Disclaimer: `text-xs text-graphite`

**"Get exact price" button** (secondary):
- Border: `border-ink`
- Background: white
- Text: `text-ink font-semibold`
- Icon: `Calculator` (lucide)
- Width: `flex-1` (shares row equally with CTA)

**"Place Order" button** (primary CTA):
- Background: `bg-berry` (`#9f1239`)
- Text: white `font-bold`
- Icon: `ArrowRight` (lucide), trailing
- Hover: `bg-rose-700`
- Width: `flex-1`
- Shadow: `shadow-md`

---

### State 4 — Exact price shown

Triggered by clicking "Get exact price". Secondary button is hidden; CTA remains.

```
├──────────────────────────────────────┤
│  $28.50  USD                          │
│  ┌────────────────────────────────┐  │
│  │ Base price for 3 pages  $16.50 │  │
│  │ Academic level (PhD)    + $5.28│  │
│  │ Deadline (6 hours) ⚡   + $7.92│  │  ← amber text if urgent
│  │ Plagiarism report       + $5.00│  │
│  │ ─────────────────────────────  │  │
│  │ Total                   $34.70 │  │  ← bold, slightly larger
│  └────────────────────────────────┘  │
│                                      │
│                    [ Place Order → ] │
│  No credit card required · 100%      │
└──────────────────────────────────────┘
```

Breakdown list styling:
- Container: `rounded-lg border border-slate-200 bg-slate-50`
- Each row: `flex justify-between px-4 py-2 text-sm divide-y divide-slate-100`
- Label: `text-graphite`
- Amount: `font-semibold text-ink`
- Total row: `font-bold text-ink` — do not show total in the breakdown if it's already shown as the headline price
- Discount rows: amount in `text-emerald-600`
- Zero-amount rows: **hide entirely** (a 1.0× multiplier with $0.00 delta is noise)

---

### State 5 — Error

Shown when the API call fails. Inputs remain interactive so the user can change their selection and retry.

```
├──────────────────────────────────────┤
│  ┌──────────────────────────────────┐│
│  │ Could not fetch price. Please    ││  ← bg-rose-50 border-rose-200
│  │ try again.                       ││     text-rose-700
│  └──────────────────────────────────┘│
│                                      │
│  [ Get exact price ]  [ Place Order → ]│
└──────────────────────────────────────┘
```

The error clears on the next successful API response.

---

## 7. Price Breakdown Lines

The `lines[]` array from the exact-price API response drives the breakdown. Use `line_type` to control rendering:

| `line_type` | Render rule |
|---|---|
| `base` | Normal row. Amount is always positive. |
| `multiplier` | Show as delta `+$X.XX` or `–$X.XX`. If `amount == "0.00"`, **skip the row**. The `metadata.multiplier` field holds the raw multiplier (e.g. `"1.40"`) — optionally show it as `(×1.4)` in muted text next to the label. |
| `fixed_fee` | Show as `+$X.XX`. Always positive. |
| `addon` | Same as `fixed_fee`. Label comes from the addon name. |
| `discount` | Amount is negative. Render in `text-emerald-600`. Label describes the discount. |
| `total` | Bold. Separator above. If you show the total as the headline price, you can skip this row in the breakdown to avoid repetition. |

### Urgency colouring

If the selected deadline option has `is_urgent: true`, render the deadline breakdown row's amount in `text-amber-600` and append ⚡ to the label. This helps the user see at a glance that the rush premium is what's driving the price up.

---

## 8. Add-Ons Panel

All three calculators support optional add-ons. They appear below the input grid as a checkbox list.

### When to show

- Load add-ons from `GET /api/pricing/public/addons/?service_code={serviceCode}` on mount alongside the other config calls.
- If the response is empty, do not render the add-ons section.
- Show add-ons only if `is_public: true` on the addon record.

### Layout

```
┌──────────────────────────────────────────────┐
│  ADD-ONS                                      │
│  ┌──────────────────────────────────────────┐│
│  │ ☐  Plagiarism report      + $5.00        ││
│  │    Turnitin originality check included   ││
│  │                                          ││
│  │ ☑  Source file (Figma)    + $8.00        ││  ← checked = included in quote
│  │    Editable original included             ││
│  │                                          ││
│  │ ☐  Priority revision      + $6.00        ││
│  │    One free revision within 24h           ││
│  └──────────────────────────────────────────┘│
└──────────────────────────────────────────────┘
```

- Checking or unchecking an add-on immediately re-triggers the debounced estimate.
- The `+$X.XX` amount next to each label comes from `addon.flat_amount`.
- If `addon.description` is non-empty, show it as a second line in `text-xs text-graphite`.
- Checked add-on rows get a subtle `bg-signal/5` tint.
- Sort by `addon.sort_order` ascending.

### API shape for an add-on

```json
{
  "addon_code": "plagiarism_report",
  "name": "Plagiarism report",
  "description": "Turnitin originality check included with your order.",
  "flat_amount": "5.00",
  "is_public": true,
  "is_active": true,
  "sort_order": 1
}
```

---

## 9. Tight Deadline Warning

When the backend detects that the selected deadline is too tight for the page count, it returns a `suggestions` array in the estimate response. Show this as a non-blocking amber banner inside Zone C, above the price.

### When it appears

`suggestions` contains an item with `type: "deadline_adjustment"`.

### Layout

```
├──────────────────────────────────────┤
│  ┌──────────────────────────────────┐│
│  │ ⚠ This deadline is tight for     ││  ← bg-amber-50 border border-amber-200
│  │   3 pages. We recommend at least ││     text-amber-800
│  │   6 hours.                       ││
│  │              [ Use 6h deadline ] ││  ← button sets deadlineHours and refetches
│  └──────────────────────────────────┘│
│                                      │
│  $22.00 – $35.00  USD                │
```

- Icon: `AlertTriangle` from lucide-vue, `text-saffron`
- "Use Xh deadline" button: small, `border border-amber-300 text-amber-800`, sets `deadlineHours` to `suggestion.recommended_deadline_hours`
- The warning disappears when the user picks a longer deadline

---

## 10. Mobile Layout

At viewports below the `sm` breakpoint (640px), the two-column input grid stacks to a single column. No other changes are needed — the widget is already responsive.

**Minimum comfortable width**: 280px.

**Touch targets**: The stepper −/+ buttons must be 40×40px (`size-10`). Do not reduce them. This is the minimum tap target size.

**CTA row on narrow screens**: Stack the two buttons vertically (`flex-col sm:flex-row`). Primary CTA goes second (bottom).

```
Mobile stacked layout:

  ACADEMIC LEVEL
  [ Undergraduate     ▾ ]

  TYPE OF PAPER
  [ Essay              ▾ ]

  PAGES
  [−]  [ 3 ]  [+]
  ≈ 825 words · double spaced

  DEADLINE
  [ 2 days             ▾ ]

  ─────────────────────
  $22.00 – $35.00  USD

  [ Get exact price      ]
  [ Place Order →        ]
```

---

## 11. Shared Composable

When you build the Design and Diagram calculator widgets, extract the shared logic from `PricingCalculator.vue` into a composable so you are not duplicating the debounce, API calls, and state management three times.

**Suggested interface**:

```typescript
// src/composables/useQuoteSession.ts

type QuoteType = "paper" | "design" | "diagram";

interface UseQuoteSessionOptions {
  type: QuoteType;
  getPayload: () => Record<string, unknown>;  // builder fn the widget provides
}

function useQuoteSession(options: UseQuoteSessionOptions) {
  // Returns:
  const sessionId    = ref<string | null>(null);
  const estimate     = ref<QuoteStartResponse | null>(null);
  const breakdown    = ref<QuoteUpdateResponse | null>(null);
  const quoteLoading = ref(false);
  const showBreakdown = ref(false);
  const quoteError   = ref("");
  const suggestions  = ref<Suggestion[]>([]);

  // Methods:
  function fetchEstimate() { /* debounced 350ms */ }
  function getExactPrice() { /* calls update endpoint */ }

  return { sessionId, estimate, breakdown, quoteLoading,
           showBreakdown, quoteError, suggestions,
           fetchEstimate, getExactPrice };
}
```

The widget then calls `fetchEstimate()` inside a `watch` on its inputs, and `getExactPrice()` on the button click. All three widgets share identical Zone C and CTA rendering — this can also be a separate `QuotePriceDisplay.vue` component.

---

## 12. API Quick Reference

### Config (load once on mount, no auth)

```
GET /api/order-configs/academic-levels/
GET /api/order-configs/paper-types/
GET /api/order-configs/writer-deadline-configs/
GET /api/pricing/public/addons/?service_code={serviceCode}
```

Response shape for all config endpoints:
```json
[
  { "id": 1, "name": "Undergraduate", "code": "undergraduate", "is_active": true }
]
```
DeadlineConfig also has `"hours": 48` and `"is_urgent": false`.

### Quote session (anonymous, no auth)

```
POST /api/pricing/quotes/paper/start/           → { session_id, estimated_min_price, estimated_max_price, currency, suggestions }
POST /api/pricing/quotes/paper/{id}/update/     → { calculated_price, currency, lines[], suggestions }

POST /api/pricing/quotes/design/start/
POST /api/pricing/quotes/design/{id}/update/

POST /api/pricing/quotes/diagram/start/
POST /api/pricing/quotes/diagram/{id}/update/
```

### Lock price at checkout (call when user navigates to order form)

```
POST /api/pricing/quotes/{session_id}/snapshot/
→ { snapshot_id, final_price, currency }
```

Pass `snapshot_id` to the order creation endpoint so the order is locked to this price.

### Handoff URL pattern

```
/auth/register?session_id={session_id}          # anonymous user → register first
/client/orders/new?session_id={session_id}      # logged-in client → go straight to order form
```
