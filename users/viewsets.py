from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied

from users.models import User
from client_management.models import ClientProfile
from writer_management.models import WriterProfile
from editor_management.models import EditorProfile
from support_management.models import SupportProfile

from users.serializers import (
    UserActivitySerializer,
    ImpersonationSerializer,
    ClientProfileSerializer,
    WriterProfileSerializer,
    AdminProfileSerializer,
    EditorProfileSerializer,
    SupportProfileSerializer,
    SuspensionSerializer,
)

### 🔹 PERMISSION CHECK FUNCTION ###
def check_admin_access(user):
    """
    Ensures only Superadmins & Admins can manage users.
    """
    if user.role not in ["superadmin", "admin"]:
        raise PermissionDenied("Only Superadmins and Admins can access this resource.")


### 🔹 USER VIEWSET ###
class UserViewSet(viewsets.ModelViewSet):
    """
    Handles listing, retrieving, updating, and managing users.
    """
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        """
        Dynamically return the correct serializer based on the user role.
        """
        profile_map = {
            "client": ClientProfileSerializer,
            "writer": WriterProfileSerializer,
            "editor": EditorProfileSerializer,
            "support": SupportProfileSerializer,
            "admin": AdminProfileSerializer,
            "superadmin": AdminProfileSerializer,
        }
        return profile_map.get(self.request.user.role, AdminProfileSerializer)

    def list(self, request, *args, **kwargs):
        """
        List users based on role (Replaces `ListUsersView`).
        """
        check_admin_access(request.user)
        role = request.query_params.get("role")

        if role not in ["client", "writer", "editor", "support", "admin", "superadmin"]:
            return Response({"error": "Invalid role"}, status=status.HTTP_400_BAD_REQUEST)

        profile_map = {
            "client": (ClientProfile, ClientProfileSerializer),
            "writer": (WriterProfile, WriterProfileSerializer),
            "editor": (EditorProfile, EditorProfileSerializer),
            "support": (SupportProfile, SupportProfileSerializer),
            "admin": (User, AdminProfileSerializer),
            "superadmin": (User, AdminProfileSerializer),
        }

        profile_model, serializer_class = profile_map[role]
        users = profile_model.objects.select_related("user").all()
        serializer = serializer_class(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a specific user's profile (Replaces `ProfileDetailView`).
        """
        check_admin_access(request.user)
        user = get_object_or_404(User, id=kwargs.get("pk"))
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        """
        Update a user's profile (Replaces `ProfileDetailView` patch method).
        """
        check_admin_access(request.user)
        user = get_object_or_404(User, id=kwargs.get("pk"))
        serializer = self.get_serializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["patch"])
    def suspend_user(self, request, pk=None):
        """
        Suspend or place a user on probation (Replaces `SuspendUserView`).
        """
        check_admin_access(request.user)
        user = get_object_or_404(User, id=pk)
        serializer = SuspensionSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def impersonate(self, request, pk=None):
        """
        Allows Admins & Superadmins to impersonate another user.
        """
        check_admin_access(request.user)
        target_user = get_object_or_404(User, id=pk)

        if target_user.is_impersonated:
            return Response({"error": "User is already being impersonated."}, status=status.HTTP_400_BAD_REQUEST)

        target_user.impersonate(request.user)
        return Response(ImpersonationSerializer(target_user).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["delete"])
    def stop_impersonation(self, request, pk=None):
        """
        Stops impersonation of a user.
        """
        check_admin_access(request.user)
        target_user = get_object_or_404(User, id=pk)

        if not target_user.is_impersonated:
            return Response({"error": "User is not being impersonated."}, status=status.HTTP_400_BAD_REQUEST)

        target_user.stop_impersonation()
        return Response({"message": "Impersonation stopped."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"])
    def activity(self, request, pk=None):
        """
        Get user activity (last login, last active time).
        """
        check_admin_access(request.user)
        user = get_object_or_404(User, id=pk)
        serializer = UserActivitySerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)