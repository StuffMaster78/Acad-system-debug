"""
Test settings for writing_system project.

Overrides production/development settings to run tests locally without
external services (PostgreSQL, Redis, Celery broker, SMTP, etc.).
"""

from .settings import *  # noqa
import os

# Ensure DEBUG true for tests
DEBUG = True

# Provide a default token encryption key for tests
TOKEN_ENCRYPTION_KEY = TOKEN_ENCRYPTION_KEY or "test-token-encryption-key"

# Database selection for tests: sqlite (default) or postgres when TEST_DB=postgres
# Check for DATABASE_URL first (for CI/CD)
database_url = os.getenv('DATABASE_URL')
if database_url:
    # Parse DATABASE_URL (format: postgresql://user:password@host:port/dbname)
    from urllib.parse import urlparse
    parsed = urlparse(database_url)
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": parsed.path[1:] if parsed.path.startswith('/') else parsed.path,  # Remove leading /
            "USER": parsed.username,
            "PASSWORD": parsed.password,
            "HOST": parsed.hostname,
            "PORT": parsed.port or 5432,
        }
    }
elif os.getenv("TEST_DB", "sqlite").lower() == "postgres":
    # Use credentials from .env file (already loaded by settings.py via load_dotenv)
    # Use same fallbacks as main settings.py
    _db_name = os.getenv("POSTGRES_DB_NAME") or "writingsondo"
    _db_user = os.getenv("POSTGRES_USER_NAME") or "awinorick"
    _db_password = os.getenv("POSTGRES_PASSWORD") or "Nyakach2030"
    _db_host = os.getenv("DB_HOST", "db")
    _db_port = int(os.getenv("DB_PORT", 5432))
    
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": _db_name,
            "USER": _db_user,
            "PASSWORD": _db_password,
            "HOST": _db_host,
            "PORT": _db_port,
            # Configure test database to be separate from production
            "TEST": {
                "NAME": f"test_{_db_name}",
                "CREATE_DB": True,
            }
        }
    }
    # Ensure notifications_system migrations are enabled for PostgreSQL
    if 'MIGRATION_MODULES' in globals():
        MIGRATION_MODULES.pop('notifications_system', None)
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",  # Use in-memory database for faster tests
        }
    }
    # For SQLite, temporarily exclude notifications_system from migrations
    # to avoid PostgreSQL-specific ArrayField issues
    MIGRATION_MODULES = {
        'notifications_system': None,  # Skip migrations for this app with SQLite
    }

# For PostgreSQL tests, ensure pricing app has migrations or skip syncing
if os.getenv("TEST_DB", "sqlite").lower() == "postgres" or database_url:
    # Skip syncing unmigrated apps that might cause dependency issues
    # This ensures migrations run first
    if 'MIGRATION_MODULES' not in globals():
        MIGRATION_MODULES = {}
    # Create migrations for pricing app or skip it during sync
    # MIGRATION_MODULES['pricing'] = None  # Uncomment if pricing causes issues
    
    # Fix corrupted content types after migrations using post_migrate signal
    from django.db.models.signals import post_migrate
    from django.db import connection
    
    def fix_content_types_after_migration(sender, **kwargs):
        """Fix corrupted content types immediately after migrations."""
        try:
            with connection.cursor() as cursor:
                # Delete corrupted content types
                cursor.execute("""
                    DELETE FROM django_content_type 
                    WHERE name IS NULL 
                    OR name = ''
                    OR (app_label = 'migrations' AND model = 'migration')
                """)
        except Exception:
            pass
    
    # Connect to post_migrate signal to clean up after each app migration
    post_migrate.connect(fix_content_types_after_migration, weak=False)

# Use in-memory cache to avoid Redis during tests
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "test-locmem",
    }
}

# Avoid Celery/Redis dependencies
CELERY_BROKER_URL = "memory://"
CELERY_RESULT_BACKEND = "cache+memory://"

# Remove optional apps not needed for tests if unavailable
for _app in [
    "drf_spectacular_sidecar",
    "django_ratelimit",
]:
    if _app in INSTALLED_APPS:
        INSTALLED_APPS.remove(_app)

# Keep notifications_system loaded because some project apps import its models
if "notifications_system" not in INSTALLED_APPS:
    INSTALLED_APPS.append("notifications_system")

# Faster password hashing during tests
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Use console email backend in tests
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Reduce throttle limits for speed (optional, but keeps structure coherent)
REST_FRAMEWORK = {
    **REST_FRAMEWORK,
    # Disable throttling in tests to avoid 429s
    "DEFAULT_THROTTLE_CLASSES": [],
    "DEFAULT_THROTTLE_RATES": {
        # ensure any custom scopes from notifications won't error
        "notifications_write_burst": "1000/min",
        "notifications_read_burst": "1000/min",
        "notifications_write_sustained": "10000/day",
        "notifications_read_sustained": "10000/day",
        "user": "1000/min",
        "anon": "1000/min",
    },
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ),
}

# Silence system checks that require external services during tests
SILENCED_SYSTEM_CHECKS = [
    "notifications_system.E011",  # Redis unreachable
    "django_ratelimit.E003",      # non-shared cache
    "admin.E035",
    "fields.E304",
    "fields.E305",
    "fields.E300",
    "fields.E307",
    # Project-specific noisy checks during tests
    "urls.W005",                  # duplicate URL namespaces (acceptable in tests)
    "notifications_system.W001",  # missing class-based templates
    "notifications_system.W026",  # missing event config file
]

# Disable noisy audit signals during tests
DISABLE_AUDIT_LOG_SIGNALS = True
DISABLE_NOTIFICATION_SIGNALS = True
DISABLE_SUPPORT_SIGNALS = True
DISABLE_REFERRAL_SIGNALS = True

# Test database configuration is set above in the DATABASES dict
# No need to set it again here

# Disable price recalculation during tests to avoid dependency on pricing services
DISABLE_PRICE_RECALC_DURING_TESTS = True


# Test-only flags
DISABLE_AUTO_CREATE_WRITER_PROFILE = True

# Allow Django test client host
ALLOWED_HOSTS = list(set((ALLOWED_HOSTS or []) + ["testserver", "localhost", "127.0.0.1"]))
