from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied
from django.db.models import Q
from django.contrib.postgres.search import TrigramSimilarity   # ✅ Fuzzy Search
from rest_framework.pagination import PageNumberPagination

from users.models import User
from client_management.models import ClientProfile
from writer_management.models import WriterProfile
from editor_management.models import EditorProfile
from support_management.models import SupportProfile
from admin_management.models import AdminProfile
from superadmin_management.models import SuperadminProfile

from users.serializers import (
    UserActivitySerializer,
    ImpersonationSerializer,
    ClientProfileSerializer,
    WriterProfileSerializer,
    AdminProfileSerializer,
    EditorProfileSerializer,
    SupportProfileSerializer,
    SuperadminProfileSerializer,
    SuspensionSerializer,
    UserSerializer
)

### 🔹 CUSTOM PAGINATION CLASS ###
class CustomUserPagination(PageNumberPagination):
    """
    Custom pagination class for user listings.
    Allows admins and superadmins to paginate user search results.
    """
    page_size = 10  # Default results per page
    page_size_query_param = "page_size"
    max_page_size = 100  # Prevents excessive page sizes


### 🔹 PERMISSION CHECK FUNCTION ###
def check_admin_access(user):
    """
    Ensures only Superadmins & Admins can manage users.
    """
    if user.role not in ["superadmin", "admin"]:
        raise PermissionDenied("Sorry! Access Denied: You cannot access this resource.")


### 🔹 USER VIEWSET ###
class UserViewSet(viewsets.ModelViewSet):
    """
    Handles listing, retrieving, updating, and managing users.
    """
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = CustomUserPagination  # Enable pagination

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
            "superadmin": SuperadminProfileSerializer,
        }
        return profile_map.get(self.request.user.role, UserSerializer)

    def list(self, request, *args, **kwargs):
        """
        List users based on role, with an option to filter by role.
        """
        check_admin_access(request.user)
        
        # Get filters from query parameters
        role = request.query_params.get("role", None)
        search_query = request.query_params.get("search", None)
        sort_by = request.query_params.get("sort", None)  # Sorting parameter

        if role and role not in ["client", "writer", "editor", "support", "admin", "superadmin"]:
            return Response({"error": "Invalid role"}, status=status.HTTP_400_BAD_REQUEST)

        profile_map = {
            "client": (ClientProfile, ClientProfileSerializer),
            "writer": (WriterProfile, WriterProfileSerializer),
            "editor": (EditorProfile, EditorProfileSerializer),
            "support": (SupportProfile, SupportProfileSerializer),
            "admin": (AdminProfile, AdminProfileSerializer),
            "superadmin": (SuperadminProfile, SuperadminProfileSerializer),
        }

        if role:
            profile_model, serializer_class = profile_map[role]
            users = profile_model.objects.select_related("user").all()
            serializer = serializer_class(users, many=True)
        else:
            # If no role filter, return all users
            users = User.objects.all()
            serializer = UserSerializer(users, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
        
    
        # Apply search filter if provided
        if search_query:
            users = users.annotate(
                similarity=TrigramSimilarity("username", search_query)
            ).filter(
                Q(username__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(admin_profile__full_name__icontains=search_query) |
                Q(superadmin_profile__full_name__icontains=search_query) |
                Q(client_profile__full_name__icontains=search_query) |
                Q(writer_profile__full_name__icontains=search_query) |
                Q(editor_profile__full_name__icontains=search_query) |
                Q(support_profile__full_name__icontains=search_query)|
                Q(similarity__gt=0.3)  # ✅ Fuzzy matching threshold
            ).order_by("-similarity")  # Sort by best match
        

        # ✅ Apply sorting
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
        paginated_users = self.paginate_queryset(users)
        serializer = UserSerializer(paginated_users, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a specific user's full profile.
        """
        check_admin_access(request.user)
        user = get_object_or_404(User, id=kwargs.get("pk"))

        profile_map = {
            "client": ClientProfileSerializer,
            "writer": WriterProfileSerializer,
            "editor": EditorProfileSerializer,
            "support": SupportProfileSerializer,
            "admin": AdminProfileSerializer,
            "superadmin": SuperadminProfileSerializer,
        }

        profile_serializer_class = profile_map.get(user.role, UserSerializer)
        serializer = profile_serializer_class(user)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        """
        Update a user's profile.
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
        Suspend or place a user on probation.
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