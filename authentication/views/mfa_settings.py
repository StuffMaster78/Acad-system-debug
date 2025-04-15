# authentication/views/mfa_settings.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from authentication.models.mfa_settings import MFASettings
from authentication.serializers import MFASettingsSerializer

class MFASettingsView(APIView):
    """
    Handles retrieving and updating MFA preferences for the authenticated user.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        mfa_settings, created = MFASettings.objects.get_or_create(user=request.user)
        serializer = MFASettingsSerializer(mfa_settings)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        mfa_settings, _ = MFASettings.objects.get_or_create(user=request.user)
        serializer = MFASettingsSerializer(mfa_settings, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        mfa_settings, _ = MFASettings.objects.get_or_create(user=request.user)
        serializer = MFASettingsSerializer(mfa_settings, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)