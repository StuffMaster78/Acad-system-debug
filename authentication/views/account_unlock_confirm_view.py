from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from authentication.services.token_services import SecureTokenService
from authentication.services.account_lockout_service import AccountLockoutService


class AccountUnlockConfirmView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        token_str = request.data.get("token")

        if not token_str:
            return Response({"error": "Token is required."}, status=400)

        token = SecureTokenService.validate_token(token_str, purpose="unlock_account")

        if not token:
            return Response({"error": "Invalid or expired token."}, status=400)

        # Unlock the user
        user = token.user
        AccountLockoutService.unlock_user(user)

        # Optionally delete token after use
        token.delete()

        return Response({"message": "Your account has been unlocked."}, status=200)
