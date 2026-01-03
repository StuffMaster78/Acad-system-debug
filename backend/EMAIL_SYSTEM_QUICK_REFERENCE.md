# 📧 Email System Quick Reference

Quick reference guide for common email operations.

## 🚀 Quick Start

### Send Marketing Email (Mass Email)

```javascript
// Frontend
import emailsAPI from '@/api/emails'

const campaign = await emailsAPI.createMassEmail({
    website: 1,
    title: "New Year Promotion",
    subject: "Happy New Year!",
    body: "<html><body><h1>Happy New Year!</h1></body></html>",
    email_type: "marketing",
    target_roles: ["client"],
    status: "draft"
})

await emailsAPI.sendMassEmailNow(campaign.id)
```

```python
# Backend
from mass_emails.models import EmailCampaign
from mass_emails.tasks import send_email_campaign

campaign = EmailCampaign.objects.create(
    website=website,
    title="New Year Promotion",
    subject="Happy New Year!",
    body="<html>...</html>",
    email_type="marketing",
    target_roles=["client"],
    status="draft",
    created_by=admin_user
)

send_email_campaign.delay(campaign.id)
```

### Send System Broadcast

```javascript
// Frontend
import emailsAPI from '@/api/emails'

const broadcast = await emailsAPI.createBroadcast({
    website: 1,
    title: "System Maintenance",
    event_type: "broadcast.system_announcement",
    message: "Maintenance scheduled...",
    channels: ["in_app", "email"],
    target_roles: ["client"]
})

await emailsAPI.sendBroadcastNow(broadcast.id)
```

```python
# Backend
from notifications_system.services.broadcast_services import BroadcastNotificationService

broadcast = BroadcastNotificationService.send_broadcast(
    event="broadcast.system_announcement",
    title="System Maintenance",
    message="Maintenance scheduled...",
    website=website,
    channels=["in_app", "email"]
)
```

## 📋 API Endpoints

### Mass Emails
```
GET    /api/v1/admin-management/emails/mass-emails/
POST   /api/v1/admin-management/emails/mass-emails/
GET    /api/v1/admin-management/emails/mass-emails/{id}/
PATCH  /api/v1/admin-management/emails/mass-emails/{id}/
DELETE /api/v1/admin-management/emails/mass-emails/{id}/
POST   /api/v1/admin-management/emails/mass-emails/{id}/send_now/
POST   /api/v1/admin-management/emails/mass-emails/{id}/schedule/
GET    /api/v1/admin-management/emails/mass-emails/{id}/analytics/
```

### Broadcasts
```
GET    /api/v1/admin-management/emails/broadcasts/
POST   /api/v1/admin-management/emails/broadcasts/
GET    /api/v1/admin-management/emails/broadcasts/{id}/
PATCH  /api/v1/admin-management/emails/broadcasts/{id}/
DELETE /api/v1/admin-management/emails/broadcasts/{id}/
POST   /api/v1/admin-management/emails/broadcasts/{id}/send_now/
POST   /api/v1/admin-management/emails/broadcasts/{id}/preview/
GET    /api/v1/admin-management/emails/broadcasts/{id}/stats/
```

## 🎯 When to Use What

| Need | System | Why |
|------|--------|-----|
| Promotional email with rich HTML | Mass Email | Full HTML control |
| System announcement (in-app + email) | Broadcast | Dual channel delivery |
| Order confirmation | Transactional | Automated, event-driven |
| Newsletter | Mass Email | Rich formatting, analytics |
| Urgent alert | Broadcast | Can require acknowledgement |
| Marketing campaign | Mass Email | Scheduling, targeting, analytics |

## 🔑 Permissions

- **Admin**: Can manage emails for their website
- **Superadmin**: Can manage all emails across all websites

## 📊 Status Values

### Mass Email Status
- `draft` - Not sent yet
- `scheduled` - Scheduled for future
- `sending` - Currently sending
- `sent` - Successfully sent
- `failed` - Failed to send
- `cancelled` - Cancelled

### Email Recipient Status
- `pending` - Queued for sending
- `sent` - Successfully sent
- `opened` - Email was opened
- `bounced` - Email bounced
- `failed` - Failed to send
- `unsubscribed` - User unsubscribed

## 🎨 Email Types (Mass Email)

- `marketing` - Marketing campaigns
- `promos` - Promotional offers
- `communication` - General communication
- `updates` - System updates

## 📧 Email Providers

1. **SMTP** (Default) - Gmail, custom SMTP
2. **SendGrid** - Professional delivery
3. **Mailgun** - Transactional service
4. **AWS SES** - Scalable, cost-effective

## 🔧 Common Tasks

### Schedule Email for Future

```javascript
await emailsAPI.scheduleMassEmail(campaignId, "2026-01-01T00:00:00Z")
```

### Get Analytics

```javascript
const analytics = await emailsAPI.getMassEmailAnalytics(campaignId)
// Returns: { total_recipients, sent, opened, bounced, failed, open_rate }
```

### Preview Broadcast

```javascript
await emailsAPI.previewBroadcast(broadcastId)
// Sends preview to current user
```

### Target Specific Roles

```javascript
// Mass Email
target_roles: ["client", "writer"]

// Broadcast
target_roles: ["client"]
```

## ⚠️ Common Issues

**Emails not sending?**
- Check Celery worker: `celery -A writing_system worker -l info`
- Verify email provider config
- Check campaign status

**High bounce rate?**
- Verify sender email authentication
- Clean email list
- Check provider reputation

**HTML not rendering?**
- Use inline CSS
- Test in multiple clients
- Validate HTML structure

## 📚 Full Documentation

See [EMAIL_SYSTEM_DOCUMENTATION.md](./EMAIL_SYSTEM_DOCUMENTATION.md) for complete guide.

