# 📧 Email Templates System

The Writing System Platform includes a comprehensive email template system that supports priority-based styling, multi-tenant customization, and flexible template rendering.

## 🎯 Overview

The email template system provides:

- **Priority-Based Templates**: Different visual styles based on notification priority
- **Multi-Tenant Support**: Website-specific template overrides
- **Internationalization**: Multi-language template support
- **Flexible Rendering**: Class-based, database, and file-based templates
- **Rich HTML Templates**: Professional, responsive email designs
- **Template Inheritance**: Base template with priority-specific overrides

## 📁 Template Structure

### Location

Email templates are stored in:
```
backend/notifications_system/templates/notifications/emails/
```

### Available Templates

| Template | Priority | Use Case | Color Scheme |
|----------|----------|----------|--------------|
| `base.html` | Base | Base template (extended by others) | Blue (#2563eb) |
| `critical.html` | Emergency | Critical/urgent notifications | Red (#dc2626) |
| `high.html` | High | Important notifications | Orange (#f97316) |
| `normal.html` | Normal | Standard notifications | Blue (#2563eb) |
| `low.html` | Low | Low-priority notifications | Gray |
| `passive.html` | Passive | Background notifications | Light Gray |
| `digest_email.html` | Digest | Daily/weekly digest emails | - |
| `medium.html` | Medium | Medium-priority notifications | - |

## 🎨 Template Hierarchy

### Base Template (`base.html`)

The base template provides the foundation for all email templates:

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>{{ subject }}</title>
  <style>
    /* Base styles */
  </style>
</head>
<body>
  <div class="email-container">
    <h2>{{ subject }}</h2>
    <p>{{ message|linebreaks }}</p>
    
    {% if cta_url %}
      <a href="{{ cta_url }}" class="btn">{{ cta_label|default:"View Details" }}</a>
    {% endif %}
    
    <div class="footer">
      Sent by {{ website_name|default:"Our Platform" }}<br>
      Do not reply to this email.
    </div>
  </div>
</body>
</html>
```

### Priority Templates

Priority templates extend the base template and add priority-specific styling:

**Critical Template** (`critical.html`):
```html
{% extends "notifications/emails/base.html" %}
{% block content %}
  <h2 style="color:#dc2626">{{ subject }}</h2>
  <p>{{ message|linebreaks }}</p>
{% endblock %}
```

**High Priority Template** (`high.html`):
```html
{% extends "notifications/emails/base.html" %}
{% block content %}
  <h2 style="color:#f97316">{{ subject }}</h2>
  <p>{{ message|linebreaks }}</p>
{% endblock %}
```

## 🔧 Template System Architecture

### 1. Priority-Based Template Selection

Templates are automatically selected based on notification priority:

```python
# backend/notifications_system/utils/template_priority.py

TEMPLATE_MAP = {
    NotificationPriority.EMERGENCY: "notifications/emails/critical.html",
    NotificationPriority.HIGH: "notifications/emails/high.html",
    NotificationPriority.MEDIUM_HIGH: "notifications/emails/high.html",
    NotificationPriority.NORMAL: "notifications/emails/normal.html",
    NotificationPriority.LOW: "notifications/emails/low.html",
    NotificationPriority.PASSIVE: "notifications/emails/passive.html",
}
```

### 2. Template Rendering

Templates are rendered using Django's template engine:

```python
from notifications_system.utils.email_renderer import render_notification_email

html_body = render_notification_email(
    subject="Order Completed",
    message="Your order #12345 has been completed.",
    priority=NotificationPriority.NORMAL,
    context={
        "order_id": 12345,
        "cta_url": "https://example.com/orders/12345",
        "cta_label": "View Order"
    }
)
```

### 3. Multi-Tenant Template Overrides

Templates can be customized per website:

```python
# Database-stored templates (NotificationTemplate model)
# Allow per-website customization via admin panel
```

## 📝 Template Variables

### Common Variables

All templates have access to these variables:

| Variable | Type | Description |
|----------|------|-------------|
| `subject` | string | Email subject line |
| `message` | string | Main message content |
| `website_name` | string | Website/tenant name |
| `user` | User | User object (if available) |
| `website` | Website | Website object (if available) |
| `cta_url` | string | Call-to-action URL (optional) |
| `cta_label` | string | Call-to-action button label (optional) |

### Context Variables

Additional context can be passed when rendering:

```python
context = {
    "order_id": 12345,
    "amount": 99.99,
    "currency": "USD",
    "cta_url": "https://example.com/orders/12345",
    "cta_label": "View Order Details"
}
```

## 🚀 Usage Examples

### Example 1: Basic Email

```python
from notifications_system.utils.email_renderer import render_notification_email
from notifications_system.utils.email_helpers import send_website_mail

# Render template
html_body = render_notification_email(
    subject="Welcome to Our Platform",
    message="Thank you for joining us!",
    priority=NotificationPriority.NORMAL
)

# Send email
send_website_mail(
    subject="Welcome to Our Platform",
    message="Thank you for joining us!",
    recipient_list=["user@example.com"],
    html_message=html_body,
    website=website
)
```

### Example 2: Priority Email with CTA

```python
html_body = render_notification_email(
    subject="Payment Required",
    message="Your invoice #INV-12345 is due.",
    priority=NotificationPriority.HIGH,
    context={
        "invoice_id": "INV-12345",
        "amount": 199.99,
        "cta_url": "https://example.com/invoices/INV-12345/pay",
        "cta_label": "Pay Now"
    }
)
```

### Example 3: Using Notification System

```python
from notifications_system.services.notification_helper import NotificationHelper

NotificationHelper.send_notification(
    user=user,
    event_key="order.completed",
    payload={
        "order_id": 12345,
        "title": "Order Completed",
        "message": "Your order has been completed successfully.",
        "cta_url": f"https://example.com/orders/12345"
    },
    priority=NotificationPriority.NORMAL
)
```

## 🎨 Creating Custom Templates

### Step 1: Create Template File

Create a new template file in `backend/notifications_system/templates/notifications/emails/`:

```html
<!-- custom_template.html -->
{% extends "notifications/emails/base.html" %}
{% block content %}
  <h2 style="color:#your-color">{{ subject }}</h2>
  <div class="custom-content">
    {{ message|linebreaks }}
    
    {% if custom_field %}
      <p><strong>Custom Field:</strong> {{ custom_field }}</p>
    {% endif %}
  </div>
{% endblock %}
```

### Step 2: Use Custom Template

```python
html_body = render_notification_email(
    subject="Custom Notification",
    message="This uses a custom template.",
    template_name="notifications/emails/custom_template.html",
    context={"custom_field": "Custom Value"}
)
```

### Step 3: Register Template (Optional)

For class-based templates, register in the template registry:

```python
# backend/notifications_system/templates/__init__.py

@register_template("custom.event")
class CustomEventTemplate(BaseNotificationTemplate):
    def render(self, payload: dict) -> tuple[str, str, str]:
        title = payload.get("title", "Custom Event")
        text = payload.get("message", "")
        html = render_to_string(
            "notifications/emails/custom_template.html",
            {"subject": title, "message": text, **payload}
        )
        return title, text, html
```

## 📊 Template Types

### 1. File-Based Templates

- **Location**: `templates/notifications/emails/`
- **Use Case**: Static, reusable templates
- **Advantages**: Version controlled, easy to edit
- **Example**: Priority-based templates

### 2. Database Templates

- **Model**: `NotificationTemplate`
- **Use Case**: User-editable, per-website customization
- **Advantages**: No code deployment needed, multi-tenant
- **Access**: Admin panel or API

### 3. Class-Based Templates

- **Location**: `notifications_system/templates/`
- **Use Case**: Programmatic template generation
- **Advantages**: Type-safe, testable, flexible
- **Example**: Order templates, payment templates

## 🔍 Template Resolution Order

The system resolves templates in this order:

1. **Explicit Template** (if `template_name` provided)
2. **Database Template** (per website/locale)
3. **Class-Based Template** (from registry)
4. **Priority-Based Template** (file-based)
5. **Default Template** (`normal.html`)

## 🌍 Internationalization

Templates support multiple languages:

```python
# Database templates support locale field
template = NotificationTemplate.objects.get(
    event__key="order.completed",
    channel="email",
    locale="de",  # German
    website=website
)
```

## 📧 Special Templates

### Digest Email Template

The `digest_email.html` template is used for daily/weekly digests:

```html
<h2>Hi {{ user.get_full_name|default:user.username }},</h2>
<p>Here's your latest digest:</p>

<ul>
  {% for item in items %}
    <li>
      <strong>{{ item.title }}</strong><br>
      {{ item.message|linebreaksbr }}
      <small>{{ item.timestamp|naturaltime }}</small>
    </li>
  {% endfor %}
</ul>
```

### Order-Specific Templates

Order-related templates are in `backend/orders/templates/notifications/`:

- `order_paid.html` - Payment confirmation
- Custom order templates can be added here

## 🛠️ Template Development

### Best Practices

1. **Extend Base Template**: Always extend `base.html` for consistency
2. **Use Semantic HTML**: Ensure email client compatibility
3. **Inline Styles**: Use inline CSS (email clients strip `<style>` tags)
4. **Test Across Clients**: Test in Gmail, Outlook, Apple Mail
5. **Responsive Design**: Use responsive email techniques
6. **Accessibility**: Use proper heading hierarchy and alt text

### Testing Templates

```python
# Preview template in Django admin
# URL: /admin/notifications/preview-email/?priority=normal

# Or programmatically
from django.template.loader import render_to_string

html = render_to_string(
    "notifications/emails/normal.html",
    {
        "subject": "Test Email",
        "message": "This is a test message.",
        "cta_url": "https://example.com",
        "cta_label": "Click Here"
    }
)
print(html)
```

## 📚 Related Documentation

- **[Notification System](./NOTIFICATION_INTEGRATION_GUIDE.md)**: Complete notification system guide
- **[Invoice System](./INVOICE_PAYMENT_SYSTEM_DESIGN.md)**: Invoice email templates
- **[Mass Emails](./mass_emails/README.md)**: Bulk email campaigns

## 🔗 API Endpoints

### Preview Template

```
GET /admin/notifications/preview-email/?priority=normal
```

### Template Management

```
GET    /api/v1/email-templates/          # List templates
POST   /api/v1/email-templates/          # Create template
GET    /api/v1/email-templates/{id}/      # Get template
PUT    /api/v1/email-templates/{id}/      # Update template
DELETE /api/v1/email-templates/{id}/      # Delete template
```

## 🎯 Summary

The email template system provides:

- ✅ Priority-based visual styling
- ✅ Multi-tenant customization
- ✅ Internationalization support
- ✅ Flexible template resolution
- ✅ Professional HTML emails
- ✅ Easy template creation and management

For questions or contributions, see [CONTRIBUTING.md](../CONTRIBUTING.md).

---

**Happy Templating! 📧**

