from django.urls import include, path
from rest_framework.routers import DefaultRouter

from users.api.views.profile_update_viewset import (
    ProfileUpdateRequestViewSet,
)
from users.api.views.profile_viewset import ProfileViewSet
from users.api.views.user_viewset import UserViewSet
from users.views.subscription_viewset import SubscriptionViewSet

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")
router.register(r"profile", ProfileViewSet, basename="profile")
router.register(
    r"profile-update-requests",
    ProfileUpdateRequestViewSet,
    basename="profile-update-request",
)
router.register(r"subscriptions", SubscriptionViewSet, basename="subscriptions")

urlpatterns = [
    path("", include(router.urls)),
]