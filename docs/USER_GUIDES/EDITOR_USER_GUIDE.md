# Editor User Guide

**Last Updated**: June 2026

Editors are responsible for quality assurance (QA). When a writer submits work, the order enters `qa_review` status and lands in the editor's queue. Editors review the work against order requirements and either approve it for delivery or return it to the writer with specific feedback.

---

## Table of Contents

1. [Getting Started](#1-getting-started)
2. [What Editors Can and Cannot Do](#2-what-editors-can-and-cannot-do)
3. [Dashboard and QA Queue](#3-dashboard-and-qa-queue)
4. [The QA Workflow](#4-the-qa-workflow)
5. [Order Detail Page](#5-order-detail-page)
6. [Staff Actions Panel](#6-staff-actions-panel)
7. [QA Checklists](#7-qa-checklists)
8. [Key Scenarios](#8-key-scenarios)
9. [Quality Standards Reference](#9-quality-standards-reference)

---

## 1. Getting Started

Navigate to the staff portal domain and log in with your editor credentials. The editor portal shows your QA queue on the dashboard. Navigation: Dashboard, QA Queue, Orders.

Editor accounts are scoped to one website.

---

## 2. What Editors Can and Cannot Do

### Can do

| Action | Where |
|---|---|
| View all orders | Orders list |
| Approve delivery (`qa_review` → `submitted`) | Staff Actions Panel |
| Return order to writer (`qa_review` → `in_progress`) | Staff Actions Panel |
| Fill in QA checklists | Quality tab |
| View and send messages | Messages tab |
| View files (download deliverables) | Files tab |
| View order history | Timeline tab |

### Cannot do

| Action | Reason |
|---|---|
| Place or release holds | Support and admin action |
| Open disputes | Support and admin action |
| Cancel orders | Admin action |
| Assign writers | Admin action |
| Approve the order as the client | Client or admin action |
| View payments | Not in editor scope |
| Access Staffing, Payments, or Audit tabs | Not shown to editors |

---

## 3. Dashboard and QA Queue

**URL**: `/editor/qa`

The QA queue shows all orders currently in `qa_review` status. Each row shows:
- Order ID and service type
- Page/word count
- Time in QA (how long since writer submitted)
- Deadline countdown
- Claim status (claimed by you / unclaimed / claimed by another editor)

### Claiming an order

Click **Claim** to take ownership of a QA item. This signals to other editors that you are reviewing it and prevents duplicate work. You can release a claim if you cannot complete the review.

Unclaimed items past your SLA threshold are highlighted.

---

## 4. The QA Workflow

```
Writer submits work
        ↓
Order enters qa_review
        ↓
Editor opens order, claims it in QA queue
        ↓
Read requirements in Details tab
        ↓
Download and review deliverable in Files tab
        ↓
Work through QA checklist in Quality tab
        ↓
        ├── Work meets requirements ──► Approve delivery
        │                                     ↓
        │                               Order → submitted
        │                               Client notified
        │
        └── Work has issues ──────────► Return to writer
                                              ↓
                                        Order → in_progress
                                        Writer sees your reason
```

---

## 5. Order Detail Page

Click any order in the QA queue or Orders list to open the detail page.

### Header

- Order ID, masked client/writer IDs, status badge
- Deadline countdown — the writer's delivery deadline. Prioritize orders where the deadline is near and the time in QA is already significant
- Contextual banners: you will typically see orders in `qa_review`; if a hold is active an amber banner shows

### Tabs visible to editors

| Tab | What to use it for |
|---|---|
| Details | Original requirements: service type, topic, instructions, word count, academic level, citation style |
| Files | Download the deliverable (Drafts & deliverables section); view all other files |
| Messages | Read conversation history; send feedback or questions |
| Quality | Fill in the QA checklist; view previous checklist results |
| Timeline | Order history: how many times returned, what feedback was given each time |

---

## 6. Staff Actions Panel

The Staff Actions Panel appears above the tabs. As an editor, you see two actions:

### Approve delivery

**When shown**: order status is `qa_review` (also available in `revision_requested` when work has been resubmitted)

**What it does**: moves the order to `submitted` and notifies the client that their order is ready for approval.

Steps:
1. Complete your review and QA checklist before approving
2. Staff Actions Panel → **Approve delivery**
3. Confirmation prompt appears: "Yes, proceed / Cancel"
4. Click **Yes, proceed**

Result: status updates to `submitted`, client receives notification.

Do not approve delivery if:
- The deliverable does not meet the stated requirements
- Word or page count is significantly short
- The work contains uncorrected errors
- The QA checklist has unresolved failing items

### Return to writer

**When shown**: order status is `qa_review` or `revision_requested`

**What it does**: moves the order back to `in_progress`. The writer receives your reason as a notification.

Steps:
1. Staff Actions Panel → **Return to writer**
2. An input form expands below the button
3. Enter a detailed reason (required) — be specific about what needs to be fixed
4. Click **Return to writer**

Result: status moves to `in_progress`, writer is notified with your reason.

**Writing effective return reasons:**
- List each issue as a separate point
- Reference specific sections or page numbers where possible
- Distinguish between must-fix items and suggestions
- Set a clear expectation: "These three items must be addressed before the next submission will be approved"

Example of a poor reason: "Please improve the quality."

Example of a good reason:
```
1. Word count is 1,840 words. Required minimum is 2,000. Add approximately 160 words.
2. Section 2 ("Market Analysis") makes claims without citations. Add at least 2 sources.
3. Conclusion does not address the original question. Rewrite to directly answer: [question text].
4. References section: use APA 7th edition format consistently — current mix of APA and MLA.
```

---

## 7. QA Checklists

**URL**: Quality tab on any order detail page

QA checklists are templates configured by admin. Each order type may have a different checklist. The checklist enforces consistent quality review across all editors.

### Using a checklist

1. Open order detail → **Quality** tab
2. The active checklist template for this order type loads automatically
3. Work through each item as you review the deliverable
4. Mark each item pass/fail (or yes/no, depending on template)
5. Add a note per item if needed — especially for failed items, explain what you found
6. Click **Submit checklist** when complete

### Checklist results are permanent

- Results are stored on the order
- Admin can view all checklist results across orders
- If you return the order to the writer, the checklist resets for the next submission cycle
- Previous results remain visible in the history for reference

### When a checklist item fails

- Fix it yourself if it is a minor correction within your scope, then mark as pass with a note explaining what you changed
- If the fix requires the writer's involvement (wrong content, missing research, short word count), include it in your return reason and send back to the writer
- Do not approve delivery with unresolved failing items unless you have a documented reason noted in the checklist

---

## 8. Key Scenarios

### Work meets requirements but has minor formatting issues

Option A — fix and approve:
1. Download the file, make the corrections
2. Upload the corrected file to Files tab → Drafts & deliverables section
3. Complete the QA checklist, noting what you corrected
4. Approve delivery

Option B — return for minor fix (if corrections are substantive):
1. Return to writer with specific formatting instructions
2. Use this when you should not be making the corrections yourself

### Work is clearly off-topic or misses the brief entirely

1. Do not approve
2. Return to writer with a detailed explanation referencing the original brief from the Details tab
3. Note this in the QA checklist
4. If this is the second or third return for the same issue: send a staff-visible message in the Messages tab flagging the pattern to admin

### Order has been returned multiple times for the same issues

1. Return to writer as normal with specific instructions
2. In the Messages tab, send a message: "This order has been returned [N] times. Writer continues to miss [specific requirement]. May need admin intervention."
3. Admin can decide to reassign the writer or open a dispute

### You are unsure whether work meets requirements

1. Check the Details tab for the original brief carefully
2. Check the Timeline tab — has this order been through revision before? What was the revision for?
3. Check the Messages tab — has the client clarified requirements through messages?
4. If still unsure: send a message in the Messages tab asking admin for guidance before approving or returning

### The deliverable file is missing or corrupted

1. Do not approve
2. Return to writer: "Deliverable file is [missing / cannot be opened]. Please re-upload."
3. Also check the Files tab — writers sometimes upload to the wrong section (e.g. Internal files instead of Drafts & deliverables)

### The deadline has already passed when the order reaches you

1. Complete the review normally — the deadline breach is already logged by the automated SLA escalation task
2. Admin sees this in the Operations Command Center
3. Do not rush the review — quality takes precedence over speed at this stage

---

## 9. Quality Standards Reference

These are general standards that apply regardless of the checklist template. Use them alongside the order-specific requirements.

### Content requirements

| Check | Standard |
|---|---|
| Word/page count | Within 5% of stated requirement. Rounding down is a fail. Significantly over may indicate padding — check for repetition. |
| Topic coverage | All major points in the brief addressed |
| Introduction | Present, relevant, and frames the piece correctly |
| Conclusion | Directly addresses the original question or objective |
| Arguments | Supported with evidence where required |
| Citations | Format matches the stated style (APA, MLA, Harvard, Chicago) if citations are required |

### Writing quality

| Check | Standard |
|---|---|
| Grammar and spelling | No obvious errors |
| Sentence structure | Varied and clear — no run-ons or fragments |
| Paragraph structure | One main idea per paragraph |
| Tone | Matches the stated tone (academic, professional, conversational) |

### Formatting

| Check | Standard |
|---|---|
| Headings | Used consistently if required |
| Font and spacing | Follows any stated formatting guidelines |
| File format | Correct format as specified in the order (DOCX, PDF, etc.) |
| References page | Present and formatted correctly if citations are required |

### Red flags that always require a return

- Plagiarism indicators: unusual phrasing, inconsistent voice, or content that reads as copied
- Unedited AI-generated content that does not meet quality standards
- Missing entire sections of the brief
- Wrong subject matter (writer may have worked on the wrong order)
- File is password protected or corrupt
- Word count is more than 10% below requirement
