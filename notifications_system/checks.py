from django.core.checks import register, Error
from notifications_system.services.templates_registry import (
    get_template as get_registered_templates
)

@register()
def check_notification_templates(app_configs, **kwargs):
    errors = []

    required_templates = [
        "order_assigned",
        "order_completed",
        "writer_declined",
        "missed_deadline",
        "fine_applied",
        "generic",
        "system_error",
        "order_created",
        "order_approved",
        "order_rejected",
        "order_archived",
        "order_cancelled",
        "order_assigned",
        "order_completed",
        "order_declined",
        "order_missed_deadline",
        "order_fine_applied",
        "order_generic",
        "order_system_error",
        "order_on_hold",
        "payment_success",
        "payment_failed",
        "payment_refunded",
        "dispute_created",
        "dispute_resolved",
        "dispute_escalated",
        "dispute_closed",
        "ticket_created",
        "ticket_updated",
        "ticket_closed",
        "ticket_reopened",
        "ticket_assigned",
        "ticket_escalated",
        "ticket_resolved",
        "message_sent",
        "message_received",
        "message_replied",
        "message_forwarded",
        "message_deleted",
        "message_edited",
        "message_flagged"
        "message_unflagged",
        "message_mentioned",
        "message_quoted",

        "referral_created",
        "referral_approved",
        "referral_rejected",
        "referral_expired",
        "referral_earned",
        "referral_success",
        "referral_bonus",

        "wallet_balance_low",
        "wallet_credited",
        "wallet_debited",
        "wallet_transaction_failed",
        "wallet_transaction_success",
        "wallet_refund_initiated",
        "wallet_refund_completed",
        "payout_processing",
        "payout_completed",
        "payout_failed",
        "payout_cancelled",

        "fine_applied",
        "fine_removed",

        "discount_applied",
        "discount_removed",
        "discount_expired",
        "discount_code_used",
        "discount_code_expired",
        "discount_code_invalid",
        "discount_code_created",
        "discount_code_updated",
        "discount_code_deleted",
        "discount_code_redeemed",

        "loyalty_points_earned",
        "loyalty_points_redeemed",
        "loyalty_points_expired",
        "loyalty_points_balance_low",
        "loyalty_points_balance_updated",

        "loyalty_points_transaction_failed",
        "loyalty_points_transaction_success",
        "loyalty_points_refund_initiated",
        "loyalty_points_refund_completed",  

        "refund_initiated",
        "refund_completed",
        "refund_failed",
        "refund_cancelled",
        "refund_requested",
        "refund_approved",
        "refund_rejected",
        "refund_processed",
        "refund_pending",
        "refund_issued",

    

        "writer_assigned",
        "writer_completed",
        "writer_declined",
        "writer_missed_deadline",
        "writer_fine_applied",
        "writer_generic",
        "writer_system_error",
        "writer_order_created",
        "writer_order_approved",
        "writer_order_rejected",
        "writer_order_expired",
        "writer_order_cancelled",
        "writer_order_assigned",
        "writer_order_completed",
        "writer_order_declined",
        "writer_order_missed_deadline",
        "writer_order_fine_applied",
        "writer_order_generic",
        "writer_order_system_error",
        "writer_order_assigned",
        "writer_order_completed",
        "writer_order_declined",
        "writer_order_missed_deadline",
        "writer_order_fine_applied",
        "writer_order_generic",
        "writer_order_system_error"

        "blog_post_published",
        "blog_post_updated",
        "blog_post_deleted",
        "blog_post_commented",
        "blog_comment_replied",
        "blog_comment_liked",
        "blog_comment_unliked", 
        "blog_comment_deleted",
        "blog_comment_flagged",
        "blog_comment_unflagged",
        "blog_comment_mentioned",
        "blog_comment_quoted",
        "blog_comment_edited",
        "blog_comment_forwarded",
        "blog_comment_deleted",
        "blog_comment_edited",
        "blog_comment_forwarded",
        "blog_comment_deleted",
        "blog_comment_edited",
        "blog_comment_forwarded",
        "blog_post_drafted",
        "blog_post_scheduled",
        "blog_post_published",
        "blog_post_updated",
        "blog_post_deleted",
        "blog_post_shared",


        "file_uploaded",
        "file_deleted",
        "file_updated",
        "file_shared",
        "file_downloaded",
        "file_access_requested",
        "file_access_granted",
        "file_access_denied",
        "file_access_revoked",
        "file_access_expired",
        "file_access_requested",
        "file_access_granted",
        "file_access_denied",
        "file_archived",
        "file_access_expired",
        "file_access_requested",
        "file_access_granted",
        "file_access_denied",

        "payment_success",
        "payment_failed",
        "payment_refunded",
        "payment_pending",
        "payment_canceled",
        "payment_received",
        "payment_processed",
        "payment_verified",
        "payment_declined",
        "payment_disputed",
        "payment_settled",
        "payment_chargeback",
        "payment_refund_initiated",
        "payment_refund_completed",
        "payment_refund_failed",    
    
    ]

    registered = get_registered_templates()

    for tpl in required_templates:
        if tpl not in registered:
            errors.append(
                Error(
                    f"Notification template '{tpl}' is not registered.",
                    id="notifications_system.E001",
                )
            )

    return errors