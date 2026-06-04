# Platform Flow Diagrams

All diagrams use [Mermaid](https://mermaid.js.org/) and render natively on GitHub, GitLab, and most modern doc platforms.

---

## Table of Contents

1. [Multi-Tenant Domain Architecture](#1-multi-tenant-domain-architecture)
2. [Standard Order — End-to-End Flow](#2-standard-order--end-to-end-flow)
3. [Express Class — End-to-End Flow](#3-express-class--end-to-end-flow)
4. [Special Order — End-to-End Flow](#4-special-order--end-to-end-flow)
5. [Client Workflow](#5-client-workflow)
6. [Writer Workflow](#6-writer-workflow)
7. [Admin Workflow](#7-admin-workflow)
8. [Editor (QA) Workflow](#8-editor-qa-workflow)
9. [Support Workflow](#9-support-workflow)
10. [Superadmin Workflow](#10-superadmin-workflow)

---

## 1. Multi-Tenant Domain Architecture

Each website is an independent tenant. Every tenant gets up to three portal surfaces on separate domains — client, writer, and staff. All surfaces route through nginx to the same Django backend, which uses the hostname to resolve the portal context and enforce access rules.

```mermaid
graph TB
    subgraph Site1["Website 1  (e.g. essaybrand.com)"]
        direction TB
        C1["client.essaybrand.com\nClient Portal\n(Vue 3 SPA)"]
        W1["writer.essaybrand.com\nWriter Portal\n(Vue 3 SPA)"]
        S1["staff.essaybrand.com\nStaff Portal\n(Vue 3 SPA)"]
    end

    subgraph Site2["Website 2  (e.g. techwriters.io)"]
        direction TB
        C2["client.techwriters.io\nClient Portal"]
        W2["writer.techwriters.io\nWriter Portal"]
        S2["staff.techwriters.io\nStaff Portal"]
    end

    subgraph Site3["Website N  (any tenant)"]
        direction TB
        C3["client.siteN.com"]
        W3["writer.siteN.com"]
        S3["staff.siteN.com"]
    end

    subgraph Platform["Platform Level"]
        SA["superadmin.platform.com\nSuperadmin Portal\n(cross-website)"]
    end

    subgraph Infra["Infrastructure  (shared)"]
        NG["nginx\nSSL · Rate-limit\nHostname routing"]
        DJ["Django + Daphne  (ASGI)\nREST API + WebSockets\nPortalTenantResolverMiddleware\nresolves hostname → website + surface"]
        PG[("PostgreSQL\nAll tenant data\nwebsite_id scoped")]
        RD[("Redis\nBroker · Cache\nChannels layer")]
        CW["Celery Worker\nBackground tasks"]
        CB["Celery Beat\nSLA · Escalation\nScheduled jobs"]
    end

    subgraph External["External Services"]
        STR["Stripe\nPayments"]
        SG["SendGrid / Mailgun\nTransactional email"]
    end

    C1 & W1 & S1 --> NG
    C2 & W2 & S2 --> NG
    C3 & W3 & S3 --> NG
    SA --> NG

    NG -->|HTTP / WS| DJ
    DJ <-->|"tenant-scoped queries\n(website_id filter)"| PG
    DJ <--> RD
    CW <--> PG
    CW <--> RD
    CB --> RD
    DJ --> STR
    DJ --> SG
    CW --> SG
```

### Portal surface access rules

| Domain resolves to | Role required | Sees data for |
|---|---|---|
| client.* | `client` | Own orders only |
| writer.* | `writer` | Assigned orders + pool |
| staff.* | `admin`, `support`, `editor` | All data on that website |
| superadmin.* | `superadmin` | All websites |

---

## 2. Standard Order — End-to-End Flow

```mermaid
flowchart TD
    A([Client visits\nclient.website.com]) --> B[Browse services\nPricing calculator]
    B --> C[Place order\nFill: type · topic · level · deadline · pages]
    C --> D{Logged in?}
    D -->|No| E[Register / Login]
    E --> D
    D -->|Yes| F[Order created\nStatus: CREATED]

    F --> G[Payment screen\nPayment Disclosure Banner shown\nStripe card  OR  wallet balance]
    G --> H{Payment method}
    H -->|Card| I[Stripe Checkout\nRedirect to Stripe]
    H -->|Wallet| J[Pay from wallet\ninstant if balance sufficient]
    I -->|Webhook confirmed| K[Status: PAID]
    J --> K
    I -->|Failed| L[Status: UNPAID\nClient can retry]

    K --> M[Admin routes order\nStatus: READY_FOR_STAFFING]
    M --> N[Writers see order in pool\nExpress interest / Bid]
    N --> O[Admin assigns writer\nStatus: IN_PROGRESS]

    O --> P[Writer works\nDeadline clock running]
    P --> Q[Writer uploads deliverable\nFiles tab ▶ Drafts & deliverables]
    Q --> R[Writer clicks Submit for QA\nStatus: QA_REVIEW]

    R --> S{Editor reviews}
    S -->|Approved| T[Status: SUBMITTED\nClient notified]
    S -->|Returned| U[Return reason sent to writer\nStatus: IN_PROGRESS]
    U --> P

    T --> V{Client reviews}
    V -->|Approves| W[Status: COMPLETED\nWriter compensation released]
    V -->|Requests revision| X[Status: REVISION_REQUESTED\nWriter reworks]
    X --> P
    V -->|No response in N days| W

    W --> Y[Admin archives\nStatus: ARCHIVED]

    O -.->|Issue detected| Z[Staff places HOLD\nStatus: ON_HOLD\nWriter cannot submit]
    Z -.->|Issue resolved| O

    O -.->|Serious issue| AA[Staff opens DISPUTE\nAll parties notified]
    AA -.->|Resolved| O
    AA -.->|Refund| AB[Status: CANCELLED → REFUNDED]
```

---

## 3. Express Class — End-to-End Flow

A class is a time-bound engagement where a writer handles coursework, assignments, or exam sittings on behalf of a client. It uses a separate `ClassOrder` model with tasks, installment payments, and portal access grants.

```mermaid
flowchart TD
    A([Client visits\nclient.website.com]) --> B[Request a class\nFill: course name · duration · schedule · tasks]
    B --> C[Class order created\nStatus: INQUIRY]

    C --> D[Admin reviews scope\nClassScopeAssessment created]
    D --> E[Admin proposes price\nClassPriceProposal sent to client]
    E --> F{Client accepts?}
    F -->|Counter-offer| G[Price negotiation\nClassPriceCounterOffer]
    G --> E
    F -->|Accepts| H[Installment plan created\nClassInstallmentPlan]

    H --> I[Client pays deposit\n1st installment via Stripe]
    I --> J[Class: ACTIVE\nWriter assigned\nClassAssignment created]

    J --> K[Writer gets portal access\nClassAccessGrant activated\nWriter uses class credentials]
    K --> L[Admin creates tasks\nClassTask per assignment/exam]

    L --> M[Writer completes tasks\nLogs work in ClassPortalWorkLog]
    M --> N[Writer delivers task\nClassTask marked done]
    N --> O{More tasks?}
    O -->|Yes| L
    O -->|No| P[All tasks complete]

    P --> Q[Final delivery\nClient reviews all deliverables]
    Q --> R{Client approves?}
    R -->|Revision| S[Specific task revision requested]
    S --> M
    R -->|Approved| T[Class: COMPLETED\nClassWriterCompensation released]

    I -.->|Remaining installments| U[Client pays remaining\ninstallments per schedule]
    U -.-> K

    J -.->|Issue| V[Staff opens ClassDispute]
    V -.->|Resolved| J
```

---

## 4. Special Order — End-to-End Flow

A special order is a custom project (e.g. a book, research report, long-form content series) with a quote-based price and milestone-based delivery. Uses `SpecialOrder` model with `SpecialOrderMilestone` records.

```mermaid
flowchart TD
    A([Client visits\nclient.website.com]) --> B[Submit special order inquiry\nFill: project description · budget · timeline\nUpload: brief, reference files]
    B --> C[SpecialOrder created\nStatus: INQUIRY\nAdmin notified]

    C --> D[Admin reviews inquiry]
    D --> E{Order type}
    E -->|Predefined config| F[Price from\nPredefinedSpecialOrderConfig\nNo negotiation needed]
    E -->|Estimated| G[Admin builds quote\nSpecialOrderQuote with line items]
    G --> H[Quote sent to client\nSpecialOrderQuoteLine breakdown]
    H --> I{Client accepts?}
    I -->|Change request| J[SpecialOrderChangeRequest\nAdmin revises quote]
    J --> H
    I -->|Accepts| F

    F --> K[Milestone plan built\nSpecialOrderMilestone × N\nEach has: title · deadline · amount]
    K --> L[Client pays deposit\nSpecialOrderFunding event]
    L --> M[SpecialOrder: ACTIVE\nWriter assigned]

    M --> N[Milestone 1: IN_PROGRESS\nWriter works on milestone]
    N --> O[Writer delivers milestone\nSpecialOrderDeliverable created\nClient notified]
    O --> P{Client reviews\nmilestone}
    P -->|Request revision| Q[Milestone revision\nWriter reworks]
    Q --> O
    P -->|Approves| R[Milestone: APPROVED\nMilestone compensation released]
    R --> S{More milestones?}
    S -->|Yes| T[Next milestone activates\nClient pays next installment]
    T --> N
    S -->|No| U[All milestones approved\nSpecialOrder: COMPLETED]
    U --> V[Final compensation\nSpecialOrderCompletionLog]

    M -.->|Issue| W[SpecialOrderDispute opened]
    W -.->|Resolved| M
    W -.->|Refund| X[Order cancelled\nPartial refund per approved milestones]
```

---

## 5. Client Workflow

```mermaid
flowchart LR
    subgraph Entry["Entry Points"]
        HP[Homepage\n/]
        CALC[Pricing calculator\n/pricing]
        BLOG[Blog / SEO pages]
        BLOG & CALC --> HP
    end

    subgraph Auth["Authentication"]
        REG[Register\n/register]
        LOGIN[Login\n/login]
    end

    subgraph Dashboard["Client Dashboard  — client.website.com"]
        DASH[Dashboard\nActive orders · Wallet · Loyalty]
        ORDERS[My Orders\n/client/orders]
        NEWORDER[Place Order\n/client/orders/new]
        PAYMENTS[Payments\n/client/payments]
        WALLET[Wallet\n/client/wallet]
        LOYALTY[Loyalty & Rewards\n/client/loyalty]
        ACCOUNT[Account\n/client/account]
        GUIDES[Guides\n/client/guides]
        CHANGELOG[What's New\n/client/changelog]
        FEEDBACK[Feedback\n/client/feedback]
    end

    subgraph OrderDetail["Order Detail  (per order)"]
        OD_DETAILS[Details tab]
        OD_FILES[Files tab\nDownload deliverables]
        OD_MSGS[Messages tab\nChat with writer]
        OD_PAY[Payments tab]
        OD_REV[Revisions tab]
        OD_TL[Timeline tab]
        OD_APPROVE[Approve delivery button]
        OD_REVISION[Request revision button]
        OD_DISPUTE[Open dispute button]
    end

    HP --> Auth --> DASH
    DASH --> ORDERS --> NEWORDER
    ORDERS --> OrderDetail
    OD_APPROVE -->|"Status → COMPLETED"| ORDERS
    OD_REVISION -->|"Status → REVISION_REQUESTED"| OD_MSGS
```

---

## 6. Writer Workflow

```mermaid
flowchart LR
    subgraph Apply["Onboarding"]
        APPLYFORM[Apply\n/apply\npublic form]
        QUIZ[Vetting quiz\nlink emailed]
        APPROVED[Account created\nwelcome email]
        APPLYFORM --> QUIZ --> APPROVED
    end

    subgraph Dashboard["Writer Portal  — writer.website.com"]
        WDASH[Dashboard\nActive orders · Earnings · Performance]
        WPOOL[Order Pool\nAvailable orders]
        WORDERS[My Assignments\n/writer/assignments]
        WEARNINGS[Earnings\n/writer/earnings]
        WANALYTICS[Analytics\n/writer/analytics]
        WRESOURCES[Resources\n/writer/resources]
        WCHANGELOG[What's New]
        WFEEDBACK[Feedback]
    end

    subgraph OrderWork["Working on an Order"]
        BID[Express interest\non pool order]
        ASSIGNED[Assigned\nStatus: IN_PROGRESS]
        READBRIEF[Read brief\nDetails tab]
        DOWNLOAD[Download client materials\nFiles tab]
        WORK[Write / research]
        UPLOAD[Upload deliverable\nFiles → Drafts & deliverables]
        SUBMIT[Click 'Submit for QA'\nStatus → QA_REVIEW]
        RETURNED[Editor returns work\nRead return reason]
        REVISION[Revision requested\nby client / admin]
        DONE[Work approved\nCompensation released]
    end

    APPROVED --> WDASH
    WPOOL --> BID --> ASSIGNED
    ASSIGNED --> READBRIEF --> DOWNLOAD --> WORK --> UPLOAD --> SUBMIT
    SUBMIT -->|"Approved by editor"| DONE
    SUBMIT -->|"Returned"| RETURNED --> WORK
    DONE -->|"Client requests revision"| REVISION --> WORK
```

---

## 7. Admin Workflow

```mermaid
flowchart TD
    subgraph Domain["Staff Portal  — staff.website.com"]
        ADASH[Dashboard\nKPIs · Activity feed]
        OPS[Operations Command Center\nOverdue · Hold · Dispute · Stuck]
        ORDERS[Orders list\nSearch · Filter · Saved presets]
        APPS[Writer Applications\nReview · Approve · Reject]
        DISPUTES[Disputes\nReview · Resolve · Escalate]
        REVIEWS[Reviews\nModerate · Approve · Shadow]
        CONFIG[Config Hub\nPricing · Service catalog\nSpecial days · System settings]
        AUDIT[Audit Log\nSecurity events]
        FEEDBACK[Feedback\nTriage · Respond]
        CHANGELOG[Changelog\nPublish release notes]
    end

    subgraph OrderActions["Order Detail — Staff Actions Panel"]
        SA_STATUS[Current status badge]
        SA_QA[Submit for QA]
        SA_APPROVE_DEL[Approve delivery]
        SA_RETURN[Return to writer\n+ reason]
        SA_APPROVE_ORD[Approve order]
        SA_HOLD[Place on hold\n+ reason]
        SA_RELEASE[Release hold]
        SA_DISPUTE[Open dispute\n+ reason]
        SA_CANCEL[Cancel order\n+ reason]
        SA_ARCHIVE[Archive]
        SA_REASSIGN[Request reassignment\n+ reason]
        SA_GUIDE[State guide toggle\nall 16 states × 5 roles]
    end

    ADASH --> OPS
    ORDERS --> OrderActions
    OPS --> ORDERS

    subgraph OrderRoutine["Daily Order Routine"]
        R1[Check Operations Command Center\nfor overdue · stuck · disputes]
        R2[Assign writers to unassigned orders]
        R3[Submit or approve orders in QA]
        R4[Resolve open disputes]
        R5[Process pending refunds]
        R1 --> R2 --> R3 --> R4 --> R5
    end
```

---

## 8. Editor (QA) Workflow

```mermaid
flowchart TD
    subgraph Domain["Staff Portal  — staff.website.com  (editor role)"]
        EDASH[Dashboard\nQA queue · Performance]
        QQ[QA Queue\n/editor/qa\nAll qa_review orders]
    end

    subgraph QAProcess["QA Review Process"]
        CLAIM[Claim order\nmarks as in-progress by you]
        READBRIEF[Details tab\nRead original requirements]
        DOWNLOAD[Files tab\nDownload deliverable]
        CHECKLIST[Quality tab\nComplete QA checklist\npass/fail per item]
        DECIDE{Meets requirements?}
        APPROVE_DEL[Staff Actions Panel\n→ Approve delivery\nStatus: SUBMITTED\nclient notified]
        RETURN_W[Staff Actions Panel\n→ Return to writer\nEnter specific return reason\nStatus: IN_PROGRESS\nwriter notified]
    end

    subgraph Tabs["Tabs visible to editor"]
        T1[Details]
        T2[Files]
        T3[Messages]
        T4[Quality]
        T5[Timeline]
    end

    QQ --> CLAIM --> READBRIEF --> DOWNLOAD --> CHECKLIST --> DECIDE
    DECIDE -->|Pass| APPROVE_DEL
    DECIDE -->|Fail| RETURN_W
    RETURN_W -->|Writer resubmits| QQ
```

---

## 9. Support Workflow

```mermaid
flowchart TD
    subgraph Domain["Staff Portal  — staff.website.com  (support role)"]
        SDASH[Dashboard\nOrders needing attention]
        SORDERS[Orders\nSearch · Filter]
        SDISPUTES[Disputes\nView only — cannot resolve]
    end

    subgraph SupportActions["Support Actions on Order Detail"]
        SA1[Place on hold\n+ reason\nin_progress · qa_review · submitted]
        SA2[Release hold\nwhen issue resolved]
        SA3[Open dispute\n+ detailed reason\nin_progress · submitted · completed]
        SA4[Cancel order\n+ reason\nper cancellation policy]
    end

    subgraph SupportTabs["Tabs visible to support"]
        ST1[Details]
        ST2[Files]
        ST3[Messages]
        ST4[Payments]
        ST5[Revisions]
        ST6[Timeline]
    end

    subgraph Escalation["Escalation Path"]
        E1[Support opens dispute\nor places hold]
        E2[Admin reviews\nand resolves]
        E3[Superadmin handles\nescalated disputes]
        E1 --> E2 --> E3
    end

    SDASH --> SORDERS --> SupportActions
```

---

## 10. Superadmin Workflow

```mermaid
flowchart TD
    subgraph Domain["Superadmin Portal  — superadmin.platform.com"]
        direction TB
        SADASH[Dashboard\nCross-website KPIs\nEscalated disputes alert]
        SWITCHER[Website Selector Bar\nswitch between tenants]
        FINANCE[Finance Center\nRevenue by website · P&L]
        WRITERPAY[Writer Pay\nPending compensation · Payout batches]
        PORTALS[Portal Definitions\nDomain · Branding · Feature flags\nper surface per website]
        ACCESS[Access Control\nAdmin accounts · Website scopes]
        SYSTEM[System Command\nCelery health · Worker status]
        AUDIT[Audit Log\nAll websites · All severities]
    end

    subgraph CrossWebsite["Cross-Website Capabilities"]
        CW1[View all orders\nacross all tenants]
        CW2[Resolve escalated disputes\nescalation ceiling — no higher level]
        CW3[Manage writer pay\nacross all websites]
        CW4[Create / deactivate\nnew tenant websites]
        CW5[Promote writers\nto editor role]
    end

    subgraph Routine["Superadmin Daily Routine"]
        R1[Check escalated disputes\nin Operations Command Center]
        R2[Review Finance Center\nrevenue vs compensation]
        R3[Process writer pay batches]
        R4[Review cross-website audit\nfor critical / sensitive events]
        R1 --> R2 --> R3 --> R4
    end

    SADASH --> SWITCHER
    SWITCHER --> CrossWebsite
    SADASH --> Routine
```

---

## Order Type Comparison

| Dimension | Standard Order | Express Class | Special Order |
|---|---|---|---|
| **What it is** | One document or set of files | Ongoing coursework / exam sittings | Custom multi-milestone project |
| **Pricing** | Fixed (from service catalog) | Negotiated per scope | Quote-based or predefined config |
| **Delivery** | Single file | Per task/session | Per milestone |
| **Payment** | Full upfront (card or wallet) | Installment plan | Deposit + milestone payments |
| **Writer access** | Order files only | Portal access grant (ClassAccessGrant) | Order files + milestone deliverables |
| **Client approval** | Single approval at submission | Per task + final | Per milestone + final |
| **QA** | Editor reviews before delivery | Admin grades tasks | Admin reviews milestones |
| **Dispute model** | `OrderDispute` | `ClassDispute` (via class_management) | `SpecialOrderDispute` |
| **Backend app** | `orders` | `class_management` | `special_orders` |
| **Admin view** | `/admin/orders` | `/admin/classes` | `/admin/special-orders` |
