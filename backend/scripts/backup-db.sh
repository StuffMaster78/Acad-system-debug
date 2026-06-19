#!/bin/sh
# =============================================================================
# Database Backup Script
#
# Dumps the PostgreSQL database, compresses and encrypts it, then uploads it to
# S3/DO Spaces.
# Keeps the last N local backups and enforces retention in S3.
#
# Environment variables (required):
#   POSTGRES_HOST         DB hostname (default: db)
#   POSTGRES_USER_NAME    DB user
#   POSTGRES_PASSWORD     DB password
#   POSTGRES_DB_NAME      DB name
#   BACKUP_ENCRYPTION_KEY Strong passphrase used for AES-256 encryption
#   AWS_ACCESS_KEY_ID     S3 / DO Spaces key
#   AWS_SECRET_ACCESS_KEY S3 / DO Spaces secret
#   AWS_STORAGE_BUCKET_NAME  Bucket name
#   AWS_S3_ENDPOINT_URL   Endpoint (leave unset for AWS; set for DO Spaces)
#   BACKUP_S3_PREFIX      Path prefix inside the bucket (default: backups/db)
#
# Optional:
#   BACKUP_LOCAL_DIR      Local directory for backups (default: /backups)
#   BACKUP_LOCAL_KEEP     Number of local backups to keep (default: 7)
#   BACKUP_S3_KEEP_DAYS   Retention in days for S3 backups (default: 30)
#
# Add to crontab on the production server (runs at 03:00 daily):
#   0 3 * * * /opt/writing-system/backend/scripts/backup-db.sh >> /var/log/db-backup.log 2>&1
#
# Or run via Docker:
#   docker compose -f docker-compose.yml -f docker-compose.prod.yml exec web \
#     /app/scripts/backup-db.sh
# =============================================================================

set -eu
set -o pipefail

# ── Configuration ─────────────────────────────────────────────────
BACKUP_LOCAL_DIR="${BACKUP_LOCAL_DIR:-/backups}"
BACKUP_LOCAL_KEEP="${BACKUP_LOCAL_KEEP:-7}"
BACKUP_S3_PREFIX="${BACKUP_S3_PREFIX:-backups/db}"
BACKUP_S3_KEEP_DAYS="${BACKUP_S3_KEEP_DAYS:-30}"

DB_HOST="${POSTGRES_HOST:-${DB_HOST:-db}}"
DB_PORT="${DB_PORT:-5432}"
DB_USER="${POSTGRES_USER_NAME}"
DB_NAME="${POSTGRES_DB_NAME}"

TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
FILENAME="${DB_NAME}_${TIMESTAMP}.sql.gz.enc"
LOCAL_PATH="${BACKUP_LOCAL_DIR}/${FILENAME}"

# ── Validate required vars ─────────────────────────────────────────
for var in POSTGRES_USER_NAME POSTGRES_PASSWORD POSTGRES_DB_NAME BACKUP_ENCRYPTION_KEY; do
    eval val=\$$var
    if [ -z "$val" ]; then
        echo "[ERROR] Required variable $var is not set." >&2
        exit 1
    fi
done

mkdir -p "$BACKUP_LOCAL_DIR"

echo "[$(date)] Starting backup of ${DB_NAME} on ${DB_HOST}:${DB_PORT}"

# ── Dump + compress + encrypt ──────────────────────────────────────
PGPASSWORD="$POSTGRES_PASSWORD" pg_dump \
    -h "$DB_HOST" \
    -p "$DB_PORT" \
    -U "$DB_USER" \
    -d "$DB_NAME" \
    --format=plain \
    --no-owner \
    --no-acl \
    | gzip -9 \
    | openssl enc -aes-256-cbc -salt -pbkdf2 \
        -pass env:BACKUP_ENCRYPTION_KEY \
        -out "$LOCAL_PATH"

BACKUP_SIZE="$(du -sh "$LOCAL_PATH" | cut -f1)"
echo "[$(date)] Backup created: $LOCAL_PATH ($BACKUP_SIZE)"

# ── Upload to S3 / DO Spaces ───────────────────────────────────────
if [ -n "$AWS_ACCESS_KEY_ID" ] && [ -n "$AWS_SECRET_ACCESS_KEY" ] && [ -n "$AWS_STORAGE_BUCKET_NAME" ]; then
    S3_DEST="s3://${AWS_STORAGE_BUCKET_NAME}/${BACKUP_S3_PREFIX}/${FILENAME}"

    # Build endpoint flag for DO Spaces / custom S3-compatible storage
    ENDPOINT_FLAG=""
    if [ -n "$AWS_S3_ENDPOINT_URL" ]; then
        ENDPOINT_FLAG="--endpoint-url $AWS_S3_ENDPOINT_URL"
    fi

    echo "[$(date)] Uploading to ${S3_DEST} ..."
    AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
    AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
    AWS_DEFAULT_REGION="${AWS_S3_REGION_NAME:-us-east-1}" \
    aws s3 cp "$LOCAL_PATH" "$S3_DEST" $ENDPOINT_FLAG --only-show-errors

    echo "[$(date)] Upload complete."

    # ── S3 retention: delete backups older than BACKUP_S3_KEEP_DAYS ──
    CUTOFF_DATE="$(date -d "${BACKUP_S3_KEEP_DAYS} days ago" +%Y-%m-%dT%H:%M:%S 2>/dev/null \
        || date -v-${BACKUP_S3_KEEP_DAYS}d +%Y-%m-%dT%H:%M:%S 2>/dev/null \
        || echo "")"

    if [ -n "$CUTOFF_DATE" ]; then
        echo "[$(date)] Pruning S3 backups older than ${BACKUP_S3_KEEP_DAYS} days..."
        AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
        AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
        AWS_DEFAULT_REGION="${AWS_S3_REGION_NAME:-us-east-1}" \
        aws s3 ls "s3://${AWS_STORAGE_BUCKET_NAME}/${BACKUP_S3_PREFIX}/" \
            $ENDPOINT_FLAG \
            | awk '{print $4}' \
            | while read -r KEY; do
                FILE_DATE="${KEY#${DB_NAME}_}"
                FILE_DATE="${FILE_DATE%%_*}"  # extract YYYYMMDD prefix
                # Compare dates in YYYYMMDD format
                if [ -n "$FILE_DATE" ] && [ "$FILE_DATE" \< "$(echo "$CUTOFF_DATE" | cut -c1-10 | tr -d '-')" ]; then
                    echo "[$(date)] Deleting old backup: $KEY"
                    AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
                    AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
                    aws s3 rm "s3://${AWS_STORAGE_BUCKET_NAME}/${BACKUP_S3_PREFIX}/${KEY}" \
                        $ENDPOINT_FLAG --only-show-errors
                fi
              done
    fi
else
    echo "[$(date)] S3 credentials not set — skipping remote upload. Local backup only."
fi

# ── Local retention: keep last N backups ───────────────────────────
echo "[$(date)] Pruning local backups (keeping last ${BACKUP_LOCAL_KEEP})..."
ls -1t "${BACKUP_LOCAL_DIR}/${DB_NAME}_"*.sql.gz.enc 2>/dev/null \
    | tail -n "+$((BACKUP_LOCAL_KEEP + 1))" \
    | xargs -r rm -f

REMAINING="$(ls -1 "${BACKUP_LOCAL_DIR}/${DB_NAME}_"*.sql.gz.enc 2>/dev/null | wc -l | tr -d ' ')"
echo "[$(date)] Local backups remaining: ${REMAINING}"

echo "[$(date)] Backup complete: $FILENAME ($BACKUP_SIZE)"
