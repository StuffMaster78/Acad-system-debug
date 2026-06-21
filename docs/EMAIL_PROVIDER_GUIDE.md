# Email Provider Guide

The platform uses [django-anymail](https://anymail.dev/) in production, which means you can
swap providers by changing two environment variables and redeploying — no code changes needed.

Three options are wired in `production.py`:

| Option | `DEFAULT_EMAIL_PROVIDER` value | Package driver |
|--------|-------------------------------|----------------|
| **Resend** _(default)_ | `resend` | `anymail.backends.resend.EmailBackend` |
| **SendGrid** | `sendgrid` | `anymail.backends.sendgrid.EmailBackend` |
| **SMTP** _(any provider)_ | anything else / unset | `django.core.mail.backends.smtp.EmailBackend` |

---

## Choosing a provider

### Resend — recommended for new deployments

**Why:** Clean API-first design, generous free tier (3 000 emails/month), excellent
deliverability, dead-simple DNS setup, real-time webhooks, and a developer-friendly dashboard.
The default `DEFAULT_EMAIL_PROVIDER=resend` is already set in `production.py`.

**Good fit when:** You want the lowest setup friction and are sending transactional email only
(order confirmations, password resets, writer notifications, receipts).

**Pricing:** Free to 3k/month, then ~$20/month for 50k. No dedicated IP until higher tiers.

**Limits:** No marketing/bulk email on free tier. Not ideal if you ever need campaign sends
from the same account.

---

### SendGrid — battle-tested, full feature set

**Why:** Industry standard, extremely reliable, detailed analytics, dedicated IPs available,
supports both transactional and marketing email from one account.

**Good fit when:** You expect high volume (>50k/month) or need marketing email and transactional
email under one roof, or your ops team already knows SendGrid.

**Pricing:** Free to 100 emails/day (very limited), then $20/month for 50k. Dedicated IPs
from $30/month extra.

**Limits:** Dashboard is cluttered. Free tier daily cap is too low for active platforms.
Domain authentication requires more DNS records than Resend.

---

### SMTP — escape hatch / existing infrastructure

**Why:** Works with any SMTP relay: Gmail Workspace, Postmark, Mailgun, Amazon SES, Brevo,
or your own mail server. No extra package needed beyond Django's built-in backend.

**Good fit when:** You already have an SMTP relay you're paying for, or you need to route
through a specific IP / custom relay for compliance reasons.

**Limits:** No webhook delivery tracking, no per-message open/click events, harder to
debug bounces. Not recommended as a primary choice for a production writing platform.

---

## Configuration

### Option A — Resend

See [RESEND_SETUP.md](RESEND_SETUP.md) for the full step-by-step guide.

Quick reference:

```env
DEFAULT_EMAIL_PROVIDER=resend
RESEND_API_KEY=re_xxxxxxxxxxxx
RESEND_WEBHOOK_SECRET=whsec_xxxxxxxxxxxx   # optional but recommended
DEFAULT_FROM_EMAIL=no-reply@yourdomain.com
```

Webhook endpoint (bounce + complaint suppression):
`POST /api/v1/notifications/webhooks/resend/`

---

### Option B — SendGrid

1. Sign up at sendgrid.com → Settings → API Keys → create key with **Mail Send** permission.
2. Authenticate your domain: Settings → Sender Authentication → Domain Authentication.
3. Set env vars:

```env
DEFAULT_EMAIL_PROVIDER=sendgrid
SENDGRID_API_KEY=SG.xxxxxxxxxxxx
DEFAULT_FROM_EMAIL=no-reply@yourdomain.com
```

---

### Option C — SMTP relay

Set `DEFAULT_EMAIL_PROVIDER` to anything that isn't `resend` or `sendgrid` (or just omit it),
then provide the SMTP credentials:

```env
# Leave DEFAULT_EMAIL_PROVIDER unset, or set to e.g. "smtp"
EMAIL_HOST=smtp.yourprovider.com
EMAIL_PORT=587
EMAIL_USE_TLS=true
EMAIL_HOST_USER=your-smtp-username
EMAIL_HOST_PASSWORD=your-smtp-password
DEFAULT_FROM_EMAIL=no-reply@yourdomain.com
```

Common SMTP hosts:

| Provider | Host | Port |
|----------|------|------|
| Gmail Workspace | `smtp.gmail.com` | 587 |
| Amazon SES | `email-smtp.<region>.amazonaws.com` | 587 |
| Postmark | `smtp.postmarkapp.com` | 587 |
| Mailgun | `smtp.mailgun.org` | 587 |
| Brevo (Sendinblue) | `smtp-relay.brevo.com` | 587 |

---

## DNS records (all providers)

Regardless of which provider you pick, configure these DNS records on every sending domain.
They are required for good deliverability and to avoid landing in spam.

### SPF
Add a `TXT` record on your domain:
```
v=spf1 include:<provider-spf-domain> ~all
```
The provider dashboard will give you the exact `include:` value.

### DKIM
Add the `TXT` record the provider generates during domain authentication.
Resend and SendGrid both show a copy-pasteable record in their dashboards.

### DMARC
Add a `TXT` record on `_dmarc.yourdomain.com`. Start permissive and tighten over time:
```
v=DMARC1; p=none; rua=mailto:dmarc-reports@yourdomain.com
```
Once you've verified no legitimate mail is failing, move to `p=quarantine` then `p=reject`.

---

## Local development

In development, email is written to the console by default:

```env
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

This is already set in `settings/development.py`. No SMTP credentials needed locally.

To test the actual provider end-to-end during dev, temporarily set:

```env
EMAIL_BACKEND=anymail.backends.resend.EmailBackend
RESEND_API_KEY=re_xxxxxxxxxxxx
DEFAULT_FROM_EMAIL=no-reply@yourdomain.com
```

---

## Verifying it works

After deploying with your chosen provider, trigger a real email send:

```bash
# From inside the running container
docker compose exec web python manage.py shell -c "
from django.core.mail import send_mail
send_mail('Test', 'If you see this, email is working.', None, ['you@example.com'])
"
```

Check the provider dashboard for delivery confirmation. If it fails, check:

1. `DEFAULT_EMAIL_PROVIDER` matches the API key you've set.
2. `DEFAULT_FROM_EMAIL` is a verified sender address in the provider dashboard.
3. `django-anymail` is installed (`pip show django-anymail`).
4. The API key has Send permission (not just read).

---

## Summary recommendation

Start with **Resend**. It takes under 10 minutes to set up, the free tier covers early-stage
volume, and switching to SendGrid or SMTP later is a two-variable change.
