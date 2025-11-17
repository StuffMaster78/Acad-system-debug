from django.utils.timezone import now
from orders.models import Order
from orders.models import Dispute
from tickets.models import Ticket
from .models import (
    SupportNotification, SupportWorkloadTracker, OrderDisputeSLA, 
    SupportActionLog, PaymentIssueLog, SupportProfile
)


# 🚀 **1️⃣ Send Support Notification**
def send_support_notification(support_staff, message, priority="medium"):
    """
    Sends a notification to a support agent.
    """
    SupportNotification.objects.create(
        support_staff=support_staff,
        message=message,
        priority=priority
    )


# 🚀 **2️⃣ Log Support Action**
def log_support_action(support_staff, action, related_order=None, related_dispute=None, related_ticket=None):
    """
    Logs an action performed by a support agent.
    """
    SupportActionLog.objects.create(
        support_staff=support_staff,
        action=action,
        related_order=related_order,
        related_dispute=related_dispute,
        related_ticket=related_ticket
    )


# 🚀 **3️⃣ Check SLA Breach**
def check_sla_status():
    """
    Checks all unresolved orders and disputes for SLA breaches and sends alerts.
    """
    breached_tasks = OrderDisputeSLA.objects.filter(
        sla_breached=False, expected_resolution_time__lte=now(), actual_resolution_time__isnull=True
    ).select_related('assigned_to')

    for task in breached_tasks:
        task.sla_breached = True
        task.save()
        
        # Send notification if assigned to a support agent
        if task.assigned_to and hasattr(task.assigned_to, 'support_profile'):
            send_support_notification(
                task.assigned_to.support_profile, 
                f"⚠️ SLA Breach Alert: {task.sla_type} - {'Order' if task.order else 'Dispute'} {task.order.id if task.order else task.dispute.id}", 
                priority="high"
            )


# 🚀 **4️⃣ Update Support Workload**
def update_support_workload(support_staff):
    """
    Updates the workload stats for a support agent.
    """
    support_workload, created = SupportWorkloadTracker.objects.get_or_create(
        support_staff=support_staff
    )
    
    support_workload.tickets_handled = Ticket.objects.filter(resolved_by=support_staff).count()
    support_workload.disputes_handled = Dispute.objects.filter(resolved_by=support_staff).count()
    support_workload.orders_managed = Order.objects.filter(updated_by=support_staff).count()
    support_workload.last_activity = now()
    support_workload.save()


# 🚀 **5️⃣ Escalate Payment Issue**
def escalate_payment_issue(payment_issue, admin):
    """
    Escalates a payment issue to an admin.
    """
    payment_issue.escalated_to = admin
    payment_issue.status = "escalated"
    payment_issue.save()

    send_support_notification(
        admin.support_profile,
        f"Payment Issue Escalated: {payment_issue.issue_type} - Order {payment_issue.order.id}",
        priority="high"
    )


# 🚀 **6️⃣ Assign a Ticket to an Available Support Agent**
def assign_ticket_to_support(ticket):
    """
    Finds the least busy support agent and assigns the ticket.
    """
    available_support = SupportWorkloadTracker.objects.order_by('tickets_handled').first()
    
    if available_support:
        ticket.assigned_to = available_support.support_staff
        ticket.save()
        send_support_notification(
            available_support.support_staff,
            f"New Ticket Assigned: {ticket.subject}",
            priority="medium"
        )


# 🚀 **7️⃣ Auto-Resolve Support Availability**
def auto_update_support_availability():
    """
    Automatically updates the availability of support agents based on activity.
    """
    support_profiles = SupportProfile.objects.all()
    
    for profile in support_profiles:
        if profile.last_logged_in and (now() - profile.last_logged_in).total_seconds() > 3600:
            profile.status = "inactive"
            profile.save()