"""
Comprehensive user management for admin/superadmin.
Allows full CRUD operations for all user roles.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from admin_management.permissions import IsAdmin, IsSuperAdmin
from admin_management.models import AdminActivityLog
from admin_management.serializers import (
    CreateUserSerializer,
    UserSerializer,
    UserDetailSerializer,
    UserUpdateSerializer,
)
from admin_management.managers import AdminManager

User = get_user_model()


class LimitedPagination(PageNumberPagination):
    """Custom pagination class with safety limits to prevent performance issues."""
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 500  # Safety limit to prevent excessive data transfer
    
    def get_paginated_response(self, data):
        """Return paginated response with metadata."""
        from rest_framework.response import Response
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data,
            'current_page': self.page.number,
            'total_pages': self.page.paginator.num_pages,
        })


class ComprehensiveUserManagementViewSet(viewsets.ModelViewSet):
    """
    Comprehensive user management for admin/superadmin.
    Supports CRUD operations for all user roles (writer, editor, support, client).
    """
    permission_classes = [IsAuthenticated, IsAdmin]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['role', 'is_active', 'is_suspended', 'is_blacklisted', 'is_on_probation']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['date_joined', 'last_login', 'username', 'email']
    ordering = ['-date_joined']
    pagination_class = LimitedPagination  # Paginated with safety limits

    def get_queryset(self):
        """Filter users based on admin's website if not superadmin."""
        # Optimize queryset with select_related to prevent N+1 queries
        queryset = User.objects.all().select_related(
            'website',              # Frequently accessed in serializers
            'notification_profile', # Used in serializers
        ).prefetch_related(
            'user_main_profile',    # OneToOne relationship
        )
        
        # Superadmins and admins can see all users
        # (Both should see all users - superadmin sees all, admin sees all from their website or all if no website filter needed)
        if self.request.user.role in ['superadmin', 'admin']:
            # For superadmin: return all users
            if self.request.user.role == 'superadmin':
                return queryset
            
            # For regular admin: see all users (no website filtering)
            # If you want admins to see only their website users, uncomment the lines below
            # website = getattr(self.request.user, 'website', None)
            # if website:
            #     queryset = queryset.filter(website=website)
            return queryset
        
        return queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return UserSerializer
        elif self.action == 'retrieve':
            return UserDetailSerializer
        elif self.action == 'create':
            return CreateUserSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer

    def get_permissions(self):
        """Superadmins can manage all roles, admins can manage non-admin roles."""
        if self.action in ['destroy', 'promote_to_admin']:
            return [IsAuthenticated(), IsSuperAdmin()]
        return [IsAuthenticated(), IsAdmin()]

    def list(self, request, *args, **kwargs):
        """List all users with filtering and pagination."""
        try:
            queryset = self.filter_queryset(self.get_queryset())
            
            # Queryset is already optimized in get_queryset() with select_related/prefetch_related
            # No need to add it again here
            
            # Role filter
            role = request.query_params.get('role')
            if role:
                queryset = queryset.filter(role=role)
            
            # Status filters
            if request.query_params.get('is_suspended') == 'true':
                queryset = queryset.filter(is_suspended=True)
            if request.query_params.get('is_active') == 'false':
                queryset = queryset.filter(is_active=False)
            if request.query_params.get('is_blacklisted') == 'true':
                queryset = queryset.filter(is_blacklisted=True)
            
            # Check if pagination is enabled (pagination_class might be None but DRF settings might have default)
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            # No pagination - return all users as array
            serializer = self.get_serializer(queryset, many=True)
            # Return as array directly (frontend handles both formats)
            return Response(serializer.data)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error listing users: {e}", exc_info=True)
            return Response(
                {"error": "Failed to retrieve users", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def retrieve(self, request, pk=None):
        """Get detailed user information."""
        user = self.get_object()
        serializer = UserDetailSerializer(user)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """Create a new user (writer, editor, support, or client)."""
        serializer = CreateUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        role = serializer.validated_data.get('role')
        if not role:
            return Response(
                {"error": "Role is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Admins cannot create superadmins
        if role == 'superadmin' and request.user.role != 'superadmin':
            return Response(
                {"error": "Only superadmins can create superadmin users."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Admins cannot create other admins (only superadmins can)
        if role == 'admin' and request.user.role != 'superadmin':
            return Response(
                {"error": "Only superadmins can create admin users."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        with transaction.atomic():
            user = serializer.save()
            
            # Assign website if not provided
            if not user.website:
                website = getattr(request.user, 'website', None)
                if website:
                    user.website = website
                    user.save()
            
            # Log activity
            AdminActivityLog.objects.create(
                admin=request.user,
                action=f"Created user {user.username} with role {role}",
                details=f"Created user: {user.email}"
            )
        
        return Response(
            UserDetailSerializer(user).data,
            status=status.HTTP_201_CREATED
        )

    def update(self, request, pk=None):
        """Update user information."""
        user = self.get_object()
        
        # Prevent admins from modifying superadmins
        if user.role == 'superadmin' and request.user.role != 'superadmin':
            return Response(
                {"error": "Cannot modify superadmin users."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = UserUpdateSerializer(user, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        
        with transaction.atomic():
            updated_user = serializer.save()
            
            AdminActivityLog.objects.create(
                admin=request.user,
                action=f"Updated user {updated_user.username}",
                details=f"Updated user: {updated_user.email}"
            )
        
        return Response(UserDetailSerializer(updated_user).data)

    def partial_update(self, request, pk=None):
        """Partially update user information."""
        user = self.get_object()
        
        # Prevent admins from modifying superadmins
        if user.role == 'superadmin' and request.user.role != 'superadmin':
            return Response(
                {"error": "Cannot modify superadmin users."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        with transaction.atomic():
            updated_user = serializer.save()
            
            AdminActivityLog.objects.create(
                admin=request.user,
                action=f"Partially updated user {updated_user.username}",
                details=f"Updated user: {updated_user.email}"
            )
        
        return Response(UserDetailSerializer(updated_user).data)

    def destroy(self, request, pk=None):
        """Delete user (superadmin only)."""
        user = self.get_object()
        
        # Cannot delete superadmin
        if user.role == 'superadmin':
            return Response(
                {"error": "Cannot delete superadmin users."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Cannot delete yourself
        if user.id == request.user.id:
            return Response(
                {"error": "Cannot delete your own account."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        username = user.username
        email = user.email
        
        with transaction.atomic():
            user.delete()
            
            AdminActivityLog.objects.create(
                admin=request.user,
                action=f"Deleted user {username}",
                details=f"Deleted user: {email}"
            )
        
        return Response(
            {"message": f"User {username} deleted successfully."},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'])
    def suspend(self, request, pk=None):
        """Suspend a user."""
        user = self.get_object()
        
        if user.role in ['superadmin', 'admin'] and request.user.role != 'superadmin':
            return Response(
                {"error": "Cannot suspend admin/superadmin users."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        reason = request.data.get('reason', 'No reason provided')
        duration_days = request.data.get('duration_days', 30)
        
        result = AdminManager.suspend_user(request.user, user, reason)
        
        if 'error' in result:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(result, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def unsuspend(self, request, pk=None):
        """Unsuspend a user."""
        user = self.get_object()
        
        if not user.is_suspended:
            return Response(
                {"error": "User is not suspended."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.is_suspended = False
        user.suspension_reason = None
        user.suspension_start_date = None
        user.suspension_end_date = None
        user.save()
        
        AdminActivityLog.objects.create(
            admin=request.user,
            action=f"Unsuspended user {user.username}",
            details=f"Unsuspended user: {user.email}"
        )
        
        return Response(
            {"message": f"User {user.username} has been unsuspended."},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'], permission_classes=[IsSuperAdmin])
    def blacklist(self, request, pk=None):
        """Blacklist a user (superadmin only)."""
        user = self.get_object()
        
        if user.role in ['superadmin', 'admin']:
            return Response(
                {"error": "Cannot blacklist admin/superadmin users."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        reason = request.data.get('reason', 'No reason provided')
        result = AdminManager.blacklist_user(request.user, user, reason)
        
        return Response(result, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def place_on_probation(self, request, pk=None):
        """Place user on probation."""
        user = self.get_object()
        
        if user.role == 'admin':
            return Response(
                {"error": "Cannot place admins on probation."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        reason = request.data.get('reason', 'No reason provided')
        duration_days = int(request.data.get('duration_days', 30))
        
        result = AdminManager.place_user_on_probation(
            request.user, user, reason, duration_days
        )
        
        if 'error' in result:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(result, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def remove_from_probation(self, request, pk=None):
        """Remove user from probation."""
        user = self.get_object()
        
        if not user.is_on_probation:
            return Response(
                {"error": "User is not on probation."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        result = AdminManager.remove_user_from_probation(request.user, user)
        
        return Response(result, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[IsSuperAdmin])
    def change_role(self, request, pk=None):
        """Change user's role (superadmin only)."""
        user = self.get_object()
        new_role = request.data.get('role')
        
        if not new_role:
            return Response(
                {"error": "Role is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if new_role not in ['client', 'writer', 'editor', 'support', 'admin']:
            return Response(
                {"error": "Invalid role."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Cannot change superadmin role
        if user.role == 'superadmin':
            return Response(
                {"error": "Cannot change superadmin role."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        old_role = user.role
        user.role = new_role
        user.save()
        
        AdminActivityLog.objects.create(
            admin=request.user,
            action=f"Changed role of {user.username} from {old_role} to {new_role}",
            details=f"Changed role: {user.email}"
        )
        
        return Response(
            {
                "message": f"User {user.username} role changed from {old_role} to {new_role}.",
                "user": UserDetailSerializer(user).data
            },
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'], permission_classes=[IsSuperAdmin])
    def promote_to_admin(self, request, pk=None):
        """Promote user to admin (superadmin only)."""
        user = self.get_object()
        
        if user.role == 'superadmin':
            return Response(
                {"error": "User is already a superadmin."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if user.role == 'admin':
            return Response(
                {"error": "User is already an admin."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        old_role = user.role
        user.role = 'admin'
        user.is_staff = True
        user.save()
        
        # Create admin profile
        from admin_management.models import AdminProfile
        AdminProfile.objects.get_or_create(user=user)
        
        AdminActivityLog.objects.create(
            admin=request.user,
            action=f"Promoted {user.username} from {old_role} to admin",
            details=f"Promoted user: {user.email}"
        )
        
        return Response(
            {
                "message": f"User {user.username} promoted to admin.",
                "user": UserDetailSerializer(user).data
            },
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'])
    def reset_password(self, request, pk=None):
        """Reset user's password (admin generates new temp password)."""
        user = self.get_object()
        
        import secrets
        import string
        temp_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
        
        user.set_password(temp_password)
        user.save()
        
        AdminActivityLog.objects.create(
            admin=request.user,
            action=f"Reset password for {user.username}",
            details=f"Password reset for: {user.email}"
        )
        
        # Send email notification (optional)
        try:
            from django.core.mail import send_mail
            from django.conf import settings
            send_mail(
                subject="Password Reset",
                message=f"Your password has been reset by an admin. Your new temporary password is: {temp_password}\n\nPlease log in and change your password immediately.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,
            )
        except Exception:
            pass
        
        return Response(
            {
                "message": f"Password reset for {user.username}. Temporary password sent to email.",
                "temp_password": temp_password  # Only return in development
            },
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get user statistics."""
        try:
            queryset = self.get_queryset()
            
            stats = {
                'total_users': queryset.count(),
                'by_role': {
                    role: queryset.filter(role=role).count()
                    for role in ['client', 'writer', 'editor', 'support', 'admin', 'superadmin']
                },
                'active_users': queryset.filter(is_active=True).count(),
                'suspended_users': queryset.filter(is_suspended=True).count(),
                'blacklisted_users': queryset.filter(is_blacklisted=True).count(),
                'on_probation': queryset.filter(is_on_probation=True).count(),
            }
            
            return Response(stats, status=status.HTTP_200_OK)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error getting user stats: {e}", exc_info=True)
            return Response(
                {"error": "Failed to retrieve user statistics", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def bulk_activate(self, request):
        """Bulk activate users."""
        user_ids = request.data.get('user_ids', [])
        if not user_ids:
            return Response(
                {"error": "No user IDs provided."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset()
        users = queryset.filter(id__in=user_ids)
        
        # Prevent activating superadmins unless current user is superadmin
        if request.user.role != 'superadmin':
            users = users.exclude(role='superadmin')
        
        activated_count = 0
        with transaction.atomic():
            for user in users:
                if not user.is_active:
                    user.is_active = True
                    user.save()
                    activated_count += 1
                    
                    AdminActivityLog.objects.create(
                        admin=request.user,
                        action=f"Activated user {user.username}",
                        details=f"Bulk activated user: {user.email}"
                    )
        
        return Response({
            "message": f"Activated {activated_count} user(s).",
            "activated_count": activated_count
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'])
    def bulk_suspend(self, request):
        """Bulk suspend users."""
        user_ids = request.data.get('user_ids', [])
        reason = request.data.get('reason', 'Bulk suspension')
        duration_days = request.data.get('duration_days', 30)
        
        if not user_ids:
            return Response(
                {"error": "No user IDs provided."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset()
        users = queryset.filter(id__in=user_ids)
        
        # Prevent suspending superadmins/admins unless current user is superadmin
        if request.user.role != 'superadmin':
            users = users.exclude(role__in=['superadmin', 'admin'])
        
        suspended_count = 0
        with transaction.atomic():
            for user in users:
                if not user.is_suspended:
                    result = AdminManager.suspend_user(request.user, user, reason)
                    if 'error' not in result:
                        suspended_count += 1
        
        return Response({
            "message": f"Suspended {suspended_count} user(s).",
            "suspended_count": suspended_count
        }, status=status.HTTP_200_OK)

