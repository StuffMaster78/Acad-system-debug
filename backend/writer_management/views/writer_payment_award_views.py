"""
Streamlined views for awarding writer bonuses and payments.
"""
import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from decimal import Decimal
from django.contrib.auth import get_user_model
from websites.utils import get_current_website
from writer_management.services.writer_payment_award_service import WriterPaymentAwardService

logger = logging.getLogger(__name__)
User = get_user_model()


class WriterPaymentAwardViewSet(viewsets.ViewSet):
    """
    Streamlined ViewSet for awarding writer bonuses and payments.
    Admin-only endpoints.
    """
    permission_classes = [IsAdminUser]
    
    @action(detail=False, methods=['post'], url_path='award-bonus')
    def award_bonus(self, request):
        """
        Award a bonus to a writer.
        
        Request body:
        {
            "writer_id": 123,
            "amount": 100.00,
            "category": "performance",  // performance, order_completion, client_tip, class_payment, other
            "reason": "Outstanding work",
            "special_order_id": 456,  // Optional
            "class_bundle_id": 789,  // Optional
            "add_to_wallet": true  // If true, add directly to wallet
        }
        """
        writer_id = request.data.get('writer_id')
        amount = request.data.get('amount')
        category = request.data.get('category', 'other')
        reason = request.data.get('reason', '')
        special_order_id = request.data.get('special_order_id')
        class_bundle_id = request.data.get('class_bundle_id')
        add_to_wallet = request.data.get('add_to_wallet', False)
        
        if not writer_id:
            return Response(
                {'error': 'writer_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not amount:
            return Response(
                {'error': 'amount is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            amount_decimal = Decimal(str(amount))
        except (ValueError, TypeError):
            return Response(
                {'error': 'Invalid amount format'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        website = get_current_website(request)
        
        try:
            result = WriterPaymentAwardService.award_bonus(
                writer_id=writer_id,
                amount=amount_decimal,
                category=category,
                reason=reason,
                special_order_id=special_order_id,
                class_bundle_id=class_bundle_id,
                add_to_wallet=add_to_wallet,
                website=website,
                admin_user=request.user
            )
            return Response(result, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.exception(f"Error awarding bonus: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'], url_path='award-class-payment')
    def award_class_payment(self, request):
        """
        Award payment to writer for a class bundle.
        
        Request body:
        {
            "class_payment_id": 123,
            "amount": 150.00,  // Optional, uses class_payment.writer_compensation_amount if not provided
            "add_to_wallet": true  // If true, add directly to wallet
        }
        """
        class_payment_id = request.data.get('class_payment_id')
        amount = request.data.get('amount')
        add_to_wallet = request.data.get('add_to_wallet', False)
        
        if not class_payment_id:
            return Response(
                {'error': 'class_payment_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        amount_decimal = None
        if amount:
            try:
                amount_decimal = Decimal(str(amount))
            except (ValueError, TypeError):
                return Response(
                    {'error': 'Invalid amount format'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        website = get_current_website(request)
        
        try:
            result = WriterPaymentAwardService.award_class_payment(
                class_payment_id=class_payment_id,
                amount=amount_decimal,
                add_to_wallet=add_to_wallet,
                website=website,
                admin_user=request.user
            )
            return Response(result, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.exception(f"Error awarding class payment: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'], url_path='pay-bonus')
    def pay_bonus(self, request):
        """
        Mark a bonus as paid and optionally add to wallet.
        
        Request body:
        {
            "bonus_id": 123,
            "add_to_wallet": true  // If true, add to writer's wallet
        }
        """
        bonus_id = request.data.get('bonus_id')
        add_to_wallet = request.data.get('add_to_wallet', True)
        
        if not bonus_id:
            return Response(
                {'error': 'bonus_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        website = get_current_website(request)
        
        try:
            result = WriterPaymentAwardService.pay_bonus(
                bonus_id=bonus_id,
                add_to_wallet=add_to_wallet,
                website=website,
                admin_user=request.user
            )
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception(f"Error paying bonus: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

