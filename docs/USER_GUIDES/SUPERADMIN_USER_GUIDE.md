# Superadmin User Guide

**Last Updated**: June 2026

Superadmin is the highest privilege role. It has everything the Admin role has, plus cross-website visibility, financial oversight, system-level controls, and handling of escalated disputes. Each section below notes where superadmin differs from admin.

---

## Table of Contents

1. [Getting Started](#1-getting-started)
2. [Dashboard](#2-dashboard)
3. [Order Management](#3-order-management)
4. [Order Detail Page](#4-order-detail-page)
5. [Operations Command Center](#5-operations-command-center)
6. [People Management](#6-people-management)
7. [Finance Center](#7-finance-center)
8. [Writer Pay](#8-writer-pay)
9. [Disputes](#9-disputes)
10. [Reviews](#10-reviews)
11. [Platform Configuration](#11-platform-configuration)
12. [Portal Definitions](#12-portal-definitions)
13. [Audit Log](#13-audit-log)
14. [Analytics](#14-analytics)
15. [System Command Center](#15-system-command-center)
16. [Quick Reference](#16-quick-reference)

---

## 1. Getting Started

Navigate to your assigned superadmin domain and log in. The portal will not load if your account does not have the `superadmin` role.

### Website Selector

A **Website Selector Bar** appears at the top of most list views. Use it to switch between tenants. Some views (Finance Center, Analytics) aggregate all websites. Others (Orders, Writers, Config) are scoped to the selected website.

### Navigation Structure

| Group | Sections |
|---|---|
| Overview | Dashboard, Analytics |
| Orders | Orders list, Operations Command Center |
| People | Clients, Writers, Applications, Vetting |
| Money | Payments, Refunds, Compensation, Financial Center, Ledger, Writer Pay, Discounts |
| Quality | Disputes, Reviews, QA Checklists |
| Content | Content, Publishing, Newsletters |
| Engagement | Feedback & Requests, Changelog, Loyalty, Rewards |
| Platform | Config Hub, Portal Definitions, Audit Log, Access Control |
| System | Support Tickets, Email Delivery, System Command |

---

## 2. Dashboard

Cross-website aggregated KPIs:

- Active orders across all websites
- Total confirmed revenue
- Open disputes count and rate
- Writers with activity in the last 24 hours
- Escalated disputes requiring superadmin action
- Pending writer applications

The recent activity feed shows notable events across all tenants: new disputes, escalations, large payments, completed orders.

---

## 3. Order Management

### Orders List (`/superadmin/orders`)

- Website Selector scopes the list to one tenant
- Search by order ID, client keyword, writer ID
- Filter by status, date range, assigned/unassigned, website
- **Saved View Presets**: save filter combinations as named presets, reload with one click (e.g. "disputed this week", "unassigned >2 days old")
- Click any row to open Order Detail

---

## 4. Order Detail Page

The order detail page is the primary workspace for a single order.

### Page structure

```
OrderHeader          (status badge, masked IDs, deadline, contextual banners)
OrderSummaryCards    (key fields at a glance)
Staff Actions Panel  (action buttons)
OrderTabs
[Tab content]
```

### Header banners

| State | Banner |
|---|---|
| created / unpaid | Sky-blue: "Payment required" |
| paid / ready_for_staffing | Indigo: "Finding a writer" |
| on_hold | Amber: role-specific hold message |
| disputed | Rose: "Dispute open — respond within SLA" |
| cancelled | Slate: "This order has been cancelled" |
| refunded | Emerald: "Payment has been refunded" |
| archived | Slate: "This order is archived and read-only" |

### Staff Actions Panel

Shows all actions available in the current state. For the full reference see [ORDER_LIFECYCLE.md](../ORDER_LIFECYCLE.md).

Superadmin can perform every action: Submit for QA, Approve delivery, Return to writer, Approve order, Place on hold, Release hold, Open dispute, Cancel order, Archive, Request reassignment.

The **State guide** toggle opens an inline reference table of all 16 states and what each role can do.

### Tabs

| Tab | Contents |
|---|---|
| Details | Order metadata, service type, deadlines, client/writer info |
| Files | 5 grouped sections with visibility badges. Staff can detach files (X button). |
| Messages | Threaded communication |
| Payments | Payment history, wallet transactions, refunds |
| Staffing | Current assignment, writer bids, pending reassignment |
| Revisions | Revision requests, approve/reject |
| Quality | QA checklist results |
| Timeline | Full chronological event log |
| Audit | Security events for this order |

**Terminal state tab dimming**: when status is cancelled, refunded, or archived — Staffing, Files, Messages, Revisions, and Quality tabs are greyed and non-clickable. Details, Timeline, Audit, and Payments remain active.

---

## 5. Operations Command Center

**URL**: `/superadmin/operations`

Real-time triage dashboard for all active orders requiring attention.

### Health bar

Percentage of active orders with no issues. Below 80% warrants attention.

### KPI strip (8 tiles)

| Tile | Meaning |
|---|---|
| Total active | Orders not in a terminal state |
| Overdue | Past writer_deadline |
| On hold | Has active hold |
| Disputed | Has active dispute |
| Unassigned | paid/ready_for_staffing with no writer |
| In QA | Status qa_review |
| Stuck | in_progress, no activity >8h |
| Escalated | Disputes escalated to superadmin |

### Item cards

Each card shows: left border color (red=overdue, amber=hold, rose=dispute, slate=stuck), order ID, status badge, deadline countdown, masked writer and client IDs.

Per-card buttons:
- **Triage** dropdown: Acknowledge / Snooze 24h / View history / Resolve
- **Claim / Release**: assign yourself or release
- **Open →**: navigate to full order detail

### Domain sidebar

Breakdown of active items by website. Useful for spotting if one tenant is generating disproportionate issues.

### Show resolved toggle

Off by default. Enable to include recently resolved items.

---

## 6. People Management

### Clients (`/superadmin/clients`)

- List with search, filter by website and status
- Click any client: order history, payment history, wallet balance, loyalty tier, notes

### Writers (`/superadmin/writers`)

- List with search, filter by level and status
- Click any writer: assignment history, performance stats, compensation history, review scores, quiz results, disciplinary notes

### Writer Applications (`/superadmin/writer-applications`)

1. Open pending application
2. Review personal statement, CV, portfolio
3. Optionally assign a vetting quiz (Vetting section)
4. **Approve**: writer account created, onboarding email sent
5. **Reject**: reason saved, applicant notified

### Writer Vetting (`/superadmin/writer-vetting`)

- Assign quiz to applicant from their application page
- View quiz attempt: score, per-question breakdown
- Results inform approval decision

### Access Control (`/superadmin/access`)

- Create/deactivate admin and staff accounts
- Set website scope per admin (which tenants they can access)
- Promote writers to editor role
- Run duplicate scan to detect shared credentials

---

## 7. Finance Center

**URL**: `/superadmin/finance`

Cross-website financial overview.

### Revenue by website

Table showing each tenant: total collected, this month, outstanding (pending_payment), refunded.

### Transaction search

Full-text search across all payment events. Filter by website, date range, payment method, status.

### P&L overview

Aggregated: gross revenue, writer compensation paid out, platform margin.

### Financial events timeline

Chronological log of all significant events with website column: payment.confirmed, refund.issued, wallet.funded, compensation.paid.

---

## 8. Writer Pay

**URL**: `/superadmin/writer-pay`

### Pending compensation

- All `CompensationEvent` records with status `pending`
- Each row: writer ID, order ID, amount, type (base / bonus / tip), due date
- Bulk-select and mark as paid
- Individual: view detail, edit amount, mark paid

### Payout batches

1. Create batch: select date range and website
2. System groups pending events by writer
3. Review batch total
4. Confirm — batch is locked
5. Generate CSV for bank transfer

### Compensation history

- Per-writer timeline of all compensation events
- Filter by writer, date range, type
- Export to CSV

---

## 9. Disputes

**URL**: `/superadmin/disputes`

Superadmin handles escalated disputes and can manage all disputes directly.

### Dispute list

- Active / resolved tabs
- Filter by website, date opened, escalation status
- Escalated tab shows disputes that were elevated from admin

### Dispute detail

Shows: parties (client and writer masked IDs), staff who opened it, timeline of all events, resolution proposals.

### Resolution options

| Type | Effect |
|---|---|
| Extend deadline | Sets new `writer_deadline` on the order |
| Reassign writer | Releases current writer, routes order to pool |
| Full refund | Cancels order, triggers refund |
| Partial refund | Issues credit/partial reversal |
| No action | Closes dispute with explanation |

### Escalation note

Superadmin is the escalation ceiling — there is no further escalation. Disputes marked as escalated in the Operations Command Center require superadmin resolution. Respond within the SLA shown on the dispute card.

---

## 10. Reviews

**URL**: `/superadmin/reviews`

Review moderation across all websites.

- Website Selector or "All websites" view
- **Approve**: makes review public on writer profile
- **Shadow**: hides from public, keeps in system for reference
- **Flag**: marks for further investigation
- Filter by rating, website, approval status, date

---

## 11. Platform Configuration

**URL**: `/superadmin/config`

### Service catalog

Central pricing and order setup for paper, design, diagram, and combo orders. Use the website selector when you need tenant-specific values.

### Pricing rules

- Base rates, minimum order price, currency, and words per page
- Deadline bands, academic-level rates, paper-type rates, subject rates, and work-type rates
- Writer-level rates, diagram complexity, design services, add-ons, and upsells
- Service catalog entries used by public calculators and the client order form

### Class and special-order configs

Class configs and SPO configs remain available from the sidebar:

- `/superadmin/class-config` for class packages, durations, workload presets, payment policies, and writer visibility rules
- `/superadmin/special-order-config` for predefined special-order templates, milestones, writer pay rules, and lifecycle presets

These configs feed the client-facing class and special-order flows; clients select business-friendly options while staff controls the underlying pricing, milestone, and writer-pay logic.

### Special days

Holiday/event calendar with custom pricing rules. Supports floating-date rules (e.g. "last Monday of November"). 40 holidays pre-seeded. Seeded records are protected from accidental deletion.

### Screened words

Content moderation list. Words that trigger review on order submission.

### System settings

Platform defaults: revision window days, auto-complete delay, max bid count. Email sender configuration.

---

## 12. Portal Definitions

**URL**: `/superadmin/portal-definitions`

Each website has up to three portal surfaces: `client`, `writer`, `staff`.

### Per-portal configuration

- **Domain**: hostname for this surface
- **Branding**: logo URL, primary color, company name, support email
- **Feature flags**: enable/disable features per surface
- **Surface type**: controls which navigation items and API endpoints are accessible

Changes take effect on next page load for users on that portal.

---

## 13. Audit Log

**URL**: `/superadmin/audit`

Security and operational events across all websites.

- **Severity filter**: info / warning / critical
- **Service filter**: auth, orders, payments, wallets, disputes, staffing, config
- **Sensitive filter**: role changes, suspensions, large payments
- **Website filter**: one tenant or all

Expand any row to see: actor ID and role, before/after diff for change events (red = before, green = after), correlation ID, full metadata payload.

**Export**: CSV of the filtered event set for compliance or incident investigation.

---

## 14. Analytics

**URL**: `/superadmin/analytics`

### Order analytics

Volume by status, website, time period. Completion rate, revision rate, dispute rate. Average time in each state.

### Writer performance

Orders completed, average rating, revision rate, dispute rate per writer. Cross-website view available.

### Client analytics

Lifetime spending, order frequency, loyalty tier distribution. Retention by cohort.

### Financial analytics

Revenue trend, refund rate, compensation ratio (writer pay / revenue). Writer performance stats correlated with payout.

---

## 15. System Command Center

**URL**: `/superadmin/system`

Platform health overview. Use after deployments to confirm all services are up.

| Check | What it shows |
|---|---|
| Celery workers | Healthy / degraded / down |
| Celery beat | Scheduler status — confirms SLA and escalation tasks are running |
| Database | Connection pool status |
| Redis | Cache and queue status |
| Background task log | Recent task executions with success/failure |

---

## 16. Quick Reference

### Handle an escalated dispute

1. Open `/superadmin/disputes` → Escalated tab
2. Click dispute → read reason and timeline
3. Choose resolution: extend deadline / reassign / refund / no action
4. Apply resolution → parties notified automatically

### Assign a writer to a paid order

1. Open order → Staffing tab
2. If bids exist: click **Assign** on the preferred bid
3. If no bids: go to Operations Command Center → Claim → open order → Staffing tab → assign manually

### Cancel an order

1. Open order detail
2. Staff Actions Panel → **Cancel order** → enter reason → confirm
3. Go to `/superadmin/refunds` to process the refund if applicable

### Onboard a new writer

1. Review application at `/superadmin/writer-applications`
2. Optionally assign vetting quiz from `/superadmin/writer-vetting`
3. Approve → writer receives onboarding email

### Create a new tenant

1. Go to `/superadmin/tenants` for tenant records or `/superadmin/website` for the active website profile
2. Fill in domain, name, branding
3. Create portal definitions for client / writer / staff surfaces
4. Configure pricing rules and service catalog
5. Run `seed_dev_data` if setting up a dev/staging instance
