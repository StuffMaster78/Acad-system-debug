"""
Shared settings inherited by development.py, production.py, and test.py.

Keep secrets in environment variables or environment-specific settings. This
module owns shared application wiring, middleware, API defaults, cache, Celery,
authentication, static/media defaults, and backend-wide feature settings.
"""

from __future__ import annotations

import base64
import importlib.util
from datetime import timedelta
from urllib.parse import quote_plus

from .env import BASE_DIR, env, env_bool, env_int, env_list


DJANGO_ENV = env("DJANGO_ENV", "development")
DEBUG = False

SECRET_KEY = env(
    "SECRET_KEY",
    "dev-insecure-secret-key-change-me",
)
DEFAULT_FIELD_ENCRYPTION_KEY = base64.urlsafe_b64encode(
    b"writing-system-dev-fernet-key!!!",
).decode()
FIELD_ENCRYPTION_KEY = env(
    "FIELD_ENCRYPTION_KEY",
    DEFAULT_FIELD_ENCRYPTION_KEY,
)
TOKEN_ENCRYPTION_KEY = env(
    "TOKEN_ENCRYPTION_KEY",
    "dev-token-encryption-key",
)

# ── Encryption key guards ─────────────────────────────────────────────────────
# Fail fast in non-development environments so a misconfigured deployment
# never silently runs with a public dev key or an invalid Fernet key.
if DJANGO_ENV != "development":
    from django.core.exceptions import ImproperlyConfigured  # noqa: PLC0415

    if FIELD_ENCRYPTION_KEY == DEFAULT_FIELD_ENCRYPTION_KEY:
        raise ImproperlyConfigured(
            "FIELD_ENCRYPTION_KEY is set to the public development default. "
            "Generate a proper Fernet key: python -c "
            "\"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
        )

    try:
        base64.urlsafe_b64decode(TOKEN_ENCRYPTION_KEY + "==")
    except Exception as _e:
        raise ImproperlyConfigured(
            "TOKEN_ENCRYPTION_KEY is not a valid URL-safe base64 string. "
            "Generate one: python -c "
            "\"import secrets, base64; print(base64.urlsafe_b64encode(secrets.token_bytes(32)).decode())\""
        ) from _e

ALLOWED_HOSTS = env_list(
    "ALLOWED_HOSTS",
    "localhost,127.0.0.1",
)
FRONTEND_URL = env("FRONTEND_URL", "http://localhost:5173")

ROOT_URLCONF = "writing_system.urls"
WSGI_APPLICATION = "writing_system.wsgi.application"
ASGI_APPLICATION = "writing_system.asgi.application"
AUTH_USER_MODEL = "users.User"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


def module_available(module_name: str) -> bool:
    """
    Return whether an optional package is importable in the current environment.
    """
    return importlib.util.find_spec(module_name) is not None


LEGACY_COMPAT_APPS: list[str] = []
ENABLE_LEGACY_WRITER_WALLET_SIGNALS = False

WAGTAIL_AVAILABLE = module_available("wagtail")
WHITENOISE_AVAILABLE = module_available("whitenoise")

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "django.contrib.sites",
    "django.contrib.postgres",
]

WAGTAIL_APPS = [
    "wagtail.contrib.forms",
    "wagtail.contrib.redirects",
    "wagtail.contrib.settings",
    "wagtail.contrib.table_block",
    "wagtail.embeds",
    "wagtail.sites",
    "wagtail.users",
    "wagtail.snippets",
    "wagtail.documents",
    "wagtail.images",
    "wagtail.search",
    "wagtail.admin",
    "wagtail",
    "modelcluster",
    "taggit",
] if WAGTAIL_AVAILABLE else []

OPTIONAL_THIRD_PARTY_APPS = [
    app
    for module_name, app in [
        ("storages", "storages"),
        ("anymail", "anymail"),
        ("actstream", "actstream"),
    ]
    if module_available(module_name)
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "drf_spectacular",
    "drf_spectacular_sidecar",
    "django_filters",
    "channels",
    "django_celery_beat",
    "django_otp",
    "django_otp.plugins.otp_totp",
    "django_otp.plugins.otp_static",
    "django_ratelimit",
    "django_countries",
    *OPTIONAL_THIRD_PARTY_APPS,
]

CMS_APPS = [
    "cms_core",
    "cms_authors",
    "cms_attachments",
    "cms_blog",
    "cms_service_pages",
    "cms_newsletters",
    "cms_references",
    "cms_engagement",
    "cms_content_graph",
    "cms_intelligence",
] if WAGTAIL_AVAILABLE else []

LOCAL_APPS = [
    "core",
    "config_system",
    "websites",
    "users",
    "accounts",
    "notifications_system.apps.NotificationsSystemConfig",
    "authentication",
    "audit_logging",
    "event_system",
    "activity",
    "communications",
    "files_management",
    *CMS_APPS,
    "orders",
    "order_configs",
    "order_pricing_core",
    "special_orders",
    "class_management",
    "billing",
    "wallets",
    *LEGACY_COMPAT_APPS,
    "ledger",
    "payments_processor",
    "discounts",
    "referrals",
    "refunds",
    "tips",
    "fines",
    "reputation_system",
    "privacy",
    "users_state",
    "seo_pages",
    "tickets",
    "feedback",
    "changelog",
    "qa_checklists",
    "saved_views",
    "mass_emails",
    "announcements",
    "analytics",
    "client_management",
    "writer_management",
    "editor_management",
    "support_management",
    "admin_management",
    "superadmin_management",
    "governance",
    "loyalty_management",
    "reviews_system",
    "holiday_management",
    "writer_compensation.apps.WriterCompensationConfig",
    "legal_pages",
    "writer_vetting",
]


INSTALLED_APPS = [
    *DJANGO_APPS,
    *WAGTAIL_APPS,
    *THIRD_PARTY_APPS,
    *LOCAL_APPS,
]


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "core.middleware.graceful_degradation.GracefulDegradationMiddleware",
    "core.middleware.portal_tenant_resolver.PortalTenantResolverMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    (
        "authentication.middleware.impersonation_middleware."
        "ImpersonationMiddleware"
    ),
    (
        "authentication.middleware.login_session_enforcement_middleware."
        "LoginSessionEnforcementMiddleware"
    ),
    (
        "authentication.middleware.session_activity_middleware."
        "SessionActivityMiddleware"
    ),
    (
        "authentication.middleware.login_session_activity_sync_middleware."
        "LoginSessionActivitySyncMiddleware"
    ),
    "audit_logging.middleware.AuditUserMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "superadmin_management.middleware.BlacklistMiddleware",
    "core.middleware.compression.EnhancedCompressionMiddleware",
    "activity.middleware.ActivityAuditMiddleware",
    "core.middleware.performance_monitoring.PerformanceMonitoringMiddleware",
]

if WHITENOISE_AVAILABLE:
    MIDDLEWARE.insert(
        MIDDLEWARE.index("corsheaders.middleware.CorsMiddleware"),
        "whitenoise.middleware.WhiteNoiseMiddleware",
    )

if WAGTAIL_AVAILABLE:
    MIDDLEWARE.insert(
        MIDDLEWARE.index("django.middleware.csrf.CsrfViewMiddleware"),
        "wagtail.contrib.redirects.middleware.RedirectMiddleware",
    )


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


LANGUAGE_CODE = "en-us"
TIME_ZONE = env("TIME_ZONE", "UTC")
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
STORAGE_BACKEND = env("STORAGE_BACKEND", "local")
USE_S3 = env_bool("USE_S3", STORAGE_BACKEND in {"s3", "do_spaces"})
WAGTAILADMIN_BASE_URL = env(
    "WAGTAILADMIN_BASE_URL",
    "http://localhost:8000",
)

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": (
            "whitenoise.storage.CompressedManifestStaticFilesStorage"
            if WHITENOISE_AVAILABLE
            else "django.contrib.staticfiles.storage.StaticFilesStorage"
        ),
    },
}

SITE_ID = env_int("SITE_ID", 1)
WAGTAIL_SITE_NAME = env("WAGTAIL_SITE_NAME", "Writing System Platform")
DATA_UPLOAD_MAX_NUMBER_FIELDS = env_int(
    "DATA_UPLOAD_MAX_NUMBER_FIELDS",
    10000,
)

ACTSTREAM_SETTINGS = {
    "MANAGER": "actstream.managers.ActionManager",
    "FETCH_RELATIONS": True,
    "USE_PREFETCH": True,
    "USE_JSONFIELD": True,
    "GFK_FETCH_DEPTH": 1,
}

MULTI_TENANT_ENABLED = env_bool("MULTI_TENANT_ENABLED", True)


AUTHENTICATION_BACKENDS = [
    "admin_management.auth.BlacklistAuthenticationBackend",
    "django.contrib.auth.backends.ModelBackend",
]

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "MinimumLengthValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "CommonPasswordValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "NumericPasswordValidator"
        ),
    },
]

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
    "django.contrib.auth.hashers.BCryptPasswordHasher",
]


REDIS_HOST = env("REDIS_HOST", "redis")
REDIS_PORT = env_int("REDIS_PORT", 6379)
REDIS_PASSWORD = env("REDIS_PASSWORD", "")


def redis_url(db: int) -> str:
    """
    Build a Redis URL for a database number.
    """
    if REDIS_PASSWORD:
        password = quote_plus(str(REDIS_PASSWORD))
        return f"redis://:{password}@{REDIS_HOST}:{REDIS_PORT}/{db}"

    return f"redis://{REDIS_HOST}:{REDIS_PORT}/{db}"


REDIS_URL = env("REDIS_URL", redis_url(0))
COMMUNICATIONS_REDIS_URL = env(
    "COMMUNICATIONS_REDIS_URL",
    redis_url(2),
)
COMMUNICATIONS_SSE_CHANNEL = env(
    "COMMUNICATIONS_SSE_CHANNEL",
    "communications:sse",
)

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": env("CACHE_URL", redis_url(1)),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "IGNORE_EXCEPTIONS": True,
        },
        "KEY_PREFIX": env("CACHE_KEY_PREFIX", "writing_system"),
        "TIMEOUT": env_int("CACHE_TIMEOUT", 300),
    },
}

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [env("CHANNEL_REDIS_URL", redis_url(3))],
        },
    },
}


CELERY_BROKER_URL = env("CELERY_BROKER_URL", REDIS_URL)
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND", REDIS_URL)
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = env("CELERY_TIMEZONE", "UTC")
CELERY_BEAT_SCHEDULER = (
    "django_celery_beat.schedulers:DatabaseScheduler"
)

# Explicitly import task sub-modules that live in packages (not flat tasks.py).
# Celery autodiscover only loads tasks/__init__.py; sub-modules must be listed
# here so every @shared_task decorated function gets registered at startup.
CELERY_IMPORTS = [
    "notifications_system.tasks.maintenance",
    "notifications_system.tasks.digest",
    "notifications_system.tasks.send",
    "payments_processor.tasks.payment_application_tasks",
    "payments_processor.tasks.payment_cleanup_tasks",
    "payments_processor.tasks.payment_reconciliation_tasks",
    "payments_processor.tasks.pending_payment_resolution_tasks",
    "payments_processor.tasks.refund_tasks",
    "orders.tasks.adjustment_tasks",
    "orders.tasks.order_adjustment_tasks",
    "orders.tasks.order_approval_tasks",
    "orders.tasks.order_archival_tasks",
    "orders.tasks.order_completion_tasks",
    "orders.tasks.order_dispute_tasks",
    "orders.tasks.order_hold_tasks",
    "orders.tasks.order_monitoring_tasks",
    "orders.tasks.order_reassignment_tasks",
    "orders.tasks.order_reminder_tasks",
    "orders.tasks.order_staffing_tasks",
    "orders.tasks.preferred_writer_tasks",
    "orders.tasks.unpaid_order_reminder_tasks",
    "files_management.tasks.quotas",
    "files_management.tasks.cleanup",
]

from celery.schedules import crontab # noqa: E402

CELERY_BEAT_SCHEDULE = {

    # ----------------------------------------------------------------
    # Files management
    # ----------------------------------------------------------------
    "files.recalculate_all_quotas": {
        "task": "files_management.tasks.quotas.recalculate_all_quotas",
        "schedule": crontab(hour=1, minute=0), # nightly 01:00
    },
    "files.cleanup_expired_files": {
        "task": "files_management.tasks.cleanup.cleanup_expired_files",
        "schedule": crontab(hour=2, minute=0), # nightly 02:00
    },

    # ----------------------------------------------------------------
    # Notifications
    # ----------------------------------------------------------------
    "notifications.process_due_digests": {
        "task": "notifications_system.tasks.digest.process_due_digests",
        "schedule": crontab(minute=0), # every hour
    },
    "notifications.requeue_pending_outbox": {
        "task": "notifications_system.tasks.maintenance.requeue_pending_outbox",
        "schedule": 300, # every 5 min (seconds)
    },
    "notifications.cleanup_processed_outbox": {
        "task": "notifications_system.tasks.maintenance.cleanup_processed_outbox",
        "schedule": crontab(hour=3, minute=0, day_of_week=0), # weekly Sunday 03:00
    },
    "notifications.rebuild_unread_counts": {
        "task": "notifications_system.tasks.maintenance.rebuild_unread_counts",
        "schedule": crontab(hour=4, minute=0), # nightly 04:00
    },
    "notifications.clear_stale_digests": {
        "task": "notifications_system.tasks.maintenance.clear_stale_digests",
        "schedule": crontab(hour=3, minute=30, day_of_week=0), # weekly Sunday 03:30
    },

    # ----------------------------------------------------------------
    # Authentication cleanup
    # ----------------------------------------------------------------
    "auth.cleanup_expired_impersonation_tokens": {
        "task": "authentication.tasks.cleanup_expired_impersonation_tokens_task",
        "schedule": crontab(minute=0), # every hour
    },
    "auth.cleanup_expired_otps": {
        "task": "authentication.tasks.cleanup_expired_otps_task",
        "schedule": crontab(minute=30), # every hour at :30
    },
    "auth.cleanup_expired_password_reset_requests": {
        "task": "authentication.tasks.cleanup_expired_password_reset_requests_task",
        "schedule": crontab(hour=0, minute=15), # nightly 00:15
    },
    "auth.cleanup_expired_registration_tokens": {
        "task": "authentication.tasks.cleanup_expired_registration_tokens_task",
        "schedule": crontab(hour=0, minute=30), # nightly 00:30
    },

    # ----------------------------------------------------------------
    # Orders
    # ----------------------------------------------------------------
    "orders.release_stale_preferred_orders": {
        "task": "orders.tasks.release_stale_preferred_orders",
        "schedule": crontab(minute="*/15"), # every 15 min
    },
    "orders.archive_approved_orders": {
        "task": "orders.tasks.archive_approved_orders",
        "schedule": crontab(hour=1, minute=30), # nightly 01:30
    },

    # ----------------------------------------------------------------
    # Payments
    # ----------------------------------------------------------------
    "payments.resolve_stale_pending": {
        "task": "payments_processor.tasks.payment_cleanup_tasks.resolve_stale_pending_payments_task",
        "schedule": crontab(minute="*/30"), # every 30 min
    },
    "payments.expire_elapsed_intents": {
        "task": "payments_processor.tasks.payment_cleanup_tasks.expire_elapsed_payment_intents_task",
        "schedule": crontab(minute="*/30"), # every 30 min
    },

    # ----------------------------------------------------------------
    # Wallets
    # ----------------------------------------------------------------
    "wallets.expire_active_holds": {
        "task": "wallets.tasks.expire_active_holds",
        "schedule": 300, # every 5 min
    },

    # ----------------------------------------------------------------
    # Discounts
    # ----------------------------------------------------------------
    "discounts.activate_and_expire_campaigns": {
        "task": "discounts.activate_and_expire_campaigns",
        "schedule": crontab(minute="*/30"), # every 30 min
    },

    # ----------------------------------------------------------------
    # Support
    # ----------------------------------------------------------------
    "support.check_sla_breaches": {
        "task": "support_management.tasks.check_sla_breaches",
        "schedule": 300, # every 5 min
    },
    "support.refresh_dashboards": {
        "task": "support_management.tasks.refresh_all_support_dashboards",
        "schedule": crontab(minute="*/15"), # every 15 min
    },
    "support.auto_reassign": {
        "task": "support_management.tasks.auto_reassign_unresolved_tasks",
        "schedule": crontab(minute="*/30"), # every 30 min
    },
    "support.update_workload_trackers": {
        "task": "support_management.tasks.update_support_workload_trackers",
        "schedule": crontab(minute="*/10"), # every 10 min
    },

    # ----------------------------------------------------------------
    # Activity feed
    # ----------------------------------------------------------------
    "activity.cleanup_dismissed_feed_states": {
        "task": "activity.tasks.cleanup_tasks.cleanup_dismissed_feed_states",
        "schedule": crontab(hour=5, minute=0, day_of_week=0), # weekly Sunday 05:00
    },

    # ----------------------------------------------------------------
    # CMS Intelligence
    # ----------------------------------------------------------------
    "cms.pull_gsc_data": {
        "task": "cms_intelligence.tasks.gsc_ingestion.pull_gsc_data",
        "schedule": crontab(hour=6, minute=0),
    },
    "cms.pull_ga4_data": {
        "task": "cms_intelligence.tasks.ga4_ingestion.pull_ga4_data",
        "schedule": crontab(hour=5, minute=30),
    },
    "cms.compute_performance_snapshots": {
        "task": "cms_intelligence.tasks.performance_snapshot.compute_performance_snapshots",
        "schedule": crontab(hour=7, minute=0),
    },
    "cms.scan_freshness": {
        "task": "cms_intelligence.tasks.freshness_scanner.scan_freshness",
        "schedule": crontab(hour=8, minute=0),
    },
    "cms.reindex_all_embeddings": {
        "task": "cms_intelligence.tasks.embedding_generation.reindex_all_embeddings",
        "schedule": crontab(hour=2, minute=0, day_of_week=1),
    },

    # ----------------------------------------------------------------
    # Referrals
    # ----------------------------------------------------------------
    "referrals.expire_stale_invitations": {
        "task": "referrals.tasks.expire_stale_referral_invitations",
        "schedule": crontab(hour=6, minute=30), # nightly 06:30
    },

    # Reputation system
    # ----------------------------------------------------------------
    "reputation.snapshot_update": {
        "task": "reputation_system.tasks.snapshot_tasks.update_snapshot_task",
        "schedule": crontab(hour=3, minute=0), # nightly 03:00
    },
    "reputation.emit_events": {
        "task": "reputation_system.tasks.events_tasks.emit_reputation_recalculated_event",
        "schedule": crontab(hour=3, minute=30), # after snapshot
    },
}

CELERY_TASK_ALWAYS_EAGER = env_bool("CELERY_TASK_ALWAYS_EAGER", False)
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_ACKS_LATE = True
CELERY_TASK_REJECT_ON_WORKER_LOST = True
CELERY_WORKER_PREFETCH_MULTIPLIER = env_int(
    "CELERY_WORKER_PREFETCH_MULTIPLIER",
    1,
)
CELERY_TASK_TIME_LIMIT = env_int("CELERY_TASK_TIME_LIMIT", 30 * 60)
CELERY_TASK_SOFT_TIME_LIMIT = env_int(
    "CELERY_TASK_SOFT_TIME_LIMIT",
    25 * 60,
)


EMAIL_BACKEND = env(
    "EMAIL_BACKEND",
    "django.core.mail.backends.smtp.EmailBackend",
)
EMAIL_HOST = env("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = env_int("EMAIL_PORT", 587)
EMAIL_USE_TLS = env_bool("EMAIL_USE_TLS", True)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = env(
    "DEFAULT_FROM_EMAIL",
    EMAIL_HOST_USER or "no-reply@example.com",
)
DEFAULT_EMAIL_PROVIDER = env("DEFAULT_EMAIL_PROVIDER", "console")


SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"
SESSION_IDLE_TIMEOUT = env_int("SESSION_IDLE_TIMEOUT", 8 * 60 * 60)
IMPERSONATION_SESSION_IDLE_TIMEOUT = env_int(
    "IMPERSONATION_SESSION_IDLE_TIMEOUT",
    15 * 60,
)
SESSION_WARNING_TIME = env_int("SESSION_WARNING_TIME", 30 * 60)

PASSKEY_CHALLENGE_TTL = env_int("PASSKEY_CHALLENGE_TTL", 300)
PASSKEY_REDIS_PREFIX = env("PASSKEY_REDIS_PREFIX", "passkey")


SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(
        minutes=env_int("JWT_ACCESS_TOKEN_MINUTES", 30),
    ),
    "REFRESH_TOKEN_LIFETIME": timedelta(
        minutes=env_int("JWT_REFRESH_TOKEN_MINUTES", 7 * 24 * 60),
    ),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
}


REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_THROTTLE_CLASSES": [
        "core.throttling.rate_limiter.BurstRateThrottle",
        "core.throttling.rate_limiter.SustainedRateThrottle",
        "core.throttling.rate_limiter.WriteOperationThrottle",
        "core.throttling.rate_limiter.IPRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
        "rest_framework.throttling.AnonRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "burst": "200/min",
        "sustained": "5000/hour",
        "user": "10000/hour",
        "anon": "2000/hour",
        "write": "200/hour",
        "read": "10000/hour",
        "ip": "1000/hour",
        "admin": "20000/hour",
        "public": "200/hour",
        "endpoint": "1000/hour",
        "login": "10/minute",
        "login_sustained": "200/day",
        "password_reset_request": "30/hour",
        "magic_link": "5/minute",
        "mfa_challenge": "120/hour",
        "mfa_verify": "120/hour",
        "magic_link_ip": "60/hour",
        "magic_link_email": "30/hour",
        "magic_link_request": "30/hour",
        "magic_link_confirm": "60/hour",
        "logout_all_sessions": "5/hour",
        "password_reset_confirm": "60/hour",
        "account_unlock_request": "30/hour",
        "account_unlock_confirm": "60/hour",
        "registration_request": "30/hour",
        "registration_resend": "18/hour",
        "registration_confirm": "60/hour",
        "backup_code_generate": "2/hour",
        "impersonation_token_create": "10/hour",
        "impersonation_start": "20/hour",
        "notifications_write_burst": "100/min",
        "notifications_read_burst": "1000/min",
        "notifications_write_sustained": "1000/day",
        "notifications_read_sustained": "10000/day",
        "communication_message_send": "60/min",
        "communication_thread_create": "20/hour",
        "communication_moderation_action": "120/hour",
        "communication_screening_rule_write": "30/hour",
        "communication_sse_connect": "30/min",
        "communication_read_receipt": "300/min",
        "audit_log": "10/minute",
        "superadmin_audit": "100/minute",
        "class_access_view": "10/min",
        "class_two_factor": "6/min",
        "class_payment_prepare": "20/hour",
        "class_proposal_action": "30/hour",
        "notification_poll": "60/minute",
    },
    "EXCEPTION_HANDLER": (
        "authentication.exceptions.custom_exception_handler"
    ),
    "DEFAULT_VERSIONING_CLASS": (
        "rest_framework.versioning.URLPathVersioning"
    ),
    "DEFAULT_VERSION": "1.0",
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PAGINATION_CLASS": (
        "rest_framework.pagination.PageNumberPagination"
    ),
    "PAGE_SIZE": env_int("DRF_PAGE_SIZE", 25),
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
    ],
}


SPECTACULAR_SETTINGS = {
    "TITLE": "Writing System Backend API",
    "DESCRIPTION": "API documentation for the Writing System backend.",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SCHEMA_PATH_PREFIX": r"/api/",
    "COMPONENT_SPLIT_REQUEST": True,
    "COMPONENT_NO_READ_ONLY_REQUIRED": True,
    "SERVE_PERMISSIONS": ["rest_framework.permissions.AllowAny"],
    "SERVE_AUTHENTICATION": None,
    "SWAGGER_UI_SETTINGS": {
        "deepLinking": True,
        "displayRequestDuration": True,
        "docExpansion": "list",
        "filter": True,
        "showExtensions": True,
        "showCommonExtensions": True,
    },
    "REDOC_UI_SETTINGS": {
        "hideDownloadButton": False,
        "expandResponses": "200,201",
        "pathInMiddlePanel": True,
    },
}


CORS_ALLOWED_ORIGINS = env_list(
    "CORS_ALLOWED_ORIGINS",
    (
        "http://localhost:5173,http://127.0.0.1:5173,"
        "http://localhost:5174,http://127.0.0.1:5174,"
        "http://localhost:3000,http://127.0.0.1:3000"
    ),
)
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = False

from corsheaders.defaults import default_headers # noqa: E402

CORS_ALLOW_HEADERS = list(default_headers) + [
    "X-Device-Fingerprint",
    "X-Session-ID",
]

CSRF_TRUSTED_ORIGINS = env_list(
    "CSRF_TRUSTED_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173,"
    "http://localhost:5174,http://127.0.0.1:5174,"
    "http://localhost:8000,http://127.0.0.1:8000",
)


SECURE_SSL_REDIRECT = False
SECURE_PROXY_SSL_HEADER = None
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"


# ── Stripe ────────────────────────────────────────────────────────────────────
STRIPE_SECRET_KEY = env("STRIPE_SECRET_KEY", "")
STRIPE_PUBLISHABLE_KEY = env("STRIPE_PUBLISHABLE_KEY", "")
STRIPE_WEBHOOK_SECRET = env("STRIPE_WEBHOOK_SECRET", "")

# ── Notification rate limiting ─────────────────────────────────────────────────
# Applies per-recipient per WINDOW seconds. Configurable without deploy.
NOTIFICATION_RATE_LIMIT_MAX = env_int("NOTIFICATION_RATE_LIMIT_MAX", 10)
NOTIFICATION_RATE_LIMIT_WINDOW_SECONDS = env_int(
    "NOTIFICATION_RATE_LIMIT_WINDOW_SECONDS", 300
)

# ── GA4 + GSC (CMS Intelligence) ────────────────────────────────────────
GA4_PROPERTY_ID = env("GA4_PROPERTY_ID", "")
GSC_PROPERTY_URL = env("GSC_PROPERTY_URL", "")
GOOGLE_SERVICE_ACCOUNT_JSON = env("GOOGLE_SERVICE_ACCOUNT_JSON", "")
EMBEDDING_API_KEY = env("EMBEDDING_API_KEY", "")

# ── File delivery guard ────────────────────────────────────────────────────────
# Signed download URL expiry for private order files (seconds).
FILE_SIGNED_URL_EXPIRY_SECONDS = env_int("FILE_SIGNED_URL_EXPIRY_SECONDS", 900)

SILENCED_SYSTEM_CHECKS = env_list("SILENCED_SYSTEM_CHECKS", "")

if not WAGTAIL_AVAILABLE:
    SILENCED_SYSTEM_CHECKS = [
        *SILENCED_SYSTEM_CHECKS,
        "fields.E300",
        "fields.E307",
    ]
