from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
from django.utils.timezone import now
from .models import (
    SupportProfile, SupportActivityLog, SupportNotification, EscalationLog, 
    SupportOrderManagement, SupportWorkloadTracker, PaymentIssueLog, SupportActionLog
)
from websites.models import Website
from .utils import send_support_notification, update_support_workload
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()


# 🚀 **1️⃣ Automatically Create Support Profile**
@receiver(post_save, sender=User)
def create_support_profile(sender, instance, created, **kwargs):
    if getattr(settings, "DISABLE_SUPPORT_SIGNALS", False):
        return
    """
    Automatically create a SupportProfile when a new user with a 'support' role is created.
    """
    if created and instance.role == "support":
        # Avoid duplicates when tests also create SupportProfile manually
        if not hasattr(instance, "support_profile"):
            default_website = Website.objects.first()
            if default_website is None:
                default_website = Website.objects.create(
                    name="Test Website",
                    domain="https://test.local",
                    is_active=True,
                )
            SupportProfile.objects.get_or_create(
                user=instance,
                defaults={
                    "name": instance.username,
                    "registration_id": f"Support #{instance.id:05d}",
                    "email": instance.email,
                    "website": default_website,
                },
            )


# 🚀 **2️⃣ Track Last Login for Support Agents**
@receiver(user_logged_in)
def update_last_logged_in(sender, request, user, **kwargs):
    if getattr(settings, "DISABLE_SUPPORT_SIGNALS", False):
        return
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
    if getattr(settings, "DISABLE_SUPPORT_SIGNALS", False):
        return
    """
    Log the creation of a SupportProfile and notify support admin.
    """
    if created:
        SupportActionLog.objects.create(
            support_staff=instance,
            action=f"Support profile created for {instance.name}."
        )
        send_support_notification(instance, f"New support profile created: {instance.name}.")


# 🚀 **4️⃣ Log All Support Actions & Send Notifications**
@receiver(post_save, sender=SupportActivityLog)
def send_activity_notification(sender, instance, **kwargs):
    if getattr(settings, "DISABLE_SUPPORT_SIGNALS", False):
        return
    """
    Send a notification to support staff when a new activity log is created.
    """
    try:
        msg = getattr(instance, "description", None) or getattr(instance, "activity", "Activity logged")
        message = f"New activity logged: {msg[:50]}..."
    except Exception:
        message = "New activity logged."
    send_support_notification(instance.support_staff.support_profile, message)


# 🚀 **5️⃣ Track Support Workload on Order Management Updates**
@receiver(post_save, sender=SupportOrderManagement)
def update_workload_on_order_management(sender, instance, **kwargs):
    if getattr(settings, "DISABLE_SUPPORT_SIGNALS", False):
        return
    """
    Update support workload tracker when an order status is changed by support.
    """
    update_support_workload(instance.support_staff)


# 🚀 **6️⃣ Notify Admin on Escalation Log Entries**
@receiver(post_save, sender=EscalationLog)
def notify_admin_on_escalation(sender, instance, created, **kwargs):
    if getattr(settings, "DISABLE_SUPPORT_SIGNALS", False):
        return
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
    if getattr(settings, "DISABLE_SUPPORT_SIGNALS", False):
        return
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
    if getattr(settings, "DISABLE_SUPPORT_SIGNALS", False):
        return
    """
    Remove workload tracker data when a support profile is deleted.
    """
    SupportWorkloadTracker.objects.filter(support_staff=instance.user).delete()