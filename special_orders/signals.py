from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from .models import SpecialOrder, InstallmentPayment
from order_communications.models import OrderMessageThread

User = get_user_model()  # Get the user model dynamically

# 🔹 Notify Admin When a New Special Order is Created
@receiver(post_save, sender=SpecialOrder)
def notify_admin_on_new_special_order(sender, instance, created, **kwargs):
    """
    Notify admins when a new special order is placed.
    """
    if created:
        admin_emails = list(User.objects.filter(is_staff=True).values_list('email', flat=True))
        if admin_emails:
            try:
                send_mail(
                    subject=f"New Special Order #{instance.id} Created",
                    message=f"A new special order has been placed by {instance.client.username}.",
                    from_email='no-reply@yourdomain.com',
                    recipient_list=admin_emails,
                    fail_silently=True,
                )
            except Exception as e:
                print(f"Error sending email to admins: {e}")

# 🔹 Notify Client When Order Status Changes
@receiver(post_save, sender=SpecialOrder)
def notify_client_on_order_status_change(sender, instance, created, **kwargs):
    """
    Notify the client when the status of their special order changes.
    """
    if not created:  # Only act on updates
        status = instance.status
        client_email = instance.client.email

        try:
            send_mail(
                subject=f"Order #{instance.id} Status Update",
                message=f"Your order status has been updated to '{status}'.",
                from_email='no-reply@yourdomain.com',
                recipient_list=[client_email],
                fail_silently=True,
            )
        except Exception as e:
            print(f"Error sending email to {client_email}: {e}")

# 🔹 Notify Admin & Client When Installment Payment is Made
@receiver(post_save, sender=InstallmentPayment)
def notify_payment_received(sender, instance, created, **kwargs):
    """
    Notify admin and client when an installment payment is made.
    """
    if created and instance.is_paid:
        client_email = instance.special_order.client.email
        admin_emails = list(User.objects.filter(is_staff=True).values_list('email', flat=True))

        try:
            # Notify Client
            send_mail(
                subject=f"Payment Received for Order #{instance.special_order.id}",
                message=f"Your installment of ${instance.amount_due} has been received for your order.",
                from_email='no-reply@yourdomain.com',
                recipient_list=[client_email],
                fail_silently=True,
            )

            # Notify Admin
            if admin_emails:
                send_mail(
                    subject=f"Installment Payment Received for Order #{instance.special_order.id}",
                    message=f"A payment of ${instance.amount_due} has been received for a special order.",
                    from_email='no-reply@yourdomain.com',
                    recipient_list=admin_emails,
                    fail_silently=True,
                )

        except Exception as e:
            print(f"Error sending payment notification emails: {e}")

# 🔹 Notify Client & Writer When Order is Completed
@receiver(post_save, sender=SpecialOrder)
def notify_on_order_completion(sender, instance, created, **kwargs):
    """
    Notify the client and writer when the order is marked as completed.
    """
    if not created and instance.status == 'completed':
        client_email = instance.client.email
        writer_email = instance.writer.email if instance.writer else None

        try:
            # Notify Client
            send_mail(
                subject=f"Your Order #{instance.id} is Completed",
                message=f"Your special order has been successfully completed.",
                from_email='no-reply@yourdomain.com',
                recipient_list=[client_email],
                fail_silently=True,
            )

            # Notify Writer (if assigned)
            if writer_email:
                send_mail(
                    subject=f"Order #{instance.id} Marked as Completed",
                    message=f"The order you worked on has been marked as completed.",
                    from_email='no-reply@yourdomain.com',
                    recipient_list=[writer_email],
                    fail_silently=True,
                )

        except Exception as e:
            print(f"Error sending order completion notifications: {e}")

# 🔹 Notify Client When Admin Overrides Payment
@receiver(post_save, sender=SpecialOrder)
def notify_client_on_admin_payment_override(sender, instance, created, **kwargs):
    """
    Notify client when admin manually marks an order as paid.
    """
    if not created and instance.admin_marked_paid:
        client_email = instance.client.email

        try:
            send_mail(
                subject=f"Payment Confirmation for Order #{instance.id}",
                message=f"An admin has manually confirmed your payment for this order.",
                from_email='no-reply@yourdomain.com',
                recipient_list=[client_email],
                fail_silently=True,
            )
        except Exception as e:
            print(f"Error sending payment confirmation email to {client_email}: {e}")

# 🔹 Automatically Create Message Thread for Special Orders
@receiver(post_save, sender=SpecialOrder)
def create_special_order_thread(sender, instance, created, **kwargs):
    """
    Automatically creates a message thread for a new special order.
    """
    if created:
        OrderMessageThread.objects.create(
            order_type='special',
            special_order=instance,
            sender_role='client',
            recipient_role='admin',
        )