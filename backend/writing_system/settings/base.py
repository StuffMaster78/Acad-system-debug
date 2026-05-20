from pathlib import Path
import os
from datetime import timedelta
from urllib.parse import quote_plus
from dotenv import load_dotenv
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(os.path.join(BASE_DIR, ".env"))

# -------------------------
# CORE ENV HELPERS
# -------------------------

def get_required_env(key, default=None, allow_empty=False):
    value = os.getenv(key, default)
    if value is None or (value == "" and not allow_empty):
        if default is not None:
            return default
        raise ImproperlyConfigured(f"Missing env var: {key}")
    return value


# -------------------------
# SECURITY CORE
# -------------------------

SECRET_KEY = os.getenv("SECRET_KEY") or "dev-insecure-secret-key-change-me"

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

DEBUG = False  # overridden in dev

# Legacy compatibility apps are installed only so historical migrations and
# data imports can still resolve their models. New code and frontend routes
# must use wallets and files_management instead.
LEGACY_COMPAT_APPS = [
    "wallet",
    "client_wallet",
    "writer_wallet",
]

ENABLE_LEGACY_WRITER_WALLET_SIGNALS = (
    os.getenv("ENABLE_LEGACY_WRITER_WALLET_SIGNALS", "False") == "True"
)


# -------------------------
# INSTALLED APPS
# -------------------------

INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # DRF & API
    "rest_framework",
    "django_filters",
    "corsheaders",
    "drf_spectacular",
    "drf_spectacular_sidecar",

    # Auth
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "django_otp",
    "django_otp.plugins.otp_totp",

    # Infra
    "django_celery_beat",
    "django_ratelimit",
    "channels",
    "django_countries",
    "import_export",

    # Notifications
    "notifications_system.apps.NotificationsSystemConfig",

    # Core apps
    "core",
    "websites",
    "users",
    "accounts",
    "authentication",
    "audit_logging",
    "event_system",
    "communications",

    # Business apps
    "orders",
    "order_configs",
    "order_pricing_core",
    "pricing",
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
    "files_management",
    "reputation_system",
    "privacy",
    "users_state",

    # Content
    "blog_pages_management",
    "service_pages_management",
    "seo_pages",
    "media_management",

    # Support
    "tickets",
    "mass_emails",
    "announcements",
    "analytics",

    # Management domains
    "client_management",
    "writer_management",
    "editor_management",
    "support_management",
    "admin_management",
    "superadmin_management",
    "governance",
    "loyalty_management",
    "activity",
    "reviews_system",
    "holiday_management",

    # Compensation
    "writer_compensation.apps.WriterCompensationConfig",
]

# -------------------------
# MIDDLEWARE
# -------------------------

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",

    "core.middleware.graceful_degradation.GracefulDegradationMiddleware",
    "core.middleware.portal_tenant_resolver.PortalTenantResolverMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",

    "authentication.middleware.impersonation_middleware.ImpersonationMiddleware",
    "authentication.middleware.login_session_enforcement_middleware.LoginSessionEnforcementMiddleware",
    "authentication.middleware.session_activity_middleware.SessionActivityMiddleware",
    "authentication.middleware.session_timeout.SessionTimeoutMiddleware",

    "audit_logging.middleware.AuditUserMiddleware",

    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",

    "superadmin_management.middleware.BlacklistMiddleware",
    "core.middleware.compression.EnhancedCompressionMiddleware",
    "activity.middleware.ActivityAuditMiddleware",
    "core.middleware.performance_monitoring.PerformanceMonitoringMiddleware",
]

ROOT_URLCONF = "writing_system.urls"
WSGI_APPLICATION = "writing_system.wsgi.application"
AUTH_USER_MODEL = "users.User"

# -------------------------
# INTERNATIONALIZATION
# -------------------------

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# -------------------------
# STATIC
# -------------------------

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# -------------------------
# TEMPLATES BASE
# -------------------------

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

# -------------------------
# DATABASE HELPERS
# -------------------------

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")

def _redis_url(db: int) -> str:
    if REDIS_PASSWORD and REDIS_PASSWORD.strip():
        return f"redis://:{quote_plus(REDIS_PASSWORD)}@{REDIS_HOST}:{REDIS_PORT}/{db}"
    return f"redis://{REDIS_HOST}:{REDIS_PORT}/{db}"

# -------------------------
# REDIS CORE SERVICES
# -------------------------

COMMUNICATIONS_REDIS_URL = os.getenv("COMMUNICATIONS_REDIS_URL", _redis_url(2))
COMMUNICATIONS_SSE_CHANNEL = "communications:sse"
REDIS_URL = os.getenv("REDIS_URL", _redis_url(0))

# -------------------------
# CELERY BASE
# -------------------------

CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

# -------------------------
# REST FRAMEWORK BASE
# -------------------------

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend"
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.URLPathVersioning",
}

# -------------------------
# CORS / CSRF BASE
# -------------------------

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:3000",
]

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:5174",
]
