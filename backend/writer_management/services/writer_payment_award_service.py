"""
Streamlined service for awarding writer bonuses and payments.
Allows admin to manually set amounts and optionally add directly to wallet.
Writers cannot see client payment amounts.
"""
import logging
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from special_orders.models import WriterBonus
from class_management.class_payment import ClassWriterPayment, ClassPayment
from wallet.models import Wallet, WalletTransaction
from websites.utils import get_current_website

logger = logging.getLogger(__name__)
User = get_user_model()


class WriterPaymentAwardService:
    """
    Streamlined service for awarding writer bonuses and payments.
    """
    
    @staticmethod
    @transaction.atomic
    def award_bonus(
        writer_id: int,
        amount: Decimal,
        category: str = 'other',
        reason: str = '',
        special_order_id: int = None,
        class_bundle_id: int = None,
        add_to_wallet: bool = False,
        website=None,
        admin_user=None
    ) -> dict:
        """
        Award a bonus to a writer.
        
        Args:
            writer_id: Writer user ID
            amount: Bonus amount
            category: Bonus category (performance, order_completion, client_tip, class_payment, other)
            reason: Reason for bonus
            special_order_id: Optional special order ID
            class_bundle_id: Optional class bundle ID
            add_to_wallet: If True, add directly to writer's wallet
            website: Website context
            admin_user: Admin user awarding the bonus
        
        Returns:
            dict: Created bonus info
        """
        try:
            writer = User.objects.get(id=writer_id, role='writer', is_active=True)
        except User.DoesNotExist:
            raise ValidationError("Writer not found or not active")
        
        if not website:
            raise ValidationError("Website context is required")
        
        # Validate amount
        if amount <= 0:
            raise ValidationError("Amount must be greater than zero")
        
        # Validate category
        valid_categories = ['performance', 'order_completion', 'client_tip', 'class_payment', 'other']
        if category not in valid_categories:
            raise ValidationError(f"Invalid category. Must be one of: {', '.join(valid_categories)}")
        
        # Create WriterBonus
        bonus = WriterBonus.objects.create(
            website=website,
            writer=writer,
            special_order_id=special_order_id,
            amount=amount,
            category=category,
            reason=reason or f"Bonus awarded by admin",
            is_paid=add_to_wallet,  # Mark as paid if adding to wallet
        )
        
        result = {
            'bonus_id': bonus.id,
            'writer_id': writer.id,
            'writer_username': writer.username,
            'amount': float(amount),
            'category': category,
            'is_paid': bonus.is_paid,
            'added_to_wallet': False,
        }
        
        # Add to wallet if requested
        if add_to_wallet:
            WriterPaymentAwardService._add_to_wallet(
                writer=writer,
                amount=amount,
                website=website,
                description=reason or f"Bonus: {category}",
                bonus=bonus,
                admin_user=admin_user
            )
            result['added_to_wallet'] = True
            result['wallet_balance'] = float(WriterPaymentAwardService._get_wallet_balance(writer, website))
        
        logger.info(
            f"Bonus awarded: ${amount} to writer {writer.id} "
            f"(category: {category}, wallet: {add_to_wallet})"
        )
        
        return result
    
    @staticmethod
    @transaction.atomic
    def award_class_payment(
        class_payment_id: int,
        amount: Decimal = None,
        add_to_wallet: bool = False,
        website=None,
        admin_user=None
    ) -> dict:
        """
        Award payment to writer for a class bundle.
        If amount is not provided, uses the writer_compensation_amount from ClassPayment.
        
        Args:
            class_payment_id: ClassPayment ID
            amount: Payment amount (optional, uses class_payment.writer_compensation_amount if not provided)
            add_to_wallet: If True, add directly to writer's wallet
            website: Website context
            admin_user: Admin user awarding the payment
        
        Returns:
            dict: Payment info
        """
        try:
            class_payment = ClassPayment.objects.select_related(
                'class_bundle', 'assigned_writer', 'website'
            ).get(id=class_payment_id)
        except ClassPayment.DoesNotExist:
            raise ValidationError("Class payment not found")
        
        if not class_payment.assigned_writer:
            raise ValidationError("No writer assigned to this class bundle")
        
        writer = class_payment.assigned_writer
        website = website or class_payment.website
        
        # Use provided amount or class payment's writer compensation
        if amount is None:
            amount = class_payment.writer_compensation_amount or Decimal('0.00')
        
        if amount <= 0:
            raise ValidationError("Amount must be greater than zero")
        
        # Check if payment already exists
        existing_payment = ClassWriterPayment.objects.filter(
            class_payment=class_payment,
            is_paid=False
        ).first()
        
        if existing_payment:
            # Update existing payment
            existing_payment.amount = amount
            existing_payment.is_paid = add_to_wallet
            if add_to_wallet:
                existing_payment.paid_at = timezone.now()
            existing_payment.save()
            
            # Update or create WriterBonus
            if existing_payment.writer_bonus:
                bonus = existing_payment.writer_bonus
                bonus.amount = amount
                bonus.is_paid = add_to_wallet
                bonus.save()
            else:
                bonus = WriterBonus.objects.create(
                    website=website,
                    writer=writer,
                    special_order=None,
                    amount=amount,
                    category='class_payment',
                    reason=f"Payment for Class Bundle #{class_payment.class_bundle.id}",
                    is_paid=add_to_wallet,
                )
                existing_payment.writer_bonus = bonus
                existing_payment.save()
        else:
            # Create new payment
            bonus = WriterBonus.objects.create(
                website=website,
                writer=writer,
                special_order=None,
                amount=amount,
                category='class_payment',
                reason=f"Payment for Class Bundle #{class_payment.class_bundle.id}",
                is_paid=add_to_wallet,
            )
            
            existing_payment = ClassWriterPayment.objects.create(
                class_payment=class_payment,
                writer_bonus=bonus,
                amount=amount,
                payment_type='full',
                is_paid=add_to_wallet,
                paid_at=timezone.now() if add_to_wallet else None,
            )
        
        result = {
            'payment_id': existing_payment.id,
            'bonus_id': bonus.id,
            'class_payment_id': class_payment.id,
            'class_bundle_id': class_payment.class_bundle.id,
            'writer_id': writer.id,
            'writer_username': writer.username,
            'amount': float(amount),
            'is_paid': existing_payment.is_paid,
            'added_to_wallet': False,
        }
        
        # Add to wallet if requested
        if add_to_wallet:
            WriterPaymentAwardService._add_to_wallet(
                writer=writer,
                amount=amount,
                website=website,
                description=f"Class payment for Bundle #{class_payment.class_bundle.id}",
                bonus=bonus,
                admin_user=admin_user
            )
            result['added_to_wallet'] = True
            result['wallet_balance'] = float(WriterPaymentAwardService._get_wallet_balance(writer, website))
            
            # Update class payment status
            class_payment.writer_payment_status = 'paid'
            class_payment.save()
        
        logger.info(
            f"Class payment awarded: ${amount} to writer {writer.id} "
            f"for bundle {class_payment.class_bundle.id} (wallet: {add_to_wallet})"
        )
        
        return result
    
    @staticmethod
    @transaction.atomic
    def pay_bonus(
        bonus_id: int,
        add_to_wallet: bool = True,
        website=None,
        admin_user=None
    ) -> dict:
        """
        Mark a bonus as paid and optionally add to wallet.
        
        Args:
            bonus_id: WriterBonus ID
            add_to_wallet: If True, add to writer's wallet
            website: Website context
            admin_user: Admin user processing the payment
        
        Returns:
            dict: Payment info
        """
        try:
            bonus = WriterBonus.objects.select_related('writer', 'website').get(id=bonus_id)
        except WriterBonus.DoesNotExist:
            raise ValidationError("Bonus not found")
        
        if bonus.is_paid:
            raise ValidationError("Bonus is already paid")
        
        website = website or bonus.website
        writer = bonus.writer
        
        # Mark as paid
        bonus.is_paid = True
        bonus.save()
        
        result = {
            'bonus_id': bonus.id,
            'writer_id': writer.id,
            'writer_username': writer.username,
            'amount': float(bonus.amount),
            'category': bonus.category,
            'added_to_wallet': False,
        }
        
        # Add to wallet if requested
        if add_to_wallet:
            WriterPaymentAwardService._add_to_wallet(
                writer=writer,
                amount=bonus.amount,
                website=website,
                description=bonus.reason or f"Bonus payment: {bonus.category}",
                bonus=bonus,
                admin_user=admin_user
            )
            result['added_to_wallet'] = True
            result['wallet_balance'] = float(WriterPaymentAwardService._get_wallet_balance(writer, website))
        
        logger.info(f"Bonus {bonus_id} marked as paid (wallet: {add_to_wallet})")
        
        return result
    
    @staticmethod
    def _add_to_wallet(writer, amount, website, description, bonus=None, admin_user=None):
        """Add amount to writer's wallet."""
        wallet, created = Wallet.objects.get_or_create(
            user=writer,
            website=website,
            defaults={'balance': Decimal('0.00')}
        )
        
        wallet.balance += amount
        wallet.save()
        
        # Create transaction record
        WalletTransaction.objects.create(
            wallet=wallet,
            website=website,
            transaction_type='credit',
            amount=amount,
            description=description,
            source='bonus' if bonus else 'admin_payment',
            note=f"Bonus ID: {bonus.id}" if bonus else "Admin payment",
        )
    
    @staticmethod
    def _get_wallet_balance(writer, website):
        """Get writer's wallet balance."""
        try:
            wallet = Wallet.objects.get(user=writer, website=website)
            return wallet.balance
        except Wallet.DoesNotExist:
            return Decimal('0.00')

