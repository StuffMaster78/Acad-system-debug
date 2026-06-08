# Admin User Guide

**Last Updated**: June 2026 (rev 2)

Admin manages a single website (tenant). For cross-website controls see the [Superadmin User Guide](SUPERADMIN_USER_GUIDE.md). For the full order state machine see [ORDER_LIFECYCLE.md](../ORDER_LIFECYCLE.md).

---

## Quick Reference

| Task | Where |
|---|---|
| Submit an in-progress order for QA | Order detail → Staff Actions Panel → Submit for QA |
| Place an order on hold | Order detail → Staff Actions Panel → Place on hold |
| Assign a writer | Order detail → Staffing tab → Assign from bid |
| Handle a dispute | `/admin/disputes` → dispute detail → Apply resolution |
| Cancel an order | Order detail → Staff Actions Panel → Cancel order |
| View overdue and stuck orders | `/admin/operations` |
| Approve a writer application | `/admin/applications` → detail → Approve |

---

## Table of Contents

1. [Getting Started](#1-getting-started)
2. [Dashboard](#2-dashboard)
3. [Orders List](#3-orders-list)
4. [Order Detail Page](#4-order-detail-page)
5. [Staff Actions Panel](#5-staff-actions-panel)
6. [Operations Command Center](#6-operations-command-center)
7. [Writer Applications and Vetting](#7-writer-applications-and-vetting)
8. [Clients](#8-clients)
9. [Writers](#9-writers)
10. [Disputes](#10-disputes)
11. [Reviews](#11-reviews)
12. [QA Checklists](#12-qa-checklists)
13. [Payments and Financials](#13-payments-and-financials)
14. [Feedback and Requests](#14-feedback-and-requests)
15. [Changelog](#15-changelog)
16. [Content](#16-content)
17. [Loyalty and Rewards](#17-loyalty-and-rewards)
18. [Config Hub](#18-config-hub)
19. [Audit Log](#19-audit-log)
20. [Payment Reminders](#20-payment-reminders)

---

## 1. Getting Started

Navigate to the staff portal domain and log in with your admin credentials. Admin accounts are scoped to one website — you see data only for the website assigned to your account.

### Navigation structure

| Group | Sections |
|---|---|
| Overview | Dashboard, Analytics |
| Orders | Orders list, Operations Command Center |
| People | Clients, Writers, Applications, Vetting |
| Money | Payments, Payment Disclosure, Payment Reminders, Refunds, Compensation, Financial Center, Ledger, Discounts |
| Quality | Disputes, Reviews, QA Checklists |
| Content | Content, Publishing, Newsletters |
| Engagement | Feedback & Requests, Changelog, Loyalty, Rewards |
| Platform | Config Hub, Portal Definitions, Audit Log, Access Control |
| System | Support Tickets, Email Delivery |

---

## 2. Dashboard

KPI cards and recent activity:

- Active orders (in_progress + qa_review + submitted)
- Open disputes and dispute rate
- Revenue collected this month
- Writers with active assignments
- Pending writer applications
- Recent activity feed: status changes, new disputes, completed orders

---

## 3. Orders List

**URL**: `/admin/orders`

### Search and filter

- Search by order ID, client keyword, or writer ID
- Filter by status, date range, assigned/unassigned, academic level, service type
- Filters stack (AND logic)

### Saved View Presets

Save any filter combination as a named preset. The preset strip appears above the filters. Examples:

- "Overdue in progress" — status=in_progress, past deadline
- "Unassigned paid" — status=paid or ready_for_staffing, no writer
- "Disputed this month" — status=disputed, date range=this month

To save: set filters → **Save view** → name it. To load: click the preset chip. To delete: hover → ✕.

---

## 4. Order Detail Page

Click any order to open the detail page.

### Page structure

```
OrderHeader          ← status badge, masked IDs, deadline, contextual banners
OrderSummaryCards    ← key fields at a glance
Staff Actions Panel  ← action buttons (staff only)
OrderTabs
[Tab content]
```

### Header banners (appear automatically)

| State | Banner |
|---|---|
| created / unpaid | Sky-blue: payment required |
| paid / ready_for_staffing | Indigo: finding a writer |
| on_hold | Amber: order is on hold |
| disputed | Rose: dispute open — respond within SLA |
| submitted | Teal: approve delivery prompt (client-visible) |
| revision_requested | Orange: revision in progress |
| cancelled | Slate: order cancelled |
| refunded | Emerald: payment refunded |
| archived | Slate: archived, read-only |

### Tabs

| Tab | Purpose |
|---|---|
| Details | Full requirements, client info, special instructions |
| Files | All attachments grouped into 5 sections (see below) |
| Messages | Threaded communication: client, writer, staff |
| Payments | Payment timeline, wallet transactions, refund records |
| Staffing | Current assignment, writer bids, pending reassignment |
| Revisions | Revision requests: scope, reason, approve/reject |
| Quality | QA checklist results |
| Timeline | Every event in chronological order |
| Audit | Security events for this order |

**Terminal state tab dimming**: when status is `cancelled`, `refunded`, or `archived`, Staffing, Files, Messages, Revisions, and Quality tabs are greyed. Details, Timeline, Audit, and Payments remain active.

### Files tab

| Section | Visibility | Contents |
|---|---|---|
| Client materials | All participants | Requirements files from client |
| Writer guides | Writer + Staff | Style sheets, rubrics, internal guides |
| Drafts & deliverables | All participants | Writer's submitted work |
| Revision files | All participants | Files from revision cycles |
| Internal files | Staff only | QA documents, admin notes |

Each tile shows file name, upload date, uploader role, and visibility badge. Staff can detach a file (X button) if it was uploaded to the wrong section.

---

## 5. Staff Actions Panel

Appears above the tabs on every order detail page for admin, superadmin, support, and editor roles.

### Panel layout

- Current status badge and your role badge
- **Available action buttons** — actions executable right now
- **State guide** toggle — inline reference table of all 16 states and role permissions
- **Blocked actions** (collapsible) — blocked-but-eligible actions with explanations

### Actions available to admin

| Action | When available | Input |
|---|---|---|
| Submit for QA | `in_progress` or `revision_requested`, no active hold | Confirm only |
| Approve delivery | `qa_review` | Confirm only |
| Return to writer | `qa_review` or `revision_requested` | Return reason (required) |
| Approve order | `submitted` or `completed`, not yet approved | Confirm only |
| Place on hold | Most active states, no active hold | Hold reason (required) |
| Release hold | Active hold exists | Confirm only |
| Open dispute | `in_progress`, `submitted`, `completed`, no open dispute | Dispute reason (required) |
| Cancel order | Per cancellation policy | Reason (required, irreversible warning shown) |
| Archive | `completed`, no open dispute | Confirm only |
| Request reassignment | Writer assigned, no pending reassignment | Reason (required) |

**One-click actions** (Submit for QA, Approve delivery, Approve order, Release hold, Archive): click → confirm bar → Yes, proceed.

**Form actions** (Return to writer, Place on hold, Open dispute, Cancel, Reassign): click → input form expands → fill reason → submit. On success, green bar appears and order re-fetches automatically.

### Blocked action examples

- Submit for QA: "Order is on hold and cannot be submitted."
- Open dispute: "An active dispute is already open on this order."
- Request revision: "Order has been approved — the revision window is closed."

---

## 6. Operations Command Center

**URL**: `/admin/operations`

Real-time triage for all active orders needing attention.

### Health bar

Percentage of active orders with no issues. Below 80% warrants attention.

### KPI strip

| Tile | Counts |
|---|---|
| Total active | Any non-terminal state |
| Overdue | Past writer_deadline |
| On hold | Active hold |
| Disputed | Active dispute |
| Unassigned | paid/ready_for_staffing, no writer |
| In QA | `qa_review` status |
| Stuck | `in_progress`, no activity >8h |
| Escalated | Disputes escalated to superadmin |

Click a tile to filter the list to that category.

### Item cards

Left border color: red (overdue), amber (hold), rose (dispute), slate (stuck), indigo (escalated).

Each card: order ID, status badge, deadline countdown, masked writer and client IDs.

Buttons per card:
- **Triage** dropdown: Acknowledge / Snooze 24h / View history / Resolve
- **Claim / Release**: assign to yourself or release
- **Open →**: go to full order detail

### Show resolved toggle

Enable to include recently resolved items. Off by default.

---

## 7. Writer Applications and Vetting

### Applications (`/admin/applications`)

1. Open a pending application
2. Review personal statement, CV, portfolio links
3. Optionally assign a vetting quiz
4. **Approve**: writer account created, onboarding email sent
5. **Reject**: enter reason (saved for records, sent to applicant)

### Writer Vetting (`/admin/vetting`)

1. From application detail → **Assign quiz** → select template
2. Writer receives quiz link
3. View results: score and per-question breakdown
4. Results inform your approval decision

---

## 8. Clients

**URL**: `/admin/clients`

- Search by name, email, or client ID
- Filter by status (All / Active / Suspended / Blacklisted), spending tier, date joined
- Click a row to open the client detail panel; click **Full profile** to go to the full profile page

### Client profile (`/admin/clients/:id`)

The full profile page shows:

- **Header strip**: email, phone number, website, join date, last login, account status
- **Contact information sidebar**: email, phone, username, website
- **Tabs**: Overview (spend, orders, wallet), Orders, Special Orders, Classes, Payments & Wallet, Activity, Profile Requests
- **Profile Requests tab**: full history of profile update requests (name, email, timezone changes) with status (pending / approved / rejected)
- **Account controls**: suspend, unsuspend, unlock, kick out, reset password, change role

---

## 9. Writers

**URL**: `/admin/writers`

- Search by name, writer ID, or level
- Filter by level, status (active / suspended / inactive), assignment count
- Click a row to open the writer detail panel (pen name, level, verification status, discipline state, capacity, availability, warnings, strikes)
- Click **Full profile** to open the full writer profile page with assignment history, performance stats, compensation history, reviews, quiz results, and disciplinary notes

> **Note**: writers must have a `WriterProfile` record (created via `seed_profiles` or the application process) for the Full profile button to appear.

---

## 10. Disputes

**URL**: `/admin/disputes`

### Dispute list

Active / resolved tabs. Rows show: order ID, reason excerpt, days open, status.

### Handling a dispute

1. Open dispute → read reason and order timeline
2. Review Messages tab on the order for context
3. Choose resolution:

| Type | When to use |
|---|---|
| Extend deadline | Writer needs more time; quality is on track |
| Reassign writer | Writer cannot complete the work |
| Full refund | Work undeliverable or grossly unsatisfactory |
| Partial refund | Work delivered but partially unsatisfactory |
| No action | Filed in error or resolved informally |

4. Apply resolution — parties notified automatically
5. Close the dispute

### Escalating to superadmin

If the situation is beyond your authority, click **Escalate** on the dispute. It moves to the superadmin's escalated queue.

---

## 11. Reviews

**URL**: `/admin/reviews`

Client reviews of writer performance.

- Filter by rating, approval status, date
- **Approve**: makes review public on writer's profile
- **Shadow**: hides from public, keeps in system
- **Flag**: marks for further investigation

Reviews are not shown on writer profiles until approved.

---

## 12. QA Checklists

### Managing templates

1. `/admin/config` → QA Checklists
2. **New template** → add items (each has label, pass/fail type, optional guidance text)
3. Assign template to one or more service types
4. Editors see the checklist in the Quality tab when reviewing orders of that type

### Viewing results

Order detail → Quality tab: pass/fail per item, editor notes, submission timestamp. Previous cycles archived below the current one.

---

## 13. Payments and Financials

### Payments (`/admin/payments`)

- All transactions for this website
- Filter by status (succeeded / failed / pending), date, amount
- Click transaction for detail: gateway reference, amount, fees, associated order
- Saved view presets available

### Payment Disclosure (`/admin/payment-disclosure`)

Configure the billing statement text shown to clients before and after payment. Sets the brand name, processor display name, statement descriptor, and client disclosure text. Clients see this on the order form and in payment confirmation screens.

### Payment Reminders (`/admin/payment-reminders`)

Configure automated reminders sent to clients who have not paid for an order. See [Section 20](#20-payment-reminders) for full details.

### Refunds (`/admin/refunds`)

- Pending refunds queue
- **Process refund**: triggers gateway refund via Stripe
- **Reject refund**: enter reason, client notified

### Compensation (`/admin/compensation`)

- Pending `CompensationEvent` records for this website's writers
- Mark individual events as paid
- For bulk payouts use Writer Pay (superadmin)

### Financial Center (`/admin/finance`)

Revenue overview: collected, outstanding, refunded. Writer compensation vs. revenue ratio.

### Ledger (`/admin/ledger`)

Full financial event log: payments, refunds, wallet transactions, compensation events. Filter by event type, date, user.

---

## 14. Feedback and Requests

**URL**: `/admin/feedback`

Platform feedback from clients and writers.

### Feedback statuses

| Status | Meaning |
|---|---|
| new | Not yet reviewed |
| under_review | Being assessed |
| planned | Accepted for future work |
| in_progress | Being built |
| done | Shipped |
| rejected | Will not be implemented |
| duplicate | Merged with another item |

### Triage workflow

1. Open item
2. Change status via **Triage** dropdown
3. **Respond**: reply visible to submitter
4. **Mark duplicate**: link to original item

Saved view presets available.

---

## 15. Changelog

**URL**: `/admin/changelog`

Release notes visible to portal users.

### Creating an entry

1. **New entry**
2. Fill in: title, body (markdown), version (optional), portal surface (client / writer / staff), is pinned
3. **Save as draft** or **Publish**

Pinned entries appear first. Draft entries are not visible to users. Use **Unpublish** to revert a published entry to draft.

---

## 16. Content

### Content (`/admin/content`)

**Legal documents**: versioned T&C, Privacy Policy, Refund Policy. Activate a version to publish; previous versions archived.

**Help center**: categories with audience filter, articles with rich text editor. Featured articles appear on Help Center home.

**Static pages**: informational pages at `/lp/<slug>` with WYSIWYG and SEO meta fields.

### Publishing (`/admin/publishing`)

Blog articles and service pages via Wagtail CMS (`/cms-admin/`). SEO landing pages directly in the publishing desk.

### Content graph (`/admin/content-graph`)

Four-tab analytics: Pillars overview, Funnel (awareness/consideration/conversion), Freshness alerts, Content health (top and worst performers).

### Newsletters (`/admin/newsletters`)

Campaign management, subscriber list, send history, open/click rates.

---

## 17. Loyalty and Rewards

### Loyalty (`/admin/loyalty`)

- Tier configuration (Bronze / Silver / Gold / Platinum)
- Points rules: points per dollar spent, per order completed, per referral
- Tier thresholds
- Analytics: tier distribution, points earned/redeemed per period

### Rewards (`/admin/rewards`)

- Reward catalog: discounts, free pages, priority support
- Create/edit/archive reward items
- Redemption history

### Discounts (`/admin/discounts`)

- Discount codes: percentage or fixed, expiry, usage limits
- Automatic discounts by loyalty tier or order value
- Usage stats per code

---

## 18. Config Hub

**URL**: `/admin/config`

### Service catalog

Central setup for paper, design, diagram, and combo orders. The service catalog, add-ons, upsells, and pricing dimensions feed public calculators, the client order form, and staff order review screens.

### Pricing rules

- Deadline bands and rush multipliers
- Academic-level, paper-type, subject, and work-type rates
- Writer-level rates and writer preference fees
- Diagram complexity and design-service pricing
- Add-ons, upsells, minimum order price, and currency

### Class and special-order configs

Class and SPO setup are available from the sidebar:

- `/admin/class-config` for class packages, durations, workload presets, payment policies, and writer-safe fields
- `/admin/special-order-config` for predefined special-order templates, milestones, lifecycle presets, and writer pay rules

Use these pages to hide business logic from clients while still giving them clear package, milestone, and scope choices.

### Special days

Holiday calendar with custom pricing rules. Supports floating-date rules. 40 holidays pre-seeded (protected from deletion).

### Screened words

Content moderation list. Words trigger review on order submission.

### System settings

- **Revision window days**: days after delivery a client can request revision
- **Auto-complete delay**: days before submitted order auto-completes without client response
- **Max bid count**: max simultaneous writer bids per order

---

## 19. Audit Log

**URL**: `/admin/audit`

Security and operational events for this website.

- **Severity**: info / warning / critical
- **Service**: auth, orders, payments, wallets, disputes, staffing, config
- **Sensitive**: role changes, suspensions, large payments
- **Search**: free-text across event descriptions and actor names

Expand any row to see: actor ID and role, before/after diff (red = before, green = after), correlation ID, full metadata.

**Export**: CSV of filtered events for compliance or incident investigation.

**Saved view presets**: save filter combos (e.g. "Critical events today", "Auth events this week", "Config changes").

---

## 20. Payment Reminders

**URL**: `/admin/payment-reminders`

Configure automated messages sent to clients who have unpaid orders. The system sends reminders based on how much of the deadline window has elapsed.

### Stats strip

| Tile | Meaning |
|---|---|
| Total Configs | Number of reminder configurations defined |
| Active | Configs that are currently enabled |
| Sent (last 7 days) | Reminders dispatched in the past week |

### Reminders tab

Each reminder fires when a specified percentage of the order's deadline window has elapsed (e.g., 30% = "a third of the time to deadline has passed").

**Creating a reminder:**

1. Click **Add Reminder**
2. Enter a name (e.g., "First Reminder", "Final Warning")
3. Set the **Deadline % elapsed** (0–100): when to send relative to order creation vs. deadline
4. Write the **Message** body (shown in the notification and email)
5. Optionally set an **Email subject**
6. Toggle **Send as notification** and/or **Send as email**
7. Set **Display order** (lower numbers sort first)
8. Enable **Active** and click **Create**

**Best practice**: configure at least two reminders — one early (e.g., 30%) and one urgent (e.g., 80%).

### Deletion Messages tab

Messages sent when an unpaid order is automatically cancelled after the deadline has elapsed. Configure at least one active deletion message per website.

### Sent Log tab

Read-only history of all reminders dispatched: which config fired, which client received it, which order, and through which channels (notification / email).

---
