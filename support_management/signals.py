from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
from django.utils.timezone import now
from .models import (
    SupportProfile, SupportActivityLog, SupportNotification, EscalationLog, 
    SupportOrderManagement, SupportWorkloadTracker, PaymentIssueLog
)
from websites.models import Website
from .utils import send_support_notification, update_support_workload
from django.contrib.auth import get_user_model

User = get_user_model()


# 🚀 **1️⃣ Automatically Create Support Profile**
@receiver(post_save, sender=User)
def create_support_profile(sender, instance, created, **kwargs):
    """
    Automatically create a SupportProfile when a new user with a 'support' role is created.
    """
    if created and instance.role == "support":
        default_website = Website.objects.first()  # Assign first website as default
        SupportProfile.objects.create(
            user=instance,
            name=instance.username,
            registration_id=f"Support #{instance.id:05d}",
            email=instance.email,
            website=default_website,
        )


# 🚀 **2️⃣ Track Last Login for Support Agents**
@receiver(user_logged_in)
def update_last_logged_in(sender, request, user, **kwargs):
    """
    Update the last_logged_in field for support staff upon login.
    """
    if user.role == "support":
        support_profile = user.support_profile
        support_profile.last_logged_in = now()
        support_profile.save()


# 🚀 **3️⃣ Log Creation of Support Profile**
@receiver(post_save, sender=SupportProfile)
def log_profile_creation(sender, instance, created, **kwargs):
    """
    Log the creation of a SupportProfile and notify support admin.
    """
    if created:
        SupportActivityLog.objects.create(
            support_staff=instance,
            activity=f"Support profile created for {instance.name}."
        )
        send_support_notification(instance, f"New support profile created: {instance.name}.")


# 🚀 **4️⃣ Log All Support Actions & Send Notifications**
@receiver(post_save, sender=SupportActivityLog)
def send_activity_notification(sender, instance, **kwargs):
    """
    Send a notification to support staff when a new activity log is created.
    """
    message = f"New activity logged: {instance.activity[:50]}..."
    send_support_notification(instance.support_staff, message)


# 🚀 **5️⃣ Track Support Workload on Order Management Updates**
@receiver(post_save, sender=SupportOrderManagement)
def update_workload_on_order_management(sender, instance, **kwargs):
    """
    Update support workload tracker when an order status is changed by support.
    """
    update_support_workload(instance.support_staff)


# 🚀 **6️⃣ Notify Admin on Escalation Log Entries**
@receiver(post_save, sender=EscalationLog)
def notify_admin_on_escalation(sender, instance, created, **kwargs):
    """
    Notify admins when a new escalation is logged by support.
    """
    if created:
        send_support_notification(
            instance.escalated_to.support_profile, 
            f"New escalation: {instance.action_type} for {instance.target_user.username}."
        )


# 🚀 **7️⃣ Track & Notify on Payment Issues**
@receiver(post_save, sender=PaymentIssueLog)
def notify_on_payment_issue(sender, instance, created, **kwargs):
    """
    Notify support when a new payment issue is logged.
    """
    if created:
        send_support_notification(
            instance.reported_by.support_profile, 
            f"Payment issue logged for Order {instance.order.id}: {instance.issue_type}."
        )


# 🚀 **8️⃣ Remove Support Workload Data on Profile Deletion**
@receiver(post_delete, sender=SupportProfile)
def cleanup_support_workload(sender, instance, **kwargs):
    """
    Remove workload tracker data when a support profile is deleted.
    """
    SupportWorkloadTracker.objects.filter(support_staff=instance.user).delete()