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
]

WAGTAIL_APPS = [
    "wagtail.contrib.forms",
    "wagtail.contrib.redirects",
    "wagtail.contrib.settings",
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
    "media_management",
    "tickets",
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
        minutes=env_int("JWT_ACCESS_TOKEN_MINUTES", 24 * 60),
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
        "user": "5000/hour",
        "anon": "500/hour",
        "write": "200/hour",
        "read": "10000/hour",
        "ip": "1000/hour",
        "admin": "20000/hour",
        "public": "200/hour",
        "endpoint": "1000/hour",
        "login": "10/minute",
        "login_sustained": "200/day",
        "password_reset_request": "5/10min",
        "magic_link": "5/minute",
        "mfa_challenge": "10/5min",
        "mfa_verify": "10/5min",
        "magic_link_ip": "10/10min",
        "magic_link_email": "5/10min",
        "magic_link_request": "5/10min",
        "magic_link_confirm": "10/10min",
        "logout_all_sessions": "5/hour",
        "password_reset_confirm": "10/10min",
        "account_unlock_request": "5/10min",
        "account_unlock_confirm": "10/10min",
        "registration_request": "5/10min",
        "registration_resend": "3/10min",
        "registration_confirm": "10/10min",
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

CSRF_TRUSTED_ORIGINS = env_list(
    "CSRF_TRUSTED_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173",
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


SILENCED_SYSTEM_CHECKS = env_list("SILENCED_SYSTEM_CHECKS", "")

if not WAGTAIL_AVAILABLE:
    SILENCED_SYSTEM_CHECKS = [
        *SILENCED_SYSTEM_CHECKS,
        "fields.E300",
        "fields.E307",
    ]
