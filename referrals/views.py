from rest_framework import viewsets, permissions, status, pagination
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.utils.timezone import now
from django.utils.dateparse import parse_date
from django.db.models import Count, Sum, Q
from datetime import timedelta

from .models import Referral, ReferralBonusConfig, ReferralCode, ReferralStats
from .serializers import ReferralSerializer, ReferralBonusConfigSerializer, ReferralCodeSerializer
from wallet.models import Wallet, WalletTransaction
from users.permissions import IsAdminUser  # Only admins can access


# Constants for transaction types
TRANSACTION_TYPE_REFERRAL_BONUS = 'referral_bonus'
TRANSACTION_TYPE_BONUS = 'bonus'


class LargeResultsSetPagination(pagination.PageNumberPagination):
    """Pagination for large admin reports"""
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 500


class ReferralViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing referrals.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ReferralSerializer

    def get_queryset(self):
        """Filter referrals by the authenticated user."""
        return Referral.objects.filter(referrer=self.request.user)

    @action(detail=False, methods=['post'], url_path='generate-code')
    def generate_code(self, request):
        """Generate a referral code for the authenticated user."""
        user = request.user
        website = request.data.get("website")  # Website must be provided

        if not website:
            return Response({"error": "Website is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if user already has a referral code for the website
        referral_code, created = ReferralCode.objects.get_or_create(user=user, website=website)

        if not created:
            return Response(
                {"message": f"Referral code already exists: {referral_code.code}"},
                status=status.HTTP_200_OK
            )

        # Generate a unique code
        referral_code.code = ReferralCode.generate_unique_code(user, website)
        referral_code.save()

        return Response({"message": f"Referral code generated: {referral_code.code}"}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='credit-bonus')
    def credit_referral_bonus(self, request):
        """
        Credit referral bonuses for a successful referral.
        """
        referral_id = request.data.get("referral_id")
        referral = get_object_or_404(Referral.objects.select_related("referrer"), id=referral_id)
        bonus_config = ReferralBonusConfig.objects.filter(website=referral.website).first()

        if not bonus_config:
            return Response({"error": "Referral bonus settings not found."}, status=status.HTTP_400_BAD_REQUEST)

        wallet, _ = Wallet.objects.get_or_create(user=referral.referrer)

        expires_at = now() + timedelta(days=bonus_config.bonus_expiry_days)

        WalletTransaction.objects.create(
            wallet=wallet,
            transaction_type=TRANSACTION_TYPE_REFERRAL_BONUS,
            amount=bonus_config.registration_referral_bonus,
            description="Referral Bonus: Successful Registration",
            expires_at=expires_at,
            website=referral.website,
        )

        referral.registration_referral_bonus_credited = True
        referral.save()
        return Response({"message": "Referral bonus credited successfully!"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='stats')
    def referral_stats(self, request):
        """Get referral stats for the logged-in user."""
        user = request.user
        website = request.query_params.get("website")

        if not website:
            return Response({"error": "Website is required"}, status=status.HTTP_400_BAD_REQUEST)

        referral_code = ReferralCode.objects.filter(user=user, website=website).first()
        referral_link = referral_code.get_referral_link() if referral_code else None

        referrals = Referral.objects.filter(referrer=user, website=website)
        referred_count = referrals.count()
        ordered_count = referrals.filter(first_order_referral_bonus_credited=True).count()

        return Response({
            "total_referred": referred_count,
            "completed_orders": ordered_count,
            "referral_code": referral_code.code if referral_code else None,
            "referral_link": referral_link,
        })

    @action(detail=False, methods=["POST"], url_path="apply-bonus")
    def apply_referral_bonus(self, request):
        """
        Apply referral bonus at checkout.
        """
        user = request.user
        bonus_config = ReferralBonusConfig.objects.first()

        if not bonus_config:
            return Response({"error": "Referral bonuses are not configured"}, status=status.HTTP_400_BAD_REQUEST)

        # Placeholder logic to apply referral bonus
        return Response({"message": "Referral bonus applied successfully"})


class ReferralBonusConfigViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing referral bonus configurations.
    """
    permission_classes = [permissions.IsAdminUser]
    serializer_class = ReferralBonusConfigSerializer
    queryset = ReferralBonusConfig.objects.all()


class ReferralAdminViewSet(viewsets.ViewSet):
    """RESTful API for Referral Management (Admin Only)"""
    permission_classes = [IsAdminUser]
    pagination_class = LargeResultsSetPagination

    def filter_by_date_and_website(self, request, queryset):
        """Filter referrals by date range & website"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        website = request.query_params.get('website')

        if start_date:
            queryset = queryset.filter(created_at__gte=parse_date(start_date))
        if end_date:
            queryset = queryset.filter(created_at__lte=parse_date(end_date))
        if website:
            queryset = queryset.filter(website=website)

        return queryset

    @action(detail=False, methods=['get'], url_path='top-referrers')
    def top_referrers(self, request):
        """Get top referrers (filtered by date & website)"""
        queryset = Referral.objects.values("referrer__username") \
            .annotate(total_referrals=Count("id")) \
            .order_by("-total_referrals")
        queryset = self.filter_by_date_and_website(request, queryset)
        queryset = self.paginate_queryset(queryset)

        return Response(queryset)

    @action(detail=False, methods=['get'], url_path='top-earners')
    def top_earners(self, request):
        """Get top referrers by earned bonuses"""
        queryset = Referral.objects.values("referrer__username") \
            .annotate(total_earned=Sum("wallettransaction__amount")) \
            .order_by("-total_earned")
        queryset = self.filter_by_date_and_website(request, queryset)
        queryset = self.paginate_queryset(queryset)

        return Response(queryset)

    @action(detail=False, methods=['get'], url_path='completed-orders')
    def completed_orders(self, request):
        """Get referrers with most completed referral orders"""
        queryset = Referral.objects.values("referrer__username") \
            .annotate(completed_orders=Count("id", filter=Q(first_order_bonus_credited=True))) \
            .order_by("-completed_orders")
        queryset = self.filter_by_date_and_website(request, queryset)
        queryset = self.paginate_queryset(queryset)

        return Response(queryset)

    @action(detail=False, methods=['post'], url_path='credit-bonus')
    def credit_bonus(self, request):
        """Admin manually credits bonus for a referral."""
        referral_id = request.data.get("referral_id")
        referral = get_object_or_404(Referral.objects.select_related("referrer"), id=referral_id)

        # Fetch referral bonus config for the same website
        bonus_config = ReferralBonusConfig.objects.filter(website=referral.website).first()

        if not bonus_config:
            return Response({"error": "Bonus configuration not found"}, status=status.HTTP_400_BAD_REQUEST)

        if referral.registration_bonus_credited:
            return Response({"error": "Bonus already credited"}, status=status.HTTP_400_BAD_REQUEST)

        # Get or create the wallet for the referrer
        wallet, _ = Wallet.objects.get_or_create(user=referral.referrer)

        expires_at = now() + timedelta(days=bonus_config.bonus_expiry_days)

        # Create a transaction for the referral bonus
        WalletTransaction.objects.create(
            wallet=wallet,
            transaction_type=TRANSACTION_TYPE_BONUS,
            amount=bonus_config.registration_bonus,
            description="Admin Credited Referral Bonus",
            expires_at=expires_at,
            website=referral.website,
        )

        # Mark the referral as credited
        referral.registration_bonus_credited = True
        referral.save()

        return Response({"message": "Bonus credited successfully"}, status=status.HTTP_200_OK)
from rest_framework import viewsets, permissions, status, pagination
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.utils.timezone import now
from django.utils.dateparse import parse_date
from django.db.models import Count, Sum, Q
from datetime import timedelta

from .models import Referral, ReferralBonusConfig, ReferralCode
from .serializers import ReferralSerializer, ReferralBonusConfigSerializer, ReferralCodeSerializer
from wallet.models import Wallet, WalletTransaction
from users.permissions import IsAdminUser  # Only admins can access

class LargeResultsSetPagination(pagination.PageNumberPagination):
    """Pagination for large admin reports"""
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 500

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
        """Generate a referral code for the authenticated user."""
        user = request.user
        website = request.data.get("website")  # Website must be provided

        if not website:
            return Response({"error": "Website is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if user already has a referral code for the website
        referral_code, created = ReferralCode.objects.get_or_create(user=user, website=website)

        if not created:
            return Response(
                {"message": f"Referral code already exists: {referral_code.code}"},
                status=status.HTTP_200_OK
            )

        # Generate a unique code
        referral_code.code = ReferralCode.generate_unique_code(user, website)
        referral_code.save()

        return Response({"message": f"Referral code generated: {referral_code.code}"}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='credit-bonus')
    def credit_referral_bonus(self, request):
        """
        Credit referral bonuses for a successful referral.
        Only credited if the referred user places and completes an order without refunds.
        """
        referral_id = request.data.get("referral_id")
        referral = get_object_or_404(Referral.objects.select_related("referrer"), id=referral_id)
        bonus_config = ReferralBonusConfig.objects.filter(website=referral.website).first()

        if not bonus_config:
            return Response({"error": "Referral bonus settings not found."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the referred user completed an order
        if not referral.first_order_referral_bonus_credited:
            return Response({"error": "Referral bonus can only be credited after the referred user places and pays for their order in full."},
                            status=status.HTTP_400_BAD_REQUEST)

        wallet, _ = Wallet.objects.get_or_create(user=referral.referrer)

        expires_at = now() + timedelta(days=bonus_config.bonus_expiry_days)

        WalletTransaction.objects.create(
            wallet=wallet,
            transaction_type='referral_bonus',
            amount=bonus_config.registration_referral_bonus,
            description="Referral Bonus: Successful Registration",
            expires_at=expires_at,
            website=referral.website,
        )

        referral.registration_referral_bonus_credited = True
        referral.save()
        return Response({"message": "Referral bonus credited successfully!"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='stats')
    def referral_stats(self, request):
        """Get referral stats for the logged-in user."""
        user = request.user
        website = request.query_params.get("website")

        if not website:
            return Response({"error": "Website is required"}, status=status.HTTP_400_BAD_REQUEST)

        referral_code = ReferralCode.objects.filter(user=user, website=website).first()
        referral_link = referral_code.get_referral_link() if referral_code else None

        referrals = Referral.objects.filter(referrer=user, website=website)
        referred_count = referrals.count()
        ordered_count = referrals.filter(first_order_referral_bonus_credited=True).count()

        return Response({
            "total_referred": referred_count,
            "completed_orders": ordered_count,
            "referral_code": referral_code.code if referral_code else None,
            "referral_link": referral_link,
        })

    @action(detail=False, methods=["POST"], url_path="apply-bonus")
    def apply_referral_bonus(self, request):
        """
        Apply referral bonus at checkout.
        Bonus applies if the referred user’s order meets the criteria.
        """
        user = request.user
        bonus_config = ReferralBonusConfig.objects.first()

        if not bonus_config:
            return Response({"error": "Referral bonuses are not configured"}, status=status.HTTP_400_BAD_REQUEST)

        # Placeholder logic to apply referral bonus if order criteria met
        return Response({"message": "Referral bonus applied successfully"})


class ReferralBonusConfigViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing referral bonus configurations.
    """
    permission_classes = [permissions.IsAdminUser]
    serializer_class = ReferralBonusConfigSerializer
    queryset = ReferralBonusConfig.objects.all()


class ReferralAdminViewSet(viewsets.ViewSet):
    """RESTful API for Referral Management (Admin Only)"""
    permission_classes = [IsAdminUser]
    pagination_class = LargeResultsSetPagination

    def filter_by_date_and_website(self, request, queryset):
        """Filter referrals by date range & website"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        website = request.query_params.get('website')

        if start_date:
            queryset = queryset.filter(created_at__gte=parse_date(start_date))
        if end_date:
            queryset = queryset.filter(created_at__lte=parse_date(end_date))
        if website:
            queryset = queryset.filter(website=website)

        return queryset

    @action(detail=False, methods=['get'], url_path='top-referrers')
    def top_referrers(self, request):
        """Get top referrers (filtered by date & website)"""
        queryset = Referral.objects.values("referrer__username") \
            .annotate(total_referrals=Count("id")) \
            .order_by("-total_referrals")
        queryset = self.filter_by_date_and_website(request, queryset)

        return Response(queryset)

    @action(detail=False, methods=['get'], url_path='top-earners')
    def top_earners(self, request):
        """Get top referrers by earned bonuses"""
        queryset = Referral.objects.values("referrer__username") \
            .annotate(total_earned=Sum("wallettransaction__amount")) \
            .order_by("-total_earned")
        queryset = self.filter_by_date_and_website(request, queryset)

        return Response(queryset)

    @action(detail=False, methods=['get'], url_path='completed-orders')
    def completed_orders(self, request):
        """Get referrers with most completed referral orders"""
        queryset = Referral.objects.values("referrer__username") \
            .annotate(completed_orders=Count("id", filter=Q(first_order_bonus_credited=True))) \
            .order_by("-completed_orders")
        queryset = self.filter_by_date_and_website(request, queryset)

        return Response(queryset)

    @action(detail=False, methods=['post'], url_path='credit-bonus')
    def credit_bonus(self, request):
        """Admin manually credits bonus for a referral."""
        referral_id = request.data.get("referral_id")
        referral = get_object_or_404(Referral.objects.select_related("referrer"), id=referral_id)
        
        # Fetch referral bonus config for the same website
        bonus_config = ReferralBonusConfig.objects.filter(website=referral.website).first()
        
        if not bonus_config:
            return Response({"error": "Bonus configuration not found"}, status=status.HTTP_400_BAD_REQUEST)

        if referral.registration_bonus_credited:
            return Response({"error": "Bonus already credited"}, status=status.HTTP_400_BAD_REQUEST)

        # Get or create the wallet for the referrer
        wallet, _ = Wallet.objects.get_or_create(user=referral.referrer)

        expires_at = now() + timedelta(days=bonus_config.bonus_expiry_days)

        # Create a transaction for the referral bonus
        WalletTransaction.objects.create(
            wallet=wallet,
            transaction_type='bonus',
            amount=bonus_config.registration_bonus,
            description="Admin Credited Referral Bonus",
            expires_at=expires_at,
            website=referral.website,
        )

        # Mark the referral as credited
        referral.registration_bonus_credited = True
        referral.save()

        return Response({"message": "Bonus credited successfully"}, status=status.HTTP_200_OK)