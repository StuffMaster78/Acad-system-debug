from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import FeedbackRequestViewSet

router = DefaultRouter()
router.register("", FeedbackRequestViewSet, basename="feedback")

urlpatterns = [
    path("", include(router.urls)),
]
