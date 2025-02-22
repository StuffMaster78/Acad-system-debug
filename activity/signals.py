from django.db.models.signals import post_save, post_delete
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import ActivityLog
from orders.models import Order  # Import Order model (adjust based on actual location)
# from payments.models import Payment  # Import Payment model (adjust if necessary)

# Utility function to log activities
def log_activity(user, action_type, description, metadata=None):
    ActivityLog.objects.create(
        user=user,
        action_type=action_type,
        description=description,
        metadata=metadata or {}
    )

# ✅ Log Order Status Updates
@receiver(post_save, sender=Order)
def log_order_update(sender, instance, created, **kwargs):
    user = instance.last_updated_by  # Ensure your Order model tracks who last updated it
    action_type = "ORDER"
    
    if created:
        description = f"New order #{instance.id} placed."
    else:
        description = f"Order #{instance.id} updated. Status: {instance.status}."
    
    log_activity(user, action_type, description, metadata={"order_id": instance.id, "status": instance.status})

# # ✅ Log Payment Transactions
# @receiver(post_save, sender=Payment)
# def log_payment(sender, instance, created, **kwargs):
#     user = instance.client  # Ensure Payment model tracks the client who paid
#     action_type = "PAYMENT"

#     if created:
#         description = f"Payment of ${instance.amount} received for Order #{instance.order.id}."
#     else:
#         description = f"Payment updated for Order #{instance.order.id}. New Status: {instance.status}."

#     log_activity(user, action_type, description, metadata={"order_id": instance.order.id, "amount": instance.amount, "status": instance.status})

# ✅ Log User Account Changes
@receiver(post_save, sender=User)
def log_user_update(sender, instance, created, **kwargs):
    action_type = "USER"
    description = f"User {instance.username} profile updated."
    
    if created:
        description = f"New user account created: {instance.username}."
    
    log_activity(instance, action_type, description)

# ✅ Log Order Deletions
@receiver(post_delete, sender=Order)
def log_order_deletion(sender, instance, **kwargs):
    user = instance.last_updated_by  # Ensure your model tracks last user who updated it
    description = f"Order #{instance.id} was deleted."
    log_activity(user, "ORDER", description, metadata={"order_id": instance.id})