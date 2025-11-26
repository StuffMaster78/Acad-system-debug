from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import action
from rest_framework.response import Response

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Count
from django.contrib.auth.models import Group

from notifications_system.models.notification_profile import NotificationProfile, NotificationGroupProfile
from notifications_system.models.notification_group import NotificationGroup
from notifications_system.serializers import (
    NotificationProfileSerializer,
    NotificationGroupProfileSerializer,
    NotificationGroupSerializer
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


class NotificationGroupViewSet(viewsets.ModelViewSet):
    """
    CRUD for notification groups.
    """
    queryset = NotificationGroup.objects.all().select_related('website').prefetch_related('users')
    serializer_class = NotificationGroupSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # Filter by website if provided
        website_id = self.request.query_params.get('website_id')
        if website_id:
            queryset = queryset.filter(website_id=website_id)
        # Search by name
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(Q(name__icontains=search) | Q(description__icontains=search))
        return queryset.order_by('-created_at')
    
    @action(detail=True, methods=['post'], url_path='add-users')
    def add_users(self, request, pk=None):
        """Add users to a notification group."""
        group = self.get_object()
        user_ids = request.data.get('user_ids', [])
        if not user_ids:
            return Response({"error": "user_ids required"}, status=status.HTTP_400_BAD_REQUEST)
        
        from django.contrib.auth import get_user_model
        User = get_user_model()
        users = User.objects.filter(id__in=user_ids)
        group.users.add(*users)
        return Response({"status": "Users added", "count": len(users)})
    
    @action(detail=True, methods=['post'], url_path='remove-users')
    def remove_users(self, request, pk=None):
        """Remove users from a notification group."""
        group = self.get_object()
        user_ids = request.data.get('user_ids', [])
        if not user_ids:
            return Response({"error": "user_ids required"}, status=status.HTTP_400_BAD_REQUEST)
        
        group.users.remove(*user_ids)
        return Response({"status": "Users removed"})


class NotificationGroupProfileViewSet(viewsets.ModelViewSet):
    """
    CRUD for notification group profiles.
    """
    queryset = NotificationGroupProfile.objects.all().select_related(
        'website', 'profile', 'group'
    ).prefetch_related('users')
    serializer_class = NotificationGroupProfileSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # Filter by website if provided
        website_id = self.request.query_params.get('website_id')
        if website_id:
            queryset = queryset.filter(website_id=website_id)
        # Filter by group
        group_id = self.request.query_params.get('group_id')
        if group_id:
            queryset = queryset.filter(group_id=group_id)
        # Filter by role
        role = self.request.query_params.get('role')
        if role:
            queryset = queryset.filter(roles=role)
        # Search
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(Q(name__icontains=search) | Q(role_slug__icontains=search))
        return queryset.order_by('-created_at')
    
    @action(detail=True, methods=['post'], url_path='add-users')
    def add_users(self, request, pk=None):
        """Add users to a group profile."""
        profile = self.get_object()
        user_ids = request.data.get('user_ids', [])
        if not user_ids:
            return Response({"error": "user_ids required"}, status=status.HTTP_400_BAD_REQUEST)
        
        from django.contrib.auth import get_user_model
        User = get_user_model()
        users = User.objects.filter(id__in=user_ids)
        profile.users.add(*users)
        return Response({"status": "Users added", "count": len(users)})
    
    @action(detail=True, methods=['post'], url_path='remove-users')
    def remove_users(self, request, pk=None):
        """Remove users from a group profile."""
        profile = self.get_object()
        user_ids = request.data.get('user_ids', [])
        if not user_ids:
            return Response({"error": "user_ids required"}, status=status.HTTP_400_BAD_REQUEST)
        
        profile.users.remove(*user_ids)
        return Response({"status": "Users removed"})
    
    @action(detail=True, methods=['post'], url_path='set-default')
    def set_default(self, request, pk=None):
        """Set this profile as the default for its website/group."""
        profile = self.get_object()
        # Unset other defaults for the same website/group
        NotificationGroupProfile.objects.filter(
            website=profile.website,
            group=profile.group
        ).exclude(id=profile.id).update(is_default=False)
        profile.is_default = True
        profile.save()
        return Response({"status": "Default profile set"})