from __future__ import annotations

from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from notifications_system.serializers import (
    NotificationPreferencesSerializer,
)
from notifications_system.services.preferences import (
    NotificationPreferenceResolver,
)


class PreferencesViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """Retrieve and update notification preferences for the user."""

    serializer_class = NotificationPreferencesSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = self.request.user
        pref = getattr(user, "notification_preferences", None)
        if not pref:
            NotificationPreferenceResolver.assign_default_preferences(user)
            pref = user.notification_preferences
        return pref