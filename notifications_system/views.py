from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from rest_framework.views import APIView
from rest_framework import generics
from django.utils.timezone import now

from notifications_system.models import (
    Notification, NotificationGroupProfile, NotificationPreference,
    NotificationProfile, EventNotificationPreference,
    BroadcastNotification, NotificationEventPreference,
    RoleNotificationPreference
)
from notifications_system.serializers import (
    NotificationSerializer,
    NotificationPreferenceSerializer,
    NotificationProfileSerializer,
    NotificationPriorityMetaSerializer,
    EventNotificationPreferenceSerializer,
    NotificationGroupProfileSerializer,
    BroadcastNotificationSerializer,
    NotificationEventPreferenceSerializer,
    RoleNotificationPreferenceSerializer
)
from notifications_system.utils.priority_mapper import (
    PRIORITY_LABEL_CHOICES
)
from notifications_system.filters import NotificationFilter
from django_filters.rest_framework import DjangoFilterBackend # type: ignore
from django.shortcuts import get_object_or_404
from websites.models import Website
from notifications_system.enums import (
    NotificationPriority, NotificationType, NotificationCategory
)
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from .utils.enums_export import export_notification_enums
from notifications_system.services.preferences import (
    reset_user_preferences, assign_default_preferences
)

class NotificationThrottle(UserRateThrottle):
    rate = '60/min'  # customize as needed for bell spam prevention


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Handles listing and interacting with user notifications.
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [NotificationThrottle]

    def get_queryset(self):
        return Notification.objects.filter(
            user=self.request.user,
            website=self.request.user.website
        ).order_by("-created_at")

    @action(detail=False, methods=["get"])
    def unread(self, request):
        qs = self.get_queryset().filter(is_read=False)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def unread_count(self, request):
        count = self.get_queryset().filter(is_read=False).count()
        return Response({"unread_count": count})

    @action(detail=True, methods=["post"])
    def mark_as_read(self, request, pk=None):
        notification = self.get_object()
        if not notification.is_read:
            notification.is_read = True
            notification.save(update_fields=["is_read"])
        return Response({"status": "marked as read"})

    @action(detail=False, methods=["post"])
    def mark_all_as_read(self, request):
        count = self.get_queryset().filter(is_read=False).update(is_read=True)
        return Response({
            "status": "all marked as read",
            "updated": count
        })

class NotificationProfileViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = NotificationProfile.objects.all()
    serializer_class = NotificationProfileSerializer
    permission_classes = [permissions.IsAdminUser, permissions.IsAuthenticatedOrReadOnly]  # Only superusers

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
    queryset = NotificationGroupProfile.objects.all()
    serializer_class = NotificationGroupProfileSerializer
    permission_classes = [permissions.IsAdminUser]

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
            # Superuser managing another user’s preferences
            return NotificationPreference.objects.filter(
                user_id=self.request.query_params["user_id"]
            )
        return NotificationPreference.objects.filter(user=user)

    def get_object(self):
        user = self.request.user
        website = self._get_website()

        # Allow superusers to view others’ preferences (e.g. from admin)
        target_user = self._get_target_user()

        obj, _ = NotificationPreference.objects.get_or_create(
            user=target_user,
            website=website
        )
        return obj

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
        # Allow override via query/data for multi-tenant admin panel
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
        # Use PRIORITY_LABEL_CHOICES or define NOTIFICATION_CHANNELS as needed
        NOTIFICATION_CHANNELS = [v for k, v in NotificationType.choices()]
        for channel in NOTIFICATION_CHANNELS:
            value = getattr(profile, f"receive_{channel}", False)
            setattr(pref, f"receive_{channel}", value)
        pref.profile = profile
        pref.save()

        return Response({"status": "Profile applied", "profile": profile.name})
    
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


class NotificationMetaView(APIView):
    """
    Expose priority levels for dropdowns etc.
    """
    permission_classes = []  # Public or auth as needed

    def get(self, request, *args, **kwargs):
        priorities = [
            {"value": value, "label": label}
            for value, label in NotificationPriority.choices()
        ]
        channels = [
            {"value": value, "label": label}
            for value, label in NotificationType.choices()
        ]
        categories = [
            {"value": value, "label": label}
            for value, label in NotificationCategory.choices()
        ]
        return Response({
            "priorities": NotificationPriorityMetaSerializer(priorities, many=True).data,
            "channels": channels,
            "categories": categories
        })


class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(
            user=self.request.user,
            website=self.request.user.website,
        ).order_by("-created_at")


class NotificationDetailView(generics.RetrieveAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)


class MarkNotificationAsReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            notification = Notification.objects.get(id=pk, user=request.user)
            notification.is_read = True
            notification.save()
            return Response({"status": "read"}, status=200)
        except Notification.DoesNotExist:
            return Response({"error": "Not found"}, status=404)
        

    def get_queryset(self):
        qs = Notification.objects.filter(user=self.request.user)
        is_read = self.request.query_params.get("is_read")
        if is_read is not None:
            qs = qs.filter(is_read=is_read.lower() == "true")
        return qs.order_by("-created_at")


class UnreadNotificationCountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        count = Notification.objects.filter(
            user=request.user,
            is_read=False,
            website=request.user.website  # Optional if multitenant
        ).count()
        return Response({"unread_count": count})


class IsSuperUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser

class NotificationAdminViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Admin-only viewset for viewing *all* notifications across users.
    """
    queryset = Notification.objects.select_related("user", "website")
    serializer_class = NotificationSerializer
    permission_classes = [IsSuperUser]
    filter_backends = [DjangoFilterBackend]
    filterset_class = NotificationFilter

    @action(detail=False, methods=["get"])
    def unread(self, request):
        qs = self.get_queryset().filter(is_read=False)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)
    

@api_view(["GET"])
@permission_classes([IsAdminUser])
def notification_enum_choices(request):
    return Response(export_notification_enums())


class MyNotificationPreferencesView(generics.RetrieveUpdateAPIView):
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return NotificationPreference.objects.get(user=self.request.user)


class MyEventNotificationPreferenceViewSet(viewsets.ModelViewSet):
    serializer_class = EventNotificationPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return EventNotificationPreference.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class BroadcastNotificationViewSet(viewsets.ModelViewSet):
    queryset = BroadcastNotification.objects.filter(is_active=True)
    serializer_class = BroadcastNotificationSerializer
    permission_classes = [permissions.IsAdminUser]


class NotificationEventPreferenceViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationEventPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser and self.request.query_params.get("user_id"):
            return NotificationPreference.objects.filter(
                user_id=self.request.query_params["user_id"]
            )
        return NotificationPreference.objects.filter(user=user)
    
    def get_object(self):
        user = self.request.user
        website = self._get_website()
        target_user = self._get_target_user()

        obj, _ = NotificationPreference.objects.get_or_create(
            user=target_user,
            website=website
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
            website=self._get_website(),
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
    
    @action(detail=False, methods=["post"], url_path="apply-profile")
    def apply_profile(self, request):
        from notifications_system.services.preferences import (
            reset_user_preferences,
            assign_default_preferences,
        )

        user = self._get_target_user()
        success = reset_user_preferences(user)
        if success:
            assign_default_preferences(user, self._get_website())
            return Response({"status": "Applied default profile."})
        return Response({"error": "No preferences found to apply."}, status=404)

    @action(detail=False, methods=["post"], url_path="reset")
    def reset_preferences(self, request):
        from notifications_system.services.preferences import (
            reset_user_preferences,
            assign_default_preferences,
        )
        from notifications_system.emails.reset_notification_preferences import (
            send_reset_confirmation_email,
        )

        user = self._get_target_user()
        website = self._get_website()
        success = reset_user_preferences(user)
        
        if success:
            assign_default_preferences(user, website)
            send_reset_confirmation_email(user, website)
            return Response({"status": "Reset and re-applied default profile. Confirmation email sent."})
        
        return Response({"error": "No preferences found to reset."}, status=404)


class RoleNotificationPreferenceViewSet(viewsets.ModelViewSet):
    queryset = RoleNotificationPreference.objects.all()
    serializer_class = RoleNotificationPreferenceSerializer
    permission_classes = [permissions.IsAdminUser]