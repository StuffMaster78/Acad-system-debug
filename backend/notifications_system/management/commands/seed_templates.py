# notifications_system/management/commands/seed_templates.py
"""
Seed default notification templates for all active events.
Run once on deploy: python manage.py seed_templates
Run again to update: python manage.py seed_templates --update
"""
from __future__ import annotations

from django.core.management.base import BaseCommand

from notifications_system.enums import NotificationChannel
from notifications_system.models.notification_event import NotificationEvent
from notifications_system.models.notifications_template import (
    NotificationTemplate,
)
from notifications_system.services.template_service import TemplateService


# Default template content per event key
# These are global templates (website=None) used as fallbacks
# Admins can override per website via the admin panel or API

DEFAULT_TEMPLATES = {
    # Orders
    'order.created': {
        NotificationChannel.EMAIL: {
            'subject': 'Your order #{{order_id}} has been placed',
            'body_html': 'notifications/emails/order_confirmation.html',
            'body_text': (
                'Your order #{{order_id}} has been placed successfully.'
            ),
            'title': 'Order Placed',
            'message': 'Your order #{{order_id}} has been placed.',
            'available_variables': ['order_id', 'user_name', 'website_name'],
        },
        NotificationChannel.IN_APP: {
            'title': 'Order #{{order_id}} placed',
            'message': 'Your order has been placed successfully.',
            'available_variables': ['order_id', 'user_name'],
        },
    },
    'order.assigned': {
        NotificationChannel.EMAIL: {
            'subject': 'Order #{{order_id}} has been assigned',
            'body_html': 'notifications/emails/order_assigned.html',
            'body_text': (
                'Order #{{order_id}} has been assigned to {{writer_name}}.'
            ),
            'available_variables': ['order_id', 'writer_name', 'user_name'],
        },
        NotificationChannel.IN_APP: {
            'title': 'Order #{{order_id}} assigned',
            'message': 'Your order has been assigned to {{writer_name}}.',
            'available_variables': ['order_id', 'writer_name'],
        },
    },
    'order.completed': {
        NotificationChannel.EMAIL: {
            'subject': 'Order #{{order_id}} is complete',
            'body_html': 'notifications/emails/order_completed.html',
            'body_text': 'Order #{{order_id}} has been completed.',
            'available_variables': ['order_id', 'user_name', 'website_name'],
        },
        NotificationChannel.IN_APP: {
            'title': 'Order #{{order_id}} completed',
            'message': 'Your order has been completed.',
            'available_variables': ['order_id'],
        },
    },
    'order.cancelled': {
        NotificationChannel.EMAIL: {
            'subject': 'Order #{{order_id}} has been cancelled',
            'body_html': 'notifications/emails/order_cancelled.html',
            'body_text': 'Order #{{order_id}} has been cancelled.',
            'available_variables': ['order_id', 'user_name', 'reason'],
        },
        NotificationChannel.IN_APP: {
            'title': 'Order #{{order_id}} cancelled',
            'message': 'Your order has been cancelled.',
            'available_variables': ['order_id', 'reason'],
        },
    },
    'order.revision_requested': {
        NotificationChannel.EMAIL: {
            'subject': 'Revision requested for Order #{{order_id}}',
            'body_html': 'notifications/emails/revision_requested.html',
            'body_text': (
                'A revision has been requested for order #{{order_id}}.'
            ),
            'available_variables': ['order_id', 'writer_name', 'reason'],
        },
        NotificationChannel.IN_APP: {
            'title': 'Revision requested',
            'message': (
                'A revision has been requested for order #{{order_id}}.'
            ),
            'available_variables': ['order_id'],
        },
    },
    'order.deadline_approaching': {
        NotificationChannel.EMAIL: {
            'subject': 'Deadline approaching for Order #{{order_id}}',
            'body_html': 'notifications/emails/deadline_reminder.html',
            'body_text': (
                'The deadline for order #{{order_id}} is approaching.'
            ),
            'available_variables': [
                'order_id', 'deadline', 'hours_remaining',
            ],
        },
        NotificationChannel.IN_APP: {
            'title': 'Deadline approaching',
            'message': (
                'Order #{{order_id}} deadline is in '
                '{{hours_remaining}} hours.'
            ),
            'available_variables': ['order_id', 'hours_remaining'],
        },
    },
    'order.submitted': {
        NotificationChannel.EMAIL: {
            'subject': 'Order #{{order_id}} has been submitted',
            'body_html': 'notifications/emails/order_submitted.html',
            'body_text': 'Order #{{order_id}} has been submitted for your review.',
            'available_variables': ['order_id', 'order_topic', 'order_reference', 'user_name'],
        },
        NotificationChannel.IN_APP: {
            'title': 'Order #{{order_id}} submitted',
            'message': 'Your order has been submitted and is ready for review.',
            'available_variables': ['order_id', 'order_topic'],
        },
    },
    'order.on_hold': {
        NotificationChannel.EMAIL: {
            'subject': 'Order #{{order_id}} has been placed on hold',
            'body_html': 'notifications/emails/order_on_hold.html',
            'body_text': 'Order #{{order_id}} has been placed on hold. Reason: {{reason}}.',
            'available_variables': ['order_id', 'order_topic', 'hold_id', 'reason', 'user_name'],
        },
        NotificationChannel.IN_APP: {
            'title': 'Order #{{order_id}} on hold',
            'message': 'Your order has been placed on hold.',
            'available_variables': ['order_id', 'reason'],
        },
    },
    'order.reopened': {
        NotificationChannel.EMAIL: {
            'subject': 'Order #{{order_id}} has been reopened',
            'body_html': 'notifications/emails/order_reopened.html',
            'body_text': 'Order #{{order_id}} has been reopened and is back in progress.',
            'available_variables': ['order_id', 'order_topic', 'reason', 'user_name'],
        },
        NotificationChannel.IN_APP: {
            'title': 'Order #{{order_id}} reopened',
            'message': 'Your order is back in progress.',
            'available_variables': ['order_id', 'reason'],
        },
    },
    'order.bid.placed': {
        NotificationChannel.IN_APP: {
            'title': 'Bid placed on order #{{order_id}}',
            'message': 'Your bid on order #{{order_id}} has been placed.',
            'available_variables': ['order_id', 'order_topic', 'interest_id'],
        },
    },
    'order.bid.accepted': {
        NotificationChannel.EMAIL: {
            'subject': 'Your bid on order #{{order_id}} was accepted',
            'body_html': 'notifications/emails/bid_accepted.html',
            'body_text': 'Your bid on order #{{order_id}} was accepted. Get started now.',
            'available_variables': ['order_id', 'order_topic', 'interest_id', 'user_name'],
        },
        NotificationChannel.IN_APP: {
            'title': 'Bid accepted — Order #{{order_id}}',
            'message': 'Your bid was accepted. The order has been assigned to you.',
            'available_variables': ['order_id', 'order_topic', 'interest_id'],
        },
    },
    'order.bid.rejected': {
        NotificationChannel.IN_APP: {
            'title': 'Bid not selected — Order #{{order_id}}',
            'message': 'Your bid on order #{{order_id}} was not selected.',
            'available_variables': ['order_id', 'order_topic', 'interest_id'],
        },
    },
    'file.delivery_unlocked': {
        NotificationChannel.EMAIL: {
            'subject': 'Your files for Order #{{order_id}} are now available',
            'body_html': 'notifications/emails/file_delivery_unlocked.html',
            'body_text': 'Your payment for order #{{order_id}} has been confirmed. You can now download all delivery files.',
            'available_variables': ['order_id', 'order_topic', 'client_name', 'website_name', 'download_url'],
        },
        NotificationChannel.IN_APP: {
            'title': 'Files unlocked — Order #{{order_id}}',
            'message': 'Your delivery files for order #{{order_id}} are ready to download.',
            'available_variables': ['order_id', 'order_topic', 'download_url'],
        },
    },
    'file.uploaded': {
        NotificationChannel.EMAIL: {
            'subject': 'New file uploaded for Order #{{order_id}}',
            'body_html': 'notifications/emails/file_uploaded.html',
            'body_text': 'A new file has been uploaded for order #{{order_id}}.',
            'available_variables': ['order_id', 'order_topic', 'attachment_id', 'purpose', 'user_name'],
        },
        NotificationChannel.IN_APP: {
            'title': 'New file on Order #{{order_id}}',
            'message': 'A new file has been uploaded for your order.',
            'available_variables': ['order_id', 'attachment_id', 'purpose'],
        },
    },
    'order.qa_review_ready': {
        NotificationChannel.EMAIL: {
            'subject': 'Order #{{order_id}} is ready for QA review',
            'body_html': 'notifications/emails/order_qa_review_ready.html',
            'body_text': 'Order #{{order_id}} ({{order_topic}}) requires QA review.',
            'available_variables': ['order_id', 'order_topic', 'total_price', 'is_urgent', 'writer_id'],
        },
        NotificationChannel.IN_APP: {
            'title': 'QA review needed — Order #{{order_id}}',
            'message': 'Order #{{order_id}} is in the QA queue.',
            'available_variables': ['order_id', 'order_topic', 'is_urgent'],
        },
    },
    'order.disputed': {
        NotificationChannel.EMAIL: {
            'subject': 'Dispute opened for Order #{{order_id}}',
            'body_html': 'notifications/emails/dispute_opened.html',
            'body_text': 'A dispute has been opened for order #{{order_id}}.',
            'available_variables': ['order_id', 'reason'],
        },
        NotificationChannel.IN_APP: {
            'title': 'Order disputed',
            'message': 'A dispute has been opened for order #{{order_id}}.',
            'available_variables': ['order_id'],
        },
    },

    # Wallet
    'wallet.credited': {
        NotificationChannel.EMAIL: {
            'subject': 'Your wallet has been credited',
            'body_html': 'notifications/emails/payment_received.html',
            'body_text': 'Your wallet has been credited with {{amount}}.',
            'available_variables': ['amount', 'user_name', 'website_name'],
        },
        NotificationChannel.IN_APP: {
            'title': 'Wallet credited',
            'message': 'Your wallet has been credited with {{amount}}.',
            'available_variables': ['amount'],
        },
    },
    'wallet.debited': {
        NotificationChannel.IN_APP: {
            'title': 'Wallet debited',
            'message': '{{amount}} has been deducted from your wallet.',
            'available_variables': ['amount'],
        },
    },
    'wallet.balance_low': {
        NotificationChannel.EMAIL: {
            'subject': 'Your wallet balance is low',
            'body_html': 'notifications/emails/payment_reminder.html',
            'body_text': (
                'Your wallet balance is low. Current balance: {{balance}}.'
            ),
            'available_variables': ['balance', 'user_name'],
        },
        NotificationChannel.IN_APP: {
            'title': 'Low wallet balance',
            'message': 'Your wallet balance is {{balance}}.',
            'available_variables': ['balance'],
        },
    },
    'wallet.refund_completed': {
        NotificationChannel.EMAIL: {
            'subject': 'Your refund has been processed',
            'body_html': 'notifications/emails/refund_processed.html',
            'body_text': 'Your refund of {{amount}} has been processed.',
            'available_variables': ['amount', 'user_name'],
        },
        NotificationChannel.IN_APP: {
            'title': 'Refund processed',
            'message': 'Your refund of {{amount}} has been processed.',
            'available_variables': ['amount'],
        },
    },

    # Payouts
    'payout.completed': {
        NotificationChannel.EMAIL: {
            'subject': 'Your payout has been sent',
            'body_html': 'notifications/emails/writer_payment.html',
            'body_text': 'Your payout of {{amount}} has been sent.',
            'available_variables': ['amount', 'user_name'],
        },
        NotificationChannel.IN_APP: {
            'title': 'Payout sent',
            'message': 'Your payout of {{amount}} has been sent.',
            'available_variables': ['amount'],
        },
    },
    'payout.failed': {
        NotificationChannel.EMAIL: {
            'subject': 'Your payout has failed',
            'body_html': 'notifications/emails/payment_failed.html',
            'body_text': (
                'Your payout of {{amount}} has failed. Reason: {{reason}}.'
            ),
            'available_variables': ['amount', 'reason'],
        },
        NotificationChannel.IN_APP: {
            'title': 'Payout failed',
            'message': 'Your payout failed. Please contact support.',
            'available_variables': ['amount', 'reason'],
        },
    },
    'compensation.payment_processing': {
        NotificationChannel.EMAIL: {
            'subject': 'Your writer payment is being processed',
            'body_html': 'notifications/emails/compensation_processing.html',
            'body_text': (
                'Your writer payment for {{window_label}} is being '
                'processed.'
            ),
            'available_variables': ['window_label', 'start_date', 'end_date'],
        },
        NotificationChannel.IN_APP: {
            'title': 'Payment processing',
            'message': (
                'Your writer payment for {{window_label}} is processing.'
            ),
            'available_variables': ['window_label'],
        },
    },
    'compensation.payment_paid': {
        NotificationChannel.EMAIL: {
            'subject': 'Your writer payment has been paid',
            'body_html': 'notifications/emails/compensation_paid.html',
            'body_text': (
                'Your writer payment of {{amount}} for {{window_label}} '
                'has been paid.'
            ),
            'available_variables': ['amount', 'window_label', 'record_id'],
        },
        NotificationChannel.IN_APP: {
            'title': 'Payment paid',
            'message': '{{amount}} for {{window_label}} has been paid.',
            'available_variables': ['amount', 'window_label'],
        },
    },
    'compensation.payment_on_hold': {
        NotificationChannel.EMAIL: {
            'subject': 'Your writer payment is on hold',
            'body_html': 'notifications/emails/compensation_on_hold.html',
            'body_text': (
                'Your writer payment for {{window_label}} is currently '
                'on hold.'
            ),
            'available_variables': ['window_label', 'record_id'],
        },
        NotificationChannel.IN_APP: {
            'title': 'Payment on hold',
            'message': 'Your payment for {{window_label}} is on hold.',
            'available_variables': ['window_label'],
        },
    },
    'compensation.fine_applied': {
        NotificationChannel.EMAIL: {
            'subject': 'A deduction has been applied',
            'body_html': (
                'notifications/emails/compensation_fine_applied.html'
            ),
            'body_text': (
                'A deduction of {{amount}} has been applied to your '
                'writer account.'
            ),
            'available_variables': [
                'amount', 'source_label', 'source_type', 'source_id',
                'event_id',
            ],
        },
        NotificationChannel.IN_APP: {
            'title': 'Deduction applied',
            'message': 'A deduction of {{amount}} has been applied.',
            'available_variables': ['amount', 'source_label'],
        },
    },
    'compensation.adjustment_applied': {
        NotificationChannel.EMAIL: {
            'subject': 'Your writer earnings were adjusted',
            'body_html': (
                'notifications/emails/compensation_adjustment_applied.html'
            ),
            'body_text': (
                'A {{direction}} adjustment of {{amount}} has been '
                'applied to your writer account.'
            ),
            'available_variables': ['amount', 'direction', 'event_id'],
        },
        NotificationChannel.IN_APP: {
            'title': 'Earnings adjusted',
            'message': (
                'A {{direction}} adjustment of {{amount}} was applied.'
            ),
            'available_variables': ['amount', 'direction'],
        },
    },

    # Writer management
    'writer.approved': {
        NotificationChannel.EMAIL: {
            'subject': 'Your writer application has been approved',
            'body_html': (
                'notifications/emails/writer_application_approved.html'
            ),
            'body_text': (
                'Congratulations! Your writer application has been approved.'
            ),
            'available_variables': ['user_name', 'website_name'],
        },
        NotificationChannel.IN_APP: {
            'title': 'Application approved',
            'message': 'Your writer application has been approved.',
            'available_variables': ['user_name'],
        },
    },
    'writer.rejected': {
        NotificationChannel.EMAIL: {
            'subject': 'Your writer application was not approved',
            'body_html': (
                'notifications/emails/writer_application_rejected.html'
            ),
            'body_text': (
                'Your writer application was not approved. '
                'Reason: {{reason}}.'
            ),
            'available_variables': ['user_name', 'reason'],
        },
        NotificationChannel.IN_APP: {
            'title': 'Application not approved',
            'message': 'Your writer application was not approved.',
            'available_variables': ['reason'],
        },
    },
    'writer.warning': {
        NotificationChannel.EMAIL: {
            'subject': 'You have received a warning',
            'body_html': 'notifications/emails/security_alert.html',
            'body_text': 'You have received a warning. Reason: {{reason}}.',
            'available_variables': ['user_name', 'reason'],
        },
        NotificationChannel.IN_APP: {
            'title': 'Warning issued',
            'message': 'You have received a warning.',
            'available_variables': ['reason'],
        },
    },
    'writer.level_up': {
        NotificationChannel.EMAIL: {
            'subject': 'Congratulations — you have leveled up!',
            'body_html': 'notifications/emails/milestone_achieved.html',
            'body_text': 'You have reached level {{level}}!',
            'available_variables': ['user_name', 'level'],
        },
        NotificationChannel.IN_APP: {
            'title': 'Level up!',
            'message': 'You have reached level {{level}}!',
            'available_variables': ['level'],
        },
    },
    'writer.badge_earned': {
        NotificationChannel.IN_APP: {
            'title': 'Badge earned',
            'message': 'You have earned the {{badge_name}} badge.',
            'available_variables': ['badge_name'],
        },
    },

    # Tickets
    'ticket.created': {
        NotificationChannel.EMAIL: {
            'subject': 'New support ticket #{{ticket_id}}',
            'body_html': 'notifications/emails/ticket_created.html',
            'body_text': (
                'Support ticket #{{ticket_id}} has been created: '
                '{{ticket_title}}.'
            ),
            'available_variables': [
                'ticket_id', 'ticket_number', 'ticket_title',
                'ticket_subject', 'ticket_status', 'ticket_priority',
                'ticket_category', 'cta_url',
            ],
        },
        NotificationChannel.IN_APP: {
            'title': 'New ticket #{{ticket_id}}',
            'message': '{{ticket_title}}',
            'available_variables': ['ticket_id', 'ticket_title'],
        },
    },
    'ticket.updated': {
        NotificationChannel.EMAIL: {
            'subject': 'Ticket #{{ticket_id}} was updated',
            'body_html': 'notifications/emails/ticket_updated.html',
            'body_text': 'Ticket #{{ticket_id}} was updated.',
            'available_variables': [
                'ticket_id', 'ticket_number', 'ticket_title',
                'ticket_subject', 'ticket_status', 'ticket_priority',
                'ticket_category', 'cta_url',
            ],
        },
        NotificationChannel.IN_APP: {
            'title': 'Ticket updated',
            'message': '{{ticket_title}} is now {{ticket_status}}.',
            'available_variables': [
                'ticket_id', 'ticket_title', 'ticket_status',
            ],
        },
    },
    'ticket.assigned': {
        NotificationChannel.EMAIL: {
            'subject': 'Ticket #{{ticket_id}} assigned to you',
            'body_html': 'notifications/emails/ticket_assigned.html',
            'body_text': 'Ticket #{{ticket_id}} has been assigned to you.',
            'available_variables': [
                'ticket_id', 'ticket_number', 'ticket_title',
                'ticket_subject', 'ticket_status', 'ticket_priority',
                'assigned_to_id', 'cta_url',
            ],
        },
        NotificationChannel.IN_APP: {
            'title': 'Ticket assigned',
            'message': 'Ticket #{{ticket_id}} was assigned to you.',
            'available_variables': ['ticket_id', 'ticket_title'],
        },
    },
    'ticket.escalated': {
        NotificationChannel.EMAIL: {
            'subject': 'Ticket #{{ticket_id}} escalated',
            'body_html': 'notifications/emails/ticket_escalated.html',
            'body_text': 'Ticket #{{ticket_id}} has been escalated.',
            'available_variables': [
                'ticket_id', 'ticket_number', 'ticket_title',
                'ticket_subject', 'ticket_status', 'ticket_priority',
                'escalated_by', 'cta_url',
            ],
        },
        NotificationChannel.IN_APP: {
            'title': 'Ticket escalated',
            'message': 'Ticket #{{ticket_id}} needs priority attention.',
            'available_variables': [
                'ticket_id', 'ticket_title', 'escalated_by',
            ],
        },
    },
    'ticket.resolved': {
        NotificationChannel.EMAIL: {
            'subject': 'Your ticket #{{ticket_id}} has been resolved',
            'body_html': 'notifications/emails/ticket_resolved.html',
            'body_text': (
                'Your support ticket #{{ticket_id}} has been resolved.'
            ),
            'available_variables': [
                'ticket_id', 'ticket_number', 'ticket_title',
                'ticket_subject', 'resolution', 'cta_url',
            ],
        },
        NotificationChannel.IN_APP: {
            'title': 'Ticket resolved',
            'message': 'Your ticket #{{ticket_id}} has been resolved.',
            'available_variables': ['ticket_id', 'ticket_title'],
        },
    },
    'ticket.closed': {
        NotificationChannel.EMAIL: {
            'subject': 'Your ticket #{{ticket_id}} has been closed',
            'body_html': 'notifications/emails/ticket_closed.html',
            'body_text': (
                'Your support ticket #{{ticket_id}} has been closed.'
            ),
            'available_variables': [
                'ticket_id', 'ticket_number', 'ticket_title',
                'ticket_subject', 'ticket_status', 'old_status', 'cta_url',
            ],
        },
        NotificationChannel.IN_APP: {
            'title': 'Ticket closed',
            'message': 'Ticket #{{ticket_id}} has been closed.',
            'available_variables': ['ticket_id', 'ticket_title'],
        },
    },
    'ticket.reopened': {
        NotificationChannel.EMAIL: {
            'subject': 'Your ticket #{{ticket_id}} has been reopened',
            'body_html': 'notifications/emails/ticket_reopened.html',
            'body_text': (
                'Your support ticket #{{ticket_id}} has been reopened.'
            ),
            'available_variables': [
                'ticket_id', 'ticket_number', 'ticket_title',
                'ticket_subject', 'ticket_status', 'old_status', 'cta_url',
            ],
        },
        NotificationChannel.IN_APP: {
            'title': 'Ticket reopened',
            'message': 'Ticket #{{ticket_id}} has been reopened.',
            'available_variables': [
                'ticket_id', 'ticket_title', 'ticket_status',
            ],
        },
    },
    'ticket.comment_added': {
        NotificationChannel.EMAIL: {
            'subject': 'New reply on ticket #{{ticket_id}}',
            'body_html': 'notifications/emails/ticket_comment_added.html',
            'body_text': (
                '{{commenter_name}} replied to ticket #{{ticket_id}}: '
                '{{message_preview}}'
            ),
            'available_variables': [
                'ticket_id', 'ticket_number', 'ticket_title',
                'ticket_subject', 'ticket_status', 'commenter_name',
                'response_message', 'message_preview', 'cta_url',
            ],
        },
        NotificationChannel.IN_APP: {
            'title': 'New comment on ticket #{{ticket_id}}',
            'message': '{{commenter_name}} added a comment.',
            'available_variables': [
                'ticket_id', 'ticket_title', 'commenter_name',
                'message_preview',
            ],
        },
    },

    # Account
    'account.suspended': {
        NotificationChannel.EMAIL: {
            'subject': 'Your account has been suspended',
            'body_html': 'notifications/emails/account_suspended.html',
            'body_text': (
                'Your account has been suspended. Reason: {{reason}}.'
            ),
            'available_variables': ['user_name', 'reason'],
        },
        NotificationChannel.IN_APP: {
            'title': 'Account suspended',
            'message': 'Your account has been suspended.',
            'available_variables': ['reason'],
        },
    },
    'account.reactivated': {
        NotificationChannel.EMAIL: {
            'subject': 'Your account has been reactivated',
            'body_html': 'notifications/emails/account_reactivated.html',
            'body_text': 'Your account has been reactivated.',
            'available_variables': ['user_name'],
        },
        NotificationChannel.IN_APP: {
            'title': 'Account reactivated',
            'message': 'Your account has been reactivated.',
            'available_variables': [],
        },
    },
    'account.login_new_device': {
        NotificationChannel.EMAIL: {
            'subject': 'New login detected',
            'body_html': 'notifications/emails/login_new_device.html',
            'body_text': (
                'A new login was detected on your account from {{device}}.'
            ),
            'available_variables': [
                'user_name', 'device', 'ip_address', 'location',
            ],
        },
        NotificationChannel.IN_APP: {
            'title': 'New device login',
            'message': 'A login was detected from a new device.',
            'available_variables': ['device'],
        },
    },
    'account.password_changed': {
        NotificationChannel.EMAIL: {
            'subject': 'Your password has been changed',
            'body_html': 'notifications/emails/password_changed.html',
            'body_text': 'Your password has been changed.',
            'available_variables': ['user_name'],
        },
        NotificationChannel.IN_APP: {
            'title': 'Password changed',
            'message': 'Your password has been changed.',
            'available_variables': [],
        },
    },
    'account.deletion_scheduled': {
        NotificationChannel.EMAIL: {
            'subject': 'Your account is scheduled for deletion',
            'body_html': 'notifications/emails/account_deletion.html',
            'body_text': (
                'Your account is scheduled for deletion on '
                '{{deletion_date}}. '
                'If this was a mistake you can cancel at {{undo_url}}.'
            ),
            'available_variables': ['user_name', 'deletion_date', 'undo_url'],
        },
        NotificationChannel.IN_APP: {
            'title': 'Account deletion scheduled',
            'message': 'Your account will be deleted on {{deletion_date}}.',
            'available_variables': ['deletion_date', 'undo_url'],
        },
    },

    # Messages
    'message.new': {
        NotificationChannel.IN_APP: {
            'title': 'New message from {{sender_name}}',
            'message': '{{message_preview}}',
            'available_variables': ['sender_name', 'message_preview'],
        },
    },
    'loyalty.points_awarded': {
        NotificationChannel.EMAIL: {
            'subject': 'You earned {{points}} loyalty points',
            'body_html': 'notifications/emails/loyalty_points_awarded.html',
            'body_text': (
                'You earned {{points}} loyalty points. '
                'Total balance: {{total_points}}.'
            ),
            'available_variables': [
                'points', 'reason', 'total_points', 'transaction_id',
                'referral_id', 'order_id',
            ],
        },
        NotificationChannel.IN_APP: {
            'title': 'Loyalty points earned',
            'message': '+{{points}} points. Balance: {{total_points}}.',
            'available_variables': ['points', 'reason', 'total_points'],
        },
    },
    'loyalty.points_converted': {
        NotificationChannel.EMAIL: {
            'subject': 'Loyalty points converted',
            'body_html': 'notifications/emails/loyalty_points_converted.html',
            'body_text': (
                '{{points}} points were converted to {{amount}} '
                'wallet balance.'
            ),
            'available_variables': ['points', 'amount', 'total_points'],
        },
        NotificationChannel.IN_APP: {
            'title': 'Points converted',
            'message': '{{points}} points were converted to wallet balance.',
            'available_variables': ['points', 'amount'],
        },
    },
    'loyalty.tier_upgraded': {
        NotificationChannel.EMAIL: {
            'subject': 'You reached {{tier_name}} tier',
            'body_html': 'notifications/emails/loyalty_tier_upgraded.html',
            'body_text': 'You reached {{tier_name}} tier.',
            'available_variables': ['tier_name', 'perks', 'total_points'],
        },
        NotificationChannel.IN_APP: {
            'title': 'Tier upgraded',
            'message': 'You reached {{tier_name}} tier.',
            'available_variables': ['tier_name', 'total_points'],
        },
    },
    'referral.reward_earned': {
        NotificationChannel.EMAIL: {
            'subject': 'Referral reward earned',
            'body_html': 'notifications/emails/referral_reward_earned.html',
            'body_text': (
                'You earned a referral reward: {{loyalty_points}} points '
                'and {{wallet_bonus}} wallet credit.'
            ),
            'available_variables': [
                'referral_id', 'order_id', 'referee_id', 'wallet_bonus',
                'loyalty_points',
            ],
        },
        NotificationChannel.IN_APP: {
            'title': 'Referral reward earned',
            'message': '+{{loyalty_points}} points from your referral.',
            'available_variables': ['wallet_bonus', 'loyalty_points'],
        },
    },
    'communications.message.created': {
        NotificationChannel.EMAIL: {
            'subject': 'New message in conversation #{{thread_id}}',
            'body_html': (
                'notifications/emails/communication_message_created.html'
            ),
            'body_text': 'A new message was added: {{message_preview}}',
            'available_variables': [
                'thread_id', 'message_id', 'sender_id', 'message_preview',
                'thread_kind', 'cta_url',
            ],
        },
        NotificationChannel.IN_APP: {
            'title': 'New message',
            'message': '{{message_preview}}',
            'available_variables': [
                'thread_id', 'message_id', 'sender_id', 'message_preview',
                'thread_kind',
            ],
        },
    },
    'communications.message.flagged': {
        NotificationChannel.EMAIL: {
            'subject': 'Message flagged in conversation #{{thread_id}}',
            'body_html': (
                'notifications/emails/communication_message_flagged.html'
            ),
            'body_text': 'A message was flagged for review: {{reason}}',
            'available_variables': [
                'thread_id', 'message_id', 'flag_id', 'severity', 'reason',
                'cta_url',
            ],
        },
        NotificationChannel.IN_APP: {
            'title': 'Message flagged',
            'message': '{{severity}}: {{reason}}',
            'available_variables': [
                'thread_id', 'message_id', 'flag_id', 'severity', 'reason',
            ],
        },
    },
    'communications.thread.escalated': {
        NotificationChannel.EMAIL: {
            'subject': 'Conversation #{{thread_id}} was escalated',
            'body_html': (
                'notifications/emails/communication_thread_escalated.html'
            ),
            'body_text': (
                'Conversation #{{thread_id}} was escalated: {{reason}}'
            ),
            'available_variables': [
                'thread_id', 'escalation_id', 'reason', 'cta_url',
            ],
        },
        NotificationChannel.IN_APP: {
            'title': 'Conversation escalated',
            'message': '{{reason}}',
            'available_variables': ['thread_id', 'escalation_id', 'reason'],
        },
    },
    'communications.link_review.created': {
        NotificationChannel.EMAIL: {
            'subject': 'Link review needed for {{domain}}',
            'body_html': (
                'notifications/emails/communication_link_review_created.html'
            ),
            'body_text': 'A shared link requires review: {{url}}',
            'available_variables': [
                'thread_id', 'message_id', 'review_id', 'domain', 'url',
                'cta_url',
            ],
        },
        NotificationChannel.IN_APP: {
            'title': 'Link review needed',
            'message': '{{domain}} requires review.',
            'available_variables': [
                'thread_id', 'message_id', 'review_id', 'domain', 'url',
            ],
        },
    },

    # System
    'system.maintenance': {
        NotificationChannel.EMAIL: {
            'subject': 'Scheduled maintenance notice',
            'body_html': 'notifications/emails/system_maintenance.html',
            'body_text': 'Scheduled maintenance: {{maintenance_window}}.',
            'available_variables': ['maintenance_window', 'website_name'],
        },
        NotificationChannel.IN_APP: {
            'title': 'Scheduled maintenance',
            'message': 'Maintenance scheduled for {{maintenance_window}}.',
            'available_variables': ['maintenance_window'],
        },
    },
    'system.broadcast': {
        NotificationChannel.EMAIL: {
            'subject': '{{title}}',
            'body_html': 'notifications/emails/feature_announcement.html',
            'body_text': '{{message}}',
            'available_variables': ['title', 'message', 'website_name'],
        },
        NotificationChannel.IN_APP: {
            'title': '{{title}}',
            'message': '{{message}}',
            'available_variables': ['title', 'message'],
        },
    },
    'system.alert': {
        NotificationChannel.EMAIL: {
            'subject': 'Important: {{title}}',
            'body_html': 'notifications/emails/security_alert.html',
            'body_text': '{{message}}',
            'available_variables': ['title', 'message'],
        },
        NotificationChannel.IN_APP: {
            'title': '{{title}}',
            'message': '{{message}}',
            'available_variables': ['title', 'message'],
        },
    },

    # Digest
    'scheduled.digest_daily': {
        NotificationChannel.EMAIL: {
            'subject': 'Your daily digest from {{website_name}}',
            'body_html': 'notifications/emails/digest_email.html',
            'body_text': 'Here is your daily digest.',
            'available_variables': [
                'user_name', 'website_name', 'digest_count', 'items'
            ],
        },
    },
    'scheduled.digest_weekly': {
        NotificationChannel.EMAIL: {
            'subject': 'Your weekly digest from {{website_name}}',
            'body_html': 'notifications/emails/digest_email.html',
            'body_text': 'Here is your weekly digest.',
            'available_variables': [
                'user_name', 'website_name', 'digest_count', 'items'
            ],
        },
    },
}


class Command(BaseCommand):
    help = 'Seed default notification templates for all active events.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--update',
            action='store_true',
            help='Update existing templates with new content.',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without writing.',
        )

    def handle(self, *args, **options):
        update = options['update']
        dry_run = options['dry_run']
        created = 0
        updated = 0
        skipped = 0

        for event_key, channels in DEFAULT_TEMPLATES.items():
            event = NotificationEvent.objects.filter(
                event_key=event_key, is_active=True
            ).first()

            if not event:
                self.stdout.write(
                    self.style.WARNING(
                        f"  SKIP  {event_key} - event not found in DB. "
                        f"Run seed_events first."
                    )
                )
                skipped += 1
                continue

            for channel, fields in channels.items():
                # Check if template already exists
                existing = NotificationTemplate.objects.filter(
                    event=event,
                    channel=channel,
                    website__isnull=True,  # global only
                    locale='en',
                ).order_by('-version').first()

                if existing and not update:
                    skipped += 1
                    continue

                if dry_run:
                    action = 'UPDATE' if existing else 'CREATE'
                    self.stdout.write(
                        f"  {action}  {event_key} / {channel}"
                    )
                    continue

                if existing and update:
                    for field, value in fields.items():
                        setattr(existing, field, value)
                    existing.save()
                    TemplateService.invalidate_cache(
                        event_key=event_key,
                        channel=channel,
                        website=None,
                    )
                    updated += 1
                else:
                    NotificationTemplate.objects.create(
                        event=event,
                        channel=channel,
                        website=None,
                        locale='en',
                        version=1,
                        is_active=True,
                        **fields,
                    )
                    created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone. Created: {created} | Updated: {updated} | "
                f"Skipped: {skipped}"
            )
        )
