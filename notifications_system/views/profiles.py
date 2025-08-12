from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import action
from rest_framework.response import Response

from notifications_system.models.notification_profile import NotificationProfile
from notifications_system.models.notification_profile import NotificationGroupProfile
from notifications_system.serializers import (
    NotificationProfileSerializer,
    NotificationGroupProfileSerializer
)
from notifications_system.models.notification_preferences import NotificationPreference
from notifications_system.serializers import NotificationPreferenceSerializer
from notifications_system.enums import NotificationType

class NotificationProfileViewSet(viewsets.ModelViewSet):
    """
    CRUD for notification profiles (templates of preference settings).
    """
    queryset = NotificationProfile.objects.all()
    serializer_class = NotificationProfileSerializer
    permission_classes = [IsAdminUser]


    
    @action(detail=True, methods=["post"], url_path="clone")
    def clone(self, request, pk=None):
        profile = self.get_object()
        name = request.data.get("name", f"{profile.name} Copy")
        clone = NotificationProfile.objects.create(
            name=name,
            description=f"Clone of {profile.name}",
            default_email=profile.default_email,
            default_sms=profile.default_sms,
            default_push=profile.default_push,
            default_in_app=profile.default_in_app,
            dnd_start=profile.dnd_start,
            dnd_end=profile.dnd_end,
        )
        return Response(NotificationProfileSerializer(clone).data)
    
    @action(detail=False, methods=["get"], url_path="my-profile")
    def my_profile(self, request):
        pref = NotificationPreference.objects.filter(user=request.user).first()
        return Response(NotificationPreferenceSerializer(pref).data)

    
    @action(detail=False, methods=["post"], url_path="apply")
    def apply_profile(self, request):
        """
        Apply a notification profile to the current user's preferences.
        """
        profile_slug = request.data.get("profile")

        if not profile_slug:
            return Response({"error": "Profile slug required."}, status=400)

        try:
            profile = NotificationProfile.objects.get(slug=profile_slug)
        except NotificationProfile.DoesNotExist:
            return Response({"error": "Profile not found."}, status=404)

        pref = NotificationPreference.objects.get(user=request.user)
        # Use PRIORITY_LABEL_CHOICES or define NOTIFICATION_CHANNELS as needed
        NOTIFICATION_CHANNELS = [v for k, v in NotificationType.choices()]
        for channel in NOTIFICATION_CHANNELS:
            value = getattr(profile, f"default_{channel}", False)
            setattr(pref, f"receive_{channel}", value)
        pref.profile = profile
        pref.save()

        return Response({"status": "Profile applied", "profile": profile.name})


class NotificationGroupProfileViewSet(viewsets.ModelViewSet):
    """
    CRUD for notification group profiles.
    """
    queryset = NotificationGroupProfile.objects.all()
    serializer_class = NotificationGroupProfileSerializer
    permission_classes = [IsAdminUser]