# Resend Setup Guide

Step-by-step instructions to activate Resend as the email provider for this platform.
Everything is already wired in the backend — this is purely account and DNS configuration.

---

## 1. Create a Resend account

Go to [resend.com](https://resend.com) and sign up. Free tier covers 3 000 emails/month
and 100/day, which is sufficient for early-stage traffic.

---

## 2. Add and verify your sending domain

You need a domain you control (e.g. `gradecrest.com`). Do this once per sending domain.

1. In the Resend dashboard: **Domains → Add Domain**
2. Enter your domain name and click **Add**
3. Resend will show you three DNS records to add:

| Type | Name | Value |
|------|------|-------|
| `TXT` | `resend._domainkey.yourdomain.com` | (DKIM key — copy from dashboard) |
| `MX` | `send.yourdomain.com` | `feedback-smtp.us-east-1.amazonses.com` |
| `TXT` | `send.yourdomain.com` | `v=spf1 include:amazonses.com ~all` |

Add all three in your DNS provider (Cloudflare, Namecheap, Route 53, etc.).
Propagation typically takes 5–30 minutes. Click **Verify** in the dashboard once they're live.

> **Tip — Cloudflare users:** Set the DKIM and SPF records to **DNS Only** (grey cloud),
> not Proxied. MX records cannot be proxied.

### DMARC (recommended)

Add a fourth record to protect your domain from spoofing:

| Type | Name | Value |
|------|------|-------|
| `TXT` | `_dmarc.yourdomain.com` | `v=DMARC1; p=none; rua=mailto:dmarc@yourdomain.com` |

Start with `p=none` (monitor mode). Once you've confirmed all legitimate mail passes, move
to `p=quarantine` then `p=reject` over the following weeks.

---

## 3. Create an API key

1. Resend dashboard → **API Keys → Create API Key**
2. Name it (e.g. `writing-platform-production`)
3. Permission: **Sending access**
4. Copy the key — it starts with `re_` and is shown only once

---

## 4. Set environment variables

Add these to your production `.env` file (or server environment):

```env
DEFAULT_EMAIL_PROVIDER=resend
RESEND_API_KEY=re_xxxxxxxxxxxxxxxxxxxx
DEFAULT_FROM_EMAIL=no-reply@yourdomain.com
```

`DEFAULT_FROM_EMAIL` must match a verified sending domain in your Resend account.

That's all that's needed to send email. The webhook secret (step 5) is optional but
strongly recommended for production.

---

## 5. Configure webhooks (recommended)

The platform has a webhook endpoint that receives bounce and complaint events from Resend
and automatically suppresses those email addresses so you stop sending to them. This
protects your sender reputation.

### Register the endpoint in Resend

1. Resend dashboard → **Webhooks → Add Endpoint**
2. URL: `https://yourdomain.com/api/v1/notifications/webhooks/resend/`
3. Events to subscribe — check these two:
   - `email.bounced`
   - `email.complained`
4. Click **Create** — Resend will show you the **Signing Secret** (`whsec_...`)
5. Copy it

### Add the signing secret to your environment

```env
RESEND_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxxxxxxxxx
```

The backend verifies every incoming webhook using this secret (Svix HMAC-SHA256 signature
on `svix-id + svix-timestamp + body`). Requests with invalid signatures return `403` and
are logged.

---

## 6. Deploy and verify

Restart the backend so the new env vars are picked up:

```bash
docker compose restart web celery
```

Send a test email from the Django shell:

```bash
docker compose exec web python manage.py shell -c "
from django.core.mail import send_mail
send_mail(
    subject='Resend test',
    message='If you see this, Resend is working.',
    from_email=None,          # uses DEFAULT_FROM_EMAIL
    recipient_list=['you@example.com'],
)
"
```

Check the Resend dashboard → **Emails** — the message should appear with status `Delivered`.

If it fails:

| Symptom | Likely cause |
|---------|-------------|
| `Authentication failed` | `RESEND_API_KEY` is wrong or has no send permission |
| `The sender address is not verified` | `DEFAULT_FROM_EMAIL` domain not verified in Resend |
| Email not in Resend dashboard at all | `DEFAULT_EMAIL_PROVIDER` not set to `resend`, or `RESEND_API_KEY` is empty — check Django is loading the correct settings file |
| Webhooks returning `403` | `RESEND_WEBHOOK_SECRET` is missing or wrong |

---

## 7. Multi-tenant note

Each brand (gradecrest.com, essaymaniacs.com, etc.) should ideally send from its own
verified domain (e.g. `no-reply@gradecrest.com`). Verify each domain in Resend following
step 2, then set `DEFAULT_FROM_EMAIL` (or a per-website `from_email` override in
`WebsiteBranding`) to the matching address.

If you want a single shared sender for all brands during early rollout, one verified
domain is fine — you can add the per-brand domains later without any code changes.
