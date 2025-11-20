from rest_framework import viewsets, permissions
from authentication.models.otp import OTP
from authentication.serializers import OTPSerializer

class OTPViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Optional: view OTPs for testing/debugging only.
    Lock this down in prod.
    """
    queryset = OTP.objects.all()
    serializer_class = OTPSerializer
    permission_classes = [permissions.IsAdminUser]  # 🔐