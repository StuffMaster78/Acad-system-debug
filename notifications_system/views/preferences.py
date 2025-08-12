from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from notifications_system.models.notification_preferences import (
    NotificationPreference,
    EventNotificationPreference,
    NotificationEventPreference,
    RoleNotificationPreference
)
from notifications_system.models.notification_profile import NotificationProfile
from notifications_system.serializers import (
    NotificationPreferenceSerializer,
    EventNotificationPreferenceSerializer,
    NotificationEventPreferenceSerializer,
    RoleNotificationPreferenceSerializer
)
from notifications_system.enums import NotificationType
from notifications_system.permissions import IsAdminUser
from websites.models import Website


class NotificationPreferenceViewSet(viewsets.ModelViewSet):
    """
    API endpoint for users to manage their notification preferences.
    Superusers can manage for others.
    """
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser and self.request.query_params.get("user_id"):
            return NotificationPreference.objects.filter(
                user_id=self.request.query_params["user_id"]
            )
        return NotificationPreference.objects.filter(user=user)

    def get_object(self):
        target_user = self._get_target_user()
        website = self._get_website()
        obj, _ = NotificationPreference.objects.get_or_create(
            user=target_user, website=website
        )
        return obj
    
    def perform_create(self, serializer):
        serializer.save(
            user=self._get_target_user(),
            website=self._get_website(),
        )

    def perform_update(self, serializer):
        serializer.save(
            user=self._get_target_user(),
            website=self._get_website()
        )

    def _get_target_user(self):
        if self.request.user.is_superuser and "user_id" in self.request.data:
            from users.models import User
            return get_object_or_404(User, id=self.request.data["user_id"])
        return self.request.user

    def _get_website(self):
        website_id = self.request.query_params.get("website_id") or self.request.data.get("website")
        if website_id:
            return get_object_or_404(Website, id=website_id)
        return getattr(self.request.user, "website", None)
    
    def partial_update(self, request, *args, **kwargs):
        """
        Allow toggling a single channel like in-app, email, etc.
        Accepts: { "channel": "email", "enabled": true }
        """
        channel = request.data.get("channel")
        enabled = request.data.get("enabled")

        if channel and enabled is not None:
            obj = self.get_object()
            # Use PRIORITY_LABEL_CHOICES or define NOTIFICATION_CHANNELS as needed
            NOTIFICATION_CHANNELS = [v for k, v in NotificationType.choices()]
            if channel not in NOTIFICATION_CHANNELS:
                return Response({"error": "Invalid channel"}, status=400)

            setattr(obj, f"receive_{channel}", enabled)
            obj.save()
            return Response(self.get_serializer(obj).data)

        return super().partial_update(request, *args, **kwargs)

    @action(detail=False, methods=["post"], url_path="apply-profile")
    def apply_profile(self, request):
        """
        Apply a saved profile to the current user's preferences.
        """
        profile_slug = request.data.get("profile")
        if not profile_slug:
            return Response({"error": "Profile slug required."}, status=400)
        try:
            profile = NotificationProfile.objects.get(slug=profile_slug)
        except NotificationProfile.DoesNotExist:
            return Response({"error": "Profile not found."}, status=404)

        pref = self.get_object()
        for channel in [v for _, v in NotificationType.choices()]:
            value = getattr(profile, f"receive_{channel}", False)
            setattr(pref, f"receive_{channel}", value)
        pref.profile = profile
        pref.save()
        return Response({"status": "Profile applied", "profile": profile.name})
    
    @action(detail=False, methods=["post"], url_path="reset")
    def reset_preferences(self, request):
        """Reset user notification preferences to default."""
        from notifications_system.services.preferences import (
            NotificationPreferenceResolver
        )
        from notifications_system.emails.reset_notification_preferences import (
            send_reset_confirmation_email,
        )

        user = self._get_target_user()
        website = self._get_website()
        success = NotificationPreferenceResolver.reset_user_preferences(user)

        if success:
            NotificationPreferenceResolver.assign_default_preferences(user, website)
            send_reset_confirmation_email(user, website)
            return Response({"status": "Reset and re-applied default profile. Confirmation email sent."})
        
        return Response({"error": "No preferences found to reset."}, status=404)
    
    @action(detail=False, methods=["post"], url_path="clone-profile")
    def clone_profile(self, request):
        """
        Clone a profile and apply it to the user's preferences.
        """
        profile_slug = request.data.get("profile")

        if not profile_slug:
            return Response({"error": "Profile slug required."}, status=400)

        try:
            profile = NotificationProfile.objects.get(slug=profile_slug)
        except NotificationProfile.DoesNotExist:
            return Response({"error": "Profile not found."}, status=404)

        pref = self.get_object()

        # Copy all receive_* fields
        for field in [
            "receive_email", "receive_in_app", "receive_push", "receive_sms"
        ]:
            setattr(pref, field, getattr(profile, field))

        pref.profile = None  # it's now a user-customized version
        pref.save()

        return Response({
            "status": "Cloned from profile",
            "preferences": NotificationPreferenceSerializer(pref).data
        })


class MyNotificationPreferencesView(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return NotificationPreference.objects.get(user=self.request.user)


class MyEventNotificationPreferenceViewSet(viewsets.ModelViewSet):
    serializer_class = EventNotificationPreferenceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return EventNotificationPreference.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class NotificationEventPreferenceViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationEventPreferenceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser and self.request.query_params.get("user_id"):
            return NotificationPreference.objects.filter(
                user_id=self.request.query_params["user_id"]
            )
        return NotificationPreference.objects.filter(user=user)
    
class RoleNotificationPreferenceViewSet(viewsets.ModelViewSet):
    queryset = RoleNotificationPreference.objects.all()
    serializer_class = RoleNotificationPreferenceSerializer
    permission_classes = [IsAdminUser]


class MyEventNotificationPreferenceViewSet(viewsets.ModelViewSet):
    serializer_class = EventNotificationPreferenceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return EventNotificationPreference.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)