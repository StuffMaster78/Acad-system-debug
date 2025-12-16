from rest_framework import viewsets, permissions, status, pagination
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.utils.timezone import now
from django.utils.dateparse import parse_date
from django.db.models import Count, Sum, Q
from datetime import timedelta
from rest_framework.views import APIView
from .models import Referral, ReferralBonusConfig, ReferralCode, ReferralStats
from .serializers import ReferralSerializer, ReferralBonusConfigSerializer, ReferralCodeSerializer
from wallet.models import Wallet, WalletTransaction
from authentication.permissions import IsAdminOrSuperAdmin
User = settings.AUTH_USER_MODEL 


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
    queryset = Referral.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ReferralSerializer

    def get_queryset(self):
        """Filter referrals by the authenticated user. Only clients can view their referrals."""
        user = self.request.user
        if user.role != 'client':
            # Non-clients get empty queryset
            return Referral.objects.none()
        return Referral.objects.filter(referrer=user)

    @action(detail=False, methods=['post'], url_path='generate-code')
    def generate_code(self, request):
        """Generate a referral code for the authenticated user. Only clients can generate codes."""
        user = request.user
        
        # Only clients can generate referral codes
        if user.role != 'client':
            return Response({
                "error": "Only clients can generate referral codes. Your role is not authorized for this action.",
                "user_role": user.role
            }, status=status.HTTP_403_FORBIDDEN)
        
        website_id = request.data.get("website")  # Website ID must be provided

        if not website_id:
            return Response({"error": "Website is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            from websites.models import Website
            website = Website.objects.get(id=website_id)
        except Website.DoesNotExist:
            return Response({"error": "Website not found"}, status=status.HTTP_404_NOT_FOUND)

        # Check if user already has a referral code (OneToOneField means only one per user)
        try:
            existing_code = ReferralCode.objects.get(user=user, website=website)
            return Response({
                "message": f"Referral code already exists: {existing_code.code}",
                "code": existing_code.code,
                "already_exists": True
            }, status=status.HTTP_200_OK)
        except ReferralCode.DoesNotExist:
            pass

        # Generate a unique code using the service
        from referrals.services.referral_service import ReferralService
        code = ReferralService.generate_unique_code(user, website)
        
        # Create referral code
        referral_code = ReferralCode.objects.create(
            user=user,
            website=website,
            code=code
        )

        return Response({
            "message": f"Referral code generated successfully: {referral_code.code}",
            "code": referral_code.code,
            "already_exists": False
        }, status=status.HTTP_201_CREATED)

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
            amount=bonus_config.first_order_bonus,
            description="Referral Bonus: Successful Registration",
            expires_at=expires_at,
            website=referral.website,
        )

        referral.first_order_bonus_credited = True
        referral.save()
        return Response({"message": "Referral bonus credited successfully!"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='stats')
    def referral_stats(self, request):
        """Get referral stats for the logged-in user."""
        user = request.user
        website = request.query_params.get("website")

        if not website:
            return Response({"error": "Website is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            from websites.models import Website
            website_obj = Website.objects.get(id=website)
        except (Website.DoesNotExist, ValueError):
            return Response({"error": "Website not found"}, status=status.HTTP_404_NOT_FOUND)

        referral_code = ReferralCode.objects.filter(user=user, website=website_obj).first()
        referral_link = referral_code.get_referral_link() if referral_code else None

        referrals = Referral.objects.filter(referrer=user, website=website_obj)
        referred_count = referrals.count()
        ordered_count = referrals.filter(first_order_referral_bonus_credited=True).count()

        return Response({
            "total_referred": referred_count,
            "completed_orders": ordered_count,
            "referral_code": referral_code.code if referral_code else None,
            "referral_link": referral_link,
        })

    @action(detail=False, methods=['post'], url_path='refer-by-email')
    def refer_by_email(self, request):
        """Send a referral invitation to someone who doesn't have an account yet."""
        user = request.user
        
        # Only clients can create referrals
        if user.role != 'client':
            return Response({
                "error": "Only clients can create referrals. Your role is not authorized for this action.",
                "user_role": user.role
            }, status=status.HTTP_403_FORBIDDEN)
        
        email = request.data.get("email")
        website_id = request.data.get("website")

        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        if not website_id:
            return Response({"error": "Website is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            from websites.models import Website
            website = Website.objects.get(id=website_id)
        except Website.DoesNotExist:
            return Response({"error": "Website not found"}, status=status.HTTP_404_NOT_FOUND)

        # Check if user already exists - if they do, they should use the referral link directly
        try:
            existing_user = User.objects.get(email=email)
            return Response({
                "error": f"User with email {email} already has an account. Please share your referral link with them instead.",
                "email": email,
                "referral_link": None  # Will be populated below if they have a code
            }, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            pass  # Good, they don't have an account yet
        except User.MultipleObjectsReturned:
            return Response({
                "error": f"Multiple accounts found for {email}. Please contact support.",
                "email": email
            }, status=status.HTTP_400_BAD_REQUEST)

        # Don't allow self-referral
        if user.email.lower() == email.lower():
            return Response({
                "error": "You cannot refer yourself."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check if invitation already exists
        from .models import PendingReferralInvitation
        existing_invitation = PendingReferralInvitation.objects.filter(
            referrer=user,
            referee_email=email.lower(),
            website=website,
            converted=False
        ).first()

        if existing_invitation:
            return Response({
                "error": f"An invitation has already been sent to {email}.",
                "invitation_id": existing_invitation.id,
                "sent_at": existing_invitation.sent_at
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get or create referral code
        referral_code_obj = ReferralCode.objects.filter(user=user, website=website).first()
        if not referral_code_obj:
            # Generate referral code if it doesn't exist
            from referrals.services.referral_service import ReferralService
            code = ReferralService.generate_unique_code(user, website)
            referral_code_obj = ReferralCode.objects.create(
                user=user,
                website=website,
                code=code
            )
        
        referral_code = referral_code_obj.code
        referral_link = referral_code_obj.get_referral_link()

        # Create pending invitation
        invitation = PendingReferralInvitation.objects.create(
            referrer=user,
            referee_email=email.lower(),
            website=website,
            referral_code=referral_code,
            referral_link=referral_link,
            invitation_sent=False
        )

        # Send invitation email
        try:
            from django.core.mail import send_mail
            from django.conf import settings
            
            subject = f"{user.username} invited you to join {website.name}"
            message = f"""
Hello!

{user.username} has invited you to join {website.name}!

Sign up using this special referral link to get started:
{referral_link}

When you sign up and place your first order, both you and {user.username} will receive rewards!

Best regards,
The {website.name} Team
"""
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            invitation.invitation_sent = True
            invitation.save()
        except Exception as e:
            # Log error but don't fail the request
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to send referral invitation email to {email}: {str(e)}")

        return Response({
            "message": f"Referral invitation sent to {email}! They will receive an email with your referral link.",
            "invitation": {
                "id": invitation.id,
                "email": invitation.referee_email,
                "referral_link": referral_link,
                "sent_at": invitation.sent_at
            }
        }, status=status.HTTP_201_CREATED)

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
    permission_classes = [IsAdminOrSuperAdmin]
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
from authentication.permissions import IsAdminOrSuperAdmin  # Only admins can access

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
        """Generate a referral code for the authenticated user. Only clients can generate codes."""
        user = request.user
        
        # Only clients can generate referral codes
        if user.role != 'client':
            return Response({
                "error": "Only clients can generate referral codes. Your role is not authorized for this action.",
                "user_role": user.role
            }, status=status.HTTP_403_FORBIDDEN)
        
        website_id = request.data.get("website")  # Website ID must be provided

        if not website_id:
            return Response({"error": "Website is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            from websites.models import Website
            website = Website.objects.get(id=website_id)
        except Website.DoesNotExist:
            return Response({"error": "Website not found"}, status=status.HTTP_404_NOT_FOUND)

        # Check if user already has a referral code (OneToOneField means only one per user)
        try:
            existing_code = ReferralCode.objects.get(user=user, website=website)
            return Response({
                "message": f"Referral code already exists: {existing_code.code}",
                "code": existing_code.code,
                "already_exists": True
            }, status=status.HTTP_200_OK)
        except ReferralCode.DoesNotExist:
            pass

        # Generate a unique code using the service
        from referrals.services.referral_service import ReferralService
        code = ReferralService.generate_unique_code(user, website)
        
        # Create referral code
        referral_code = ReferralCode.objects.create(
            user=user,
            website=website,
            code=code
        )

        return Response({
            "message": f"Referral code generated successfully: {referral_code.code}",
            "code": referral_code.code,
            "already_exists": False
        }, status=status.HTTP_201_CREATED)

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
            amount=bonus_config.first_order_bonus,
            description="Referral Bonus: Successful Registration",
            expires_at=expires_at,
            website=referral.website,
        )

        referral.first_order_bonus_credited = True
        referral.save()
        return Response({"message": "Referral bonus credited successfully!"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='stats')
    def referral_stats(self, request):
        """Get referral stats for the logged-in user."""
        user = request.user
        website = request.query_params.get("website")

        if not website:
            return Response({"error": "Website is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            from websites.models import Website
            website_obj = Website.objects.get(id=website)
        except (Website.DoesNotExist, ValueError):
            return Response({"error": "Website not found"}, status=status.HTTP_404_NOT_FOUND)

        referral_code = ReferralCode.objects.filter(user=user, website=website_obj).first()
        referral_link = referral_code.get_referral_link() if referral_code else None

        referrals = Referral.objects.filter(referrer=user, website=website_obj)
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
    permission_classes = [IsAdminOrSuperAdmin]
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
    
class ReferralCodeViewSet(viewsets.ModelViewSet):
    queryset = ReferralCode.objects.all()
    serializer_class = ReferralCodeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter codes based on user role."""
        user = self.request.user
        if user.role == 'client':
            # Clients can only see their own code
            return ReferralCode.objects.filter(user=user)
        elif user.is_staff or user.role in ['admin', 'superadmin']:
            # Admins can see all codes
            return ReferralCode.objects.all()
        else:
            # Other roles see nothing
            return ReferralCode.objects.none()
    
    @action(detail=False, methods=['get'], url_path='my-code')
    def my_code(self, request):
        """
        Get the authenticated client's referral code with usage statistics.
        Only available for clients.
        """
        user = request.user
        
        if user.role != 'client':
            return Response({
                "error": "Only clients can access their referral code."
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get user's website
        website = getattr(user, 'website', None)
        if not website:
            # Try to get from query params
            website_id = request.query_params.get('website')
            if website_id:
                try:
                    from websites.models import Website
                    website = Website.objects.get(id=website_id)
                except Website.DoesNotExist:
                    return Response({
                        "error": "Website not found"
                    }, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({
                    "error": "User must have a website assigned or provide website parameter"
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get or create referral code
        referral_code = ReferralCode.objects.filter(user=user, website=website).first()
        
        if not referral_code:
            # Auto-generate if doesn't exist
            from referrals.services.referral_service import ReferralService
            code = ReferralService.generate_unique_code(user, website)
            referral_code = ReferralCode.objects.create(
                user=user,
                website=website,
                code=code
            )
        
        # Serialize with usage stats
        serializer = ReferralCodeSerializer(referral_code)
        return Response(serializer.data)


class ReferralStatsViewSet(viewsets.ViewSet):
    permission_classes = [IsAdminOrSuperAdmin]

    def list(self, request):
        # Dummy data – replace with real stats
        return Response({
            "total_referrals": 10,
            "successful_referrals": 6,
            "pending_referrals": 4,
        })
    
class ReferralBonusDecayViewSet(viewsets.ViewSet):
    permission_classes = [IsAdminOrSuperAdmin]

    def list(self, request):
        return Response({
            "status": "Referral bonus decay placeholder working."
        })
    

class ReferralReportsAPI(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def get(self, request):
        return Response({
            "status": "Referral reports coming soon.",
        })
    
class AwardReferralBonusAPI(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def post(self, request):
        """
        Manually award a referral bonus to a referee.
        Admin must pass 'referral_id' in the request data.
        """
        referral_id = request.data.get("referral_id")
        if not referral_id:
            return Response(
                {"detail": "Missing 'referral_id' in request."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            referral = Referral.objects.get(id=referral_id, is_deleted=False)
        except Referral.DoesNotExist:
            return Response(
                {"detail": "Referral not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        if referral.bonus_awarded:
            return Response(
                {"detail": "Bonus already awarded for this referral."},
                status=status.HTTP_400_BAD_REQUEST
            )

        referral.award_bonus()

        return Response(
            {"detail": "Referral bonus awarded successfully."},
            status=status.HTTP_200_OK
        )