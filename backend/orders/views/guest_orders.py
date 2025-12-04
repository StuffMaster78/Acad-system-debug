"""
Guest order endpoints for anonymous checkout.
"""
from django.utils import timezone
from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string
from hashlib import sha256
from datetime import timedelta

from websites.models import Website, GuestAccessToken
from client_management.models import ClientProfile
from orders.models import Order
from orders.services.create_order_service import CreateOrderService
from orders.services.pricing_calculator import PricingCalculatorService

User = get_user_model()


class GuestOrderViewSet(viewsets.ViewSet):
    """
    ViewSet for guest order creation and email verification.
    """
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['post'], url_path='start')
    def start(self, request):
        """
        Initiate a guest order.
        
        Expected payload:
        {
            "website_id": int,
            "email": str,
            "order_data": {
                "topic": str,
                "paper_type_id": int,
                "number_of_pages": int,
                "client_deadline": str (ISO datetime),
                "order_instructions": str,
                ... (other order fields)
            }
        }
        
        Returns:
        {
            "order_id": int (if email verification not required),
            "verification_required": bool,
            "verification_token": str (if verification required),
            "message": str
        }
        """
        website_id = request.data.get('website_id')
        email = request.data.get('email', '').strip().lower()
        order_data = request.data.get('order_data', {})
        
        if not website_id:
            return Response(
                {"detail": "website_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not email:
            return Response(
                {"detail": "email is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            website = Website.objects.get(id=website_id, is_active=True, is_deleted=False)
        except Website.DoesNotExist:
            return Response(
                {"detail": "Website not found or inactive"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if guest checkout is enabled
        if not website.allow_guest_checkout:
            return Response(
                {"detail": "Guest checkout is not enabled for this website"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Validate order data
        required_fields = ['topic', 'paper_type_id', 'number_of_pages', 'client_deadline', 'order_instructions']
        missing = [f for f in required_fields if not order_data.get(f)]
        if missing:
            return Response(
                {"detail": f"Missing required order fields: {', '.join(missing)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check order amount limit
        # Calculate estimated price
        try:
            estimated_price = PricingCalculatorService.calculate_total_price(
                website=website,
                paper_type_id=order_data.get('paper_type_id'),
                number_of_pages=order_data.get('number_of_pages', 0),
                number_of_slides=order_data.get('number_of_slides', 0),
                academic_level_id=order_data.get('academic_level_id'),
                type_of_work_id=order_data.get('type_of_work_id'),
                deadline=order_data.get('client_deadline'),
                extra_services=order_data.get('extra_services', []),
            )
        except Exception as e:
            return Response(
                {"detail": f"Error calculating price: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if website.guest_max_order_amount and estimated_price > website.guest_max_order_amount:
            return Response(
                {
                    "detail": f"Order amount (${estimated_price}) exceeds maximum allowed for guest orders (${website.guest_max_order_amount})"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check deadline restriction
        from datetime import datetime
        try:
            deadline = datetime.fromisoformat(order_data['client_deadline'].replace('Z', '+00:00'))
            if deadline.tzinfo is None:
                deadline = timezone.make_aware(deadline)
            
            hours_until_deadline = (deadline - timezone.now()).total_seconds() / 3600
            if hours_until_deadline < website.guest_block_urgent_before_hours:
                return Response(
                    {
                        "detail": f"Guest orders cannot have deadlines sooner than {website.guest_block_urgent_before_hours} hours"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        except (ValueError, KeyError) as e:
            return Response(
                {"detail": f"Invalid deadline format: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get or create guest user
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': email,
                'role': 'client',
                'is_active': True,
            }
        )
        
        # Get or create client profile
        client_profile, profile_created = ClientProfile.objects.get_or_create(
            user=user,
            website=website,
            defaults={
                'is_guest': True,
            }
        )
        
        # Mark as guest if not already
        if not client_profile.is_guest:
            client_profile.is_guest = True
            client_profile.save(update_fields=['is_guest'])
        
        # If email verification is required
        if website.guest_requires_email_verification:
            # Generate verification token
            verification_token = get_random_string(64)
            token_hash = sha256(verification_token.encode()).hexdigest()
            
            # Store verification token (we can use a simple model or cache)
            # For now, we'll create a temporary GuestAccessToken for verification
            expires_at = timezone.now() + timedelta(hours=website.guest_magic_link_ttl_hours)
            
            # Delete any existing verification tokens for this user/website
            GuestAccessToken.objects.filter(
                website=website,
                user=user,
                scope=GuestAccessToken.SCOPE_ORDER
            ).delete()
            
            # Create new verification token
            guest_token = GuestAccessToken.objects.create(
                website=website,
                user=user,
                token_hash=token_hash,
                scope=GuestAccessToken.SCOPE_ORDER,
                expires_at=expires_at,
                created_ip=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
            )
            
            # Store order data temporarily (in a session or cache)
            # For simplicity, we'll store it in the token's metadata via a separate model
            # For now, we'll return the token and expect the frontend to resubmit with it
            
            # Send verification email
            verification_url = f"{settings.FRONTEND_URL}/guest-orders/verify?token={verification_token}"
            send_mail(
                subject="Verify your email to complete your order",
                message=f"Click this link to verify your email and complete your order: {verification_url}",
                from_email=website.default_sender_email or settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            
            return Response({
                "verification_required": True,
                "verification_token": verification_token,  # In production, don't return this
                "message": "Verification email sent. Please check your inbox.",
                "order_data": order_data,  # Frontend should resubmit with token
            }, status=status.HTTP_200_OK)
        
        # No verification required - create order immediately
        with transaction.atomic():
            order = CreateOrderService().create_order(
                user=user,
                website=website,
                **order_data
            )
        
        return Response({
            "order_id": order.id,
            "verification_required": False,
            "message": "Order created successfully",
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'], url_path='verify-email')
    def verify_email(self, request):
        """
        Verify email and create guest order.
        
        Expected payload:
        {
            "verification_token": str,
            "website_id": int,
            "order_data": {
                "topic": str,
                ... (order fields)
            }
        }
        """
        verification_token = request.data.get('verification_token')
        website_id = request.data.get('website_id')
        order_data = request.data.get('order_data', {})
        
        if not verification_token:
            return Response(
                {"detail": "verification_token is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not website_id:
            return Response(
                {"detail": "website_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            website = Website.objects.get(id=website_id, is_active=True, is_deleted=False)
        except Website.DoesNotExist:
            return Response(
                {"detail": "Website not found or inactive"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verify token
        token_hash = sha256(verification_token.encode()).hexdigest()
        
        try:
            guest_token = GuestAccessToken.objects.get(
                website=website,
                token_hash=token_hash,
                scope=GuestAccessToken.SCOPE_ORDER,
                expires_at__gt=timezone.now(),
            )
        except GuestAccessToken.DoesNotExist:
            return Response(
                {"detail": "Invalid or expired verification token"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Mark token as used
        guest_token.used_at = timezone.now()
        guest_token.save(update_fields=['used_at'])
        
        user = guest_token.user
        
        # Validate order data
        required_fields = ['topic', 'paper_type_id', 'number_of_pages', 'client_deadline', 'order_instructions']
        missing = [f for f in required_fields if not order_data.get(f)]
        if missing:
            return Response(
                {"detail": f"Missing required order fields: {', '.join(missing)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create order
        with transaction.atomic():
            order = CreateOrderService().create_order(
                user=user,
                website=website,
                **order_data
            )
        
        return Response({
            "order_id": order.id,
            "message": "Order created successfully",
        }, status=status.HTTP_201_CREATED)

