from django.urls import include
from django.urls import path

from rest_framework.routers import DefaultRouter

from audit_logging.api.views.audit_dead_letter_views import (
    AuditDeadLetterViewSet,
)
from audit_logging.api.views.audit_event_views import (
    AuditEventViewSet,
)

router = DefaultRouter()

router.register(
    r"events",
    AuditEventViewSet,
    basename="audit-events",
)

router.register(
    r"dlq",
    AuditDeadLetterViewSet,
    basename="audit-dlq",
)

urlpatterns = [
    path(
        "v1/",
        include(router.urls),
    ),
]