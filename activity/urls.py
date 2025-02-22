from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ActivityLogViewSet

# Create a router to automatically handle routes for ActivityLog
router = DefaultRouter()
router.register(r'activities', ActivityLogViewSet, basename='activitylog')

urlpatterns = [
    path('', include(router.urls)),  # Include all routes handled by the router
]