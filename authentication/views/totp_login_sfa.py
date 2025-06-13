from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import pyotp
from authentication.models import MFASettings

class TOTPLogin2FAView(APIView):
    def post(self, request):
        user_id = request.data.get("user_id")
        otp_code = request.data.get("otp_code")

        try:
            mfa = MFASettings.objects.get(user_id=user_id, is_mfa_enabled=True)
        except MFASettings.DoesNotExist:
            return Response({"detail": "MFA not enabled"}, status=400)

        totp = pyotp.TOTP(mfa.mfa_secret)
        if not totp.verify(otp_code, valid_window=1):
            return Response({"detail": "Invalid OTP"}, status=400)

        # Issue token
        token = self.issue_token(mfa.user)
        return Response({"token": token})

    def issue_token(self, user):
        # JWT or session logic here
        pass