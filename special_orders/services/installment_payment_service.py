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
        Generates two installments: a 50% deposit and a 50% balance.
        
        Args:
            order (SpecialOrder): The order for which to generate installments.
        """
        if not order.total_cost:
            return

        InstallmentPayment.objects.bulk_create([
            InstallmentPayment(
                special_order=order,
                amount_due=order.total_cost / 2,
                due_date=order.created_at.date()
            ),
            InstallmentPayment(
                special_order=order,
                amount_due=order.total_cost / 2,
                due_date=order.created_at.date() + timedelta(days=7)
            ),
        ])

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