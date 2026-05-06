from django.urls import path

from audit_logging.api.views import (
    AuditHealthView,
    AuditRecentView,
)

app_name = "audit_logging"

urlpatterns = [
    path("health/", AuditHealthView.as_view(), name="audit-health"),
    path("recent/", AuditRecentView.as_view(), name="audit-recent"),
]