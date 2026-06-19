# DigitalOcean Production Runbook

This runbook deploys the platform as immutable Docker images behind nginx and
Cloudflare. PostgreSQL and Redis remain private; only ports 80 and 443 are
published.

## 1. Provision external services

Create:

- Ubuntu 24.04 DigitalOcean Droplet (recommended starting size: 4 vCPU / 8 GB)
- DigitalOcean Reserved IP
- DigitalOcean Cloud Firewall
- Public/media, private-files, and backup Spaces buckets
- Cloudflare DNS zone for each brand
- Resend transactional email account
- Managed mailbox provider for support replies

Firewall rules:

- SSH/22: trusted administrator IPs only
- HTTP/80: public during certificate bootstrap, then Cloudflare ranges only
- HTTPS/443: public during verification, then Cloudflare ranges only
- Never expose 5432, 6379, 8000, 8080, 3000, or 3001

## 2. Create the deployment user

```bash
adduser deploy
usermod -aG sudo deploy
rsync -a --chown=deploy:deploy ~/.ssh /home/deploy
```

Install Docker Engine and the Compose plugin using Docker's official Ubuntu
instructions. Then:

```bash
usermod -aG docker deploy
mkdir -p /opt/writing-system
chown deploy:deploy /opt/writing-system
```

Reconnect as `deploy` before continuing.

## 3. Prepare the checkout and environment

```bash
git clone <repository-url> /opt/writing-system
cd /opt/writing-system
cp .env.production.example .env
chmod 600 .env
```

Replace every placeholder. Generate independent values for Django, PostgreSQL,
Redis, field encryption, token encryption, and backup encryption.

The application Spaces key may access application media buckets. The backup key
must be a separate restricted key that can access only the backup bucket.

Database dumps are compressed and AES-256 encrypted before upload. Store
`BACKUP_ENCRYPTION_KEY` in your password manager as well as the production
environment; losing it makes the backups unrecoverable.

## 4. Configure DNS

Point these names to the Reserved IP:

```text
writerscreek.com
www.writerscreek.com
app.writerscreek.com
admin.writerscreek.com

gradecrest.com
www.gradecrest.com
app.gradecrest.com

nursemygrade.com
www.nursemygrade.com
app.nursemygrade.com

essaymaniacs.com
www.essaymaniacs.com
app.essaymaniacs.com

researchpapermate.com
www.researchpapermate.com
app.researchpapermate.com
```

Keep records in Cloudflare's DNS-only mode until certificates and direct-origin
checks pass.

## 5. Bootstrap TLS

The normal nginx configuration cannot start before certificates exist. Start
the HTTP-only overlay:

```bash
docker compose \
  --env-file .env \
  -f docker-compose.yml \
  -f docker-compose.prod.yml \
  -f docker-compose.bootstrap.yml \
  up -d nginx
```

Issue certificates:

```bash
COMPOSE="docker compose --env-file .env -f docker-compose.yml -f docker-compose.prod.yml --profile tools"

$COMPOSE run --rm certbot certonly --webroot -w /var/www/certbot \
  --cert-name writerscreek.com \
  -d writerscreek.com -d www.writerscreek.com \
  --email admin@writerscreek.com --agree-tos --non-interactive

$COMPOSE run --rm certbot certonly --webroot -w /var/www/certbot \
  -d app.writerscreek.com \
  --email admin@writerscreek.com --agree-tos --non-interactive

$COMPOSE run --rm certbot certonly --webroot -w /var/www/certbot \
  -d admin.writerscreek.com \
  --email admin@writerscreek.com --agree-tos --non-interactive

$COMPOSE run --rm certbot certonly --webroot -w /var/www/certbot \
  --cert-name client-portals \
  -d app.gradecrest.com \
  -d app.nursemygrade.com \
  -d app.essaymaniacs.com \
  -d app.researchpapermate.com \
  --email admin@writerscreek.com --agree-tos --non-interactive
```

Repeat for each client marketing domain, including its `www` name. The
certificate name defaults to the first `-d` value, matching `nginx/nginx.conf`.

Start the HTTPS configuration:

```bash
docker compose \
  --env-file .env \
  -f docker-compose.yml \
  -f docker-compose.prod.yml \
  up -d --remove-orphans
```

Validate:

```bash
docker compose --env-file .env \
  -f docker-compose.yml -f docker-compose.prod.yml ps

curl --fail https://writerscreek.com/health/ready/
curl --fail https://admin.writerscreek.com/api/v1/portal-context/
curl --fail https://app.writerscreek.com/api/v1/portal-context/
curl --fail https://app.gradecrest.com/api/v1/portal-context/
```

## 6. Enable Cloudflare

After direct-origin HTTPS works:

- Switch web records to proxied/orange-cloud
- Set SSL/TLS mode to Full (strict)
- Enable Always Use HTTPS, Brotli, and HTTP/3
- Enable managed WAF rules and Bot Fight Mode
- Add rate limits for login, registration, password reset, magic link, contact,
  quote, and writer-application endpoints
- Exclude Stripe and verified provider webhooks from interactive challenges

nginx restores the visitor address from `CF-Connecting-IP` using the published
Cloudflare ranges in `nginx/includes/cloudflare-real-ip.conf`.

## 7. Configure Resend

Verify one notification subdomain per brand and set:

```text
DEFAULT_EMAIL_PROVIDER=resend
RESEND_API_KEY=...
RESEND_WEBHOOK_SECRET=...
```

Configure the delivery webhook:

```text
https://writerscreek.com/api/v1/notifications/webhooks/resend/
```

Subscribe to delivered, bounced, and complained events. Hard bounces and
complaints feed the platform suppression list.

## 8. Configure GitHub

Create a protected GitHub environment named `production`.

Secrets:

```text
PROD_SSH_HOST
PROD_SSH_USER
PROD_SSH_KEY
PROD_DEPLOY_PATH
PROD_ENV_FILE
GHCR_DEPLOY_TOKEN
```

Variables:

```text
PROD_DOMAIN=writerscreek.com
```

`GHCR_DEPLOY_TOKEN` needs read access to packages. `PROD_ENV_FILE` contains the
production environment but not image names; CI appends immutable image tags.

## 9. Release

```bash
git tag -a v1.0.0 -m "Initial production release"
git push origin v1.0.0
```

The production workflow:

1. Tests Django and all six frontends.
2. Builds seven Docker images.
3. Pushes immutable SHA-tagged images to GHCR.
4. Uploads `.env.next`.
5. Creates a pre-deploy database backup when the backup service is available.
6. Pulls images, migrates, starts services, and waits for health checks.
7. Restores the previous environment and images if deployment fails.

## 10. Renew certificates

Run from a root-owned cron entry or systemd timer:

```bash
cd /opt/writing-system &&
docker compose --env-file .env \
  -f docker-compose.yml \
  -f docker-compose.prod.yml \
  --profile tools run --rm certbot renew &&
docker compose --env-file .env \
  -f docker-compose.yml \
  -f docker-compose.prod.yml exec nginx nginx -s reload
```

Test renewal before relying on automation:

```bash
docker compose --env-file .env \
  -f docker-compose.yml \
  -f docker-compose.prod.yml \
  --profile tools run --rm certbot renew --dry-run
```

## 11. Test database recovery

Regularly download a backup into an isolated environment and verify it:

```bash
openssl enc -d -aes-256-cbc -pbkdf2 \
  -pass env:BACKUP_ENCRYPTION_KEY \
  -in writing_system_db_YYYYMMDD_HHMMSS.sql.gz.enc \
  | gzip -dc \
  | psql "$RESTORE_DATABASE_URL"
```

Never test restoration against the live production database.

## 12. Turnstile rollout

Backend verification is available for the highest-risk anonymous endpoints.
Keep `TURNSTILE_ENABLED=False` until the corresponding frontend widgets have
been configured with production site keys. Cloudflare managed challenges and
rate limits can be enabled independently at the edge.
