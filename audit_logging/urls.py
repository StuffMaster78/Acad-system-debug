from rest_framework.routers import DefaultRouter
from audit_logging.views import AuditLogEntryViewSet

router = DefaultRouter()
router.register(r'logs', AuditLogEntryViewSet, basename='auditlog')

urlpatterns = router.urls