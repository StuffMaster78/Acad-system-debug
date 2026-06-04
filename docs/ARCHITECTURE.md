# Architecture Reference

> Diagrams and flow documentation for the Writing System Platform.
> All diagrams use [Mermaid](https://mermaid.js.org/) — rendered natively on GitHub/GitLab.

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Multi-Tenant Portal Architecture](#multi-tenant-portal-architecture)
3. [Frontend Surface Routing](#frontend-surface-routing)
4. [Order Lifecycle](#order-lifecycle)
5. [Writer Assignment Flow](#writer-assignment-flow)
6. [Payment & Wallet Pipeline](#payment--wallet-pipeline)
7. [Compensation Event Pipeline](#compensation-event-pipeline)
8. [Notification Pipeline](#notification-pipeline)
9. [Authentication Flow](#authentication-flow)
10. [Vetting & Application Pipeline](#vetting--application-pipeline)
11. [Dispute Resolution Flow](#dispute-resolution-flow)
12. [Background Task Architecture](#background-task-architecture)

---

## System Overview

```mermaid
graph TB
    subgraph Clients["Client Devices"]
        B1[Browser / Client Portal]
        B2[Browser / Writer Portal]
        B3[Browser / Staff Portal]
    end

    subgraph Infra["Infrastructure"]
        NG[nginx\nSSL · Rate-limit · Static files]
        DJ[Django + Daphne\nASGI — HTTP + WebSocket]
        CW[Celery Worker\nAsync tasks]
        CB[Celery Beat\nScheduled tasks]
        PG[(PostgreSQL 15\nPrimary datastore)]
        RD[(Redis 7\nBroker · Cache · Channels)]
        S3[(S3 / Spaces\nMedia & static files)]
    end

    subgraph External["External Services"]
        ST[Stripe\nPayments]
        SG[SendGrid\nEmail]
        SN[Sentry\nError tracking]
    end

    B1 & B2 & B3 --> NG
    NG -->|HTTP| DJ
    NG -->|WebSocket upgrade| DJ
    DJ <--> PG
    DJ <--> RD
    DJ --> S3
    DJ --> ST
    DJ --> SG
    DJ --> SN
    CW <--> PG
    CW <--> RD
    CB --> RD
    CW --> SG
```

---

## Multi-Tenant Portal Architecture

Each domain resolves to a surface (client / writer / staff) via middleware before any view logic runs.

```mermaid
flowchart LR
    subgraph Domains
        D1["essaybrand.com\n(client domain)"]
        D2["writers.platform.com\n(writer domain)"]
        D3["staff.platform.com\n(staff domain)"]
    end

    subgraph Middleware["PortalTenantResolverMiddleware"]
        MW1["Match domain\nagainst PortalDefinition"]
        MW2["Match domain\nagainst Website"]
        MW3["Attach request.portal\n+ request.website"]
    end

    subgraph PortalContext["PortalContextView\n/api/v1/portal-context/"]
        PC["Returns:\n• surface\n• branding\n• allowed_roles\n• payment_disclosure"]
    end

    subgraph Surfaces
        SC[surface = 'client'\nallows: client]
        SW[surface = 'writer'\nallows: writer]
        SS[surface = 'staff'\nallows: admin, editor,\nsuperadmin, support]
    end

    D1 & D2 & D3 --> MW1
    MW1 -->|found| MW3
    MW1 -->|not found| MW2
    MW2 --> MW3
    MW3 --> PortalContext
    PC -->|code = client_portal| SC
    PC -->|code = writer_portal| SW
    PC -->|code = internal_admin| SS
```

---

## Frontend Surface Routing

```mermaid
flowchart TD
    Start([App boot]) --> Init["portalContextStore.init()\nfetch /portal-context/"]
    Init --> Surface{surface?}

    Surface -->|client| CRoutes["Register /client/* routes only\nallowed roles: client"]
    Surface -->|writer| WRoutes["Register /writer/* routes only\nallowed roles: writer"]
    Surface -->|staff| SRoutes["Register /admin/* routes only\nallowed roles: admin · superadmin · editor · support"]
    Surface -->|error / unknown| Err[Error page\n503 — domain not configured]

    CRoutes --> Guard
    WRoutes --> Guard
    SRoutes --> Guard

    Guard["router.beforeEach\n1. Auth check\n2. Role check"]

    Guard -->|pass| View[Render view]
    Guard -->|unauthenticated| Login[/login for this surface]
    Guard -->|wrong role| Forbidden[403 page]
```

---

## Order Lifecycle

```mermaid
stateDiagram-v2
    [*] --> created: Client submits form
    created --> unpaid: Order saved, awaiting payment
    unpaid --> pending_payment: Payment initiated
    pending_payment --> paid: Payment confirmed (Stripe webhook)
    paid --> ready_for_staffing: Admin routes order
    ready_for_staffing --> preferred_writer_pending: Preferred writer invited
    preferred_writer_pending --> assigned: Writer accepts
    preferred_writer_pending --> ready_for_staffing: Invitation expires / declined
    ready_for_staffing --> assigned: Admin assigns writer
    assigned --> in_progress: Writer acknowledges
    in_progress --> qa_review: Writer submits
    qa_review --> submitted: QA approves delivery
    qa_review --> in_progress: QA returns to writer
    submitted --> completed: Client approves OR auto-approve window passes
    submitted --> revision_requested: Client requests revision
    revision_requested --> in_progress: Writer acknowledges revision
    completed --> archived: Auto-archive after grace period
    in_progress --> disputed: Client or writer raises dispute
    submitted --> disputed: Client raises dispute
    completed --> disputed: Client raises dispute (within window)
    disputed --> in_progress: Dispute closed, order restored
    disputed --> submitted: Dispute closed, order restored
    disputed --> completed: Dispute closed, order restored
    paid --> cancelled: Admin or client cancels
    assigned --> cancelled: Admin cancels
    in_progress --> cancelled: Admin cancels
    cancelled --> refunded: Refund issued
```

---

## Writer Assignment Flow

```mermaid
sequenceDiagram
    participant Admin
    participant API
    participant OrderStaffingService
    participant WriterEligibilityService
    participant OrderAssignment
    participant NotificationService
    participant Celery

    Admin->>API: POST /orders/:id/assign/ {writer_id}
    API->>OrderStaffingService: assign(order, writer, actor)
    OrderStaffingService->>WriterEligibilityService: check_eligibility(writer, order)
    WriterEligibilityService-->>OrderStaffingService: eligible / raise IneligibleWriterError
    OrderStaffingService->>OrderAssignment: create(order, writer, is_current=True)
    OrderStaffingService->>OrderStaffingService: order.status = 'assigned'
    OrderStaffingService->>NotificationService: notify_order_assigned(order, writer)
    NotificationService->>Celery: queue send_channel_notification
    Celery-->>WriterApp: WebSocket push / email
    OrderStaffingService-->>API: OrderAssignment
    API-->>Admin: 201 {assignment_id, writer_id}
```

---

## Payment & Wallet Pipeline

```mermaid
flowchart TD
    Client([Client]) --> CO["Create Order\nPOST /orders/"]
    CO --> PI["Create PaymentIntent\nStripe checkout"]
    PI --> Stripe{Stripe}
    Stripe -->|card charged| WH["POST /webhooks/stripe/\npayment_intent.succeeded"]
    WH --> PW["PaymentProcessor\nrecord_payment()"]
    PW --> WA["WalletAllocation\nreserve funds"]
    WA --> OS["Order.payment_status = 'paid'\nOrder.amount_paid updated"]
    OS --> OL["OrderLifecycleTrigger\nroute to staffing"]

    subgraph WalletPath["Wallet-funded path"]
        WF["Client pays from wallet\nPOST /wallet/checkout/"]
        WB["Wallet.available_balance -= amount\nWalletEntry (debit)"]
        WF --> WB --> OS
    end
```

---

## Compensation Event Pipeline

```mermaid
flowchart TD
    OC["Order status → 'completed'\n(post_save signal)"] --> CT["Celery task\ncreate_order_compensation_event"]
    CT --> EIS["EventIntakeService.record()\nwriter, amount, idempotency_key"]
    EIS -->|open window exists| CE["CompensationEvent created\nstatus: PENDING_CONFIRMATION\nassigned to current PaymentWindow"]
    EIS -->|no open window| Retry["Task retries with backoff\n(NoOpenWindowError)"]
    CE --> Admin["Admin reviews\nmatured / held / confirmed"]
    Admin --> MW["Close PaymentWindow\nWindowService.close_window()"]
    MW --> PB["PayoutBatch created\n1 PayoutRecord per writer"]
    PB --> Payout["Admin marks PAID\nPOST /admin/payout-items/:id/mark-paid/"]
    Payout --> WE["WalletEntry (credit)\nwriter balance updated"]

    BF["backfill_compensation_events\nmanage.py command"] -->|historical orders| EIS
    FB["WriterPaymentViewSerializer\nfallback query"] -->|no events exist yet| OQ["Query Order + Assignment\ndirectly for display"]
```

---

## Notification Pipeline

```mermaid
flowchart LR
    subgraph Triggers["Event Triggers"]
        T1["Order lifecycle\ne.g. order.assigned"]
        T2["Celery beat\ne.g. order.deadline_approaching\nevery 30 min"]
        T3["Dispute / payment\ne.g. order.disputed"]
    end

    subgraph Service["NotificationService.notify()"]
        S1["Rate-limit check"]
        S2["Resolve channels\n(in_app, email)"]
        S3["Write Outbox row"]
        S4["Queue Celery task"]
    end

    subgraph Delivery["Celery delivery task"]
        D1["Resolve template"]
        D2["Render content"]
        D3["Create Delivery row"]
        D4["Send email via SendGrid"]
        D5["Push via WebSocket\n_push_ws()"]
    end

    subgraph Frontend["Frontend"]
        F1["NotificationConsumer\nWebSocket connected"]
        F2["store.push()\nbell badge updates instantly"]
        F3["Polling fallback\nGET /notifications/poll/\nevery 30 s"]
    end

    T1 & T2 & T3 --> Service
    S1 --> S2 --> S3 --> S4
    S4 --> Delivery
    D3 --> D4
    D3 --> D5
    D5 -->|channel_layer.group_send| F1
    F1 --> F2
    F3 -.->|backup path| F2
```

---

## Authentication Flow

```mermaid
sequenceDiagram
    participant Browser
    participant API
    participant AuthService
    participant JWT
    participant Session

    Browser->>API: POST /auth/login/ {email, password, portal_code}
    API->>AuthService: authenticate(email, password)
    AuthService->>AuthService: verify MFA if enabled
    AuthService->>Session: create UserSession (device fingerprint, IP)
    AuthService->>JWT: generate access + refresh tokens\n(embed session_id, website_id)
    JWT-->>API: access_token (15 min), refresh_token (7 days)
    API-->>Browser: {access_token, refresh_token, user}

    Note over Browser,API: Subsequent requests
    Browser->>API: Authorization: Bearer <access_token>
    API->>JWT: verify + extract claims
    JWT-->>API: user_id, session_id, website_id

    Note over Browser,API: Token refresh
    Browser->>API: POST /auth/token/refresh/ {refresh_token}
    API->>Session: validate session still active
    Session-->>API: valid
    API->>JWT: issue new access_token
    JWT-->>Browser: {access_token}

    Note over Browser,API: Impersonation
    Browser->>API: POST /auth/impersonation/ {target_user_id}\n(staff only)
    API->>AuthService: create ImpersonationToken\nlog audit event
    API-->>Browser: {impersonation_token}\namber banner shown in UI
    Browser->>API: POST /auth/impersonation/end/
    API->>AuthService: revoke token, restore original session
```

---

## Vetting & Application Pipeline

```mermaid
flowchart TD
    A([Applicant]) --> AF["Public apply form\n/apply"]
    AF --> WA["WriterApplication created\nstatus: pending"]
    WA --> AR["Admin reviews\n/admin/writer-applications"]
    AR --> QG{Quiz gate\nall required quizzes passed?}
    QG -->|no| QB["Approve button disabled\nquiz status shown"]
    QG -->|yes| AP["Admin approves\nPOST /applications/:id/approve/"]
    AP --> WAS["WriterApplicationService.approve()\n1. _check_required_quizzes()\n2. Create WriterProfile\n3. Create User account\n4. Send welcome email"]
    WAS --> Writer([Writer can log in])

    subgraph QuizFlow["Quiz pathway"]
        QR["VettingQuiz with\nis_required_for_approval=True"]
        WL["Writer logs in to writer portal\n/vetting"]
        WT["Takes quiz attempt"]
        WS["Auto-scored (MCQ/T-F)\nor PENDING_REVIEW (essay)"]
        WP["Status: PASSED"]
        QR --> WL --> WT --> WS --> WP
    end

    QB -.->|writer takes quiz| QuizFlow
    QuizFlow --> QG
```

---

## Dispute Resolution Flow

```mermaid
stateDiagram-v2
    [*] --> open: Client/Writer raises dispute\nOrder → DISPUTED

    open --> in_review: Admin assigns reviewer\nDispute → IN_REVIEW

    in_review --> escalated: Admin escalates\nDispute → ESCALATED

    in_review --> resolved: Admin resolves\nOutcome recorded\nDisputeResolution created
    escalated --> resolved: Senior admin resolves

    resolved --> closed: Admin closes\nOrder status restored\nDisputeEvent logged

    open --> cancelled: Withdrawn by opener
    in_review --> cancelled: Withdrawn

    closed --> [*]
    cancelled --> [*]
```

---

## Background Task Architecture

```mermaid
graph TD
    subgraph Beat["Celery Beat (scheduled)"]
        B1["Every 5 min\nnotifs.requeue_pending_outbox"]
        B2["Every 30 min\norders.check_order_deadlines\n(24h / 6h / 1h warnings)"]
        B3["Every 30 min\norders.writer_acknowledgement_reminders"]
        B4["Every 15 min\norders.operational_writer_reminders"]
        B5["Nightly 23:50\ncompensation.close_windows"]
        B6["Nightly 00:05\ncompensation.open_windows"]
        B7["Daily 09:00\ncompensation.alert_pending_events"]
        B8["Every 30 min\nnotifs.expire_stale"]
        B9["Hourly\norders.archive_completed_orders"]
    end

    subgraph Signals["Django Signals → Tasks"]
        S1["Order.status → completed\npost_save signal"]
        S2["OrderAssignment created\npost_save"]
        S3["Notification created\nin dispatcher"]
    end

    subgraph Tasks["Celery Tasks"]
        T1["create_order_compensation_event\n(idempotent, retries on NoOpenWindowError)"]
        T2["notify_order_assigned\n(email + in_app + WebSocket push)"]
        T3["send_channel_notification\n(email or in_app delivery)"]
    end

    S1 --> T1
    S2 --> T2
    S3 --> T3
    Beat --> Tasks
```

---

## Data Model Summary

```mermaid
erDiagram
    Website ||--o{ Order : "scopes"
    Website ||--o{ WriterProfile : "scopes"
    Website ||--o{ PaymentWindow : "scopes"
    Website ||--o{ PortalDefinition : "defines surface"

    User ||--o| WriterProfile : "has profile"
    User ||--o{ Order : "places as client"

    Order ||--o| OrderAssignment : "has current assignment"
    OrderAssignment }o--|| WriterProfile : "assigned to"
    Order ||--o{ OrderDispute : "may have"
    Order ||--o| OrderPricingSnapshot : "priced via"

    WriterProfile ||--o| WriterLevel : "has level"
    WriterLevel ||--o| WriterLevelSettings : "configured by"
    WriterProfile ||--o| WriterPerformance : "tracked via"

    WriterProfile ||--o{ CompensationEvent : "earns via"
    CompensationEvent }o--|| PaymentWindow : "assigned to window"
    PaymentWindow ||--o{ PayoutBatch : "generates"
    PayoutBatch ||--o{ PayoutRecord : "contains"

    User ||--o{ Notification : "receives"
    Notification ||--o| NotificationsUserStatus : "read state"

    Order ||--o{ Review : "reviewed via"
    Review }o--|| WriterProfile : "rates"
```
