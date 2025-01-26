from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from .models import User
from .serializers import (
    ClientProfileSerializer,
    WriterProfileSerializer,
    AdminProfileSerializer,
    EditorProfileSerializer,
)


class UserProfileView(APIView):
    """
    Base view to handle user profile based on roles.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        if user.is_client():
            return Response(ClientProfileSerializer(user).data)
        elif user.is_writer():
            return Response(WriterProfileSerializer(user).data)
        elif user.is_admin():
            return Response(AdminProfileSerializer(user).data)
        elif user.is_editor():
            return Response(EditorProfileSerializer(user).data)
        else:
            raise PermissionDenied("Invalid role or unauthorized access.")


class ClientListView(APIView):
    """
    List all clients for admin purposes.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        if not request.user.is_admin():
            raise PermissionDenied("Only admins can view client data.")
        clients = User.objects.filter(role="client")
        return Response(ClientProfileSerializer(clients, many=True).data)


class WriterListView(APIView):
    """
    List all writers for admin purposes.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        if not request.user.is_admin():
            raise PermissionDenied("Only admins can view writer data.")
        writers = User.objects.filter(role="writer")
        return Response(WriterProfileSerializer(writers, many=True).data)


class WriterDetailView(APIView):
    """
    Retrieve and update writer profile.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, *args, **kwargs):
        if not request.user.is_admin():
            raise PermissionDenied("Only admins can view writer details.")
        writer = get_object_or_404(User, pk=pk, role="writer")
        return Response(WriterProfileSerializer(writer).data)

    def patch(self, request, pk, *args, **kwargs):
        if not request.user.is_admin():
            raise PermissionDenied("Only admins can update writer details.")
        writer = get_object_or_404(User, pk=pk, role="writer")
        serializer = WriterProfileSerializer(writer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)


class EditorListView(APIView):
    """
    List all editors for admin purposes.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        if not request.user.is_admin():
            raise PermissionDenied("Only admins can view editor data.")
        editors = User.objects.filter(role="editor")
        return Response(EditorProfileSerializer(editors, many=True).data)


class SupportListView(APIView):
    """
    List all support staff for admin purposes.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        if not request.user.is_admin():
            raise PermissionDenied("Only admins can view support data.")
        support_staff = User.objects.filter(role="support")
        return Response(EditorProfileSerializer(support_staff, many=True).data)