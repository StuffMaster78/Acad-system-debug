# Uptime Kuma — Monitor Setup

Uptime Kuma is the self-hosted uptime dashboard. It runs as a Docker container alongside the application stack and provides:

- Real-time status page for all services
- SMS/email/Slack/Telegram/webhook alerts
- TLS certificate expiry tracking
- Response-time graphs with 90-day history

---

## 1. Run Uptime Kuma

Add to your `docker-compose.yml` (or a separate `monitoring/docker-compose.yml`):

```yaml
services:
  uptime-kuma:
    image: louislam/uptime-kuma:1
    container_name: uptime-kuma
    restart: unless-stopped
    ports:
      - "3001:3001"
    volumes:
      - uptime_kuma_data:/app/data
    networks:
      - monitoring

networks:
  monitoring:
    external: true   # shared with the app stack

volumes:
  uptime_kuma_data:
```

Start it:

```bash
docker compose -f monitoring/docker-compose.yml up -d
```

Access at `http://your-server:3001` and create an admin account on first visit.

> **Tip:** Reverse-proxy Kuma behind nginx so it's reachable at `https://status.yourdomain.com` — use the same Let's Encrypt cert process in `DEPLOYMENT_GUIDE.md`.

---

## 2. Required Monitors

Set up the following monitors immediately after install. Use **Type: HTTP(s)** unless noted.

### Core application

| Monitor name | URL | Method | Interval | Expected status |
|---|---|---|---|---|
| **API — Live** | `https://<DOMAIN>/health/live/` | GET | 60s | 200 |
| **API — Ready** | `https://<DOMAIN>/health/ready/` | GET | 60s | 200 |
| **Frontend** | `https://<DOMAIN>/` | GET | 120s | 200 |
| **Wagtail CMS admin** | `https://<DOMAIN>/cms-admin/` | GET | 300s | 200 or 302 |

### Background workers

| Monitor name | Type | URL | Notes |
|---|---|---|---|
| **Celery Beat** | HTTP(s) | `https://<DOMAIN>/health/ready/` | Alerts if Beat has not registered tasks in Redis — this health endpoint reflects queue health |
| **Redis** | TCP Port | `<HOST>:6379` | Type: TCP Port; no HTTP required |

> For a richer Celery health check, expose `GET /health/celery/` from `health_checks/views.py` and point Kuma at it. The endpoint runs `celery inspect ping` and returns 200 only if at least one worker responds.

### Database

| Monitor name | Type | Notes |
|---|---|---|
| **PostgreSQL** | HTTP(s) | Point at `/health/ready/` — Django's health check includes a DB ping. Alternatively create a dedicated TCP Port monitor on port 5432. |

### TLS certificates

| Monitor name | Type | Domain |
|---|---|---|
| **TLS — Main domain** | SSL Certificate | `<DOMAIN>` |
| **TLS — Status page** | SSL Certificate | `status.<DOMAIN>` (if using a status subdomain) |

Kuma will alert when certificates are fewer than 14 days from expiry.

---

## 3. Notification channels

Set up at least one notification channel under **Settings → Notifications** before monitors go live.

### Recommended: Slack

1. Create an Incoming Webhook in your Slack workspace (App → Incoming Webhooks → Add to Slack)
2. In Kuma: **Settings → Notifications → Add → Slack**
3. Paste the webhook URL
4. Test → Save
5. Assign to all monitors

### Recommended: Email (SMTP)

1. **Settings → Notifications → Add → SMTP**
2. Fill in your SMTP server details (same as `EMAIL_*` settings in Django)
3. Send test → Save
4. Assign to all monitors

### Optional: Telegram / PagerDuty / Webhook

Kuma supports 90+ notification providers. For PagerDuty, use **Type: PagerDuty** and paste your Integration Key.

---

## 4. Status page (public-facing)

Create a public status page under **Status Pages → New Status Page**:

- **Slug:** `status` → accessible at `http://kuma-host:3001/status/status`
- **Title:** `[Platform Name] System Status`
- Add all monitors from section 2 to the page
- Enable **Custom Domain** if you reverse-proxy to `status.yourdomain.com`

---

## 5. Maintenance windows

When deploying, create a maintenance window to suppress false alerts:

1. **Maintenance → Schedule Maintenance**
2. Set start/end time to cover the deploy window (allow +15 min buffer)
3. Select all monitors
4. Save

Or use the Kuma API (see `/api/v1/maintenance` in the Kuma docs).

---

## 6. Alert thresholds (recommended settings)

For each monitor set:

| Setting | Value |
|---|---|
| **Max retries before alert** | 3 |
| **Retry interval** | 20s |
| **Heartbeat interval** | 60s (API), 120s (frontend) |
| **Response timeout** | 10s |

This prevents alert storms from transient network hiccups during deploys.

---

## 7. API automation (optional)

Kuma exposes a REST API. To seed monitors programmatically after a fresh install:

```bash
# Authenticate
TOKEN=$(curl -s -X POST http://localhost:3001/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"YOUR_PASSWORD"}' | jq -r .token)

# Create a monitor
curl -s -X POST http://localhost:3001/api/monitors \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "http",
    "name": "API — Live",
    "url": "https://YOUR_DOMAIN/health/live/",
    "interval": 60,
    "maxretries": 3
  }'
```

Repeat the POST for each monitor in section 2.

---

## 8. Relationship to GitHub Actions uptime check

The `.github/workflows/uptime-check.yml` workflow is a **secondary, independent probe** — it runs from GitHub's infrastructure every 5 minutes and can detect outages even if the Kuma container itself is down or unreachable from within the server network.

| | Uptime Kuma | GitHub Actions probe |
|---|---|---|
| Check interval | 60s | 5 min |
| Hosted on | Your server | GitHub infrastructure |
| Alerts via | Slack/Email/SMS | Slack webhook |
| Historical graphs | Yes | No |
| TLS tracking | Yes | No |
| Works if server is down | No | Yes |

Run **both** in production for maximum coverage.
