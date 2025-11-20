from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SupportProfileViewSet, SupportNotificationViewSet, SupportOrderManagementViewSet,
    SupportMessageViewSet, EscalationLogViewSet, SupportWorkloadTrackerViewSet,
    PaymentIssueLogViewSet, FAQManagementViewSet, SupportDashboardViewSet
)

# 📌 **Initialize Router for ViewSets**
router = DefaultRouter()
router.register(r"support-profiles", SupportProfileViewSet, basename="support-profile")
router.register(r"notifications", SupportNotificationViewSet, basename="support-notifications")
router.register(r"order-management", SupportOrderManagementViewSet, basename="support-order-management")
router.register(r"messages", SupportMessageViewSet, basename="support-messages")
router.register(r"escalations", EscalationLogViewSet, basename="escalation-log")
router.register(r"workload-tracker", SupportWorkloadTrackerViewSet, basename="workload-tracker")
router.register(r"payment-issues", PaymentIssueLogViewSet, basename="payment-issues")
router.register(r"faqs", FAQManagementViewSet, basename="faqs")
router.register(r"dashboard", SupportDashboardViewSet, basename="support-dashboard")

# 📌 **Define API URL Patterns**
urlpatterns = [
    path("", include(router.urls)),

    # Auto-generated schema
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    
    # Swagger UI
    path("swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    
    # ReDoc UI
    path("redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]