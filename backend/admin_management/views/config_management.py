"""
Configuration management for admin/superadmin.
Allows managing all system configurations (pricing, writer configs, discounts, etc.)
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from admin_management.permissions import IsAdmin, IsSuperAdmin
from admin_management.models import AdminActivityLog


# ---------------------------------------------------------------------------
# Shared mixin
# ---------------------------------------------------------------------------

class WebsiteFilteredMixin:
    """
    Filters querysets to the requesting user's website.
    Superadmins see all websites.
    """

    def _get_user_website(self):
        return getattr(self.request.user, 'website', None)

    def _is_superadmin(self):
        return self.request.user.role == 'superadmin'

    def get_website_filtered_queryset(self, queryset):
        if not self._is_superadmin():
            website = self._get_user_website()
            if website:
                queryset = queryset.filter(website=website)
        return queryset

    def perform_create_with_website(self, serializer, action_label):
        website = self._get_user_website()
        if not website and not self._is_superadmin():
            raise ValidationError("Website is required.")
        kwargs = {'website': website} if website else {}
        serializer.save(**kwargs)
        AdminActivityLog.objects.create(
            admin=self.request.user,
            action=f"Created {action_label}",
            details=f"Created {action_label} for {serializer.instance.website}",
        )

    def perform_update_with_log(self, serializer, action_label):
        serializer.save()
        AdminActivityLog.objects.create(
            admin=self.request.user,
            action=f"Updated {action_label}",
            details=f"Updated {action_label} for {serializer.instance.website}",
        )


# ---------------------------------------------------------------------------
# Pricing
# ---------------------------------------------------------------------------

class PricingConfigManagementViewSet(WebsiteFilteredMixin, viewsets.ModelViewSet):
    """Manage pricing configurations."""
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_queryset(self):
        from order_pricing_core.models import PricingConfiguration
        return self.get_website_filtered_queryset(PricingConfiguration.objects.all())

    def get_serializer_class(self):
        from order_pricing_core.serializers import PricingConfigurationSerializer
        return PricingConfigurationSerializer

    def perform_create(self, serializer):
        self.perform_create_with_website(serializer, "pricing configuration")

    def perform_update(self, serializer):
        self.perform_update_with_log(serializer, "pricing configuration")


# ---------------------------------------------------------------------------
# Writer config
# ---------------------------------------------------------------------------

class WriterConfigManagementViewSet(WebsiteFilteredMixin, viewsets.ModelViewSet):
    """Manage writer configurations."""
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_queryset(self):
        from writer_management.models.configs import WriterConfig
        return self.get_website_filtered_queryset(WriterConfig.objects.all())

    def get_serializer_class(self):
        from writer_management.serializers import WriterConfigSerializer
        return WriterConfigSerializer

    def perform_create(self, serializer):
        self.perform_create_with_website(serializer, "writer configuration")

    def perform_update(self, serializer):
        self.perform_update_with_log(serializer, "writer configuration")


# ---------------------------------------------------------------------------
# Discount config
# ---------------------------------------------------------------------------

class DiscountConfigManagementViewSet(WebsiteFilteredMixin, viewsets.ModelViewSet):
    """Manage discount configurations."""
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_queryset(self):
        from discounts.models.discount_configs import DiscountConfig
        return self.get_website_filtered_queryset(DiscountConfig.objects.all())

    def get_serializer_class(self):
        from discounts.serializers import DiscountConfigSerializer
        return DiscountConfigSerializer

    def perform_create(self, serializer):
        self.perform_create_with_website(serializer, "discount configuration")

    def perform_update(self, serializer):
        self.perform_update_with_log(serializer, "discount configuration")


# ---------------------------------------------------------------------------
# Notification profiles
# ---------------------------------------------------------------------------

class NotificationConfigManagementViewSet(WebsiteFilteredMixin, viewsets.ModelViewSet):
    """Manage notification preference profiles."""
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_queryset(self):
        from notifications_system.models.notification_preferences import NotificationPreferenceProfile
        queryset = NotificationPreferenceProfile.objects.select_related('website').all()
        queryset = self.get_website_filtered_queryset(queryset)

        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)

        return queryset.order_by('-is_default', 'name')

    def get_serializer_class(self):
        from notifications_system.profile_serializers.notification_profile_serializer import (
            NotificationProfileSerializer,
            NotificationProfileCreateSerializer,
        )
        if self.action == 'create':
            return NotificationProfileCreateSerializer
        return NotificationProfileSerializer

    def perform_create(self, serializer):
        from notifications_system.services.notification_profile_service import NotificationProfileService

        website = self._get_user_website()
        if not website and not self._is_superadmin():
            website = serializer.validated_data.get('website')
            if not website:
                raise ValidationError("Website is required.")

        profile = NotificationProfileService.create_profile(
            website=website or serializer.validated_data.get('website'),
            **{k: v for k, v in serializer.validated_data.items() if k != 'website'},
        )

        AdminActivityLog.objects.create(
            admin=self.request.user,
            action="Created notification profile",
            details=f"Created profile: {profile.name}",
        )
        serializer.instance = profile

    def perform_update(self, serializer):
        from notifications_system.services.notification_profile_service import NotificationProfileService

        old_name = serializer.instance.name
        updated_profile = NotificationProfileService.update_profile(
            profile=serializer.instance,
            **serializer.validated_data,
        )

        AdminActivityLog.objects.create(
            admin=self.request.user,
            action="Updated notification profile",
            details=f"Updated profile: {old_name}",
        )
        serializer.instance = updated_profile

    def perform_destroy(self, instance):
        name = instance.name
        instance.delete()
        AdminActivityLog.objects.create(
            admin=self.request.user,
            action="Deleted notification profile",
            details=f"Deleted profile: {name}",
        )

    @action(detail=True, methods=['post'])
    def apply_to_user(self, request, pk=None):
        """Apply this profile to a single user."""
        from notifications_system.services.notification_profile_service import NotificationProfileService
        from notifications_system.profile_serializers.notification_profile_serializer import ApplyProfileSerializer
        from django.contrib.auth import get_user_model

        profile = self.get_object()
        serializer = ApplyProfileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = request.data.get('user_id')
        if not user_id:
            return Response({"error": "user_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        User = get_user_model()
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        result = NotificationProfileService.apply_profile_to_user(
            profile=profile,
            user=user,
            website=profile.website or self._get_user_website(),
            override_existing=serializer.validated_data.get('override_existing', False),
        )

        AdminActivityLog.objects.create(
            admin=request.user,
            action="Applied notification profile to user",
            details=f"Applied profile '{profile.name}' to user {user.email}",
        )
        return Response(result, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def apply_to_users(self, request, pk=None):
        """Apply this profile to multiple users."""
        from notifications_system.services.notification_profile_service import NotificationProfileService
        from notifications_system.profile_serializers.notification_profile_serializer import ApplyProfileSerializer

        profile = self.get_object()
        serializer = ApplyProfileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_ids = serializer.validated_data.get('user_ids', [])
        if not user_ids:
            return Response({"error": "user_ids is required."}, status=status.HTTP_400_BAD_REQUEST)

        result = NotificationProfileService.apply_profile_to_users(
            profile=profile,
            user_ids=user_ids,
            website=profile.website or self._get_user_website(),
            override_existing=serializer.validated_data.get('override_existing', False),
        )

        AdminActivityLog.objects.create(
            admin=request.user,
            action="Applied notification profile to multiple users",
            details=f"Applied profile '{profile.name}' to {len(user_ids)} users",
        )
        return Response(result, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Get statistics for a notification profile."""
        from notifications_system.services.notification_profile_service import NotificationProfileService
        profile = self.get_object()
        return Response(
            NotificationProfileService.get_profile_statistics(profile),
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Duplicate a notification profile."""
        from notifications_system.services.notification_profile_service import NotificationProfileService
        from notifications_system.profile_serializers.notification_profile_serializer import (
            DuplicateProfileSerializer,
            NotificationProfileSerializer,
        )

        profile = self.get_object()
        serializer = DuplicateProfileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_profile = NotificationProfileService.duplicate_profile(
            source_profile=profile,
            new_name=serializer.validated_data['new_name'],
            website=serializer.validated_data.get('website'),
        )

        AdminActivityLog.objects.create(
            admin=request.user,
            action="Duplicated notification profile",
            details=f"Duplicated '{profile.name}' to '{new_profile.name}'",
        )
        return Response(
            NotificationProfileSerializer(new_profile).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=['get'])
    def default(self, request):
        """Get the default notification profile for the current website."""
        from notifications_system.models.notification_preferences import NotificationPreferenceProfile
        from notifications_system.profile_serializers.notification_profile_serializer import (
            NotificationProfileSerializer,
        )

        website = self._get_user_website()
        qs = NotificationPreferenceProfile.objects.filter(is_default=True)
        if website:
            qs = qs.filter(website=website)

        profile = qs.first()
        if not profile:
            return Response({"error": "No default profile found."}, status=status.HTTP_404_NOT_FOUND)

        return Response(NotificationProfileSerializer(profile).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get a summary count of notification profiles by channel and DND."""
        queryset = self.get_queryset()
        return Response({
            'total_profiles': queryset.count(),
            'default_profiles': queryset.filter(is_default=True).count(),
            'channels': {
                'email_enabled': queryset.filter(email_enabled=True).count(),
                'sms_enabled': queryset.filter(sms_enabled=True).count(),
                'push_enabled': queryset.filter(push_enabled=True).count(),
                'in_app_enabled': queryset.filter(in_app_enabled=True).count(),
            },
            'dnd_enabled': queryset.filter(dnd_enabled=True).count(),
        }, status=status.HTTP_200_OK)


# ---------------------------------------------------------------------------
# System config overview
# ---------------------------------------------------------------------------

class SystemConfigManagementViewSet(viewsets.ViewSet):
    """Read-only overview of all configuration types."""
    permission_classes = [IsAuthenticated, IsAdmin]

    def _website_filter(self, queryset, website):
        if website and self.request.user.role != 'superadmin':
            return queryset.filter(website=website)
        return queryset

    @action(detail=False, methods=['get'])
    def list_all_configs(self, request):
        """Return a summarised list of all config types."""
        from order_pricing_core.models import PricingConfiguration
        from order_pricing_core.serializers import PricingConfigurationSerializer
        from writer_management.models.configs import WriterConfig
        from writer_management.serializers import WriterConfigSerializer
        from discounts.models.discount_configs import DiscountConfig
        from discounts.serializers import DiscountConfigSerializer
        from notifications_system.models.notification_preferences import NotificationPreferenceProfile
        from notifications_system.profile_serializers.notification_profile_serializer import (
            NotificationProfileSerializer,
        )

        website = getattr(request.user, 'website', None)

        return Response({
            'pricing_configs': PricingConfigurationSerializer(
                self._website_filter(PricingConfiguration.objects.all(), website)[:10], many=True
            ).data,
            'writer_configs': WriterConfigSerializer(
                self._website_filter(WriterConfig.objects.all(), website)[:10], many=True
            ).data,
            'discount_configs': DiscountConfigSerializer(
                self._website_filter(DiscountConfig.objects.all(), website)[:10], many=True
            ).data,
            'notification_profiles': NotificationProfileSerializer(
                NotificationPreferenceProfile.objects.all()[:10], many=True
            ).data,
        })


# ---------------------------------------------------------------------------
# Screened words
# ---------------------------------------------------------------------------

class ScreenedWordManagementViewSet(viewsets.ModelViewSet):
    """Manage global screened words for content filtering."""
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_queryset(self):
        from communications.models import ScreenedWord
        return ScreenedWord.objects.all().order_by('word')

    def get_serializer_class(self):
        from communications.serializers import ScreenedWordSerializer
        return ScreenedWordSerializer

    def _check_word_unique(self, word, exclude_id=None):
        from communications.models import ScreenedWord
        qs = ScreenedWord.objects.filter(word__iexact=word)
        if exclude_id:
            qs = qs.exclude(id=exclude_id)
        if qs.exists():
            raise ValidationError({"word": f"'{word}' already exists in the screened words list."})

    def perform_create(self, serializer):
        word = serializer.validated_data.get('word', '').strip().lower()
        self._check_word_unique(word)
        serializer.save(word=word)
        AdminActivityLog.objects.create(
            admin=self.request.user,
            action=f"Added screened word: {word}",
        )

    def perform_update(self, serializer):
        old_word = serializer.instance.word
        new_word = serializer.validated_data.get('word', '').strip().lower()
        self._check_word_unique(new_word, exclude_id=serializer.instance.id)
        serializer.save(word=new_word)
        AdminActivityLog.objects.create(
            admin=self.request.user,
            action=f"Updated screened word: {old_word} → {new_word}",
        )

    def perform_destroy(self, instance):
        word = instance.word
        instance.delete()
        AdminActivityLog.objects.create(
            admin=self.request.user,
            action=f"Removed screened word: {word}",
        )

    @action(detail=False, methods=['post'])
    @transaction.atomic
    def bulk_create(self, request):
        """Bulk create screened words. Rolls back entirely on unexpected errors."""
        from communications.models import ScreenedWord
        from communications.serializers import ScreenedWordSerializer

        words = request.data.get('words', [])
        if not isinstance(words, list):
            return Response({"error": "words must be a list of strings."}, status=status.HTTP_400_BAD_REQUEST)

        created = []
        errors = []

        for raw in words:
            if not isinstance(raw, str) or not raw.strip():
                errors.append(f"Invalid entry: {raw}")
                continue

            word = raw.strip().lower()

            if ScreenedWord.objects.filter(word__iexact=word).exists():
                errors.append(f"'{word}' already exists.")
                continue

            screened_word = ScreenedWord.objects.create(word=word)
            created.append(ScreenedWordSerializer(screened_word).data)

        AdminActivityLog.objects.create(
            admin=request.user,
            action=f"Bulk added screened words: {len(created)} created, {len(errors)} errors",
        )
        return Response({
            "created": created,
            "errors": errors,
            "created_count": len(created),
            "error_count": len(errors),
        })

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Screened word and flagged message counts."""
        from communications.models import ScreenedWord, FlaggedMessage
        return Response({
            "total_screened_words": ScreenedWord.objects.count(),
            "total_flagged_messages": FlaggedMessage.objects.count(),
            "flagged_last_7_days": FlaggedMessage.objects.filter(
                flagged_at__gte=timezone.now() - timezone.timedelta(days=7)
            ).count(),
        })


# ---------------------------------------------------------------------------
# Blog author personas
# ---------------------------------------------------------------------------

class BlogAuthorPersonaManagementViewSet(WebsiteFilteredMixin, viewsets.ModelViewSet):
    """Manage blog author personas for post attribution."""
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_queryset(self):
        from blog_pages_management.models import AuthorProfile
        queryset = AuthorProfile.objects.select_related('website').order_by('display_order', 'name')
        return self.get_website_filtered_queryset(queryset)

    def get_serializer_class(self):
        from blog_pages_management.serializers import AuthorProfileSerializer
        return AuthorProfileSerializer

    def _check_author_unique(self, name, website, exclude_id=None):
        from blog_pages_management.models import AuthorProfile
        qs = AuthorProfile.objects.filter(website=website, name__iexact=name)
        if exclude_id:
            qs = qs.exclude(id=exclude_id)
        if qs.exists():
            raise ValidationError({"name": f"Author '{name}' already exists for this website."})

    def perform_create(self, serializer):
        website = self._get_user_website()
        if not website and not self._is_superadmin():
            raise ValidationError("Website is required.")

        name = serializer.validated_data.get('name', '').strip()
        self._check_author_unique(name, website)
        serializer.save(website=website)

        AdminActivityLog.objects.create(
            admin=self.request.user,
            action="Created blog author persona",
            details=f"Created author: {name} for {website.name if website else 'all websites'}",
        )

    def perform_update(self, serializer):
        old_name = serializer.instance.name
        new_name = serializer.validated_data.get('name', '').strip()
        self._check_author_unique(new_name, serializer.instance.website, exclude_id=serializer.instance.id)
        serializer.save()

        AdminActivityLog.objects.create(
            admin=self.request.user,
            action="Updated blog author persona",
            details=f"Updated author: {old_name} → {new_name}",
        )

    def perform_destroy(self, instance):
        name = instance.name
        website_name = instance.website.name if instance.website else 'Unknown'
        instance.delete()
        AdminActivityLog.objects.create(
            admin=self.request.user,
            action="Removed blog author persona",
            details=f"Removed author: {name} from {website_name}",
        )

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Author and post attribution statistics."""
        from blog_pages_management.models import AuthorProfile, BlogPost

        queryset = self.get_queryset()
        blog_qs = BlogPost.objects.filter(is_deleted=False)
        if not self._is_superadmin():
            website = self._get_user_website()
            if website:
                blog_qs = blog_qs.filter(website=website)

        return Response({
            "total_authors": queryset.count(),
            "active_authors": queryset.filter(is_active=True).count(),
            "fake_authors": queryset.filter(is_fake=True).count(),
            "total_posts_with_authors": blog_qs.filter(authors__isnull=False).distinct().count(),
            "authors_with_posts": queryset.filter(blog_posts__isnull=False).distinct().count(),
        })

    @action(detail=True, methods=['get'])
    def posts(self, request, pk=None):
        """All posts attributed to this author."""
        from blog_pages_management.models import BlogPost
        from blog_pages_management.serializers import BlogPostSerializer

        author = self.get_object()
        posts = BlogPost.objects.filter(authors=author, is_deleted=False).order_by('-created_at')

        return Response({
            "author": {
                "id": author.id,
                "name": author.name,
                "website": author.website.name if author.website else None,
            },
            "posts": BlogPostSerializer(posts, many=True, context={'request': request}).data,
            "total_posts": posts.count(),
        })

    @action(detail=False, methods=['post'])
    @transaction.atomic
    def bulk_create(self, request):
        """Bulk create author personas. Atomic — all or nothing on hard errors."""
        from blog_pages_management.models import AuthorProfile
        from blog_pages_management.serializers import AuthorProfileSerializer

        authors_data = request.data.get('authors', [])
        if not isinstance(authors_data, list):
            return Response({"error": "authors must be a list of objects."}, status=status.HTTP_400_BAD_REQUEST)

        website = self._get_user_website()
        if not website and not self._is_superadmin():
            return Response({"error": "Website is required."}, status=status.HTTP_400_BAD_REQUEST)

        created = []
        errors = []

        for entry in authors_data:
            if not isinstance(entry, dict):
                errors.append(f"Invalid entry: {entry}")
                continue

            name = entry.get('name', '').strip()
            if not name:
                errors.append("Author name is required.")
                continue

            if AuthorProfile.objects.filter(website=website, name__iexact=name).exists():
                errors.append(f"Author '{name}' already exists.")
                continue

            entry['website'] = website.id
            serializer = AuthorProfileSerializer(data=entry, context={'request': request})
            if serializer.is_valid():
                author = serializer.save()
                created.append(AuthorProfileSerializer(author, context={'request': request}).data)
            else:
                errors.append(f"Validation error for '{name}': {serializer.errors}")

        AdminActivityLog.objects.create(
            admin=request.user,
            action="Bulk created blog authors",
            details=f"Created {len(created)}, {len(errors)} errors",
        )
        return Response({
            "created": created,
            "errors": errors,
            "created_count": len(created),
            "error_count": len(errors),
        })