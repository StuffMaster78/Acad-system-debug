## Messaging & API Security Hardening (Dec 2025)

### Frontend changes

- **Unified tabbed messaging UI**
  - `OrderDetail.vue`: Messages tab now uses `OrderMessagesTabbed` exclusively for all roles (client, writer, admin, support, editor).
  - `OrderThreadsModal.vue` (admin/superadmin “View Messages” modal) now embeds `OrderMessagesTabbed` instead of its own ad‑hoc thread list + nested modal.
  - Role-based tabs determine who a user can start conversations with (e.g. clients → writer/admin/support/editor; writers → client/admin/support/editor).

- **New message creation**
  - `OrderNewMessageModal.vue`:
    - Simplified UX: selecting a **recipient role tab** immediately shows the message textarea.
    - **Send** button is enabled when a role tab is chosen and message text is non-empty.
    - Backed by `communicationsAPI.startThreadForOrder(orderId)` to auto-create an order-specific thread and `sendMessageSimple` to send the first message.

- **Typing indicator (current state)**
  - Frontend still calls `/communication-threads/{id}/typing/` for typing indicators.
  - Backend does not yet implement a `typing` action on `CommunicationThreadViewSet`, so these calls currently 500 but do **not** affect send/read; they are cosmetic and can be implemented or disabled later.

### Backend changes

- **Notification service robustness**
  - `NotificationService.notify_user_on_message` and `notify_admin_on_sensitive_upload` previously assumed `recipient.profile.role` / `sender.profile.role`.
  - Updated to support the current `User` model (where `role` is on the user itself):
    - Safely resolve role via `recipient.profile.role` **or** `recipient.role`.
    - Safely resolve sender role via `sender.profile.role` **or** `sender.role`.
  - This removes `AttributeError: 'User' object has no attribute 'profile'` when sending messages via the simplified endpoint.

- **Read receipts query fix**
  - `CommunicationMessageSerializer.get_read_receipts` previously used:
    - `obj.messagereadreceipt_set.select_related("user__profile")`
  - The `User` model no longer has a generic `profile` relation, causing:
    - `FieldError: Invalid field name(s) given in select_related: 'profile'`
  - Updated to:
    - `select_related("user")` and read `receipt.user.role` directly.
  - This fixes listing threads when read receipts are present.

- **Simplified send-message endpoint**
  - `CommunicationThreadViewSet.send_message_simple`:
    - Uses `CommunicationGuardService.can_send_message` to enforce:
      - Only participants or users with order access can send.
      - No messaging on archived / special / class orders unless `admin_override` is set.
    - Auto-detects recipient from:
      - Other thread participants; or
      - Order client / assigned writer when participants are not yet resolved.
    - Delegates creation to `MessageService.create_message` and returns a compact success payload.

### Role & visibility rules (enforced by services)

- **Visibility**
  - Threads and messages are visible only to:
    - Users who are **participants** in the thread, or
    - Staff roles (admin/superadmin, and limited support/editor) where explicitly allowed.
  - Writers and clients only see **their own** conversations; they do not see staff-only or other‑user threads.

- **Who can message whom**
  - **Clients**: may message their writer (if assigned) and staff roles (admin, support, editor) for that order.
  - **Writers**: may message the client for the specific order and staff roles (admin, support, editor) tied to that order.
  - **Admins/Superadmins**: can see and participate in all order threads.
  - All of the above are further constrained by `CommunicationGuardService` and `communications.permissions.can_send_message`.

### Known follow‑ups

- Implement a proper `typing` action on `CommunicationThreadViewSet` (or disable frontend typing calls) to remove noisy 500s on `/typing/`.
- Add explicit tests around:
  - Cross‑role and cross‑tenant access to threads/messages.
  - Ensuring simplified `start-for-order` + `send-message-simple` flows respect role rules and archived/special/class order restrictions.


