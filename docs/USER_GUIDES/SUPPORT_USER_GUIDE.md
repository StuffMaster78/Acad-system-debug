# Support User Guide

**Last Updated**: June 2026

Support staff handle client-facing issue resolution. The support role can view all orders, intervene with holds and disputes, and cancel orders. It does not have access to writer assignment, QA approval, financial configuration, or platform settings.

---

## Table of Contents

1. [Getting Started](#1-getting-started)
2. [What Support Can and Cannot Do](#2-what-support-can-and-cannot-do)
3. [Dashboard](#3-dashboard)
4. [Orders](#4-orders)
5. [Order Detail Page](#5-order-detail-page)
6. [Staff Actions Panel](#6-staff-actions-panel)
7. [Disputes](#7-disputes)
8. [Key Workflows](#8-key-workflows)
9. [Escalation Path](#9-escalation-path)

---

## 1. Getting Started

Navigate to the staff portal domain and log in with your support credentials. After login you will see the support dashboard. Navigation: Dashboard, Orders, Disputes, Payments, Timeline.

Support accounts are scoped to one website.

---

## 2. What Support Can and Cannot Do

### Can do

| Action | Where |
|---|---|
| View all orders and their full history | Orders list, Order detail |
| Place an order on hold | Staff Actions Panel |
| Release a hold | Staff Actions Panel |
| Open a dispute | Staff Actions Panel |
| Cancel an order | Staff Actions Panel |
| View and send messages | Messages tab |
| View payment history | Payments tab |
| View timeline and audit events | Timeline tab |
| View revision requests | Revisions tab |

### Cannot do

| Action | Reason |
|---|---|
| Submit for QA | Writer and admin action |
| Approve delivery | Editor and admin action |
| Approve order | Client or admin action |
| Assign writers | Admin action |
| Access Staffing tab | Not in support role scope |
| Access Quality tab | Not in support role scope |
| Resolve disputes | Admin and superadmin action |
| Modify pricing or config | Admin and superadmin action |

---

## 3. Dashboard

The support dashboard shows:

- Orders in `on_hold` or `disputed` state requiring attention
- Your recent actions with timestamps
- Orders with unread client messages

---

## 4. Orders

**URL**: `/support/orders`

### List view

- Search by order ID or client keyword
- Filter by status, date range
- **Saved View Presets**: save filter combinations you use regularly (e.g. "on hold this week", "disputed last 30 days")

### Status color reference

| Color | States |
|---|---|
| Blue | in_progress |
| Amber | on_hold, unpaid |
| Violet | qa_review |
| Teal | submitted |
| Emerald | completed |
| Rose | disputed |
| Slate | cancelled, archived |

---

## 5. Order Detail Page

Click any order to open the detail page.

### Header

- Order ID, masked client/writer IDs, status badge
- Deadline countdown — turns amber then red as deadline approaches
- Contextual banners: amber (on hold), rose (dispute open — respond within SLA), slate (cancelled/archived)

### Summary cards

Key order fields at a glance: service type, word/page count, deadline, writer compensation (internal).

### Tabs visible to support

| Tab | What you see |
|---|---|
| Details | Full order metadata and requirements |
| Files | All files grouped by section |
| Messages | Client/writer/staff message thread |
| Payments | Payment history |
| Revisions | Revision requests and history |
| Timeline | Every event on the order in chronological order |

The Staffing, Quality, and Audit tabs are not shown to support.

---

## 6. Staff Actions Panel

The Staff Actions Panel appears above the tabs on every order detail page. It shows the current order status, your role badge, and the actions available to you right now.

### Actions available to support

**Place on hold**

Available when order is in `in_progress`, `qa_review`, `submitted`, or `revision_requested`.

Steps:
1. Staff Actions Panel → **Place on hold**
2. Enter the reason (required — logged in timeline and visible to admin)
3. Click **Place on hold** to confirm

Result: order moves to `on_hold`. Writer sees: "This order has been paused by the operations team." Client sees: "Your order has been temporarily paused and will resume shortly."

**Release hold**

Available when `has_active_hold` is true.

Steps:
1. Staff Actions Panel → **Release hold**
2. Confirm with **Yes, proceed**

Result: order returns to its previous active state. Writer is notified.

**Open dispute**

Available in `in_progress`, `submitted`, `completed` when no dispute is already open.

Steps:
1. Staff Actions Panel → **Open dispute**
2. Enter the dispute reason (required — be specific; this is recorded and visible to all parties including the writer and client)
3. Click **Open dispute** to confirm

Result: admin and superadmin are notified. The order enters `disputed` state.

**Cancel order**

Available per the cancellation policy (most active states allow cancellation).

Steps:
1. Staff Actions Panel → **Cancel order**
2. Enter the reason (required)
3. Read the warning: "Cancellation triggers a refund review. This action cannot be undone."
4. Click **Cancel order** to confirm

### Blocked actions

If an action is eligible but currently blocked, the panel shows a collapsible "Blocked actions" section. Examples:
- Open dispute blocked: "An active dispute is already open on this order."
- Submit for QA blocked: not shown (not in support's scope)

### State guide

Click **State guide** in the panel header to open a reference table of all 16 order states and what each role can do. Use this when deciding how to handle an unusual situation.

---

## 7. Disputes

**URL**: `/support/disputes`

Support can view disputes but cannot resolve them. Resolution (extend deadline / reassign / refund / partial refund) is an admin/superadmin action.

### Support's role in disputes

1. **Gather context**: read the dispute reason, timeline, and messages before taking action
2. **Open disputes**: if a client reports a problem and you determine a dispute is warranted, open it via the Staff Actions Panel with a clear, detailed reason
3. **Document thoroughly**: the reason you enter when opening a dispute is the primary record. Write it as a handoff to someone who knows nothing about the situation
4. **Inform the client**: after opening a dispute, let the client know it has been raised and that the resolution team will respond within your SLA

Support cannot change dispute status, add resolutions, or close disputes. If a dispute needs urgent attention, notify admin directly.

---

## 8. Key Workflows

### Client says the writer has stopped responding

1. Open the order → Timeline tab
2. Check the last writer activity (file upload, message, status change)
3. Check Messages tab: has the writer responded to recent messages?
4. If inactive more than 8 hours: the system may have already flagged it as "stuck" — look for a `stuck_detected` timeline event
5. **To pause the order**: Staff Actions Panel → Place on hold → reason: "Writer unresponsive — placed on hold pending investigation"
6. Send a message to the writer via Messages tab requesting an update
7. If no response within your SLA: Staff Actions Panel → Open dispute → document the full situation clearly

### Client disputes the quality of delivered work

1. Open the order → Files tab → Drafts & deliverables section
2. Review the delivered file yourself if possible
3. Check Details tab for the original requirements
4. Check Revisions tab — has a revision already been requested?
5. If quality is genuinely substandard: Staff Actions Panel → Open dispute → specify exactly what is wrong vs. what was required
6. If the client wants to try a revision first: advise the client to use the "Request revision" option on their portal (support cannot request revisions on behalf of clients)

### Client wants to cancel

1. Confirm the client's intent
2. Open the order → Staff Actions Panel → Cancel order
3. Reason: include that this is client-requested
4. Confirm
5. Advise the client that a refund review will be initiated; processing time depends on the payment method

### Order stuck in payment processing

1. Open the order → Payments tab — check the last payment event
2. If `pending_payment` for more than 30 minutes: escalate to admin — payment may need a manual webhook retry
3. Support cannot retry payments — this requires admin access

### Order has been on hold for longer than expected

1. Check when the hold was placed (Timeline tab)
2. Review the hold reason
3. If the issue is resolved: Staff Actions Panel → Release hold → confirm
4. If unsure whether the issue is resolved: contact admin before releasing

### Writer requests a deadline extension

Support cannot modify deadlines. Escalate to admin. If the request is urgent, place the order on hold while admin reviews: Staff Actions Panel → Place on hold → reason: "Writer requested deadline extension — pending admin review."

---

## 9. Escalation Path

Support → Admin → Superadmin

| Situation | Who handles it |
|---|---|
| Order quality issue, writer dispute | Support opens dispute; Admin/Superadmin resolves |
| Refund decision | Admin / Superadmin |
| Writer discipline or termination | Admin / Superadmin |
| Payment failure investigation | Admin |
| Escalated dispute (from admin) | Superadmin |
| Platform configuration changes | Admin / Superadmin |
| Writer deadline extension | Admin |

To escalate to admin: use the Messages tab to leave a staff-visible note on the order, or contact admin through your internal communication channel. There is no escalate button for support — escalation happens through communication.
