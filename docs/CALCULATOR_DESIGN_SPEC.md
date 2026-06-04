# Pricing Calculator — Frontend Design Specification

This document covers everything a frontend developer or designer needs to build, extend, or re-skin the pricing calculators. Three calculator types exist in the backend. One (`PaperOrderCalculator`) is fully wired. Two (`DesignOrderCalculator`, `DiagramOrderCalculator`) have complete backend endpoints but no frontend widget yet.

---

## Table of Contents

1. [How the System Works](#1-how-the-system-works)
2. [API Reference](#2-api-reference)
3. [Calculator 1 — Paper Orders (built)](#3-calculator-1--paper-orders-built)
4. [Calculator 2 — Design Orders (needs widget)](#4-calculator-2--design-orders-needs-widget)
5. [Calculator 3 — Diagram Orders (needs widget)](#5-calculator-3--diagram-orders-needs-widget)
6. [Price Line Breakdown](#6-price-line-breakdown)
7. [Optional Enhancements (already in backend)](#7-optional-enhancements-already-in-backend)
8. [Session Handoff to Order Form](#8-session-handoff-to-order-form)
9. [CMS Block Embedding](#9-cms-block-embedding)
10. [UX Rules](#10-ux-rules)
11. [Component Props Reference](#11-component-props-reference)

---

## 1. How the System Works

Every calculator follows the same two-phase pattern regardless of type:

```
Phase 1 — ESTIMATE
  User changes any input
        ↓
  (350ms debounce)
        ↓
  POST /api/pricing/quotes/{type}/start/
        ↓
  Backend returns: { session_id, estimated_min_price, estimated_max_price, currency }
        ↓
  Show range: "$28 – $35"    ← live, updates on every change

Phase 2 — EXACT
  User clicks "Get exact price"
        ↓
  POST /api/pricing/quotes/{type}/{session_id}/update/
        ↓
  Backend returns: { calculated_price, currency, lines[] }
        ↓
  Show exact price + itemised breakdown

Phase 3 — HANDOFF
  User clicks "Place Order"
        ↓
  Navigate to /auth/register?session_id={session_id}
        ↓
  Order form reads session_id and pre-fills all fields + locks the price
```

**No authentication required for phases 1 and 2.** The session is anonymous and lives in the backend by `session_id` (a UUID). This means the calculator works on public pages, blog posts, and landing pages.

---

## 2. API Reference

### Config endpoints (public, no auth, load once on mount)

| Endpoint | Returns | Used by |
|---|---|---|
| `GET /api/order-configs/academic-levels/` | `ConfigOption[]` | Paper |
| `GET /api/order-configs/paper-types/` | `ConfigOption[]` | Paper |
| `GET /api/order-configs/writer-deadline-configs/` | `DeadlineConfig[]` | All |
| `GET /api/order-configs/subjects/` | `ConfigOption[]` | Paper (optional) |
| `GET /api/order-configs/types-of-work/` | `ConfigOption[]` | Paper (optional) |

### Quote endpoints (anonymous, stateful by session_id)

| Endpoint | Method | Phase |
|---|---|---|
| `/api/pricing/quotes/paper/start/` | POST | Estimate |
| `/api/pricing/quotes/paper/{session_id}/update/` | POST | Exact |
| `/api/pricing/quotes/design/start/` | POST | Estimate |
| `/api/pricing/quotes/design/{session_id}/update/` | POST | Exact |
| `/api/pricing/quotes/diagram/start/` | POST | Estimate |
| `/api/pricing/quotes/diagram/{session_id}/update/` | POST | Exact |
| `/api/pricing/quotes/{session_id}/snapshot/` | POST | Lock price at checkout |

### TypeScript interfaces

```typescript
// Shared option shape (used for levels, types, subjects, deadlines)
interface ConfigOption {
  id: number;
  name: string;
  code: string;
  is_active?: boolean;
  display_order?: number;
}

interface DeadlineConfig extends ConfigOption {
  hours?: number;         // number of hours this option represents
  is_urgent?: boolean;    // true → show urgency indicator (⚡)
}

// Phase 1 response (estimate range)
interface QuoteStartResponse {
  session_id: string;               // UUID — keep this for phase 2
  status: string;
  current_step: number;
  estimated_min_price: string | null;
  estimated_max_price: string | null;
  currency: string;                 // e.g. "USD"
  suggestions?: Suggestion[];       // warnings (e.g. tight deadline)
}

// Phase 2 response (exact price + breakdown)
interface QuoteUpdateResponse {
  session_id: string;
  status: string;
  current_step: number;
  calculated_price: string | null;  // e.g. "32.00"
  currency: string;
  lines: PriceLine[];
  suggestions?: Suggestion[];
}

// One line in the price breakdown
interface PriceLine {
  line_type: "base" | "multiplier" | "fixed_fee" | "addon" | "discount" | "total";
  code: string;          // e.g. "academic_level", "deadline", "addon_plagiarism"
  label: string;         // human-readable, e.g. "Academic level (Master's)"
  amount: string;        // decimal string, e.g. "4.00" — can be negative for discounts
  metadata: Record<string, unknown>;  // includes "multiplier" for multiplier lines
}

// Warning that deadline is tight or other advisory
interface Suggestion {
  type: "deadline_adjustment" | "rush_order";
  message: string;
  recommended_deadline_hours?: number;
}

// Snapshot response (at checkout — locks the price)
interface PricingSnapshotResponse {
  snapshot_id: number;
  final_price: string;
  currency: string;
}
```

---

## 3. Calculator 1 — Paper Orders (built)

**File**: `src/components/cms/PricingCalculator.vue`

**What it prices**: Essays, research papers, coursework, dissertations — anything priced per page.

### Inputs

| Field | Control | Default | Notes |
|---|---|---|---|
| Academic level | `<select>` | Undergraduate | Loaded from API |
| Type of paper | `<select>` | Essay | Loaded from API |
| Pages | Number input with +/− buttons | 1 | Range: 1–500. Shows word estimate below (pages × 275) |
| Deadline | `<select>` | 48h | Loaded from API; urgent options show ⚡ |
| Spacing | Toggle (single / double) | Double | Affects word count display |

### Payload sent to API

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

### What the backend applies (in order)

1. `base_price_per_page × pages` → base amount
2. `spacing_multiplier` (double vs single — configured per website)
3. `paper_type_rate.multiplier` (e.g. dissertation = 1.4×)
4. `work_type_rate.multiplier`
5. `academic_level_rate.multiplier` (e.g. PhD = 1.6×)
6. `subject_rate.multiplier` (e.g. medicine subject category = 1.2×)
7. `deadline_rate.multiplier` (the rush premium — 3h = 2.0×, 48h = 1.0×)
8. `minimum_paper_order_charge` floor applied after all multipliers
9. Total line appended

### Current widget appearance

```
┌─────────────────────────────────────────────────────┐
│ ■  Get your instant price                            │ ← dark gradient header
│    No account needed — see your price in seconds.    │
├─────────────────────────────────────────────────────┤
│  Academic level      │  Type of paper               │
│  [Undergraduate ▼]   │  [Essay       ▼]             │
│                                                     │
│  Pages               │  Deadline                    │
│  [−] [ 3 ] [+]       │  [2 days      ▼]             │
│  ≈ 825 words · double spaced                        │
├─────────────────────────────────────────────────────┤
│  Estimated price                                    │
│  $22.00 – $35.00  USD                               │
│  Final price may vary by subject and writer level.  │
│                                                     │
│  [ Get exact price ]    [ Place Order → ]           │
│                                                     │
│       No credit card required · 100% confidential   │
└─────────────────────────────────────────────────────┘
```

After "Get exact price":

```
├─────────────────────────────────────────────────────┤
│  $28.50  USD                                        │
│  ┌─────────────────────────────────────────────┐   │
│  │ Base price for 3 pages              $16.50  │   │
│  │ Paper type (Essay)                   $0.00  │   │
│  │ Academic level (Undergraduate)       $0.00  │   │
│  │ Subject (General)                    $0.00  │   │
│  │ Deadline (2 days)                    $0.00  │   │
│  │ Total                               $28.50  │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
│                        [ Place Order → ]            │
└─────────────────────────────────────────────────────┘
```

---

## 4. Calculator 2 — Design Orders (needs widget)

**Backend endpoints**: `/api/pricing/quotes/design/start/` and `/api/pricing/quotes/design/{session_id}/update/`

**What it prices**: Presentation slides, infographics, posters, book covers — anything priced per unit/piece.

### Inputs

| Field | Control | Notes |
|---|---|---|
| Number of slides / pieces | Number stepper | Min 1 |
| Deadline | `<select>` | Same deadline options as paper |
| Add-ons | Checkbox list | Loaded from backend (e.g. "Source file included", "Rush revision") |

### Payload

```json
{
  "service_code": "presentation_design",
  "quantity": 10,
  "deadline_hours": 48,
  "selected_addon_codes": ["source_file_included"]
}
```

### What the backend applies

1. `service.base_price × quantity` (or `service.flat_rate` if non-quantity service)
2. Deadline multiplier (same `DeadlineRate` bands as paper)
3. Each selected addon: flat fee added

### Suggested widget

```
┌────────────────────────────────────────────────────┐
│ 🎨  Presentation Design Price                       │
├────────────────────────────────────────────────────┤
│  Number of slides                                   │
│  [−] [ 10 ] [+]                                     │
│                                                     │
│  Deadline                                           │
│  [48 hours ▼]                                       │
│                                                     │
│  Add-ons                                            │
│  ☑ Source file (Figma/PowerPoint editable)  +$5.00 │
│  ☐ Priority revision                        +$8.00 │
├────────────────────────────────────────────────────┤
│  Estimated price                                    │
│  $45.00 – $72.00  USD                               │
│  [ Get exact price ]    [ Place Order → ]           │
└────────────────────────────────────────────────────┘
```

---

## 5. Calculator 3 — Diagram Orders (needs widget)

**Backend endpoints**: `/api/pricing/quotes/diagram/start/` and `/api/pricing/quotes/diagram/{session_id}/update/`

**What it prices**: Charts, flowcharts, concept maps, org charts, process diagrams — priced by quantity and complexity.

### Inputs

| Field | Control | Notes |
|---|---|---|
| Number of diagrams | Number stepper | Min 1 |
| Complexity | Radio or `<select>` | `simple` / `moderate` / `complex` — loaded from `DiagramComplexityRate` |
| Deadline | `<select>` | Same deadline options |
| Add-ons | Checkbox list | Same addon model |

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

### What the backend applies

1. `base_price × quantity`
2. `DiagramComplexityRate.multiplier` (e.g. simple = 1.0×, moderate = 1.3×, complex = 1.7×)
3. Deadline multiplier
4. Addons

### Suggested widget

```
┌────────────────────────────────────────────────────┐
│ 📊  Diagram & Chart Price                           │
├────────────────────────────────────────────────────┤
│  Number of diagrams                                 │
│  [−] [ 3 ] [+]                                      │
│                                                     │
│  Complexity                                         │
│  ○ Simple    ● Moderate    ○ Complex                │
│  Basic flowchart or bar chart                       │
│                                                     │
│  Deadline                                           │
│  [3 days ▼]                                         │
├────────────────────────────────────────────────────┤
│  Estimated price                                    │
│  $30.00 – $48.00  USD                               │
│  [ Get exact price ]    [ Place Order → ]           │
└────────────────────────────────────────────────────┘
```

---

## 6. Price Line Breakdown

When the user requests an exact price, the API returns a `lines[]` array. Each line has a `line_type` which tells you how to display it:

| `line_type` | Meaning | How to render |
|---|---|---|
| `base` | Starting price from page/unit rate | Normal row |
| `multiplier` | A multiplier was applied (level, deadline, etc.) | Show as `+$X.XX` or `−$X.XX` delta; metadata includes `"multiplier": "1.40"` |
| `fixed_fee` | Flat fee added (addon, preferred writer, etc.) | Show as `+$X.XX` |
| `addon` | Named add-on service | Show with addon name |
| `discount` | Discount applied | Show as `−$X.XX` in green |
| `total` | Grand total | Bold, slightly larger, separator above |

### Visual treatment

```
Base price for 3 pages             $16.50
Paper type (Dissertation)          + $6.60   ← multiplier, amber if > 0
Academic level (PhD)               + $5.28   ← multiplier
Deadline (6 hours) ⚡              + $7.92   ← urgent: show in amber/orange
Plagiarism report                  + $5.00   ← addon
─────────────────────────────────────────
Total                             $41.30     ← bold
```

**Multiplier lines with amount = $0.00** (meaning 1.0× — no change): hide these entirely or show in muted grey. Don't show "Essay × 1.0 = +$0.00" — it adds noise.

**Negative amounts** (discounts): render in emerald green.

**Urgent deadlines**: if `deadline_rate.is_urgent` is true for the selected deadline, highlight the deadline line in amber.

---

## 7. Optional Enhancements (already in backend)

These fields exist in the `PaperQuotePayload` and are fully handled by the backend. The widget doesn't expose them yet. Add them as your design evolves:

### Writer level upgrade

```json
"writer_level_code": "professional"
```

Adds a flat fee or multiplier depending on the writer level config. Typical UX: a "Writer level" selector in the calculator with labels like "Standard", "Professional (+ $8.00)", "Expert (+ $15.00)". Exact amounts come from `WriterLevelRate` on the backend — fetch them alongside academic levels on mount.

### Preferred writer fee

```json
"preferred_writer_id": "WR-1001"
```

Adds a flat fee configured in `WebsitePricingProfile.preferred_writer_fee`. Only relevant post-login when a client has worked with a writer before. Not shown in the public calculator — add to the order confirmation flow instead.

### Analysis level

```json
"analysis_level": "advanced"
```

An additional multiplier for how deeply the paper needs to analyse its sources. Rarely surfaced in the calculator UI — more commonly set during order creation.

### Add-ons (all calculators)

```json
"selected_addon_codes": ["plagiarism_report", "table_of_contents", "abstract"]
```

Each is a `ServiceAddon` record with `addon_code`, `name`, `flat_amount`. Load them from the backend and display as checkboxes below the main inputs. Show the `+$X.XX` price next to each checkbox so clients can see the cost before clicking. Addons update the live estimate when checked/unchecked.

---

## 8. Session Handoff to Order Form

After phase 2, `session_id` holds a server-side snapshot of all the pricing inputs and the computed price. When the user clicks "Place Order", pass it to the order creation form:

```
/auth/register?session_id=3f7a2b91-...
```

Or for already-logged-in users:
```
/client/orders/new?session_id=3f7a2b91-...
```

The order form reads this and:
1. Pre-fills page count, deadline, paper type, academic level
2. Calls `POST /api/pricing/quotes/{session_id}/snapshot/` to lock in the price
3. The `snapshot_id` returned is stored on the order so the price is frozen

**What happens if session expires**: sessions are not persisted indefinitely. If the user takes more than ~30 minutes between estimate and order, re-run the estimate on order form load and show the current price. Do not show a "Your price has changed" warning unless the total has actually changed.

---

## 9. CMS Block Embedding

Any Wagtail page (blog post, landing page, service page) can embed a calculator via a StreamField block. The block type is `calculator` and it renders `PricingCalculator.vue` with configurable props.

### CMS block fields (set in Wagtail admin)

| Field | Type | Default | Effect |
|---|---|---|---|
| `title` | string | "Get your instant price" | Heading in dark header |
| `subtitle` | string | "No account needed…" | Sub-text |
| `service_code` | string | `standard_paper` | Which backend service to price |
| `default_pages` | integer | 1 | Pre-selected page count |
| `default_deadline_hours` | integer | 48 | Pre-selected deadline |
| `default_academic_level_code` | string | (first option) | Pre-selected level |
| `default_paper_type_code` | string | (first option) | Pre-selected type |
| `show_line_breakdown` | boolean | true | Whether to show itemised lines |
| `cta_text` | string | "Place Order" | CTA button label |
| `cta_url` | string | `/auth/register` | CTA button destination |

### Placement recommendations

- **Homepage hero** — full-width, prominent. All defaults. Best conversion.
- **Blog post sidebar** — narrow widget. Hide line breakdown (`show_line_breakdown: false`). Use article's subject as default.
- **Service page** — pre-set `service_code`, `default_academic_level_code`, `default_paper_type_code` to match the page's service. Reduces friction.
- **Pricing page** — full breakdown visible. No pre-selections — let users explore all combinations.

---

## 10. UX Rules

### Debounce
The estimate call fires 350ms after the last input change. Do not fire on every keystroke. The debounce is already implemented — do not remove it.

### Loading state
Show a spinning icon next to the price range while a quote fetch is in flight. Do not disable the inputs or show a full-page spinner — the form should remain interactive.

### Deadline urgency signal
If the selected deadline has `is_urgent: true`:
- Show ⚡ next to its name in the dropdown
- After exact price, show the deadline line in amber in the breakdown
- Show a soft advisory: "This is a rush deadline and incurs a higher rate."

### Tight deadline warning
If the backend returns `suggestions` with `type: "deadline_adjustment"`:
- Show a non-blocking amber notice: "This deadline may be tight for {N} pages. We recommend at least {X} hours."
- Include a "Use recommended deadline" button that sets `deadlineHours` to `suggested.recommended_deadline_hours` and re-fetches

### Price changes between estimate and exact
The estimate is intentionally a range (1.0× to 1.6× base). When the user clicks "Get exact price" and the exact price falls within the range, no special treatment is needed. If for any reason the exact price is outside the range, do not show an error — just display the exact price.

### Zero-amount breakdown lines
Hide any breakdown line where `amount == "0.00"`. These represent 1.0× multipliers (no change) and add visual noise.

### Currency symbol
The currency is returned by the API (e.g. `"USD"`, `"GBP"`). Use the correct symbol, not hardcoded `$`. A simple map is sufficient: `{ USD: "$", GBP: "£", EUR: "€", KES: "KSh" }`.

### Mobile layout
The two-column grid collapses to a single column below `sm:` breakpoint. This is already handled. Ensure the stepper buttons (−/+) are large enough to tap: minimum `40×40px`.

---

## 11. Component Props Reference

This is the full prop interface for `PricingCalculator.vue`:

```typescript
interface PricingCalculatorProps {
  // Display
  title?: string;                     // Default: "Get your instant price"
  subtitle?: string;                  // Default: "No account needed…"

  // Calculator type
  serviceCode?: string;               // Default: "standard_paper"
                                      // Other valid values depend on backend ServiceConfig

  // Pre-selected values
  defaultPages?: number;              // Default: 1
  defaultDeadlineHours?: number;      // Default: 48
  defaultAcademicLevelCode?: string;  // Default: "" (auto-selects first active)
  defaultPaperTypeCode?: string;      // Default: "" (auto-selects first active)

  // Display options
  showLineBreakdown?: boolean;        // Default: true

  // CTA
  ctaText?: string;                   // Default: "Place Order"
  ctaUrl?: string;                    // Default: "/auth/register"
                                      // Append ?session_id={id} programmatically
}
```

### To add the Design or Diagram calculators

Create `DesignCalculator.vue` and `DiagramCalculator.vue` following the same two-phase pattern. The only differences are:

1. Different payload fields (quantity + complexity instead of pages + level)
2. Different API endpoints (`/quotes/design/` or `/quotes/diagram/`)
3. No academic level or paper type dropdowns
4. Diagram calculator adds a complexity selector (simple / moderate / complex)

The config loading, estimate range display, exact breakdown display, session handoff, debounce, and CTA are identical to the paper calculator. Extract the shared pieces into a `useQuoteSession(type)` composable to avoid duplication.

```typescript
// Suggested composable signature
function useQuoteSession(type: "paper" | "design" | "diagram") {
  // Returns: { sessionId, estimate, breakdown, quoteLoading, quoteError,
  //            fetchEstimate, getExactPrice }
  // Handles debounce, API calls, error state internally
}
```
