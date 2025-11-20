# Tickets App

A robust Django REST Framework app for managing support tickets, messages, attachments, notifications, and statistics with strict role-based permissions.

---

## Features

- **Ticket Management:**  
  Create, assign, escalate, and close support tickets.
- **Role-Based Access:**  
  - Writers/clients see only their own tickets, messages, and attachments.
  - Admins/support/superadmins see all tickets and can download attachments.
- **Messaging:**  
  Threaded ticket messages with notifications to assigned users and ticket creators.
- **Attachments:**  
  Secure file uploads to tickets, with download permissions enforced.
- **Notifications:**  
  In-app notifications for assignment, escalation, closure, new messages, and attachments.
- **Audit Logging:**  
  All major actions (assignment, escalation, message, attachment) are logged.
- **Statistics:**  
  Dynamic statistics endpoint for ticket analytics.
- **Comprehensive Testing:**  
  Unit and edge case tests for all major features and permissions.

---

## API Endpoints

- `/tickets/` — List, create, retrieve, update, and assign tickets.
- `/tickets/{id}/assign/` — Assign a ticket to a support/admin user.
- `/tickets/{id}/escalate/` — Escalate a ticket to critical priority.
- `/messages/` — List and create ticket messages.
- `/attachments/` — Upload and list ticket attachments.
- `/attachments/{id}/` — Download attachment (admin/support/superadmin only).
- `/logs/` — View ticket logs.
- `/statistics/generate_statistics/` — Get ticket statistics.

---

## Permissions

- **Writers/Clients:**  
  - Can only see and act on their own tickets, messages, and attachments.
  - Cannot assign, escalate, or download attachments they do not own.
- **Admins/Support/Superadmins:**  
  - Full access to all tickets, messages, and attachments.
  - Can assign, escalate, close tickets, and download any attachment.

---

## Notifications

Notifications are sent for:
- Ticket assignment
- Ticket escalation
- Ticket closure
- New ticket messages (to assigned user and/or creator)
- New attachments (to assigned user)

---

## Testing

Run all tests with:
```sh
python manage.py test tickets
```
Tests cover:
- Ticket creation, assignment, escalation, closure
- Message and attachment creation and permissions
- Notification triggers (mocked)
- Edge cases (invalid data, unauthorized access, double actions)
- Statistics endpoint

---

## Example Usage

```python
# Assign a ticket
response = client.post('/tickets/1/assign/', {"assigned_to": user_id})

# Escalate a ticket
response = client.post('/tickets/1/escalate/')

# Add a message
response = client.post('/messages/', {"ticket": 1, "content": "Reply"})

# Upload an attachment
with open('file.pdf', 'rb') as fp:
    response = client.post('/attachments/', {"ticket": 1, "file": fp})
```

---

## Extending

- Add new notification channels (email, SMS) in the `notifications_system` app.
- Customize ticket categories, priorities, or statuses in the model.
- Integrate with external support or CRM systems via signals or Celery tasks.

---

## License

MIT (or your license here)

---

## Authors

- Your team or company name

---

## Support

For issues, open a GitHub issue or contact the maintainers.
