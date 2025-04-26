# passkeys/devices.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from authentication.models.passkeys import WebAuthnCredential
from authentication.models.audit import AuditLog
from django.shortcuts import get_object_or_404


class ListDevicesView(APIView):
    """
    List all registered passkey devices for the logged-in user.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        creds = WebAuthnCredential.objects.filter(user=request.user)

        devices = [
            {
                "id": cred.id,
                "device_label": cred.device_label or "Unknown Device",
                "last_used": cred.updated_at if hasattr(cred, "updated_at") else None,
            }
            for cred in creds
        ]

        return Response(devices, status=status.HTTP_200_OK)


class RevokeDeviceView(APIView):
    """
    Revoke (delete) a specific passkey device by its ID.
    """
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, credential_id):
        try:
            cred = WebAuthnCredential.objects.get(
                id=credential_id, user=request.user
            )
            cred.delete()
            return Response(
                {"detail": "Device revoked successfully."},
                status=status.HTTP_204_NO_CONTENT,
            )
        except WebAuthnCredential.DoesNotExist:
            return Response(
                {"detail": "Device not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        

class RenameDeviceView(APIView):
    """
    Allow a user to rename one of their registered passkey devices.
    """
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, credential_id):
        new_name = request.data.get("device_name")

        if not new_name:
            return Response(
                {"detail": "Device name is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        cred = get_object_or_404(
            WebAuthnCredential,
            credential_id=credential_id,
            user=request.user
        )

        cred.device_name = new_name
        cred.is_device_name_custom = True
        cred.save()

        return Response(
            {"detail": "Device renamed successfully."},
            status=status.HTTP_200_OK
        )
    

class DeleteDeviceView(APIView):
    """
    Allow a user to delete one of their registered passkey devices.
    """
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, credential_id):
        cred = get_object_or_404(
            WebAuthnCredential,
            credential_id=credential_id,
            user=request.user
        )

        # Log the device deletion in AuditLog
        AuditLog.log_device_deletion(request.user, credential_id, request)

        cred.delete()

        return Response(
            {"detail": "Device deleted successfully."},
            status=status.HTTP_204_NO_CONTENT
        )