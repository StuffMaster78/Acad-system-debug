# Subscription Management & Privacy/Security Page Implementation

## Overview

Implemented a comprehensive subscription management system for clients and a privacy/security information page that reflects standard operation procedures (SOPs).

---

## Features Implemented

### 1. Subscription Management System

#### Models
- **File**: `backend/users/models/subscriptions.py`
- **Models**:
  - `ClientSubscription`: Manages individual subscription types for clients
  - `SubscriptionPreference`: Global subscription preferences for clients
  - `SubscriptionType`: Enum for available subscription types
  - `DeliveryChannel`: Enum for delivery channels

#### Subscription Types Available
- Newsletter
- Blog Post Updates
- Coupon Updates
- Marketing Messages
- Unread Messages
- Transactional Messages (cannot be unsubscribed)
- Notifications
- Order Updates
- Promotional Offers
- Product Updates
- Security Alerts
- Account Updates

#### Delivery Channels
- Email
- SMS
- Push Notifications
- In-App Notifications

#### Service
- **File**: `backend/users/services/subscription_service.py`
- **Features**:
  - Subscribe/unsubscribe to subscription types
  - Update subscription frequency (immediate, daily, weekly, monthly)
  - Update preferred delivery channels
  - Manage global subscription preferences
  - Marketing consent management
  - Do-not-disturb hours
  - Check if user can receive specific subscription types

### 2. API Endpoints

#### Subscription Management
- `GET /api/users/subscriptions/list-all/` - List all subscriptions with status
- `POST /api/users/subscriptions/subscribe/` - Subscribe to a type
- `POST /api/users/subscriptions/unsubscribe/` - Unsubscribe from a type
- `PUT /api/users/subscriptions/update-frequency/` - Update frequency
- `PUT /api/users/subscriptions/update-channels/` - Update preferred channels
- `GET /api/users/subscriptions/preferences/` - Get preferences
- `PUT /api/users/subscriptions/update-preferences/` - Update preferences

#### Privacy & Security Information
- `GET /api/users/privacy-security/privacy-policy/` - Privacy policy
- `GET /api/users/privacy-security/security-practices/` - Security practices & SOPs
- `GET /api/users/privacy-security/data-rights/` - User data rights
- `GET /api/users/privacy-security/cookie-policy/` - Cookie policy
- `GET /api/users/privacy-security/terms-of-service/` - Terms of service
- `GET /api/users/privacy-security/all/` - Summary of all sections

---

## Subscription Features

### Subscription Preferences
- **Master Switch**: Enable/disable all subscriptions
- **Marketing Consent**: Separate consent for marketing communications
- **Channel Preferences**: Enable/disable specific delivery channels
- **Do-Not-Disturb**: Set quiet hours for non-critical messages
- **Transactional Messages**: Always enabled (cannot be disabled)

### Subscription Frequency Options
- **Immediate**: Receive messages as they occur
- **Daily Digest**: Receive once per day
- **Weekly Digest**: Receive once per week
- **Monthly Digest**: Receive once per month

### Subscription Management Rules
1. **Transactional Messages**: Cannot be unsubscribed (required for service)
2. **Marketing Messages**: Require explicit marketing consent
3. **Do-Not-Disturb**: Only critical messages (security alerts, order updates, account updates) are sent during DND hours
4. **Master Switch**: When disabled, all subscriptions are disabled except transactional

---

## Privacy & Security Information

### Privacy Policy Sections
- Information We Collect
- How We Use Your Information
- Data Sharing
- Data Security
- Your Rights
- Data Retention

### Security Practices & SOPs
- **Authentication & Access Control**
  - Multi-factor authentication (2FA)
  - Strong password requirements
  - Session management
  - Account lockout
  - Device fingerprinting
  - IP whitelisting

- **Password Security**
  - Hashed passwords
  - Password history
  - Password expiration
  - Password breach detection
  - Password strength requirements

- **Account Protection**
  - Account suspension
  - Probation system
  - Email change approval
  - Phone verification
  - Security questions
  - Account takeover protection

- **Data Encryption**
  - TLS/SSL for data in transit
  - Encryption at rest
  - Encrypted security questions
  - Secure payment handling

- **Privacy Controls**
  - Writer/client ID/pen name visibility
  - Profile visibility controls
  - Admin approval for changes
  - Avatar approval

- **Monitoring & Logging**
  - Login attempt logging
  - Activity audit logs
  - Security event monitoring
  - Data access logs

- **Incident Response**
  - Prompt investigation
  - User notification
  - Immediate remediation
  - Post-incident reviews

- **Compliance**
  - GDPR compliance
  - Data subject rights
  - Privacy by design
  - Security assessments

### Data Rights
- Right to Access
- Right to Rectification
- Right to Erasure
- Right to Restrict Processing
- Right to Data Portability
- Right to Object
- Right to Withdraw Consent

---

## Usage Examples

### Subscribe to Newsletter
```http
POST /api/users/subscriptions/subscribe/
Content-Type: application/json

{
  "subscription_type": "newsletter",
  "frequency": "weekly",
  "preferred_channels": ["email", "in_app"]
}
```

### Unsubscribe from Marketing
```http
POST /api/users/subscriptions/unsubscribe/
Content-Type: application/json

{
  "subscription_type": "marketing_messages"
}
```

### Update Preferences
```http
PUT /api/users/subscriptions/update-preferences/
Content-Type: application/json

{
  "all_subscriptions_enabled": true,
  "marketing_consent": true,
  "email_enabled": true,
  "sms_enabled": false,
  "push_enabled": false,
  "in_app_enabled": true,
  "dnd_enabled": true,
  "dnd_start_hour": 22,
  "dnd_end_hour": 6
}
```

### Get Privacy Policy
```http
GET /api/users/privacy-security/privacy-policy/
```

### Get Security Practices
```http
GET /api/users/privacy-security/security-practices/
```

---

## Database Schema

### ClientSubscription
- `user` (ForeignKey to User)
- `website` (ForeignKey to Website)
- `subscription_type` (CharField)
- `is_subscribed` (BooleanField)
- `subscribed_at` (DateTimeField)
- `unsubscribed_at` (DateTimeField, nullable)
- `last_sent_at` (DateTimeField, nullable)
- `preferred_channels` (JSONField)
- `frequency` (CharField)
- `metadata` (JSONField)

### SubscriptionPreference
- `user` (OneToOneField to User)
- `website` (ForeignKey to Website)
- `all_subscriptions_enabled` (BooleanField)
- `marketing_consent` (BooleanField)
- `marketing_consent_date` (DateTimeField, nullable)
- `email_enabled` (BooleanField)
- `sms_enabled` (BooleanField)
- `push_enabled` (BooleanField)
- `in_app_enabled` (BooleanField)
- `dnd_enabled` (BooleanField)
- `dnd_start_hour` (PositiveSmallIntegerField)
- `dnd_end_hour` (PositiveSmallIntegerField)
- `transactional_enabled` (BooleanField)

---

## Frontend Integration

### Subscription Management UI
1. **Subscription List**: Show all available subscriptions with toggle switches
2. **Frequency Selector**: Dropdown for each subscription type
3. **Channel Preferences**: Checkboxes for preferred channels
4. **Master Switch**: Toggle for all subscriptions
5. **Marketing Consent**: Separate checkbox with date
6. **Do-Not-Disturb**: Time picker for quiet hours

### Privacy & Security Page
1. **Tabbed Interface**: Separate tabs for each section
2. **Last Updated**: Display last updated timestamp
3. **Expandable Sections**: Collapsible sections for better UX
4. **Print/Export**: Option to print or export policies

---

## Future Enhancements

1. **Social Account Linking**: Link Apple/Google accounts (mentioned for later)
2. **Subscription Analytics**: Track subscription engagement
3. **A/B Testing**: Test different subscription messaging
4. **Custom Subscription Types**: Allow admins to create custom types
5. **Subscription Templates**: Pre-configured subscription bundles
6. **Email Preferences**: Granular email type preferences
7. **Unsubscribe Links**: One-click unsubscribe in emails
8. **Subscription History**: Track subscription changes over time

---

## Migration Required

A migration needs to be created for the new models:
- `ClientSubscription`
- `SubscriptionPreference`

Run:
```bash
python manage.py makemigrations users
python manage.py migrate
```

---

*Implementation completed: December 3, 2025*

