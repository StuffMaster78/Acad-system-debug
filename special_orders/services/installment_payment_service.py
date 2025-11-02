import logging
from datetime import timedelta
from django.core.exceptions import PermissionDenied
from special_orders.models import InstallmentPayment


logger = logging.getLogger("installments")

class InstallmentPaymentService:
    """
    Handles installment generation and payment tracking for special orders.
    """

    @staticmethod
    def generate_installments(order):
        """
        Generates installments based on order type and deposit requirements.
        
        - For predefined orders: Creates a single installment for full amount 
          (since deposit_required = total_cost)
        - For estimated orders: Creates two installments (deposit + balance)
          based on deposit_required amount
        
        Args:
            order (SpecialOrder): The order for which to generate installments.
        """
        if not order.total_cost or not order.deposit_required:
            return

        # Check if installments already exist (avoid duplicates)
        if order.installments.exists():
            logger.warning(
                f"Installments already exist for order #{order.id}. Skipping generation."
            )
            return

        installments = []
        
        # For predefined orders: deposit_required equals total_cost (full payment upfront)
        if order.order_type == 'predefined' and order.deposit_required == order.total_cost:
            # Single installment for full amount
            installments.append(
                InstallmentPayment(
                    special_order=order,
                    amount_due=order.total_cost,
                    due_date=order.created_at.date()
                )
            )
        else:
            # For estimated orders: deposit + balance split
            deposit_amount = order.deposit_required
            balance_amount = order.total_cost - deposit_amount
            
            # First installment: deposit (due immediately)
            installments.append(
                InstallmentPayment(
                    special_order=order,
                    amount_due=deposit_amount,
                    due_date=order.created_at.date()
                )
            )
            
            # Second installment: balance (due in 7 days, if balance exists)
            if balance_amount > 0:
                installments.append(
                    InstallmentPayment(
                        special_order=order,
                        amount_due=balance_amount,
                        due_date=order.created_at.date() + timedelta(days=7)
                    )
                )
        
        if installments:
            InstallmentPayment.objects.bulk_create(installments)
            logger.info(
                f"Generated {len(installments)} installment(s) for order #{order.id}"
            )

    @staticmethod
    def create_installment(special_order, due_date, amount_due):
        """
        Creates a new installment payment for a special order.

        Args:
            special_order (SpecialOrder): The related special order.
            due_date (date): Due date of the installment.
            amount_due (float): The installment amount.

        Returns:
            InstallmentPayment: The created installment payment.
        """
        return InstallmentPayment.objects.create(
            special_order=special_order,
            due_date=due_date,
            amount_due=amount_due
        )

    @staticmethod
    def mark_installment_as_paid(installment):
        """
        Marks the given installment as paid.

        Args:
            installment (InstallmentPayment): Installment to update.

        Returns:
            InstallmentPayment: The updated installment object.
        """
        installment.is_paid = True
        installment.save()
        return installment

    def get_user_installments(user):
        """
        Return installments visible to the user.
        Admins see all. Clients see their own.
        """
        if user.is_staff:
            return InstallmentPayment.objects.all()
        return InstallmentPayment.objects.filter(special_order__client=user)


    def create_installment(serializer, user):
        """
        Create an installment if user owns the linked special order.
        """
        special_order = serializer.validated_data['special_order']
        if special_order.client != user:
            raise PermissionDenied("You do not own this order.")
        return serializer.save()

    def validate_and_save_installment(serializer, user):
        """
        Validate and save an installment payment only if the client owns the order.
        """
        special_order = serializer.validated_data['special_order']

        if special_order.client != user:
            message = f"User {user.username} is not authorized to pay for order #{special_order.id}."
            logger.warning(message)
            raise PermissionDenied(message)

        serializer.save()
        logger.info(
            f"Installment payment of ${serializer.validated_data['amount_due']} saved for order #{special_order.id}."
        )