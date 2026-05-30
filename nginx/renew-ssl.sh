#!/bin/sh
# =============================================================================
# SSL Certificate Renewal Script
# Run via cron twice daily — certbot only renews if expiry is within 30 days.
#
# Add to crontab on the production server:
#   0 0,12 * * * /opt/writing-system/nginx/renew-ssl.sh >> /var/log/certbot-renew.log 2>&1
#
# Initial certificate issuance (run once after first deploy):
#   docker compose -f docker-compose.yml -f docker-compose.prod.yml run --rm certbot \
#     certonly --webroot -w /var/www/certbot \
#     -d yourdomain.com -d www.yourdomain.com \
#     --email admin@yourdomain.com --agree-tos --non-interactive
# =============================================================================

set -e

COMPOSE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
COMPOSE_CMD="docker compose -f docker-compose.yml -f docker-compose.prod.yml"

echo "[$(date)] Starting SSL renewal check..."

cd "$COMPOSE_DIR"

# Attempt renewal (no-op if certs are fresh)
$COMPOSE_CMD run --rm certbot renew --webroot -w /var/www/certbot

# Reload nginx to pick up any new certs without dropping connections
$COMPOSE_CMD exec nginx nginx -s reload

echo "[$(date)] SSL renewal check complete."
