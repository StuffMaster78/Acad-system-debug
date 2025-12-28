# Website Integration Configuration Guide

## Overview

The `WebsiteIntegrationConfig` model provides a centralized, secure way to store API keys and configuration for third-party services per website. All sensitive credentials are encrypted using Fernet encryption before storage.

## Features

✅ **Encrypted Storage** - API keys, secrets, and tokens are encrypted at rest  
✅ **Per-Website Configuration** - Each website can have its own integration settings  
✅ **Multiple Integration Types** - Support for 40+ integration types  
✅ **Flexible Configuration** - JSON config field for custom settings  
✅ **Admin Interface** - Full Django admin support  
✅ **REST API** - Complete CRUD API for managing integrations  
✅ **Security** - Masked keys in API responses (only last 4 chars visible)

## Supported Integration Types

### Payment Gateways
- Stripe
- PayPal
- Razorpay
- Square
- Mollie

### Email Services
- SendGrid
- Mailgun
- AWS SES
- Postmark
- SparkPost
- Mandrill

### SMS Services
- Twilio
- Vonage (Nexmo)
- AWS SNS
- MessageBird

### File Storage
- AWS S3
- DigitalOcean Spaces
- Google Cloud Storage
- Azure Blob Storage

### CDN
- Cloudflare
- AWS CloudFront
- Fastly

### Social Authentication
- Google OAuth
- Facebook OAuth
- GitHub OAuth
- LinkedIn OAuth
- Twitter OAuth

### Analytics & Tracking
- Facebook Pixel
- Pinterest Tag
- TikTok Pixel
- Hotjar
- Mixpanel
- Segment

### Communication
- Intercom
- Zendesk
- Drift
- Crisp

### Document Processing
- PDF Generation API
- DocuSign
- HelloSign

### AI Services
- OpenAI
- Anthropic
- Cohere

### Automation
- Zapier
- Make (Integromat)
- Custom Webhook

## Usage

### 1. Django Admin

Navigate to: **Django Admin → Website Integration Configurations**

- Create new integrations
- View existing integrations
- Edit configurations
- Enable/disable integrations

**Note:** Encrypted fields are read-only in admin. Use the API or frontend to set values.

### 2. REST API

#### List Integrations
```bash
GET /api/v1/websites/integrations/?website=1
```

#### Get Integration
```bash
GET /api/v1/websites/integrations/{id}/
```

#### Create Integration
```bash
POST /api/v1/websites/integrations/
{
  "website": 1,
  "integration_type": "stripe",
  "name": "Production Stripe",
  "api_key": "sk_live_...",
  "secret_key": "sk_live_...",
  "config": {
    "webhook_secret": "whsec_...",
    "currency": "usd"
  },
  "is_active": true
}
```

#### Update Integration
```bash
PATCH /api/v1/websites/integrations/{id}/
{
  "api_key": "sk_new_...",
  "is_active": false
}
```

#### Delete Integration
```bash
DELETE /api/v1/websites/integrations/{id}/
```

### 3. Python Code

#### Get Integration Credentials
```python
from websites.models_integrations import WebsiteIntegrationConfig
from websites.models import Website

website = Website.objects.get(id=1)

# Get active Stripe integration
integration = WebsiteIntegrationConfig.get_active_integration(
    website=website,
    integration_type='stripe'
)

if integration:
    api_key = integration.get_api_key()
    secret_key = integration.get_secret_key()
    config = integration.config
```

#### Get Credentials (Helper Method)
```python
credentials = WebsiteIntegrationConfig.get_integration_credentials(
    website=website,
    integration_type='stripe'
)

if credentials:
    api_key = credentials['api_key']
    secret_key = credentials['secret_key']
    config = credentials['config']
```

#### Create Integration Programmatically
```python
integration = WebsiteIntegrationConfig.objects.create(
    website=website,
    integration_type='stripe',
    name='Production Stripe',
    created_by=request.user
)

# Set encrypted keys
integration.set_api_key('sk_live_...')
integration.set_secret_key('sk_live_...')
integration.config = {
    'webhook_secret': 'whsec_...',
    'currency': 'usd'
}
integration.save()
```

## Security

### Encryption
- Uses Fernet symmetric encryption (AES-128)
- Encryption key stored in `TOKEN_ENCRYPTION_KEY` environment variable
- Keys are encrypted before database storage
- Decryption only happens when explicitly requested

### API Security
- Only admins and superadmins can manage integrations
- API responses mask sensitive fields (only last 4 characters shown)
- Full keys only available through encrypted storage methods

### Best Practices
1. **Never log decrypted keys** - Always use encrypted storage
2. **Rotate keys regularly** - Update integrations when keys change
3. **Use environment variables** - For system-level encryption key
4. **Limit access** - Only grant admin access to trusted users
5. **Audit changes** - Monitor integration config changes

## Migration

Run the migration to create the table:

```bash
python manage.py migrate websites
```

## Frontend Integration

The frontend API is available at `frontend/src/api/websites.js`:

```javascript
import websitesAPI from '@/api/websites'

// List integrations for a website
const integrations = await websitesAPI.listIntegrations({ website: 1 })

// Create integration
await websitesAPI.createIntegration({
  website: 1,
  integration_type: 'stripe',
  api_key: 'sk_live_...',
  secret_key: 'sk_live_...',
  config: { currency: 'usd' }
})

// Update integration
await websitesAPI.updateIntegration(integrationId, {
  is_active: false
})
```

## Example Use Cases

### Stripe Payment Gateway
```python
stripe_config = WebsiteIntegrationConfig.get_active_integration(
    website=website,
    integration_type='stripe'
)

if stripe_config:
    import stripe
    stripe.api_key = stripe_config.get_api_key()
    # Use Stripe API
```

### SendGrid Email
```python
sendgrid_config = WebsiteIntegrationConfig.get_active_integration(
    website=website,
    integration_type='sendgrid'
)

if sendgrid_config:
    import sendgrid
    sg = sendgrid.SendGridAPIClient(sendgrid_config.get_api_key())
    # Send email
```

### Twilio SMS
```python
twilio_config = WebsiteIntegrationConfig.get_active_integration(
    website=website,
    integration_type='twilio'
)

if twilio_config:
    from twilio.rest import Client
    client = Client(
        twilio_config.get_api_key(),  # Account SID
        twilio_config.get_secret_key()  # Auth Token
    )
    # Send SMS
```

## Future Enhancements

- [ ] Frontend UI in WebsiteManagement.vue
- [ ] Integration testing/validation
- [ ] Webhook endpoint management
- [ ] Integration templates/presets
- [ ] Usage analytics per integration
- [ ] Key rotation reminders
- [ ] Integration health checks

## Troubleshooting

### "TOKEN_ENCRYPTION_KEY not configured"
Set the `TOKEN_ENCRYPTION_KEY` environment variable:
```bash
export TOKEN_ENCRYPTION_KEY=$(python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
```

### "Failed to decrypt"
- Ensure `TOKEN_ENCRYPTION_KEY` matches the one used for encryption
- Check that the integration exists and is active
- Verify database integrity

### Integration not found
- Check `is_active=True`
- Verify `website` and `integration_type` match
- Check if `name` parameter is required

