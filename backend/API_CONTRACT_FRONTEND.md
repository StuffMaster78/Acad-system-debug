# Frontend API Contract

This is the canonical contract for the new frontend. Legacy apps may still
exist for migrations, compatibility, or admin backfill, but the frontend should
not build new workflows against them.

## Core Rules

- Identity belongs to `users`.
- Login/session/token flows belong to `authentication`.
- Account lifecycle and role access belong to `accounts`.
- Client and writer wallet workflows belong to `wallets`.
- All uploaded assets belong to `files_management`.
- Tickets use `tickets`; threaded conversations use `communications`.
- Notification delivery and templates belong to `notifications_system`.
- Referral attribution belongs to `referrals`; points and redemption belong to
  `loyalty_management`.
- Admin apps orchestrate operations; they should not duplicate wallet, file,
  account, or governance state.

## Canonical Routes

### Auth, Users, Accounts

- `POST /api/v1/auth/...`
- `GET /api/v1/users/...`
- `GET /api/v1/admin-management/...`
- `GET /api/v1/superadmin-management/...`

Frontend status fields such as `is_suspended`, `is_blacklisted`, and
`is_on_probation` may still appear in admin responses for compatibility, but
their source is canonical account, blacklist, or writer discipline state.

### Wallets

- `GET /api/v1/wallets/me/`
- `GET /api/v1/wallets/me/entries/`
- `GET /api/v1/wallets/me/holds/`
- `GET|POST /api/v1/wallets/me/payout-requests/`
- `GET /api/v1/wallets/admin/wallets/`
- `GET /api/v1/wallets/admin/wallets/<id>/entries/`
- `GET /api/v1/wallets/admin/wallets/<id>/holds/`
- `POST /api/v1/wallets/admin/wallets/<id>/fund/`
- `POST /api/v1/wallets/admin/wallets/<id>/debit/`
- `POST /api/v1/wallets/admin/wallets/<id>/reconcile/`

Do not use `client_wallet`, `writer_wallet`, or `wallet` routes in the new
frontend.

### Files

- `POST /api/v1/files/upload/`
- `POST /api/v1/files/attach/`
- `GET /api/v1/files/download/<attachment_id>/`
- `POST /api/v1/files/deletion/request/`
- `GET /api/v1/files/admin/files/`
- `POST /api/v1/files/admin/cms/upload/`
- `POST /api/v1/files/admin/files/<attachment_id>/replace/`
- `POST /api/v1/files/admin/deletion-requests/<id>/approve/`
- `POST /api/v1/files/admin/deletion-requests/<id>/reject/`

Do not build against `order_files`; order, ticket, communication, CMS, sample,
and blog files should flow through `files_management`.

### Tickets

- `GET|POST /api/v1/tickets/tickets/`
- `GET|PATCH /api/v1/tickets/tickets/<id>/`
- `GET|POST /api/v1/tickets/messages/`
- `GET|POST /api/v1/tickets/attachments/`
- `GET /api/v1/tickets/...sla...`
- `GET /api/v1/tickets/...statistics...`

Ticket messages are bridged to `communications` where threaded message storage
is needed.

### Communications

- `GET|POST /api/v1/communications/threads/`
- `GET|POST /api/v1/communications/messages/`
- `GET|POST /api/v1/communications/attachments/`
- `GET|POST /api/v1/communications/participants/`
- `GET /api/v1/communications/events/`
- `GET|POST /api/v1/communications/saved-replies/`
- `GET|POST /api/v1/communications/escalations/`
- `GET|POST /api/v1/communications/moderation-flags/`

Use `/api/v1/communications/` for all new frontend communication workflows.

### Loyalty And Referrals

- `GET|POST /api/v1/referrals/...`
- `GET|POST /api/v1/loyalty-management/...`

Referral wallet rewards and loyalty cash redemption credit canonical wallet
entries in `wallets`.

### Orders

- `GET|POST /api/v1/orders/orders/` — list / create
- `GET|PATCH /api/v1/orders/orders/{id}/` — detail / update
- `POST /api/v1/orders/orders/create/` — client order creation (all service families)
- `GET /api/v1/orders/orders/{id}/lifecycle/` — order state snapshot (clients, writers, staff)
- `GET /api/v1/orders/orders/{id}/files/` — list attached files
- `POST /api/v1/orders/orders/{id}/files/instructions/`
- `POST /api/v1/orders/orders/{id}/files/references/`
- `POST /api/v1/orders/orders/{id}/files/style-references/` — designs, diagrams, templates
- `POST /api/v1/orders/orders/{id}/files/drafts/`
- `POST /api/v1/orders/orders/{id}/files/final/`

> Note: all file endpoints use the pattern `/orders/orders/{id}/files/...` — the double `orders/` is intentional (router prefix + mount point).

The `POST /api/v1/orders/orders/create/` endpoint accepts a `service_family` field:

| `service_family` | Description |
|---|---|
| `paper_order` | Writing (pages) — default |
| `design_order` | Presentation, infographic, poster (slides / concepts) |
| `diagram_order` | Flowchart, ERD, UML, architecture (diagrams) |
| `combo_order` | Writing + design or writing + diagrams — pass `total_price_override` for the combined total |

### Pricing

- `POST /api/v1/pricing/quotes/paper/start/`
- `POST /api/v1/pricing/quotes/paper/{session_id}/update/`
- `POST /api/v1/pricing/quotes/design/start/`
- `POST /api/v1/pricing/quotes/design/{session_id}/update/`
- `POST /api/v1/pricing/quotes/diagram/start/`
- `POST /api/v1/pricing/quotes/diagram/{session_id}/update/`
- `POST /api/v1/pricing/quotes/composite/create/` — combine paper + design/diagram session IDs
- `POST /api/v1/pricing/quotes/composite/{session_id}/finalize/`
- `POST /api/v1/pricing/quotes/{session_id}/snapshot/` — lock price before order creation

### Payment reminders (admin)

- `GET|POST /api/v1/admin-management/payment-reminders/configs/` — CRUD
- `GET /api/v1/admin-management/payment-reminders/configs/stats/`
- `GET|POST /api/v1/admin-management/payment-reminders/deletion-messages/`
- `GET /api/v1/admin-management/payment-reminders/sent/` — read-only log

## Legacy Names To Avoid

- `client_wallet`
- `writer_wallet`
- `wallet`
- `order_files`
- `events_system` (the installed app is `event_system`)
- direct `User.is_suspended`, `User.is_blacklisted`, or `User.is_on_probation`

The legacy wallet apps may still appear in `INSTALLED_APPS` as
`LEGACY_COMPAT_APPS`. That is intentional migration ballast only: they keep old
database migrations and imports resolvable while the active runtime contract
uses `wallets` and `files_management`.
