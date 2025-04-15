from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
import pyotp # type: ignore
from authentication.utils_backp import generate_totp_secret

class VerifyMFAView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        mfa_code = request.data.get('mfa_code')

        if not mfa_code:
            return Response(
                {"error": "MFA code is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        totp = pyotp.TOTP(user.mfa_secret)
        if totp.verify(mfa_code):
            return Response(
                {"message": "MFA verified successfully!"},
                status=status.HTTP_200_OK
            )
        
        return Response(
            {"error": "Invalid MFA code."},
            status=status.HTTP_400_BAD_REQUEST
        )