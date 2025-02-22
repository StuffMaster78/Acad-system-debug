from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from users.models import User
from users.serializers import (
    ImpersonationSerializer,
    UserActivitySerializer,
)
from client_management.models import ClientProfile
from writer_management.models import WriterProfile
from editor_management.models import EditorProfile
from support_management.models import SupportProfile
from users.serializers import (
    ClientProfileSerializer,
    WriterProfileSerializer,
    AdminProfileSerializer,
    EditorProfileSerializer,
    SupportProfileSerializer,
)

### 🔹 PERMISSION CHECK FUNCTION ###
def check_admin_access(user):
    """
    Ensures only Superadmins & Admins can manage users.
    """
    if user.role not in ["superadmin", "admin"]:
        raise PermissionDenied("Only Superadmins and Admins can access this resource.")


### 🔹 USER PROFILE VIEW (Authenticated Users) ###
class UserProfileView(APIView):
    """
    Retrieve the authenticated user's profile.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
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


### 🔹 IMPERSONATION FEATURE ###
class ImpersonationView(APIView):
    """
    Allows Superadmins/Admins to impersonate another user.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id, *args, **kwargs):
        check_admin_access(request.user)
        target_user = get_object_or_404(User, id=user_id)

        if target_user.is_impersonated:
            return Response({"error": "User is already being impersonated."}, status=status.HTTP_400_BAD_REQUEST)

        target_user.impersonate(request.user)
        return Response(ImpersonationSerializer(target_user).data, status=status.HTTP_200_OK)

    def delete(self, request, user_id, *args, **kwargs):
        check_admin_access(request.user)
        target_user = get_object_or_404(User, id=user_id)

        if not target_user.is_impersonated:
            return Response({"error": "User is not being impersonated."}, status=status.HTTP_400_BAD_REQUEST)

        target_user.stop_impersonation()
        return Response({"message": "Impersonation stopped."}, status=status.HTTP_200_OK)


### 🔹 TRACK USER ACTIVITY ###
class UserActivityView(APIView):
    """
    Track user activity and last login.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id, *args, **kwargs):
        check_admin_access(request.user)

        user = get_object_or_404(User, id=user_id)
        serializer = UserActivitySerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)