import logging
from django.contrib.auth import authenticate, login, logout
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django.conf import settings
from rest_framework.decorators import action, throttle_classes
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.contrib.postgres.search import TrigramSimilarity  # Fuzzy Search
from rest_framework.pagination import PageNumberPagination
from users.utils import send_deletion_confirmation_email, send_unlock_email, send_security_alert
from django.core.mail import send_mail
from users.models import (
    User, ProfileUpdateRequest,
)
from authentication.models import (
    AccountDeletionRequest, SecureToken, UserSession
)
from users.utils import (
    notify_mfa_enabled, notify_mfa_disabled, notify_mfa_reset,
    send_mfa_recovery_email,log_audit_action
)

from .serializers import (
    UserActivitySerializer,
    ClientProfileSerializer,
    WriterProfileSerializer,
    AdminProfileSerializer,
    SuperadminProfileSerializer,
    EditorProfileSerializer,
    SupportProfileSerializer,
    UserProfileSerializer,
    ImpersonateSerializer,
)
from client_management.models import ClientProfile
from writer_management.models import WriterProfile
from editor_management.models import EditorProfile
from support_management.models import SupportProfile
from superadmin_management.models import SuperadminProfile
from admin_management.models import AdminProfile
from websites.models import Website
from users.utils import get_client_ip, generate_otp, send_otp_email, send_otp_sms, verify_totp
from django.utils.timezone import now, timedelta
from users.utils import get_client_ip, get_device_info
from django.http import JsonResponse
from datetime import timedelta
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.exceptions import InvalidToken
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
import base64
from django.contrib.sessions.models import Session
from django.contrib.sessions.backends.db import SessionStore
from django.utils.timezone import now, timedelta
import base64
from .utils import generate_totp_qr_code, send_unlock_email
from users.utils import store_active_token, revoke_token, is_token_revoked
from io import BytesIO
from authentication.throttling import LoginRateThrottle, MagicLinkThrottle
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ViewSet
import uuid
from rest_framework.exceptions import APIException

logger = logging.getLogger(__name__)

def check_admin_access(user):
    if not user.is_authenticated or user.role not in ["admin", "superadmin"]:
        raise PermissionDenied("You do not have admin access.")



class CustomUserPagination(PageNumberPagination):
    """Pagination settings for user listings."""
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class UserViewSet(viewsets.ModelViewSet):
    """Handles user-related operations including profile, impersonation, and activity"""
    
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = CustomUserPagination  # Enable pagination
    serializer_class = UserProfileSerializer  # Default serializer

    

    def get_serializer_class(self):
        """Dynamically return the correct serializer based on the user role."""
        role_serializers = {
            "client": ClientProfileSerializer,
            "writer": WriterProfileSerializer,
            "editor": EditorProfileSerializer,
            "support": SupportProfileSerializer,
            "admin": AdminProfileSerializer,
            "superadmin": SuperadminProfileSerializer,
        }
        role = self.request.user.role
        if role not in role_serializers:
            # Log a warning or raise an exception here if the role is unexpected
            raise ValueError(f"Unknown role: {role}")
    
        return role_serializers.get(role, UserProfileSerializer)  # Fallback if the role is valid but not mapped

    # user = User.objects.select_related("writer_profile", "client_profile").get(id=request.user.id)


    def get_queryset(self):
        """Restrict access based on user roles."""
        user = self.request.user

        if user.role in ["client", "writer"]:
            return User.objects.filter(id=user.id)  # Clients & Writers only see themselves

        elif user.role == "editor":
            return User.objects.filter(role="writer")  # Editors only see writers

        elif user.role == "support":
            return User.objects.filter(role="client")  # Support staff only see clients

        return User.objects.all()  # Admins & Superadmins see all users



    def list(self, request, *args, **kwargs):
        """List users with filtering, search, sorting, and pagination."""
        
    
        check_admin_access(request.user)

        # Filters
        role = request.query_params.get("role")
        search_query = request.query_params.get("search")
        sort_by = request.query_params.get("sort")

        # Validate role filter
        allowed_roles = ["client", "writer", "editor", "support", "admin", "superadmin"]
        if role and role not in allowed_roles:
            return Response({"error": "Invalid role"}, status=status.HTTP_400_BAD_REQUEST)

        # Get queryset based on role

        # Get queryset based on role
        users = User.objects.filter(role=role) if role else User.objects.all()

        # Apply search filter if provided
        direct_matches = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query)
        )

        if not direct_matches.exists():
            users = users.annotate(similarity=TrigramSimilarity("username", search_query)).filter(similarity__gt=0.3)

        users = users.order_by("-similarity")

        # Sorting
        sorting_options = {
            "newest": "-date_joined",
            "oldest": "date_joined",
            "alphabetical": "username",
            "reverse-alphabetical": "-username",
            "last-active": "-last_active",
        }
        if sort_by in sorting_options:
            users = users.order_by(sorting_options[sort_by])

        # Paginate results
        paginator = self.pagination_class()
        paginated_users = paginator.paginate_queryset(users, request, view=self)
        return paginator.get_paginated_response(serializer_class(paginated_users, many=True).data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def active_tokens(self, request):
        """Retrieve all active tokens for the logged-in user."""
        tokens = SecureToken.objects.filter(user=request.user, is_active=True).order_by("-created_at")
        token_data = [
            {
                "id": token.id,
                "purpose": token.purpose,
                "created_at": token.created_at,
                "expires_at": token.expires_at,
                "is_active": token.is_active,
            }
            for token in tokens
        ]
        return Response({"active_tokens": token_data}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def request_update(self, request, pk=None):
        """Allows clients & writers to request a profile update."""
        user = self.get_object()
        if request.user != user:
            raise PermissionDenied("You can only request updates for your own profile.")

        requested_data = request.data
        ProfileUpdateRequest.objects.create(user=user, requested_data=requested_data)

        return Response({"message": "Profile update request submitted successfully."}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def request_deletion(self, request, pk=None):
        """Allows clients & writers to request account deletion."""
        user = self.get_object()
        if request.user != user:
            raise PermissionDenied("You can only request deletion for your own account.")

        reason = request.data.get("reason")
        AccountDeletionRequest.objects.create(user=user, reason=reason)

        return Response({"message": "Account deletion request submitted successfully."}, status=status.HTTP_201_CREATE)
        if request.user != user:
            raise PermissionDenied("You can only request deletion for your own account.")

        reason = request.data.get("reason")
        AccountDeletionRequest.objects.create(user=user, reason=reason)

        # Notify admins
        admin_emails = User.objects.filter(role="admin").values_list("email", flat=True)
        send_mail(
            "New Account Deletion Request",
            f"User {user.email} has requested account deletion. Please review.",
            settings.DEFAULT_FROM_EMAIL,
            list(admin_emails),
            fail_silently=False,
        )

        return Response({"message": "Account deletion request submitted successfully."}, status=status.HTTP_201_CREATED)
    @action(detail=False, methods=['get'])
    def profile(self, request):
        """Retrieve the authenticated user's profile."""
        user = request.user
        profile_map = {
            "client": (ClientProfile, ClientProfileSerializer),
            "writer": (WriterProfile, WriterProfileSerializer),
            "editor": (EditorProfile, EditorProfileSerializer),
            "support": (SupportProfile, SupportProfileSerializer),
            "admin": (User, AdminProfileSerializer),
            "superadmin": (User, AdminProfileSerializer),
        }

        profile_model, serializer_class = profile_map.get(user.role, (None, None))
        if profile_model:
            profile_instance = get_object_or_404(profile_model, user=user)
            serializer = serializer_class(profile_instance)
            return Response(serializer.data)

        raise PermissionDenied("Invalid role or unauthorized access.")

    @method_decorator(ratelimit(key="user", rate="3/m", method="POST", block=True))
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def impersonate(self, request, pk=None):
        """Allows Superadmins/Admins to impersonate another user."""
        check_admin_access(request.user)
        target_user = get_object_or_404(User, id=pk)

        if target_user.is_impersonated:
            return Response({"error": "User is already being impersonated."}, status=status.HTTP_400_BAD_REQUEST)

        target_user.impersonate(request.user)

        # Log impersonation action
        log_audit_action(request.user, "USER_IMPERSONATION", request)

        return Response(ImpersonateSerializer(target_user).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['delete'], permission_classes=[permissions.IsAdminUser])
    def stop_impersonation(self, request, pk=None):
        """Stops impersonation of a user."""
        check_admin_access(request.user)
        target_user = get_object_or_404(User, id=pk)

        if not target_user.is_impersonated:
            return Response({"error": "User is not being impersonated."}, status=status.HTTP_400_BAD_REQUEST)

        target_user.stop_impersonation()
        return Response({"message": "Impersonation stopped."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAdminUser])
    def activity(self, request, pk=None):
        """Fetches user activity logs."""
        check_admin_access(request.user)

        user = get_object_or_404(User, id=pk)
        serializer = UserActivitySerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def unlock_user(self, request, pk=None):
        """Admin manually unlocks a locked user account."""
        user = get_object_or_404(User, id=pk)
        if not user.is_locked:
            return Response({"message": "User is not locked."}, status=status.HTTP_400_BAD_REQUEST)

        user.unlock_account()
        return Response({"message": "User account has been unlocked."}, status=status.HTTP_200_OK)
    

    @action(detail=False, methods=['get'])
    def active_sessions(self, request):
        """Returns a list of active sessions for the logged-in user."""
        sessions = UserSession.objects.filter(user=request.user).order_by("-last_active")
        session_data = [
            {
                "session_key": session.session_key,
                "ip_address": session.ip_address,
                "device": session.device,
                "login_time": session.login_time,
                "last_active": session.last_active,
                "expires_at": session.expires_at,
            }
            for session in sessions
        ]
        return Response({"active_sessions": session_data}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def logout_session(self, request, pk=None):
        """Allows a user to log out from a specific session."""
        session = get_object_or_404(UserSession, session_key=pk, user=request.user)
        session.delete()  # Ends session
        return Response({"message": "Session logged out successfully."}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated], url_path="terminate-session")
    def terminate_session(self, request, pk=None):
        """Terminates a specific session for the user."""
        session = get_object_or_404(UserSession, id=pk, user=request.user, is_active=True)
        if not session:
            return Response({"error": "Session not found or already logged out."}, status=404)
        session.terminate()
        return Response({"message": "Session terminated successfully."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def force_logout_all(self, request):
        """Admin can log out all users from all sessions."""
        current_admin_session = request.session.session_key
        UserSession.objects.exclude(session_key=current_admin_session).delete()
        return Response({"message": "All user sessions have been terminated, except the current admin.."}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout_all_sessions(self, request):
        """Terminates all active sessions for the user."""
        sessions = UserSession.objects.filter(user=request.user, is_active=True)
        
        for session in sessions:
            session.terminate()
        
        return Response({"message": "All sessions terminated successfully."}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=["post"], url_path="logout-from-all-devices")
    def logout_from_all_devices(self, request):
        """
        Logs out the user from all devices except the current session.
        """
        current_session = request.session.session_key
        request.user.sessions.exclude(session_key=current_session).update(is_active=False)
        
        for session in request.user.sessions.exclude(session_key=current_session):
            session.terminate()

        return Response({"message": "Logged out from all devices except the current one."})
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def admin_terminate_all_sessions(self, request, pk=None):
        """Admin forcibly logs out all sessions of a user."""
        user = get_object_or_404(User, id=pk)
        sessions = UserSession.objects.filter(user=user, is_active=True)

        for session in sessions:
            session.terminate()

        return Response({"message": f"All sessions for {user.email} terminated."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="expire-old-sessions")
    def expire_old_sessions(self, request):
        """
        Automatically expires sessions inactive for more than 24 hours.
        """
        expired_sessions = request.user.sessions.filter(last_activity__lt=now() - timedelta(hours=24))
        count = expired_sessions.count()

        for session in expired_sessions:
            session.terminate()

        return Response({"message": f"{count} expired sessions have been removed."})


class AccountDeletionRequestViewSet(viewsets.ViewSet):
    """Handles user account deletion requests."""

    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'])
    def request_deletion(self, request):
        """Clients & Writers request account deletion."""
        user = request.user
        if user.is_frozen:
            return Response({"error": "Your account is already scheduled for deletion."}, status=status.HTTP_400_BAD_REQUEST)

        reason = request.data.get("reason", "No reason provided")
        AccountDeletionRequest.objects.create(user=user, reason=reason)
        user.freeze_account()

        return Response({"message": "Your account is now frozen and scheduled for deletion in 3 months."}, status=status.HTTP_201_CREATED)
    @action(detail=True, methods=['post'], permission_classes=[permissions.AllowAny])
    def confirm_deletion(self, request, pk=None):
        """Confirms the account deletion request and freezes the account."""
        user = get_object_or_404(User, id=pk)

        # Ensure the request exists and is pending confirmation
        deletion_request = AccountDeletionRequest.objects.filter(user=user, status="Pending Confirmation").first()
        if not deletion_request:
            return Response({"error": "No pending deletion request found."}, status=status.HTTP_400_BAD_REQUEST)

        # Freeze account and update request status
        user.freeze_account()
        deletion_request.status = "confirmed"
        deletion_request.save()

        return Response({"message": "Account deletion confirmed. Your account is now frozen for 3 months."}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def approve_deletion(self, request, pk=None):
        """Admin approves account deletion request."""
        deletion_request = get_object_or_404(AccountDeletionRequest, id=pk, status="pending")

        # Log admin action
        logger.info(f"Admin {request.user.email} approved deletion for {deletion_request.user.email}")

        deletion_request.status = "approved"
        deletion_request.save()

         # Freeze the user
        deletion_request.user.freeze_account()

        return Response({"message": "Account deletion request approved. Account is now frozen."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def reject_deletion(self, request, pk=None):
        """Admin rejects account deletion request."""
        deletion_request = get_object_or_404(
            AccountDeletionRequest,
            id=pk,
            status="pending"
        )
        reason = request.data.get("reason", "No reason provided")
        deletion_request.status = "rejected"
        deletion_request.admin_response = reason
        deletion_request.save()

        return Response({"message": "Account deletion request rejected."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def reinstate_account(self, request, pk=None):
        """Admin reinstates a frozen account."""
        user = get_object_or_404(User, id=pk, is_frozen=True)
        user.reinstate_account()

        return Response({"message": "User account has been reinstated."}, status=status.HTTP_200_OK)

class AdminProfileRequestViewSet(viewsets.ViewSet):
    """Allows admins to review and approve/reject profile update and deletion requests."""

    permission_classes = [permissions.IsAdminUser]

    @action(detail=True, methods=['post'])
    def approve_update(self, request, pk=None):
        """Approve a profile update request."""
        update_request = get_object_or_404(ProfileUpdateRequest, id=pk, status="pending")
        update_request.approve()
        return Response({"message": "Profile update approved."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def reject_update(self, request, pk=None):
        """Reject a profile update request."""
        update_request = get_object_or_404(
            ProfileUpdateRequest,
            id=pk,
            status="pending"
        )
        reason = request.data.get("reason")
        update_request.reject(reason)
        return Response({"message": "Profile update rejected."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def approve_deletion(self, request, pk=None):
        """Approve an account deletion request."""
        deletion_request = get_object_or_404(
            AccountDeletionRequest,
            id=pk,
            status="pending"
        )
        deletion_request.approve()
        return Response({"message": "Account deletion approved."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def reject_deletion(self, request, pk=None):
        """Reject an account deletion request."""
        deletion_request = get_object_or_404(AccountDeletionRequest, id=pk, status="pending")
        reason = request.data.get("reason")
        deletion_request.reject(reason)
        return Response({"message": "Account deletion rejected."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["patch"], url_path="update-profile")
    def update_profile(self, request):
        """
        Allows users to update their profile. 
        - Basic updates (bio, phone number, avatar) are auto-approved.
        - Sensitive updates (email, role, website) require admin approval.
        """
        user = request.user
        update_fields = request.data

        # Fields that require admin approval
        admin_approval_fields = ["email", "role", "website"]

        # Separate updates
        auto_approve_updates = {}
        admin_approval_updates = {}

        for field, value in update_fields.items():
            if field in admin_approval_fields:
                admin_approval_updates[field] = value
            else:
                auto_approve_updates[field] = value

        # Auto-approve basic updates
        for field, value in auto_approve_updates.items():
            setattr(user, field, value)
        user.save()

        # Store admin approval request if necessary
        if admin_approval_updates:
            ProfileUpdateRequest.objects.create(user=user, requested_data=admin_approval_updates)
            return Response({"message": "Profile updated. Some changes require admin approval."})

        return Response({"message": "Profile updated successfully."})

    @action(detail=False, methods=["get"], url_path="profile-update-requests", permission_classes=[IsAuthenticated])
    def get_update_requests(self, request):
        """
        Allows users to view their pending profile update requests.
        """
        requests = request.user.update_requests.filter(status="pending").values()
        return Response({"pending_requests": list(requests)})
class AdminUserManagementViewSet(viewsets.ViewSet):
    """Allows admins to manage user accounts."""

    permission_classes = [permissions.IsAdminUser]

    @action(detail=True, methods=['post'])
    def restore_archived_account(self, request, pk=None):
        """Restores an archived account."""
        user = get_object_or_404(User, id=pk, is_archived=True)
        user.is_archived = False
        user.is_active = True
        user.save()

        return Response({"message": "User account restored successfully."}, status=status.HTTP_200_OK)

    @method_decorator(ratelimit(key="user", rate="2/m", method="POST", block=True))    
    @action(detail=True, methods=['post'])
    def suspend(self, request, pk=None):
        """Admin suspends a user."""
        user = get_object_or_404(User, id=pk)
        user.is_suspended = True
        user.suspension_reason = request.data.get("reason", "No reason provided")
        user.suspension_start_date = now()
        user.suspension_end_date = now() + timedelta(days=30)  # Default 30-day suspension
        user.save()

        logger.info(f"Admin {request.user.email} suspended {user.email}")
        return Response({"message": "User suspended."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def lift_suspension(self, request, pk=None):
        """Admin lifts a user's suspension."""
        user = get_object_or_404(User, id=pk)
        user.is_suspended = False
        user.suspension_reason = None
        user.suspension_start_date = None
        user.suspension_end_date = None
        user.save()

        logger.info(f"Admin {request.user.email} lifted suspension for {user.email}")
        return Response({"message": "User suspension lifted."}, status=status.HTTP_200_OK)

# Moved to Auth
    # @action(detail=True, methods=['post'])
    # def force_reset_password(self, request, pk=None):
    #     """Admin forces a user to reset their password."""
    #     user = get_object_or_404(User, id=pk)
    #     new_password = "TemporaryPass123"  # Generate a secure random password in production
    #     user.set_password(new_password)
    #     user.save()

    #     send_mail(
    #         "Your Password Has Been Reset",
    #         f"Your new temporary password is: {new_password}. Please change it after login.",
    #         "no-reply@yourdomain.com",
    #         [user.email]
    #     )

    #     logger.info(f"Admin {request.user.email} forced password reset for {user.email}")
    #     return Response({"message": "User password has been reset and emailed to them."}, status=status.HTTP_200_OK)

    @method_decorator(ratelimit(key="user", rate="1/m", method="POST", block=True))
    @action(detail=False, methods=['get'])
    def user_reports(self, request):
        """Admin gets reports on user activities."""
        active_users = User.objects.filter(is_active=True).count()
        suspended_users = User.objects.filter(is_suspended=True).count()
        pending_deletion = AccountDeletionRequest.objects.filter(status="pending").count()

        return Response({
            "total_users": User.objects.count(),
            "active_users": active_users,
            "suspended_users": suspended_users,
            "pending_deletion_requests": pending_deletion
        }, status=status.HTTP_200_OK)