from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK
from .models import User
from .serializers import (
    ClientProfileSerializer,
    WriterProfileSerializer,
    AdminProfileSerializer,
    EditorProfileSerializer,
    SupportProfileSerializer,
)


class UserProfileView(APIView):
    """
    Base view to handle user profile based on roles.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        serializer_map = {
            "client": ClientProfileSerializer,
            "writer": WriterProfileSerializer,
            "admin": AdminProfileSerializer,
            "editor": EditorProfileSerializer,
            "support": SupportProfileSerializer,
        }
        serializer_class = serializer_map.get(user.role)
        if serializer_class:
            return Response(serializer_class(user).data)
        raise PermissionDenied("Invalid role or unauthorized access.")


class ListUsersView(APIView):
    """
    Generic view to list users based on role.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, role, *args, **kwargs):
        if not request.user.is_admin():
            raise PermissionDenied("Only admins can view user data.")
        valid_roles = ["client", "writer", "editor", "support"]
        if role not in valid_roles:
            return Response({"error": "Invalid role"}, status=HTTP_400_BAD_REQUEST)

        role_serializer_map = {
            "client": ClientProfileSerializer,
            "writer": WriterProfileSerializer,
            "editor": EditorProfileSerializer,
            "support": SupportProfileSerializer,
        }

        users = User.objects.filter(role=role)
        serializer = role_serializer_map[role](users, many=True)
        return Response(serializer.data, status=HTTP_200_OK)


class WriterDetailView(APIView):
    """
    Retrieve and update writer profile.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, *args, **kwargs):
        if not request.user.is_admin():
            raise PermissionDenied("Only admins can view writer details.")
        writer = get_object_or_404(User, pk=pk, role="writer")
        return Response(WriterProfileSerializer(writer).data, status=HTTP_200_OK)

    def patch(self, request, pk, *args, **kwargs):
        if not request.user.is_admin():
            raise PermissionDenied("Only admins can update writer details.")
        writer = get_object_or_404(User, pk=pk, role="writer")
        serializer = WriterProfileSerializer(writer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=HTTP_200_OK)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class EditorDetailView(APIView):
    """
    Retrieve and update editor profile.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, *args, **kwargs):
        if not request.user.is_admin():
            raise PermissionDenied("Only admins can view editor details.")
        editor = get_object_or_404(User, pk=pk, role="editor")
        return Response(EditorProfileSerializer(editor).data, status=HTTP_200_OK)

    def patch(self, request, pk, *args, **kwargs):
        if not request.user.is_admin():
            raise PermissionDenied("Only admins can update editor details.")
        editor = get_object_or_404(User, pk=pk, role="editor")
        serializer = EditorProfileSerializer(editor, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=HTTP_200_OK)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class SupportDetailView(APIView):
    """
    Retrieve and update support staff profile.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, *args, **kwargs):
        if not request.user.is_admin():
            raise PermissionDenied("Only admins can view support details.")
        support = get_object_or_404(User, pk=pk, role="support")
        return Response(SupportProfileSerializer(support).data, status=HTTP_200_OK)

    def patch(self, request, pk, *args, **kwargs):
        if not request.user.is_admin():
            raise PermissionDenied("Only admins can update support details.")
        support = get_object_or_404(User, pk=pk, role="support")
        serializer = SupportProfileSerializer(support, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=HTTP_200_OK)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)