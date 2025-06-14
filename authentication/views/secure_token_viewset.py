from rest_framework import viewsets, status, mixins
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

from authentication.models.tokens import (
    SecureToken, EncryptedRefreshToken
)
from authentication.serializers import (
    SecureTokenCreateSerializer,
    SecureTokenListSerializer,
    SecureTokenDecryptSerializer,
    EncryptedRefreshTokenSerializer
)

class SecureTokenViewSet(viewsets.GenericViewSet,
                         mixins.ListModelMixin):
    """
    Handles secure token creation, listing, and decryption.
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SecureToken.objects.filter(user=self.request.user, website=self.request.website)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["website"] = self.request.website
        return context

    def get_serializer_class(self):
        if self.action == "create_token":
            return SecureTokenCreateSerializer
        if self.action == "decrypt_token":
            return SecureTokenDecryptSerializer
        return SecureTokenListSerializer

    def list(self, request, *args, **kwargs):
        """
        Lists secure tokens for the current user & website.
        """
        return super().list(request, *args, **kwargs)

    @action(detail=False, methods=["post"], url_path="create")
    def create_token(self, request):
        """
        Creates a new encrypted secure token.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.save()
        return Response({"id": str(token.id)}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"], url_path="decrypt")
    def decrypt_token(self, request):
        """
        Decrypts a secure token (once only).
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        return Response(result, status=status.HTTP_200_OK)


class EncryptedRefreshTokenViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for listing encrypted refresh tokens (admin/debug use).
    """
    permission_classes = [IsAuthenticated]
    serializer_class = EncryptedRefreshTokenSerializer

    def get_queryset(self):
        return EncryptedRefreshToken.objects.filter(user=self.request.user)