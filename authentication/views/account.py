from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from users.models import User
from authentication.utilsy import decode_verification_token
from authentication.serializers import RegisterSerializer


class FinalizeAccountView(APIView):
    """
    Finalizes the account activation process using a verification token.

    This view accepts a `POST` request with a token, which is used to verify and 
    activate a user account. If the token is valid and the user is not already active, 
    the user's account is activated. If the user is already active, the request will 
    return a message indicating that the account is already activated.

    Responses:
        - 200 OK: If the account is successfully activated.
        - 400 Bad Request: If the token is invalid or expired, or if the account is already active.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        """Finalizes account activation using a verification token."""
        token = request.data.get('token')

        if not token:
            return Response(
                {"error": "Verification token is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = decode_verification_token(token)
        except Exception:
            return Response(
                {"error": "Invalid or expired token."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if user:
            if user.is_active:
                return Response(
                    {"error": "Account is already activated."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.is_active = True
            user.save()

            return Response(
                {"message": "Account activated successfully."},
                status=status.HTTP_200_OK
            )

        return Response(
            {"error": "User associated with token not found."},
            status=status.HTTP_400_BAD_REQUEST
        )


class RegisterView(APIView):
    """
    Handles user registration.
    """
    def post(self, request):
        """Handles user registration and sends an activation email."""
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # Create activation token
            token = default_token_generator.make_token(user)
            activation_url = f"{settings.FRONTEND_URL}/activate/{token}/?email={user.email}"

            # Send activation email
            try:
                send_mail(
                    'Activate your account',
                    f'Please click the link to activate your account: {activation_url}',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
                return Response({"message": "Registration successful. Please check your email for activation."}, 
                                status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"error": f"Error sending email: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ActivationView(APIView):
    """
    Handles account activation using the token sent via email.
    """
    def get(self, request, token):
        """Activates user account based on token."""
        email = request.query_params.get('email')

        if not email:
            return Response({"error": "Email parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
            if default_token_generator.check_token(user, token):
                user.is_active = True
                user.save()
                return Response({"message": "Account activated successfully!"}, status=status.HTTP_200_OK)

            return Response({"error": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)

        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)