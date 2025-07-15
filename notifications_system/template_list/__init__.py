from notifications_system.services.templates_registry import register_template

register_template(
    event_name="order_assigned",
    title_template="You've been assigned Order #{{ order.id }}",
    body_template="Hello {{ user.username }},\nA new order '{{ order.title }}' has been assigned to you.",
    html_template="""
        <p>Hello {{ user.username }},</p>
        <p>You’ve been assigned a new order: <strong>{{ order.title }}</strong>.</p>
        <p><a href="{{ frontend_base_url }}/orders/{{ order.id }}">View Order</a></p>
    """
)

# Register more...
register_template(
    event_name="order_completed",
    title_template="Order #{{ order.id }} Completed",
    body_template="Congratulations {{ user.username }},\nYour order '{{ order.title }}' has been completed.",
    html_template="""
        <p>Congratulations {{ user.username }},</p>
        <p>Your order <strong>{{ order.title }}</strong> has been completed.</p>
        <p><a href="{{ frontend_base_url }}/orders/{{ order.id }}">View Order</a></p>
    """
)
register_template(
    event_name="order_cancelled",
    title_template="Order #{{ order.id }} Cancelled",
    body_template="Hello {{ user.username }},\nYour order '{{ order.title }}' has been cancelled.",
    html_template="""
        <p>Hello {{ user.username }},</p>
        <p>Your order <strong>{{ order.title }}</strong> has been cancelled.</p>
        <p><a href="{{ frontend_base_url }}/orders/{{ order.id }}">View Order</a></p>
    """
)
register_template(
    event_name="user_registered",
    title_template="Welcome {{ user.username }}!",
    body_template="Hello {{ user.username }},\nThank you for registering on our platform.",
    html_template="""
        <p>Hello {{ user.username }},</p>
        <p>Thank you for registering on our platform!</p>
        <p><a href="{{ frontend_base_url }}">Visit your dashboard</a></p>
    """
)
register_template(
    event_name="password_reset",
    title_template="Password Reset Request",
    body_template="Hello {{ user.username }},\nYou requested a password reset. Click the link below to reset your password.",
    html_template="""
        <p>Hello {{ user.username }},</p>
        <p>You requested a password reset. Click the link below to reset your password:</p>
        <p><a href="{{ frontend_base_url }}/reset-password/{{ token }}">Reset Password</a></p>
    """
)
register_template(
    event_name="order_payment_success",
    title_template="Payment Successful for Order #{{ order.id }}",
    body_template="Hello {{ user.username }},\nYour payment for order '{{ order.title }}' was successful.",
    html_template="""
        <p>Hello {{ user.username }},</p>
        <p>Your payment for order <strong>{{ order.title }}</strong> was successful.</p>
        <p><a href="{{ frontend_base_url }}/orders/{{ order.id }}">View Order</a></p>
    """
)
register_template(
    event_name="order_payment_failed",
    title_template="Payment Failed for Order #{{ order.id }}",
    body_template="Hello {{ user.username }},\nYour payment for order '{{ order.title }}' failed. Please try again.",
    html_template="""
        <p>Hello {{ user.username }},</p>
        <p>Your payment for order <strong>{{ order.title }}</strong> failed. Please try again.</p>
        <p><a href="{{ frontend_base_url }}/orders/{{ order.id }}">View Order</a></p>
    """
)
register_template(
    event_name="order_refunded",
    title_template="Order #{{ order.id }} Refunded",
    body_template="Hello {{ user.username }},\nYour order '{{ order.title }}' has been refunded.",
    html_template="""
        <p>Hello {{ user.username }},</p>
        <p>Your order <strong>{{ order.title }}</strong> has been refunded.</p>
        <p><a href="{{ frontend_base_url }}/orders/{{ order.id }}">View Order</a></p>
    """
)
register_template(
    event_name="order_on_hold",
    title_template="Order #{{ order.id }} On Hold",
    body_template="Hello {{ user.username }},\nYour order '{{ order.title }}' is currently on hold.",
    html_template="""
        <p>Hello {{ user.username }},</p>
        <p>Your order <strong>{{ order.title }}</strong> is currently on hold.</p>
        <p><a href="{{ frontend_base_url }}/orders/{{ order.id }}">View Order</a></p>
    """
)
register_template(
    event_name="order_dispute_resolved",
    title_template="Order #{{ order.id }} Dispute Resolved",
    body_template="Hello {{ user.username }},\nThe dispute for your order '{{ order.title }}' has been resolved.",
    html_template="""
        <p>Hello {{ user.username }},</p>
        <p>The dispute for your order <strong>{{ order.title }}</strong> has been resolved.</p>
        <p><a href="{{ frontend_base_url }}/orders/{{ order.id }}">View Order</a></p>
    """
)
register_template(
    event_name="order_dispute_escalted",
    title_template="Order #{{ order.id }} Dispute Escalated",
    body_template="Hello {{ user.username }},\nThe dispute for your order '{{ order.title }}' has been escalated.",
    html_template="""
        <p>Hello {{ user.username }},</p>
        <p>The dispute for your order <strong>{{ order.title }}</strong> has been escalated.</p>
        <p><a href="{{ frontend_base_url }}/orders/{{ order.id }}">View Order</a></p>
    """
)
register_template(
    event_name="order_dispute_closed",
    title_template="Order #{{ order.id }} Dispute Closed",
    body_template="Hello {{ user.username }},\nThe dispute for your order '{{ order.title }}' has been closed.",
    html_template="""
        <p>Hello {{ user.username }},</p>
        <p>The dispute for your order <strong>{{ order.title }}</strong> has been closed.</p>
        <p><a href="{{ frontend_base_url }}/orders/{{ order.id }}">View Order</a></p>
    """
)
register_template(
    event_name="order_review_requested",
    title_template="Review Requested for Order #{{ order.id }}",
    body_template="Hello {{ user.username }},\nA review has been requested for your order '{{ order.title }}'.",
    html_template="""
        <p>Hello {{ user.username }},</p>
        <p>A review has been requested for your order <strong>{{ order.title }}</strong>.</p>
        <p><a href="{{ frontend_base_url }}/orders/{{ order.id }}">View Order</a></p>
    """
)
register_template(
    event_name="order_review_submitted",
    title_template="Review Submitted for Order #{{ order.id }}",
    body_template="Hello {{ user.username }},\nA review has been submitted for your order '{{ order.title }}'.",
    html_template="""
        <p>Hello {{ user.username }},</p>
        <p>A review has been submitted for your order <strong>{{ order.title }}</strong>.</p>
        <p><a href="{{ frontend_base_url }}/orders/{{ order.id }}">View Order</a></p>
    """
)
register_template(
    event_name="order_review_approved",
    title_template="Review Approved for Order #{{ order.id }}",
    body_template="Hello {{ user.username }},\nYour review for order '{{ order.title }}' has been approved.",
    html_template="""
        <p>Hello {{ user.username }},</p>
        <p>Your review for order <strong>{{ order.title }}</strong> has been approved.</p>
        <p><a href="{{ frontend_base_url }}/orders/{{ order.id }}">View Order</a></p>
    """
)
register_template(
    event_name="order_review_rejected",
    title_template="Review Rejected for Order #{{ order.id }}",
    body_template="Hello {{ user.username }},\nYour review for order '{{ order.title }}' has been rejected.",
    html_template="""
        <p>Hello {{ user.username }},</p>
        <p>Your review for order <strong>{{ order.title }}</strong> has been rejected.</p>
        <p><a href="{{ frontend_base_url }}/orders/{{ order.id }}">View Order</a></p>
    """
)
register_template(
    event_name="order_archived",
    title_template="Order #{{ order.id }} Archived",
    body_template="Hello {{ user.username }},\nYour order '{{ order.title }}' has been archived.",
    html_template="""
        <p>Hello {{ user.username }},</p>
        <p>Your order <strong>{{ order.title }}</strong> has been archived.</p>
        <p><a href="{{ frontend_base_url }}/orders/{{ order.id }}">View Order</a></p>
    """
)
register_template(
    event_name="order_approved",
    title_template="Order #{{ order.id }} Approved",
    body_template="Hello {{ user.username }},\nYour order '{{ order.title }}' has been approved.",
    html_template="""
        <p>Hello {{ user.username }},</p>
        <p>Your order <strong>{{ order.title }}</strong> has been approved.</p>
        <p><a href="{{ frontend_base_url }}/orders/{{ order.id }}">View Order</a></p>
    """
)
register_template(
    event_name="order_restored",
    title_template="Order #{{ order.id }} Restored",
    body_template="Hello {{ user.username }},\nYour order '{{ order.title }}' has been restored.",
    html_template="""
        <p>Hello {{ user.username }},</p>
        <p>Your order <strong>{{ order.title }}</strong> has been restored.</p>
        <p><a href="{{ frontend_base_url }}/orders/{{ order.id }}">View Order</a></p>
    """
)
register_template(
    event_name="payout_processing",
    title_template="Payout Processing",
    body_template="Hello {{ user.username }},\nYour payout is currently being processed.",
    html_template="""
        <p>Hello {{ user.username }},</p>
        <p>Your payout is currently being processed.</p>
        <p><a href="{{ frontend_base_url }}/payouts">View Payouts</a></p>
    """
)
register_template(
    event_name="payout_completed",
    title_template="Payout Completed",
    body_template="Hello {{ user.username }},\nYour payout has been successfully completed.",
    html_template="""
        <p>Hello {{ user.username }},</p>
        <p>Your payout has been successfully completed.</p>
        <p><a href="{{ frontend_base_url }}/payouts">View Payouts</a></p>
    """
)
register_template(
    event_name="payout_failed",
    title_template="Payout Failed",
    body_template="Hello {{ user.username }},\nYour payout has failed. Please check your account details.",
    html_template="""
        <p>Hello {{ user.username }},</p>
        <p>Your payout has failed. Please check your account details.</p>
        <p><a href="{{ frontend_base_url }}/payouts">View Payouts</a></p>
    """
)
register_template(
    event_name="payout_cancelled",
    title_template="Payout Cancelled",
    body_template="Hello {{ user.username }},\nYour payout has been cancelled.",
    html_template="""
        <p>Hello {{ user.username }},</p>
        <p>Your payout has been cancelled.</p>
        <p><a href="{{ frontend_base_url }}/payouts">View Payouts</a></p>
    """
)
register_template(
    event_name="ticket_created",
    title_template="New Ticket Created",
    body_template="Hello {{ user.username }},\nA new support ticket has been created.",
    html_template="""
        <p>Hello {{ user.username }},</p>
        <p>A new support ticket has been created.</p>
        <p><a href="{{ frontend_base_url }}/tickets">View Tickets</a></p>
    """
)
register_template(
    event_name="ticket_updated",
    title_template="Ticket Updated",
    body_template="Hello {{ user.username }},\nYour support ticket has been updated.",
    html_template="""
        <p>Hello {{ user.username }},</p>
        <p>Your support ticket has been updated.</p>
        <p><a href="{{ frontend_base_url }}/tickets">View Tickets</a></p>
    """
)
register_template(
    event_name="ticket_closed",
    title_template="Ticket Closed",
    body_template="Hello {{ user.username }},\nYour support ticket has been closed.",
    html_template="""
        <p>Hello {{ user.username }},</p>
        <p>Your support ticket has been closed.</p>
        <p><a href="{{ frontend_base_url }}/tickets">View Tickets</a></p>
    """
)
register_template(
    event_name="ticket_reopened",
    title_template="Ticket Reopened",
    body_template="Hello {{ user.username }},\nYour support ticket has been reopened.",
    html_template="""
        <p>Hello {{ user.username }},</p>
        <p>Your support ticket has been reopened.</p>
        <p><a href="{{ frontend_base_url }}/tickets">View Tickets</a></p>
    """
)
register_template(
    event_name="ticket_comment_added",
    title_template="New Comment on Ticket",
    body_template="Hello {{ user.username }},\nA new comment has been added to your support ticket.",
    html_template="""
        <p>Hello {{ user.username }},</p>
        <p>A new comment has been added to your support ticket.</p>
        <p><a href="{{ frontend_base_url }}/tickets">View Tickets</a></p>
    """
)
register_template(
    event_name="ticket_comment_updated",
    title_template="Comment Updated on Ticket",
    body_template="Hello {{ user.username }},\nA comment on your support ticket has been updated.",
    html_template="""
        <p>Hello {{ user.username }},</p>
        <p>A comment on your support ticket has been updated.</p>
        <p><a href="{{ frontend_base_url }}/tickets">View Tickets</a></p>
    """
)
register_template(
    event_name="ticket_comment_deleted",
    title_template="Comment Deleted on Ticket",
    body_template="Hello {{ user.username }},\nA comment on your support ticket has been deleted.",
    html_template="""
        <p>Hello {{ user.username }},</p>
        <p>A comment on your support ticket has been deleted.</p>
        <p><a href="{{ frontend_base_url }}/tickets">View Tickets</a></p>
    """
)
register_template(
    event_name="ticket_assigned",
    title_template="Ticket Assigned",
    body_template="Hello {{ user.username }},\nYour support ticket has been assigned to an agent.",
    html_template="""
        <p>Hello {{ user.username }},</p>
        <p>Your support ticket has been assigned to an agent.</p>
        <p><a href="{{ frontend_base_url }}/tickets">View Tickets</a></p>
    """
)
register_template(
    event_name="ticket_unassigned",
    title_template="Ticket Unassigned",
    body_template="Hello {{ user.username }},\nYour support ticket has been unassigned from the agent.",
    html_template="""
        <p>Hello {{ user.username }},</p>
        <p>Your support ticket has been unassigned from the agent.</p>
        <p><a href="{{ frontend_base_url }}/tickets">View Tickets</a></p>
    """
)
register_template(
    event_name="ticket_escalated",
    title_template="Ticket Escalated",
    body_template="Hello {{ user.username }},\nYour support ticket has been escalated to a higher level.",
    html_template="""
        <p>Hello {{ user.username }},</p>
        <p>Your support ticket has been escalated to a higher level.</p>
        <p><a href="{{ frontend_base_url }}/tickets">View Tickets</a></p>
    """
)
register_template(
    event_name="ticket_resolved",
    title_template="Ticket Resolved",
    body_template="Hello {{ user.username }},\nYour support ticket has been resolved.",
    html_template="""
        <p>Hello {{ user.username }},</p>
        <p>Your support ticket has been resolved.</p>
        <p><a href="{{ frontend_base_url }}/tickets">View Tickets</a></p>
    """
)
register_template(
    event_name="feedback_received",
    title_template="Feedback Received",
    body_template="Hello {{ user.username }},\nWe have received your feedback.",
    html_template="""
        <p>Hello {{ user.username }},</p>
        <p>We have received your feedback. Thank you!</p>
        <p><a href="{{ frontend_base_url }}/feedback">View Feedback</a></p>
    """
)
register_template(
    event_name="password_reset",
    title_template="Password Reset Request",
    body_template="Hello {{ user.username }},\nYou have requested a password reset. Click the link below to reset your password.",
    html_template="""
        <p>Hello {{ user.username }},</p>
        <p>You have requested a password reset. Click the link below to reset your password:</p>
        <p><a href="{{ frontend_base_url }}/reset-password/{{ token }}">Reset Password</a></p>
    """
)
register_template(
    event_name="account_suspended",
    title_template="Account Suspended",
    body_template="Hello {{ user.username }},\nYour account has been suspended. Please contact support for more information.",
    html_template="""
        <p>Hello {{ user.username }},</p>
        <p>Your account has been suspended. Please contact support for more information.</p>
        <p><a href="{{ frontend_base_url }}/support">Contact Support</a></p>
    """
)
register_template(
    event_name="new_message",
    title_template="New Message Received",
    body_template="Hello {{ user.username }},\nYou have received a new message.",
    html_template="""
        <p>Hello {{ user.username }},</p>
        <p>You have received a new message. Click the link below to view it:</p>
        <p><a href="{{ frontend_base_url }}/messages">View Messages</a></p>
    """
)
register_template(
    event_name="order_rated",
    title_template="Order #{{ order.id }} Rated",
    body_template="Hello {{ user.username }},\nYour order '{{ order.title }}' has been rated.",
    html_template="""
        <p>Hello {{ user.username }},</p>
        <p>Your order <strong>{{ order.title }}</strong> has been rated.</p>
        <p><a href="{{ frontend_base_url }}/orders/{{ order.id }}">View Order</a></p>
    """
)
register_template(
    event_name="order_delivered",
    title_template="Order #{{ order.id }} Delivered",
    body_template="Hello {{ user.username }},\nYour order '{{ order.title }}' has been delivered.",
    html_template="""
        <p>Hello {{ user.username }},</p>
        <p>Your order <strong>{{ order.title }}</strong> has been delivered.</p>
        <p><a href="{{ frontend_base_url }}/orders/{{ order.id }}">View Order</a></p>
    """
)
register_template(
    event_name="writer_reviewed",
    title_template="Writer Reviewed",
    body_template="Hello {{ user.username }},\nYour writer has been reviewed.",
    html_template="""
        <p>Hello {{ user.username }},</p>
        <p>Your writer has been reviewed. Click the link below to view the review:</p>
        <p><a href="{{ frontend_base_url }}/reviews">View Reviews</a></p>
    """
)
register_template(
    event_name="order_reassignment_requested",
    title_template="Order #{{ order.id }} Reassignment Requested",
    body_template="Hello {{ user.username }},\nA reassignment has been requested for your order '{{ order.title }}'.",
    html_template="""
        <p>Hello {{ user.username }},</p>
        <p>A reassignment has been requested for your order <strong>{{ order.title }}</strong>.</p>
        <p><a href="{{ frontend_base_url }}/orders/{{ order.id }}">View Order</a></p>
    """
)
register_template(
    event_name="order_reassignment_approved",
    title_template="Order #{{ order.id }} Reassignment Approved",
    body_template="Hello {{ user.username }},\nYour order '{{ order.title }}' reassignment has been approved.",
    html_template="""
        <p>Hello {{ user.username }},</p>
        <p>Your order <strong>{{ order.title }}</strong> reassignment has been approved.</p>
        <p><a href="{{ frontend_base_url }}/orders/{{ order.id }}">View Order</a></p>
    """
)
register_template(
    event_name="writer_suspended",
    title_template="Writer Suspended",
    body_template="Hello {{ user.username }},\nYour writer account has been suspended.",
    html_template="""
        <p>Hello {{ user.username }},</p>
        <p>Your writer account has been suspended. Please contact support for more information.</p>
        <p><a href="{{ frontend_base_url }}/support">Contact Support</a></p>
    """
)
register_template(
    event_name="writer_sent_on_probation",
    title_template="Writer Sent on Probation",
    body_template="Hello {{ user.username }},\nYour writer account has been sent on probation.",
    html_template="""
        <p>Hello {{ user.username }},</p>
        <p>Your writer account has been sent on probation. Please contact support for more information.</p>
        <p><a href="{{ frontend_base_url }}/support">Contact Support</a></p>
    """
)
register_template(
    event_name="user_blacklisted",
    title_template="User Blacklisted",
    body_template="Hello {{ user.username }},\nYour account has been blacklisted.",
    html_template="""
        <p>Hello {{ user.username }},</p>
        <p>Your account has been blacklisted. Please contact support for more information.</p>
        <p><a href="{{ frontend_base_url }}/support">Contact Support</a></p>
    """
)
register_template(
    event_name="user_unblacklisted",
    title_template="User Unblacklisted",
    body_template="Hello {{ user.username }},\nYour account has been unblacklisted.",
    html_template="""
        <p>Hello {{ user.username }},</p>
        <p>Your account has been unblacklisted. You can now access your account.</p>
        <p><a href="{{ frontend_base_url }}">Login</a></p>
    """
)
register_template(
    event_name="user_verified",
    title_template="User Account Verified",
    body_template="Hello {{ user.username }},\nYour account has been successfully verified.",
    html_template="""
        <p>Hello {{ user.username }},</p>
        <p>Your account has been successfully verified. You can now access all features.</p>
        <p><a href="{{ frontend_base_url }}">Login</a></p>
    """
)
register_template(
    event_name="user_unverified",
    title_template="User Account Unverified",
    body_template="Hello {{ user.username }},\nYour account has been unverified. Please contact support for more information.",
    html_template="""
        <p>Hello {{ user.username }},</p>
        <p>Your account has been unverified. Please contact support for more information.</p>
        <p><a href="{{ frontend_base_url }}/support">Contact Support</a></p>
    """
)
register_template(
    event_name="user_email_changed",
    title_template="Email Address Changed",
    body_template="Hello {{ user.username }},\nYour email address has been successfully changed.",
    html_template="""
        <p>Hello {{ user.username }},</p>
        <p>Your email address has been successfully changed. If this wasn't you, please contact support immediately.</p>
        <p><a href="{{ frontend_base_url }}">Login</a></p>
    """
)
register_template(
    event_name="user_password_changed",
    title_template="Password Changed",
    body_template="Hello {{ user.username }},\nYour password has been successfully changed.",
    html_template="""
        <p>Hello {{ user.username }},</p>
        <p>Your password has been successfully changed. If this wasn't you, please contact support immediately.</p>
        <p><a href="{{ frontend_base_url }}">Login</a></p>
    """
)
register_template(
    event_name="user_profile_updated",
    title_template="Profile Updated",
    body_template="Hello {{ user.username }},\nYour profile has been successfully updated.",
    html_template="""
        <p>Hello {{ user.username }},</p>
        <p>Your profile has been successfully updated.</p>
        <p><a href="{{ frontend_base_url }}/profile">View Profile</a></p>
    """
)
register_template(
    event_name="user_two_factor_enabled",
    title_template="Two-Factor Authentication Enabled",
    body_template="Hello {{ user.username }},\nTwo-factor authentication has been successfully enabled on your account.",
    html_template="""
        <p>Hello {{ user.username }},</p>
        <p>Two-factor authentication has been successfully enabled on your account. This adds an extra layer of security.</p>
        <p><a href="{{ frontend_base_url }}">Login</a></p>
    """
)
register_template(
    event_name="user_two_factor_disabled",
    title_template="Two-Factor Authentication Disabled",
    body_template="Hello {{ user.username }},\nTwo-factor authentication has been successfully disabled on your account.",
    html_template="""
        <p>Hello {{ user.username }},</p>
        <p>Two-factor authentication has been successfully disabled on your account. If this wasn't you, please contact support immediately.</p>
        <p><a href="{{ frontend_base_url }}">Login</a></p>
    """
)
register_template(
    event_name="user_subscription_renewed",
    title_template="Subscription Renewed",
    body_template="Hello {{ user.username }},\nYour subscription has been successfully renewed.",
    html_template="""
        <p>Hello {{ user.username }},</p>
        <p>Your subscription has been successfully renewed. Thank you for your continued support!</p>
        <p><a href="{{ frontend_base_url }}/subscriptions">View Subscriptions</a></p>
    """
)
register_template(
    event_name="user_subscription_cancelled",
    title_template="Subscription Cancelled",
    body_template="Hello {{ user.username }},\nYour subscription has been successfully cancelled.",
    html_template="""
        <p>Hello {{ user.username }},</p>
        <p>Your subscription has been successfully cancelled. We're sorry to see you go!</p>
        <p><a href="{{ frontend_base_url }}/subscriptions">View Subscriptions</a></p>
    """
)
register_template(
    event_name="user_subscription_expired",
    title_template="Subscription Expired",
    body_template="Hello {{ user.username }},\nYour subscription has expired. Please renew to continue enjoying our services.",
    html_template="""
        <p>Hello {{ user.username }},</p>
        <p>Your subscription has expired. Please renew to continue enjoying our services.</p>
        <p><a href="{{ frontend_base_url }}/subscriptions">Renew Subscription</a></p>
    """
)
register_template(
    event_name="user_subscription_upgraded",
    title_template="Subscription Upgraded",
    body_template="Hello {{ user.username }},\nYour subscription has been successfully upgraded.",
    html_template="""
        <p>Hello {{ user.username }},</p>
        <p>Your subscription has been successfully upgraded. Enjoy the new features!</p>
        <p><a href="{{ frontend_base_url }}/subscriptions">View Subscriptions</a></p>
    """
)
register_template(
    event_name="user_subscription_downgraded",
    title_template="Subscription Downgraded",
    body_template="Hello {{ user.username }},\nYour subscription has been successfully downgraded.",
    html_template="""
        <p>Hello {{ user.username }},</p>
        <p>Your subscription has been successfully downgraded. If you have any questions, please contact support.</p>
        <p><a href="{{ frontend_base_url }}/subscriptions">View Subscriptions</a></p>
    """
)
register_template(
    event_name="user_account_recovered",
    title_template="Account Recovered",
    body_template="Hello {{ user.username }},\nYour account has been successfully recovered.",
    html_template="""
        <p>Hello {{ user.username }},</p>
        <p>Your account has been successfully recovered. You can now access your account.</p>
        <p><a href="{{ frontend_base_url }}">Login</a></p>
    """
)
register_template(
    event_name="user_account_locked",
    title_template="Account Locked",
    body_template="Hello {{ user.username }},\nYour account has been locked due to suspicious activity. Please contact support.",
    html_template="""
        <p>Hello {{ user.username }},</p>
        <p>Your account has been locked due to suspicious activity. Please contact support for assistance.</p>
        <p><a href="{{ frontend_base_url }}/support">Contact Support</a></p>
    """
)
register_template(
    event_name="user_account_unlocked",
    title_template="Account Unlocked",
    body_template="Hello {{ user.username }},\nYour account has been successfully unlocked.",
    html_template="""
        <p>Hello {{ user.username }},</p>
        <p>Your account has been successfully unlocked. You can now access your account.</p>
        <p><a href="{{ frontend_base_url }}">Login</a></p>
    """
)
register_template(
    event_name="user_account_deleted",
    title_template="Account Deleted",
    body_template="Hello {{ user.username }},\nYour account has been successfully deleted. We're sorry to see you go!",
    html_template="""
        <p>Hello {{ user.username }},</p>
        <p>Your account has been successfully deleted. We're sorry to see you go!</p>
        <p><a href="{{ frontend_base_url }}">Visit our website</a></p>
    """
)
register_template(
    event_name="user_account_reactivated",
    title_template="Account Reactivated",
    body_template="Hello {{ user.username }},\nYour account has been successfully reactivated.",
    html_template="""
        <p>Hello {{ user.username }},</p>
        <p>Your account has been successfully reactivated. You can now access your account.</p>
        <p><a href="{{ frontend_base_url }}">Login</a></p>
    """
)
register_template(
    event_name="user_account_suspended",
    title_template="Account Suspended",
    body_template="Hello {{ user.username }},\nYour account has been suspended. Please contact support for more information.",
    html_template="""
        <p>Hello {{ user.username }},</p>
        <p>Your account has been suspended. Please contact support for more information.</p>
        <p><a href="{{ frontend_base_url }}/support">Contact Support</a></p>
    """
)