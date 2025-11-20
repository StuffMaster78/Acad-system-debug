"""
Configuration management for admin/superadmin.
Allows managing all system configurations (pricing, writer configs, discounts, etc.)
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone

from admin_management.permissions import IsAdmin, IsSuperAdmin
from admin_management.models import AdminActivityLog


class PricingConfigManagementViewSet(viewsets.ModelViewSet):
    """Manage pricing configurations."""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get_queryset(self):
        from pricing_configs.models import PricingConfiguration
        queryset = PricingConfiguration.objects.all()
        
        # Filter by website if not superadmin
        if self.request.user.role != 'superadmin':
            website = getattr(self.request.user, 'website', None)
            if website:
                queryset = queryset.filter(website=website)
        
        return queryset
    
    def get_serializer_class(self):
        try:
            from pricing_configs.serializers import PricingConfigurationSerializer
            return PricingConfigurationSerializer
        except ImportError:
            from rest_framework import serializers
            from pricing_configs.models import PricingConfiguration
            
            class PricingConfigurationSerializer(serializers.ModelSerializer):
                class Meta:
                    model = PricingConfiguration
                    fields = '__all__'
            
            return PricingConfigurationSerializer
    
    def perform_create(self, serializer):
        """Create pricing configuration."""
        from rest_framework import serializers as drf_serializers
        website = getattr(self.request.user, 'website', None)
        if not website and self.request.user.role != 'superadmin':
            raise drf_serializers.ValidationError("Website is required.")
        
        if website:
            serializer.save(website=website)
        else:
            serializer.save()
        
        AdminActivityLog.objects.create(
            admin=self.request.user,
            action="Created pricing configuration",
            details=f"Created pricing config for {serializer.instance.website}"
        )
    
    def perform_update(self, serializer):
        """Update pricing configuration."""
        serializer.save()
        
        AdminActivityLog.objects.create(
            admin=self.request.user,
            action="Updated pricing configuration",
            details=f"Updated pricing config for {serializer.instance.website}"
        )


class WriterConfigManagementViewSet(viewsets.ModelViewSet):
    """Manage writer configurations."""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get_queryset(self):
        from writer_management.models.configs import WriterConfig
        queryset = WriterConfig.objects.all()
        
        # Filter by website if not superadmin
        if self.request.user.role != 'superadmin':
            website = getattr(self.request.user, 'website', None)
            if website:
                queryset = queryset.filter(website=website)
        
        return queryset
    
    def get_serializer_class(self):
        try:
            from writer_management.serializers import WriterConfigSerializer
            return WriterConfigSerializer
        except ImportError:
            from rest_framework import serializers
            from writer_management.models.configs import WriterConfig
            
            class WriterConfigSerializer(serializers.ModelSerializer):
                class Meta:
                    model = WriterConfig
                    fields = '__all__'
            
            return WriterConfigSerializer
    
    def perform_create(self, serializer):
        """Create writer configuration."""
        from rest_framework import serializers as drf_serializers
        website = getattr(self.request.user, 'website', None)
        if not website and self.request.user.role != 'superadmin':
            raise drf_serializers.ValidationError("Website is required.")
        
        if website:
            serializer.save(website=website)
        else:
            serializer.save()
        
        AdminActivityLog.objects.create(
            admin=self.request.user,
            action="Created writer configuration",
            details=f"Created writer config for {serializer.instance.website}"
        )
    
    def perform_update(self, serializer):
        """Update writer configuration."""
        serializer.save()
        
        AdminActivityLog.objects.create(
            admin=self.request.user,
            action="Updated writer configuration",
            details=f"Updated writer config for {serializer.instance.website}"
        )


class DiscountConfigManagementViewSet(viewsets.ModelViewSet):
    """Manage discount configurations."""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get_queryset(self):
        from discounts.models.discount_configs import DiscountConfig
        queryset = DiscountConfig.objects.all()
        
        # Filter by website if not superadmin
        if self.request.user.role != 'superadmin':
            website = getattr(self.request.user, 'website', None)
            if website:
                queryset = queryset.filter(website=website)
        
        return queryset
    
    def get_serializer_class(self):
        try:
            from discounts.serializers import DiscountConfigSerializer
            return DiscountConfigSerializer
        except ImportError:
            from rest_framework import serializers
            from discounts.models.discount_configs import DiscountConfig
            
            class DiscountConfigSerializer(serializers.ModelSerializer):
                class Meta:
                    model = DiscountConfig
                    fields = '__all__'
            
            return DiscountConfigSerializer


class NotificationConfigManagementViewSet(viewsets.ModelViewSet):
    """Manage notification preference profiles."""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get_queryset(self):
        from notifications_system.models.notification_preferences import NotificationPreferenceProfile
        queryset = NotificationPreferenceProfile.objects.select_related('website').all()
        
        # Filter by website if not superadmin
        if self.request.user.role != 'superadmin':
            website = getattr(self.request.user, 'website', None)
            if website:
                queryset = queryset.filter(website=website)
        
        # Search by name
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(name__icontains=search)
        
        return queryset.order_by('-is_default', 'name')
    
    def get_serializer_class(self):
        from notifications_system.profile_serializers.notification_profile_serializer import (
            NotificationProfileSerializer,
            NotificationProfileCreateSerializer,
            ApplyProfileSerializer,
            DuplicateProfileSerializer,
        )
        
        if self.action == 'create':
            return NotificationProfileCreateSerializer
        return NotificationProfileSerializer
    
    def perform_create(self, serializer):
        """Create notification profile."""
        from rest_framework import serializers as drf_serializers
        from notifications_system.services.notification_profile_service import (
            NotificationProfileService
        )
        
        website = getattr(self.request.user, 'website', None)
        if not website and self.request.user.role != 'superadmin':
            website = serializer.validated_data.get('website')
            if not website:
                raise drf_serializers.ValidationError("Website is required.")
        
        # Use service to create profile
        profile = NotificationProfileService.create_profile(
            name=serializer.validated_data['name'],
            description=serializer.validated_data.get('description', ''),
            website=website or serializer.validated_data.get('website'),
            default_email=serializer.validated_data.get('default_email', True),
            default_sms=serializer.validated_data.get('default_sms', False),
            default_push=serializer.validated_data.get('default_push', False),
            default_in_app=serializer.validated_data.get('default_in_app', True),
            email_enabled=serializer.validated_data.get('email_enabled', True),
            sms_enabled=serializer.validated_data.get('sms_enabled', False),
            push_enabled=serializer.validated_data.get('push_enabled', False),
            in_app_enabled=serializer.validated_data.get('in_app_enabled', True),
            dnd_enabled=serializer.validated_data.get('dnd_enabled', False),
            dnd_start_hour=serializer.validated_data.get('dnd_start_hour', 22),
            dnd_end_hour=serializer.validated_data.get('dnd_end_hour', 6),
            is_default=serializer.validated_data.get('is_default', False),
        )
        
        AdminActivityLog.objects.create(
            admin=self.request.user,
            action="Created notification profile",
            details=f"Created profile: {profile.name}"
        )
        
        # Set the instance for serializer
        serializer.instance = profile
    
    def perform_update(self, serializer):
        """Update notification profile."""
        from notifications_system.services.notification_profile_service import (
            NotificationProfileService
        )
        
        old_name = serializer.instance.name
        updated_profile = NotificationProfileService.update_profile(
            profile=serializer.instance,
            **serializer.validated_data
        )
        
        AdminActivityLog.objects.create(
            admin=self.request.user,
            action="Updated notification profile",
            details=f"Updated profile: {old_name}"
        )
        
        serializer.instance = updated_profile
    
    def perform_destroy(self, instance):
        """Delete notification profile."""
        name = instance.name
        instance.delete()
        
        AdminActivityLog.objects.create(
            admin=self.request.user,
            action="Deleted notification profile",
            details=f"Deleted profile: {name}"
        )
    
    @action(detail=True, methods=['post'])
    def apply_to_user(self, request, pk=None):
        """Apply this profile to a specific user."""
        from notifications_system.services.notification_profile_service import (
            NotificationProfileService
        )
        from notifications_system.profile_serializers.notification_profile_serializer import (
            ApplyProfileSerializer
        )
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        profile = self.get_object()
        
        serializer = ApplyProfileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user_id = serializer.validated_data.get('user_ids', [None])[0] if serializer.validated_data.get('user_ids') else request.data.get('user_id')
        
        if not user_id:
            return Response(
                {"error": "user_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        override_existing = serializer.validated_data.get('override_existing', False)
        
        result = NotificationProfileService.apply_profile_to_user(
            profile=profile,
            user=user,
            website=profile.website or getattr(request.user, 'website', None),
            override_existing=override_existing
        )
        
        AdminActivityLog.objects.create(
            admin=request.user,
            action="Applied notification profile to user",
            details=f"Applied profile '{profile.name}' to user {user.email}"
        )
        
        return Response(result, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def apply_to_users(self, request, pk=None):
        """Apply this profile to multiple users."""
        from notifications_system.services.notification_profile_service import (
            NotificationProfileService
        )
        from notifications_system.profile_serializers.notification_profile_serializer import (
            ApplyProfileSerializer
        )
        
        profile = self.get_object()
        
        serializer = ApplyProfileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user_ids = serializer.validated_data.get('user_ids', [])
        if not user_ids:
            return Response(
                {"error": "user_ids is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        override_existing = serializer.validated_data.get('override_existing', False)
        
        result = NotificationProfileService.apply_profile_to_users(
            profile=profile,
            user_ids=user_ids,
            website=profile.website or getattr(request.user, 'website', None),
            override_existing=override_existing
        )
        
        AdminActivityLog.objects.create(
            admin=request.user,
            action="Applied notification profile to multiple users",
            details=f"Applied profile '{profile.name}' to {len(user_ids)} users"
        )
        
        return Response(result, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Get statistics for a notification profile."""
        from notifications_system.services.notification_profile_service import (
            NotificationProfileService
        )
        
        profile = self.get_object()
        stats = NotificationProfileService.get_profile_statistics(profile)
        
        return Response(stats, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Duplicate a notification profile."""
        from notifications_system.services.notification_profile_service import (
            NotificationProfileService
        )
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
            website=serializer.validated_data.get('website')
        )
        
        AdminActivityLog.objects.create(
            admin=request.user,
            action="Duplicated notification profile",
            details=f"Duplicated profile '{profile.name}' to '{new_profile.name}'"
        )
        
        return Response(
            NotificationProfileSerializer(new_profile).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=False, methods=['get'])
    def default(self, request):
        """Get the default notification profile."""
        from notifications_system.models.notification_preferences import NotificationPreferenceProfile
        from notifications_system.profile_serializers.notification_profile_serializer import (
            NotificationProfileSerializer
        )
        
        website = getattr(request.user, 'website', None)
        
        try:
            if website:
                default_profile = NotificationPreferenceProfile.objects.get(
                    is_default=True,
                    website=website
                )
            else:
                default_profile = NotificationPreferenceProfile.objects.filter(
                    is_default=True
                ).first()
            
            if not default_profile:
                return Response(
                    {"error": "No default profile found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return Response(
                NotificationProfileSerializer(default_profile).data,
                status=status.HTTP_200_OK
            )
        except NotificationPreferenceProfile.DoesNotExist:
            return Response(
                {"error": "No default profile found"},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get summary of all notification profiles."""
        from notifications_system.models.notification_preferences import NotificationPreferenceProfile
        
        queryset = self.get_queryset()
        
        total_profiles = queryset.count()
        default_profiles = queryset.filter(is_default=True).count()
        
        # Count by channel
        email_enabled_count = queryset.filter(email_enabled=True).count()
        sms_enabled_count = queryset.filter(sms_enabled=True).count()
        push_enabled_count = queryset.filter(push_enabled=True).count()
        in_app_enabled_count = queryset.filter(in_app_enabled=True).count()
        
        # Count by DND
        dnd_enabled_count = queryset.filter(dnd_enabled=True).count()
        
        return Response({
            'total_profiles': total_profiles,
            'default_profiles': default_profiles,
            'channels': {
                'email_enabled': email_enabled_count,
                'sms_enabled': sms_enabled_count,
                'push_enabled': push_enabled_count,
                'in_app_enabled': in_app_enabled_count,
            },
            'dnd_enabled': dnd_enabled_count,
        }, status=status.HTTP_200_OK)


class SystemConfigManagementViewSet(viewsets.ViewSet):
    """Manage various system configurations."""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    @action(detail=False, methods=['get'])
    def list_all_configs(self, request):
        """List all available configuration types."""
        website = getattr(request.user, 'website', None)
        
        configs = {
            'pricing_configs': [],
            'writer_configs': [],
            'discount_configs': [],
            'notification_profiles': [],
        }
        
        # Get pricing configs
        from pricing_configs.models import PricingConfiguration
        pricing_qs = PricingConfiguration.objects.all()
        if website and request.user.role != 'superadmin':
            pricing_qs = pricing_qs.filter(website=website)
        configs['pricing_configs'] = [
            {'id': c.id, 'website': c.website.name, 'base_price': str(c.base_price_per_page)}
            for c in pricing_qs[:10]
        ]
        
        # Get writer configs
        from writer_management.models.configs import WriterConfig
        writer_qs = WriterConfig.objects.all()
        if website and request.user.role != 'superadmin':
            writer_qs = writer_qs.filter(website=website)
        configs['writer_configs'] = [
            {'id': c.id, 'website': c.website.name, 'takes_enabled': c.takes_enabled}
            for c in writer_qs[:10]
        ]
        
        # Get discount configs
        from discounts.models.discount_configs import DiscountConfig
        discount_qs = DiscountConfig.objects.all()
        if website and request.user.role != 'superadmin':
            discount_qs = discount_qs.filter(website=website)
        configs['discount_configs'] = [
            {'id': c.id, 'website': getattr(c, 'website', {}).name if hasattr(c, 'website') else 'N/A'}
            for c in discount_qs[:10]
        ]
        
        # Get notification profiles
        from notifications_system.models.notification_preferences import NotificationPreferenceProfile
        configs['notification_profiles'] = [
            {'id': p.id, 'name': p.name, 'is_default': p.is_default}
            for p in NotificationPreferenceProfile.objects.all()[:10]
        ]
        
        return Response(configs)


class ScreenedWordManagementViewSet(viewsets.ModelViewSet):
    """Manage global screened words for content filtering."""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get_queryset(self):
        from communications.models import ScreenedWord
        return ScreenedWord.objects.all().order_by('word')
    
    def get_serializer_class(self):
        from communications.serializers import ScreenedWordSerializer
        return ScreenedWordSerializer
    
    def perform_create(self, serializer):
        """Create a new screened word."""
        word = serializer.validated_data.get('word', '').strip().lower()
        
        # Check if word already exists (case-insensitive)
        from communications.models import ScreenedWord
        if ScreenedWord.objects.filter(word__iexact=word).exists():
            from rest_framework.exceptions import ValidationError
            raise ValidationError({"word": f"Word '{word}' already exists in the screened words list."})
        
        serializer.save(word=word)
        
        AdminActivityLog.objects.create(
            admin=self.request.user,
            action="Added screened word",
            details=f"Added word: {word}"
        )
    
    def perform_update(self, serializer):
        """Update a screened word."""
        old_word = serializer.instance.word
        new_word = serializer.validated_data.get('word', '').strip().lower()
        
        # Check if new word already exists (excluding current instance)
        from communications.models import ScreenedWord
        if ScreenedWord.objects.filter(word__iexact=new_word).exclude(id=serializer.instance.id).exists():
            from rest_framework.exceptions import ValidationError
            raise ValidationError({"word": f"Word '{new_word}' already exists in the screened words list."})
        
        serializer.save(word=new_word)
        
        AdminActivityLog.objects.create(
            admin=self.request.user,
            action="Updated screened word",
            details=f"Updated word: {old_word} → {new_word}"
        )
    
    def perform_destroy(self, instance):
        """Delete a screened word."""
        word = instance.word
        instance.delete()
        
        AdminActivityLog.objects.create(
            admin=self.request.user,
            action="Removed screened word",
            details=f"Removed word: {word}"
        )
    
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """Bulk create screened words from a list."""
        words = request.data.get('words', [])
        if not isinstance(words, list):
            return Response(
                {"error": "Words must be a list of strings."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        created = []
        errors = []
        
        from communications.models import ScreenedWord
        from communications.serializers import ScreenedWordSerializer
        
        for word in words:
            if not isinstance(word, str) or not word.strip():
                errors.append(f"Invalid word: {word}")
                continue
            
            word = word.strip().lower()
            
            # Check if word already exists
            if ScreenedWord.objects.filter(word__iexact=word).exists():
                errors.append(f"Word '{word}' already exists")
                continue
            
            try:
                screened_word = ScreenedWord.objects.create(word=word)
                created.append(ScreenedWordSerializer(screened_word).data)
            except Exception as e:
                errors.append(f"Error creating word '{word}': {str(e)}")
        
        AdminActivityLog.objects.create(
            admin=request.user,
            action="Bulk added screened words",
            details=f"Added {len(created)} words, {len(errors)} errors"
        )
        
        return Response({
            "created": created,
            "errors": errors,
            "created_count": len(created),
            "error_count": len(errors)
        })
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get statistics about screened words."""
        from communications.models import ScreenedWord, FlaggedMessage
        
        total_words = ScreenedWord.objects.count()
        flagged_messages_count = FlaggedMessage.objects.count()
        
        return Response({
            "total_screened_words": total_words,
            "total_flagged_messages": flagged_messages_count,
            "recent_flagged_count": FlaggedMessage.objects.filter(
                flagged_at__gte=timezone.now() - timezone.timedelta(days=7)
            ).count()
        })


class BlogAuthorPersonaManagementViewSet(viewsets.ModelViewSet):
    """Manage blog author personas/profiles for post attribution."""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get_queryset(self):
        from blog_pages_management._legacy_models import AuthorProfile
        queryset = AuthorProfile.objects.all().select_related('website').order_by('display_order', 'name')
        
        # Filter by website if not superadmin
        if self.request.user.role != 'superadmin':
            website = getattr(self.request.user, 'website', None)
            if website:
                queryset = queryset.filter(website=website)
        
        return queryset
    
    def get_serializer_class(self):
        from blog_pages_management._legacy_serializers import AuthorProfileSerializer
        return AuthorProfileSerializer
    
    def perform_create(self, serializer):
        """Create a new author persona."""
        from rest_framework import serializers as drf_serializers
        from blog_pages_management._legacy_models import AuthorProfile
        website = getattr(self.request.user, 'website', None)
        
        if not website and self.request.user.role != 'superadmin':
            raise drf_serializers.ValidationError("Website is required.")
        
        # Check if name already exists for this website
        name = serializer.validated_data.get('name', '').strip()
        if AuthorProfile.objects.filter(website=website, name__iexact=name).exists():
            raise drf_serializers.ValidationError(
                {"name": f"Author '{name}' already exists for this website."}
            )
        
        serializer.save(website=website)
        
        AdminActivityLog.objects.create(
            admin=self.request.user,
            action="Created blog author persona",
            details=f"Created author: {name} for {website.name if website else 'all websites'}"
        )
    
    def perform_update(self, serializer):
        """Update an author persona."""
        from blog_pages_management._legacy_models import AuthorProfile
        old_name = serializer.instance.name
        new_name = serializer.validated_data.get('name', '').strip()
        
        # Check if new name already exists (excluding current instance)
        website = serializer.instance.website
        if AuthorProfile.objects.filter(website=website, name__iexact=new_name).exclude(id=serializer.instance.id).exists():
            from rest_framework.exceptions import ValidationError
            raise ValidationError(
                {"name": f"Author '{new_name}' already exists for this website."}
            )
        
        serializer.save()
        
        AdminActivityLog.objects.create(
            admin=self.request.user,
            action="Updated blog author persona",
            details=f"Updated author: {old_name} → {new_name}"
        )
    
    def perform_destroy(self, instance):
        """Delete an author persona."""
        name = instance.name
        website_name = instance.website.name if instance.website else 'Unknown'
        instance.delete()
        
        AdminActivityLog.objects.create(
            admin=self.request.user,
            action="Removed blog author persona",
            details=f"Removed author: {name} from {website_name}"
        )
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get statistics about blog authors."""
        from blog_pages_management._legacy_models import AuthorProfile, BlogPost
        
        website = getattr(request.user, 'website', None)
        queryset = AuthorProfile.objects.all()
        
        if website and request.user.role != 'superadmin':
            queryset = queryset.filter(website=website)
        
        total_authors = queryset.count()
        active_authors = queryset.filter(is_active=True).count()
        fake_authors = queryset.filter(is_fake=True).count()
        
        # Get post counts
        blog_queryset = BlogPost.objects.filter(is_deleted=False)
        if website and request.user.role != 'superadmin':
            blog_queryset = blog_queryset.filter(website=website)
        
        total_posts_with_authors = blog_queryset.filter(authors__isnull=False).distinct().count()
        
        return Response({
            "total_authors": total_authors,
            "active_authors": active_authors,
            "fake_authors": fake_authors,
            "total_posts_with_authors": total_posts_with_authors,
            "authors_with_posts": queryset.filter(blog_posts__isnull=False).distinct().count()
        })
    
    @action(detail=True, methods=['get'])
    def posts(self, request, pk=None):
        """Get all posts attributed to this author."""
        author = self.get_object()
        from blog_pages_management._legacy_models import BlogPost
        from blog_pages_management._legacy_serializers import BlogPostSerializer
        
        posts = BlogPost.objects.filter(
            authors=author,
            is_deleted=False
        ).order_by('-created_at')
        
        serializer = BlogPostSerializer(posts, many=True, context={'request': request})
        return Response({
            "author": {
                "id": author.id,
                "name": author.name,
                "website": author.website.name if author.website else None
            },
            "posts": serializer.data,
            "total_posts": posts.count()
        })
    
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """Bulk create author personas."""
        authors_data = request.data.get('authors', [])
        if not isinstance(authors_data, list):
            return Response(
                {"error": "Authors must be a list of objects."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        website = getattr(request.user, 'website', None)
        if not website and request.user.role != 'superadmin':
            return Response(
                {"error": "Website is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        created = []
        errors = []
        
        from blog_pages_management._legacy_models import AuthorProfile
        from blog_pages_management._legacy_serializers import AuthorProfileSerializer
        
        for author_data in authors_data:
            if not isinstance(author_data, dict):
                errors.append(f"Invalid author data: {author_data}")
                continue
            
            name = author_data.get('name', '').strip()
            if not name:
                errors.append("Author name is required")
                continue
            
            # Check if author already exists
            if AuthorProfile.objects.filter(website=website, name__iexact=name).exists():
                errors.append(f"Author '{name}' already exists")
                continue
            
            try:
                author_data['website'] = website.id
                serializer = AuthorProfileSerializer(data=author_data, context={'request': request})
                if serializer.is_valid():
                    author = serializer.save()
                    created.append(AuthorProfileSerializer(author, context={'request': request}).data)
                else:
                    errors.append(f"Validation error for '{name}': {serializer.errors}")
            except Exception as e:
                errors.append(f"Error creating author '{name}': {str(e)}")
        
        AdminActivityLog.objects.create(
            admin=request.user,
            action="Bulk created blog authors",
            details=f"Created {len(created)} authors, {len(errors)} errors"
        )
        
        return Response({
            "created": created,
            "errors": errors,
            "created_count": len(created),
            "error_count": len(errors)
        })

