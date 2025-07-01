from django.urls import path, include
from rest_framework.routers import DefaultRouter
from audit_logging.views import AuditLogEntryViewSet

router = DefaultRouter()
router.register(r"audit-logs", AuditLogEntryViewSet, basename="auditlog")

urlpatterns = [
    path("", include(router.urls)),
]