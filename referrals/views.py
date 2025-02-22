from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Referral, ReferralBonusConfig, ReferralCode
from .serializers import ReferralSerializer, ReferralBonusConfigSerializer, ReferralCodeSerializer
from wallet.models import Wallet, WalletTransaction
from django.utils.timezone import now


class ReferralViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing referrals.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ReferralSerializer

    def get_queryset(self):
        """
        Filter referrals by the authenticated user.
        """
        return Referral.objects.filter(referrer=self.request.user)

    @action(detail=False, methods=['post'], url_path='generate-code')
    def generate_code(self, request):
        """
        Generate a referral code for the authenticated user.
        """
        user = request.user
        if hasattr(user, "referral_code"):
            return Response(
                {"message": f"Referral code already exists: {user.referral_code.code}"},
                status=status.HTTP_200_OK
            )

        code = f"REF-{user.id}-{now().strftime('%Y%m%d%H%M%S')}"
        ReferralCode.objects.create(user=user, code=code, website=user.website)
        return Response({"message": f"Referral code generated: {code}"}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='credit-bonus')
    def credit_bonus(self, request):
        """
        Credit referral bonuses for a successful referral.
        """
        referral_id = request.data.get("referral_id")
        referral = Referral.objects.get(id=referral_id)
        bonus_config = ReferralBonusConfig.objects.get(website=referral.website)

        # Credit bonuses based on the event
        if not referral.registration_bonus_credited:
            wallet = Wallet.objects.get(user=referral.referrer)
            WalletTransaction.objects.create(
                wallet=wallet,
                transaction_type='bonus',
                amount=bonus_config.registration_bonus,
                description="Referral Bonus: Successful Registration",
                website=referral.website,
            )
            referral.registration_bonus_credited = True
            referral.save()

        return Response({"message": "Referral bonus credited successfully!"}, status=status.HTTP_200_OK)


class ReferralBonusConfigViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing referral bonus configurations.
    """
    permission_classes = [permissions.IsAdminUser]
    serializer_class = ReferralBonusConfigSerializer
    queryset = ReferralBonusConfig.objects.all()