# Docker Rebuild Instructions for ARM64

## Quick Fix Commands

Run these commands to rebuild your containers with native ARM64 architecture:

```bash
# Stop all running containers
docker-compose down

# Remove old AMD64 images (optional but recommended)
docker-compose rm -f

# Rebuild containers from scratch (this will use native ARM64)
docker-compose build --no-cache

# Start containers
docker-compose up -d

# Verify architecture
docker-compose exec web uname -m
# Should output: aarch64 (ARM64) instead of x86_64
```

## What Changed

✅ **Removed `platform: linux/amd64`** from:
- `web` service
- `celery` service  
- `beat` service

✅ **Database and Redis** already use multi-platform images (no change needed)

## Expected Performance Improvements

**Before (with emulation):**
- Container startup: 30-60 seconds
- High CPU usage (50-100%)
- Slower response times (2-5x slower)
- Potential failures under load

**After (native ARM64):**
- Container startup: 10-20 seconds
- Lower CPU usage (10-30%)
- Native speed performance
- More stable operation

## Troubleshooting

### If containers still show x86_64:

1. **Clear Docker build cache:**
   ```bash
   docker builder prune -a
   ```

2. **Remove old images:**
   ```bash
   docker image prune -a
   ```

3. **Rebuild with pull:**
   ```bash
   docker-compose build --no-cache --pull
   ```

### Verify Architecture:

```bash
# Check web container
docker-compose exec web uname -m

# Check celery container
docker-compose exec celery uname -m

# Check beat container
docker-compose exec beat uname -m

# All should output: aarch64
```

### Check Performance:

```bash
# Monitor resource usage
docker stats

# You should see:
# - Lower CPU usage
# - Lower memory usage
# - Faster response times
```

## Notes

- All base images (Python 3.11, PostgreSQL 15, Redis, Node 18) support ARM64 natively
- No code changes required
- Works on both Apple Silicon and Intel Macs
- Production servers can still use AMD64 if needed (just specify platform there)

