# 📧 Email System Documentation

Complete guide to the Writing System Platform's email infrastructure, covering Mass Emails, Broadcast Messages, and Transactional Notifications.

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Mass Email System](#mass-email-system)
3. [Broadcast System](#broadcast-system)
4. [Transactional Notifications](#transactional-notifications)
5. [Email Service Providers](#email-service-providers)
6. [API Reference](#api-reference)
7. [Configuration](#configuration)
8. [Usage Examples](#usage-examples)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)

---

## 🎯 System Overview

The Writing System Platform uses a **three-tier email architecture** that separates concerns and follows enterprise best practices:

```
┌─────────────────────────────────────────────────────────┐
│              Email System Architecture                   │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  1. Mass Email System      → Marketing/Promotional      │
│     - Rich HTML campaigns                                 │
│     - Scheduled sending                                   │
│     - Analytics & tracking                                │
│                                                           │
│  2. Broadcast System       → System Announcements      │
│     - In-app + Email delivery                            │
│     - Event-based templates                              │
│     - Role targeting                                      │
│                                                           │
│  3. Transactional Notifications → Order/System Events     │
│     - Order confirmations                                │
│     - Password resets                                     │
│     - System alerts                                       │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

### When to Use Each System

| System | Use Case | HTML Support | Channels | Best For |
|--------|----------|--------------|----------|----------|
| **Mass Email** | Marketing campaigns, promotions, newsletters | ✅ Full HTML | Email only | Promotional content, rich formatting |
| **Broadcast** | System announcements, alerts, updates | ⚠️ Template-based | In-app + Email | Simple announcements, dual-channel delivery |
| **Transactional** | Order confirmations, password resets | ✅ Template-based | Email only | Automated system notifications |

---

## 📨 Mass Email System

The Mass Email System is designed for **marketing campaigns** and **promotional communications** with full HTML support.

### Features

- ✅ **Rich HTML Content**: Full control over email design and formatting
- ✅ **Scheduled Sending**: Schedule campaigns for future delivery
- ✅ **Role Targeting**: Target specific user roles (clients, writers, etc.)
- ✅ **Analytics**: Track opens, clicks, bounces, and failures
- ✅ **Templates**: Reusable email templates
- ✅ **Attachments**: Support for file attachments
- ✅ **Multi-tenant**: Website-specific campaigns

### Permissions

- **Admin** and **Superadmin** roles can create and send mass emails
- Admins are limited to their website's campaigns
- Superadmins can manage all campaigns

### Models

#### EmailCampaign

Represents a marketing email campaign.

```python
{
    "id": 1,
    "website": 1,
    "title": "New Year Promotion",
    "subject": "Happy New Year from GradeCrest TEAM",
    "body": "<html>...</html>",  # Full HTML content
    "email_type": "marketing",  # marketing, promos, communication, updates
    "target_roles": ["client", "writer"],
    "status": "draft",  # draft, scheduled, sending, sent, failed, cancelled
    "scheduled_time": "2026-01-01T00:00:00Z",
    "sent_time": null,
    "created_by": 1,
    "created_at": "2025-12-31T10:00:00Z"
}
```

#### EmailRecipient

Tracks individual recipients and their status.

```python
{
    "id": 1,
    "campaign": 1,
    "user": 123,
    "email": "user@example.com",
    "status": "sent",  # pending, sent, opened, bounced, failed, unsubscribed
    "sent_at": "2026-01-01T00:05:00Z",
    "opened_at": null
}
```

### API Endpoints

#### Base URL: `/api/v1/admin-management/emails/mass-emails/`

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/` | List all campaigns | Admin/Superadmin |
| `POST` | `/` | Create new campaign | Admin/Superadmin |
| `GET` | `/{id}/` | Get campaign details | Admin/Superadmin |
| `PATCH` | `/{id}/` | Update campaign | Admin/Superadmin |
| `DELETE` | `/{id}/` | Delete campaign | Admin/Superadmin |
| `POST` | `/{id}/send_now/` | Send immediately | Admin/Superadmin |
| `POST` | `/{id}/schedule/` | Schedule campaign | Admin/Superadmin |
| `GET` | `/{id}/analytics/` | Get analytics | Admin/Superadmin |

#### Create Campaign Request

```json
{
    "website": 1,
    "title": "New Year Promotion 2026",
    "subject": "Happy New Year from GradeCrest TEAM",
    "body": "<html><body><h1>Happy New Year!</h1><p>Content here...</p></body></html>",
    "email_type": "marketing",
    "target_roles": ["client"],
    "status": "draft"
}
```

#### Schedule Campaign Request

```json
{
    "scheduled_time": "2026-01-01T00:00:00Z"
}
```

#### Analytics Response

```json
{
    "total_recipients": 1000,
    "sent": 995,
    "opened": 450,
    "bounced": 3,
    "failed": 2,
    "open_rate": 45.23
}
```

### Frontend Integration

The frontend provides a complete UI at `/admin/EmailManagement`:

```javascript
import emailsAPI from '@/api/emails'

// Create campaign
await emailsAPI.createMassEmail({
    website: 1,
    title: "New Year Promotion",
    subject: "Happy New Year!",
    body: "<html>...</html>",
    email_type: "marketing",
    target_roles: ["client"]
})

// Send immediately
await emailsAPI.sendMassEmailNow(campaignId)

// Schedule
await emailsAPI.scheduleMassEmail(campaignId, "2026-01-01T00:00:00Z")

// Get analytics
const analytics = await emailsAPI.getMassEmailAnalytics(campaignId)
```

---

## 📢 Broadcast System

The Broadcast System is designed for **system-wide announcements** that can be delivered via both **in-app notifications** and **email**.

### Features

- ✅ **Dual Channel**: Send to both in-app and email simultaneously
- ✅ **Event-Based**: Uses predefined event types
- ✅ **Role Targeting**: Target specific user roles
- ✅ **Acknowledgements**: Track user acknowledgements
- ✅ **Scheduling**: Schedule broadcasts for future delivery
- ✅ **Expiration**: Set expiration dates for broadcasts

### Permissions

- **Admin** and **Superadmin** roles can create and send broadcasts
- Admins are limited to their website's broadcasts
- Superadmins can manage all broadcasts

### Models

#### BroadcastNotification

Represents a system broadcast message.

```python
{
    "id": 1,
    "website": 1,
    "title": "System Maintenance Alert",
    "event_type": "broadcast.system_announcement",
    "message": "System will be under maintenance...",
    "target_roles": ["client", "writer"],
    "channels": ["in_app", "email"],
    "is_active": true,
    "require_acknowledgement": true,
    "pinned": false,
    "scheduled_for": null,
    "sent_at": null,
    "expires_at": "2026-01-15T00:00:00Z",
    "created_by": 1
}
```

### Available Event Types

- `broadcast.system_announcement` - System-wide announcements
- `broadcast.website_alert` - Website-specific alerts
- `broadcast.discount_code_alert` - Promotional discount alerts

### API Endpoints

#### Base URL: `/api/v1/admin-management/emails/broadcasts/`

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/` | List all broadcasts | Admin/Superadmin |
| `POST` | `/` | Create new broadcast | Admin/Superadmin |
| `GET` | `/{id}/` | Get broadcast details | Admin/Superadmin |
| `PATCH` | `/{id}/` | Update broadcast | Admin/Superadmin |
| `DELETE` | `/{id}/` | Delete broadcast | Admin/Superadmin |
| `POST` | `/{id}/send_now/` | Send immediately | Admin/Superadmin |
| `POST` | `/{id}/preview/` | Preview to current user | Admin/Superadmin |
| `GET` | `/{id}/stats/` | Get statistics | Admin/Superadmin |

#### Create Broadcast Request

```json
{
    "website": 1,
    "title": "System Maintenance Alert",
    "event_type": "broadcast.system_announcement",
    "message": "Our system will be under maintenance on January 15th from 2-4 AM EST.",
    "target_roles": ["client", "writer"],
    "channels": ["in_app", "email"],
    "require_acknowledgement": true,
    "is_active": true
}
```

#### Statistics Response

```json
{
    "total_recipients": 5000,
    "acknowledged": 3200,
    "acknowledgement_rate": 64.0
}
```

### Frontend Integration

```javascript
import emailsAPI from '@/api/emails'

// Create broadcast
await emailsAPI.createBroadcast({
    website: 1,
    title: "System Maintenance",
    event_type: "broadcast.system_announcement",
    message: "Maintenance scheduled...",
    channels: ["in_app", "email"],
    target_roles: ["client"]
})

// Send immediately
await emailsAPI.sendBroadcastNow(broadcastId)

// Preview
await emailsAPI.previewBroadcast(broadcastId)

// Get stats
const stats = await emailsAPI.getBroadcastStats(broadcastId)
```

---

## 🔔 Transactional Notifications

Transactional notifications are **automated system emails** triggered by user actions or system events.

### Features

- ✅ **Event-Driven**: Automatically triggered by system events
- ✅ **Template-Based**: Uses predefined templates
- ✅ **Priority-Based**: Different styling based on priority
- ✅ **Multi-Channel**: Can be sent via email, in-app, SMS, etc.

### Common Transactional Events

- `order.created` - Order confirmation
- `order.completed` - Order completion notification
- `auth.password_reset` - Password reset email
- `auth.email_verification` - Email verification
- `payment.received` - Payment confirmation
- `dispute.created` - Dispute notification

### Usage (Backend)

```python
from notifications_system.services.core import NotificationService

# Send transactional notification
NotificationService.send_notification(
    user=user,
    event="order.created",
    payload={
        "order_id": order.id,
        "order_total": order.total,
        "items": order.items
    },
    website=website,
    channels=["email"]
)
```

---

## 🔌 Email Service Providers

The system supports multiple email service providers for sending emails.

### Supported Providers

1. **SMTP** (Default)
   - Standard SMTP server
   - Gmail SMTP supported
   - Requires: `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USER`, `EMAIL_PASSWORD`

2. **SendGrid**
   - Professional email delivery
   - High deliverability
   - Requires: API Key

3. **Mailgun**
   - Transactional email service
   - Analytics included
   - Requires: API Key, Domain

4. **AWS SES**
   - Amazon Simple Email Service
   - Cost-effective at scale
   - Requires: AWS Credentials

### Configuration

#### Via Website Integration Config

```python
from websites.models import WebsiteIntegrationConfig

# Configure SendGrid
integration = WebsiteIntegrationConfig.objects.create(
    website=website,
    integration_type='sendgrid',
    api_key='SG.xxxxx',  # Encrypted storage
    config={
        'sender_email': 'noreply@example.com',
        'sender_name': 'GradeCrest Team'
    },
    is_active=True
)
```

#### Via Mass Email Service Integration

```python
from mass_emails.models import EmailServiceIntegration

integration = EmailServiceIntegration.objects.create(
    website=website,
    provider_name='sendgrid',
    api_key='SG.xxxxx',
    sender_email='noreply@example.com',
    sender_name='GradeCrest Team',
    is_active=True
)
```

### Environment Variables (SMTP)

```bash
# Gmail SMTP Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

---

## 📚 API Reference

### Mass Email Endpoints

#### List Campaigns

```http
GET /api/v1/admin-management/emails/mass-emails/
Authorization: Bearer {token}

Query Parameters:
- website_id: Filter by website
- status: Filter by status (draft, scheduled, sent, etc.)
- email_type: Filter by type (marketing, promos, etc.)
```

#### Create Campaign

```http
POST /api/v1/admin-management/emails/mass-emails/
Authorization: Bearer {token}
Content-Type: application/json

{
    "website": 1,
    "title": "Campaign Title",
    "subject": "Email Subject",
    "body": "<html>...</html>",
    "email_type": "marketing",
    "target_roles": ["client"],
    "status": "draft"
}
```

#### Send Campaign

```http
POST /api/v1/admin-management/emails/mass-emails/{id}/send_now/
Authorization: Bearer {token}
```

#### Schedule Campaign

```http
POST /api/v1/admin-management/emails/mass-emails/{id}/schedule/
Authorization: Bearer {token}
Content-Type: application/json

{
    "scheduled_time": "2026-01-01T00:00:00Z"
}
```

#### Get Analytics

```http
GET /api/v1/admin-management/emails/mass-emails/{id}/analytics/
Authorization: Bearer {token}
```

### Broadcast Endpoints

#### List Broadcasts

```http
GET /api/v1/admin-management/emails/broadcasts/
Authorization: Bearer {token}

Query Parameters:
- website_id: Filter by website
- is_active: Filter by active status
```

#### Create Broadcast

```http
POST /api/v1/admin-management/emails/broadcasts/
Authorization: Bearer {token}
Content-Type: application/json

{
    "website": 1,
    "title": "Broadcast Title",
    "event_type": "broadcast.system_announcement",
    "message": "Broadcast message text",
    "channels": ["in_app", "email"],
    "target_roles": ["client"],
    "require_acknowledgement": true
}
```

#### Send Broadcast

```http
POST /api/v1/admin-management/emails/broadcasts/{id}/send_now/
Authorization: Bearer {token}
```

#### Preview Broadcast

```http
POST /api/v1/admin-management/emails/broadcasts/{id}/preview/
Authorization: Bearer {token}
```

#### Get Statistics

```http
GET /api/v1/admin-management/emails/broadcasts/{id}/stats/
Authorization: Bearer {token}
```

---

## ⚙️ Configuration

### Website Email Settings

Each website can have its own email configuration:

```python
from websites.models import Website

website = Website.objects.get(id=1)

# Marketing sender email
website.marketing_sender_email = "marketing@example.com"

# Default sender
website.default_sender_email = "noreply@example.com"
website.default_sender_name = "GradeCrest Team"

website.save()
```

### Email Templates

#### Create Reusable Template

```python
from mass_emails.models import EmailTemplate

template = EmailTemplate.objects.create(
    name="New Year Promotion Template",
    subject="Happy New Year from {{ website_name }}",
    body="""
    <html>
    <body>
        <h1>Happy New Year!</h1>
        <p>{{ message }}</p>
        <a href="{{ cta_url }}">{{ cta_label }}</a>
    </body>
    </html>
    """,
    is_global=True,
    created_by=admin_user
)
```

---

## 💡 Usage Examples

### Example 1: Send New Year Promotion Email

```python
from mass_emails.models import EmailCampaign
from mass_emails.tasks import send_email_campaign
from websites.models import Website

website = Website.objects.get(id=1)

campaign = EmailCampaign.objects.create(
    website=website,
    title="New Year 2026 Promotion",
    subject="Happy New Year from GradeCrest TEAM",
    body="""
    <html>
    <body style="font-family: Arial, sans-serif;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h1 style="color: #2563eb;">Happy New Year from GradeCrest TEAM</h1>
            <p>You have been our best in 2025. Because of you, our writers got to write 
            the most assignments in 2025.</p>
            <ul>
                <li>Essays and research papers</li>
                <li>Assignments and coursework</li>
                <li>Literature reviews and case studies</li>
            </ul>
            <p>Ask the support for discount codes.</p>
        </div>
    </body>
    </html>
    """,
    email_type="marketing",
    target_roles=["client"],
    status="draft",
    created_by=admin_user
)

# Send immediately
send_email_campaign.delay(campaign.id)

# Or schedule
campaign.scheduled_time = timezone.now() + timedelta(days=1)
campaign.status = "scheduled"
campaign.save()
```

### Example 2: Send System Maintenance Broadcast

```python
from notifications_system.services.broadcast_services import BroadcastNotificationService
from websites.models import Website

website = Website.objects.get(id=1)

broadcast = BroadcastNotificationService.send_broadcast(
    event="broadcast.system_announcement",
    title="Scheduled Maintenance",
    message="Our system will be under maintenance on January 15th from 2-4 AM EST. "
            "Please plan accordingly.",
    website=website,
    channels=["in_app", "email"],
    priority=5
)
```

### Example 3: Create and Send via API

```bash
# Create campaign
curl -X POST https://api.example.com/api/v1/admin-management/emails/mass-emails/ \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "website": 1,
    "title": "New Year Promotion",
    "subject": "Happy New Year!",
    "body": "<html><body><h1>Happy New Year!</h1></body></html>",
    "email_type": "marketing",
    "target_roles": ["client"],
    "status": "draft"
  }'

# Send campaign
curl -X POST https://api.example.com/api/v1/admin-management/emails/mass-emails/1/send_now/ \
  -H "Authorization: Bearer {token}"
```

---

## ✅ Best Practices

### Mass Email Best Practices

1. **Test Before Sending**
   - Always preview campaigns before sending
   - Send test emails to yourself first
   - Check HTML rendering in multiple email clients

2. **Segment Your Audience**
   - Use `target_roles` to send relevant content
   - Consider creating separate campaigns for different user segments

3. **Monitor Analytics**
   - Track open rates and click rates
   - Monitor bounce rates and failures
   - Adjust content based on performance

4. **Comply with Regulations**
   - Include unsubscribe links
   - Respect user preferences
   - Follow CAN-SPAM and GDPR requirements

5. **Optimize HTML**
   - Use inline CSS for email compatibility
   - Test in multiple email clients
   - Keep file sizes reasonable

### Broadcast Best Practices

1. **Use Appropriate Channels**
   - Use `in_app` for non-urgent announcements
   - Use `email` for important updates
   - Use both for critical announcements

2. **Set Expiration Dates**
   - Set `expires_at` for time-sensitive broadcasts
   - Clean up expired broadcasts regularly

3. **Target Appropriately**
   - Use `target_roles` to reach relevant users
   - Avoid broadcasting to all users unless necessary

4. **Require Acknowledgements for Critical Messages**
   - Set `require_acknowledgement=True` for important announcements
   - Track acknowledgement rates

### General Best Practices

1. **Email Provider Selection**
   - Use SMTP for development/testing
   - Use SendGrid/Mailgun for production
   - Monitor deliverability rates

2. **Rate Limiting**
   - Respect email provider rate limits
   - Use Celery for background processing
   - Implement retry logic for failed sends

3. **Error Handling**
   - Log all email failures
   - Implement retry mechanisms
   - Alert admins on high failure rates

4. **Security**
   - Encrypt API keys in database
   - Validate email addresses
   - Sanitize HTML content

---

## 🔧 Troubleshooting

### Common Issues

#### Emails Not Sending

**Problem**: Campaigns stuck in "sending" status

**Solutions**:
1. Check Celery worker is running: `celery -A writing_system worker -l info`
2. Verify email provider configuration
3. Check email provider rate limits
4. Review error logs in `campaign.failure_report`

#### High Bounce Rate

**Problem**: Many emails bouncing

**Solutions**:
1. Verify sender email is authenticated (SPF/DKIM)
2. Clean email list (remove invalid addresses)
3. Check email provider reputation
4. Review bounce messages in analytics

#### HTML Not Rendering

**Problem**: HTML emails appear as plain text

**Solutions**:
1. Ensure `body` field contains valid HTML
2. Use inline CSS (not external stylesheets)
3. Test in multiple email clients
4. Check email provider HTML support

#### Broadcast Not Reaching Users

**Problem**: Broadcast not appearing for users

**Solutions**:
1. Verify `target_roles` includes user's role
2. Check `is_active=True`
3. Verify `channels` includes desired channel
4. Check user notification preferences

### Debugging

#### Check Campaign Status

```python
from mass_emails.models import EmailCampaign

campaign = EmailCampaign.objects.get(id=1)
print(f"Status: {campaign.status}")
print(f"Recipients: {campaign.recipients.count()}")
print(f"Sent: {campaign.recipients.filter(status='sent').count()}")
print(f"Failed: {campaign.recipients.filter(status='failed').count()}")
```

#### Test Email Provider

```python
from django.core.mail import send_mail

send_mail(
    subject='Test Email',
    message='This is a test',
    from_email='noreply@example.com',
    recipient_list=['test@example.com'],
    fail_silently=False,
)
```

#### Check Email Service Integration

```python
from mass_emails.models import EmailServiceIntegration

integration = EmailServiceIntegration.objects.get(website_id=1)
print(f"Provider: {integration.provider_name}")
print(f"Active: {integration.is_active}")
print(f"Sender: {integration.sender_email}")
```

---

## 📖 Additional Resources

- [Email Templates Guide](./EMAIL_TEMPLATES.md) - Template system documentation
- [Email Template Guide](./EMAIL_TEMPLATE_GUIDE.md) - Creating custom templates
- [Gmail SMTP Setup](./GMAIL_SMTP_SETUP.md) - Gmail configuration
- [Website Integration Guide](./websites/INTEGRATION_CONFIG_GUIDE.md) - Email provider setup

---

## 🆘 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review error logs in Django admin
3. Contact system administrator
4. Review email provider documentation

---

**Last Updated**: January 2026  
**Version**: 1.0

