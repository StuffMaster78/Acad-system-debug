# Order Lifecycle Reference

This is the authoritative reference for order states, allowed transitions, and role-based actions. All transitions are enforced server-side.

---

## Table of Contents

1. [State Definitions](#1-state-definitions)
2. [State Transition Map](#2-state-transition-map)
3. [Role-Action Matrix](#3-role-action-matrix)
4. [Blocked Actions](#4-blocked-actions)
5. [SLA and Escalation](#5-sla-and-escalation)
6. [Staff Actions Panel](#6-staff-actions-panel)
7. [Lifecycle Flags](#7-lifecycle-flags)

---

## 1. State Definitions

| Status | Human Label | Description |
|---|---|---|
| `created` | Pending payment | Order submitted. Awaiting payment. No writer assigned. |
| `unpaid` | Unpaid | Payment failed or not attempted after creation. |
| `pending_payment` | Payment processing | Payment initiated; awaiting gateway webhook. No actions possible during this window. |
| `paid` | Paid | Payment confirmed. Queued for writer assignment. |
| `ready_for_staffing` | Ready for staffing | Routed to staffing queue. Visible to bidding writers. |
| `in_progress` | In progress | Writer assigned and actively working. Deadline clock running. |
| `on_hold` | On hold | Paused by staff. An `OrderHold` record is active. Writer cannot submit. |
| `qa_review` | QA review | Writer submitted work. Under internal quality review. |
| `under_editing` | Under editing | Work passed QA and is being polished before delivery. |
| `submitted` | Ready for your approval | Delivered to client. Awaiting approval or revision request. |
| `completed` | Completed | Client approved or auto-completion triggered. Revision window may still be open. |
| `revision_requested` | Revision in progress | Rework requested. Writer must address feedback and resubmit. |
| `disputed` | Dispute open | An `OrderDispute` record is active. All parties notified. |
| `cancelled` | Cancelled | Permanently stopped. Triggers refund review. Cannot be undone. |
| `refunded` | Refunded | Payment reversed. Order is closed. |
| `archived` | Archived | Closed and read-only. No further actions possible. |

---

## 2. State Transition Map

```
             created ──► unpaid
                │              │
                └──────┬───────┘
                       │ payment initiated
                       ▼
              pending_payment
                       │ payment confirmed
                       ▼
                     paid
                       │ routed to staffing
                       ▼
            ready_for_staffing
                       │ writer assigned
                       ▼
          ┌────── in_progress ──────────────────────────┐
          │            │                                 │
      hold placed   submitted                      revision done
          ▼            ▼                                 │
       on_hold      qa_review ──(approved)──► under_editing
          │            │                          │
     hold released  returned                   delivered
          │            │                          │
          └────────────┘                          ▼
                                             submitted
                                                  │
                               ┌──────────────────┤
                               │                  │
                          approved          revision requested
                               │                  │
                               ▼                  ▼
                           completed     revision_requested ──► in_progress
                               │
                           archived

From any active state:
  ──► cancelled  (per cancellation policy)
  ──► refunded   (after cancellation with payment reversal)

disputed is a flag state — order stays in its current status while a dispute is open.
```

### Allowed Transitions (key paths)

| From | To | Triggered by |
|---|---|---|
| created / unpaid | pending_payment | Client initiates payment |
| pending_payment | paid | System (payment webhook success) |
| pending_payment | unpaid | System (payment webhook failure) |
| paid | ready_for_staffing | Admin (route to staffing) |
| paid / ready_for_staffing | in_progress | Admin (assign writer) |
| in_progress | on_hold | Staff (place hold) |
| on_hold | in_progress | Staff (release hold) |
| in_progress / revision_requested | qa_review | Writer or Admin (submit for QA) |
| qa_review | under_editing | Editor / Admin (approve delivery) |
| qa_review | in_progress | Editor / Admin (return to writer) |
| under_editing | submitted | System / Editor (deliver) |
| submitted | completed | Client (approve) or System (auto-complete after window) |
| submitted | revision_requested | Client / Admin (request revision) |
| revision_requested | qa_review | Writer / Admin (resubmit) |
| completed | archived | Admin / Superadmin |
| any active | cancelled | Per cancellation policy |
| cancelled | refunded | System (payment reversal) |

---

## 3. Role-Action Matrix

Actions marked **(P)** are accessible via the Staff Actions Panel on the order detail page.

| State | Client | Writer | Support | Editor | Admin / Superadmin |
|---|---|---|---|---|---|
| **created** | Pay, Cancel | — | Cancel | — | Cancel **(P)**, Hold **(P)**, Route to staffing |
| **unpaid** | Pay, Cancel | — | Cancel | — | Cancel **(P)**, Hold **(P)**, Route to staffing |
| **pending_payment** | — | — | — | — | — |
| **paid** | — | — | — | — | Assign writer, Hold **(P)**, Cancel **(P)** |
| **ready_for_staffing** | — | — | — | — | Assign writer, Release to pool, Hold **(P)**, Cancel **(P)** |
| **in_progress** | Open dispute, Cancel | Submit for QA, Open dispute | Hold **(P)**, Open dispute **(P)**, Cancel **(P)** | — | Submit for QA **(P)**, Hold **(P)**, Open dispute **(P)**, Cancel **(P)**, Reassign **(P)** |
| **on_hold** | — | — | Release hold **(P)** | — | Release hold **(P)**, Cancel **(P)** |
| **qa_review** | — | — | Hold **(P)** | Approve delivery **(P)**, Return to writer **(P)** | Approve delivery **(P)**, Return to writer **(P)**, Hold **(P)**, Reassign **(P)** |
| **under_editing** | — | — | Hold **(P)** | — | Hold **(P)**, Cancel **(P)** |
| **submitted** | Approve order, Request revision, Open dispute | — | Open dispute **(P)** | — | Approve order **(P)**, Request revision, Open dispute **(P)** |
| **completed** | Request revision (if window open) | — | — | — | Archive **(P)**, Request revision (if window open) |
| **revision_requested** | Open dispute | Submit for QA, Open dispute | Hold **(P)**, Open dispute **(P)** | Approve delivery **(P)**, Return to writer **(P)** | Submit for QA **(P)**, Hold **(P)**, Open dispute **(P)**, Reassign **(P)** |
| **disputed** | — | — | Escalate, Resolve, Close | — | Escalate, Resolve, Close |
| **cancelled** | — | — | — | — | — |
| **refunded** | — | — | — | — | Archive **(P)** |
| **archived** | — | — | — | — | — |

---

## 4. Blocked Actions

Some actions are status-eligible but blocked by the current lifecycle state. The Staff Actions Panel shows blocked actions in a collapsible section with plain-language explanations.

| Action | Blocked when | Reason shown |
|---|---|---|
| `submit_for_qa` | `has_active_hold = true` | "Order is on hold and cannot be submitted." |
| `raise_dispute` | `has_active_dispute = true` | "An active dispute is already open on this order." |
| `archive_order` | `has_active_dispute = true` | "Cannot archive while a dispute is open." |
| `archive_order` | `archived_at` is already set | "Order has already been archived." |
| `approve_order` | `approved_at` is already set | "Order has already been approved." |
| `request_revision` | `approved_at` is set | "Order has been approved — the revision window is closed." |

Blocked reasons are computed by `OrderAvailableActionsService.build_blocked_reasons()` on the backend and returned in the lifecycle endpoint under `blocked_actions`.

---

## 5. SLA and Escalation

### Overdue detection (every 30 minutes)

Celery beat task `escalate_overdue_orders` runs every 30 minutes. An order is overdue when:
- Status is `in_progress` or `qa_review`
- Current time has passed `writer_deadline`

On detection: a `sla_breach` timeline event is created and staff are notified. The order appears in the Operations Command Center with a red left border.

### Stuck order detection (every hour)

Celery beat task `detect_stuck_orders` runs hourly. An order is stuck when:
- Status is `in_progress`
- No timeline activity in the past 8 hours

On detection: a `stuck_detected` timeline event is created. The order appears in the Operations Command Center with a slate border.

---

## 6. Staff Actions Panel

Every order detail page shows a Staff Actions Panel above the tab navigation for `admin`, `superadmin`, `support`, and `editor` roles.

### Panel layout

- **Status badge** — color-coded current status
- **Role badge** — the logged-in user's role
- **Available action buttons** — only actions executable right now
- **Blocked actions** (collapsible) — status-eligible actions that are currently blocked, with reasons
- **State guide** (toggle) — inline reference table of all states and role permissions

### Action types

**One-click with confirm**: Submit for QA, Approve delivery, Approve order, Release hold, Archive. Click shows "Yes, proceed / Cancel" before executing.

**Form actions** (input required before submitting):

| Action | Input required |
|---|---|
| Return to writer | Return reason |
| Place on hold | Hold reason |
| Open dispute | Dispute reason (recorded, visible to all parties) |
| Cancel order | Cancellation reason (irreversible warning shown) |
| Request reassignment | Reassignment reason |

On success: green confirmation bar appears, order is re-fetched so status and available actions update immediately.

---

## 7. Lifecycle Flags

The `GET /orders/{id}/lifecycle/` endpoint returns real-time flags used by the frontend.

| Field | Type | Meaning |
|---|---|---|
| `has_current_assignment` | bool | A writer is currently assigned |
| `current_writer_id` | int\|null | User ID of the assigned writer |
| `active_hold_id` | int\|null | ID of the active hold record |
| `has_active_hold` | bool | An `OrderHold` is currently active |
| `has_pending_reassignment_request` | bool | A reassignment request is pending |
| `active_dispute_id` | int\|null | ID of the open dispute |
| `has_active_dispute` | bool | An `OrderDispute` is currently open |
| `available_actions` | string[] | Actions the requesting user can take now |
| `blocked_actions` | object | Staff-facing map of action → reason why blocked |
| `is_revision_window_open` | bool | Whether the revision window is still open |
| `revision_window_days` | int | How many days the revision window lasts |
