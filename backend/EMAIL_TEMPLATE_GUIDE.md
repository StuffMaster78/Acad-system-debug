# 📧 Email Template Creation Guide

This guide explains how to create and use email templates in the Writing System Platform.

## 📁 Template Location

All email templates are stored in:
```
backend/notifications_system/templates/notifications/emails/
```

## 🎨 Available Templates

### Priority-Based Templates
- `base.html` - Base template (extended by others)
- `critical.html` - Emergency/Critical priority (Red)
- `high.html` - High priority (Orange)
- `normal.html` - Normal priority (Blue)
- `low.html` - Low priority (Gray)
- `passive.html` - Passive/Background (Light Gray)
- `medium.html` - Medium priority

### Custom Templates
- `welcome.html` - Welcome email for new users
- `email_verification.html` - Email verification/confirmation
- `account_activation.html` - Account activation emails
- `magic_link_login.html` - Magic link login emails
- `magic_link_verification.html` - Magic link verification emails
- `order_confirmation.html` - Order confirmation emails
- `order_assigned.html` - Order assignment notifications (for writers)
- `order_completed.html` - Order completion notifications
- `order_status_update.html` - Order status change notifications
- `order_cancelled.html` - Order cancellation notifications
- `revision_requested.html` - Revision request notifications
- `dispute_opened.html` - Dispute opened notifications
- `password_reset.html` - Password reset emails
- `password_change_request.html` - Password change request emails
- `password_changed.html` - Password changed confirmation
- `email_changed.html` - Email address changed confirmation
- `email_change_verification.html` - Email change verification
- `two_factor_code.html` - Two-factor authentication codes
- `mfa_setup.html` - Two-factor authentication setup
- `mfa_disabled.html` - Two-factor authentication disabled
- `account_locked.html` - Account locked notifications
- `account_recovery.html` - Account recovery emails
- `login_new_device.html` - New device login notifications
- `session_expired.html` - Session expired notifications
- `invoice.html` - Invoice emails
- `payment_received.html` - Payment confirmation emails
- `payment_reminder.html` - Payment reminder/overdue notices
- `refund_processed.html` - Refund processed notifications
- `writer_payment.html` - Writer payment notifications
- `writer_application_approved.html` - Writer application approval
- `writer_application_rejected.html` - Writer application rejection
- `subscription_renewal.html` - Subscription renewal reminders
- `subscription_expired.html` - Subscription expired notifications
- `account_suspended.html` - Account suspension notifications
- `account_deletion.html` - Account deletion confirmation
- `support_ticket_response.html` - Support ticket updates
- `referral_invitation.html` - Referral program invitations
- `newsletter.html` - Newsletter/announcement emails
- `deadline_reminder.html` - Deadline reminder notifications
- `system_maintenance.html` - System maintenance announcements
- `comment_reply.html` - Comment reply notifications
- `document_shared.html` - Document sharing notifications
- `team_invitation.html` - Team invitation emails
- `milestone_achieved.html` - Milestone achievement notifications
- `rating_request.html` - Rating/feedback request emails
- `trial_ending.html` - Trial ending reminders
- `feature_announcement.html` - New feature announcements
- `security_alert.html` - Security alert notifications
- `export_ready.html` - Data export ready notifications
- `api_key_generated.html` - API key generation notifications
- `bulk_action_completed.html` - Bulk action completion notifications
- `backup_completed.html` - Data backup completion notifications
- `account_reactivated.html` - Account reactivation notifications
- `payment_failed.html` - Payment failure notifications
- `order_delivered.html` - Order delivery notifications
- `contract_signed.html` - Contract signed notifications
- `contract_pending.html` - Contract pending signature notifications
- `approval_request.html` - Approval request notifications
- `approval_decision.html` - Approval decision notifications
- `workspace_invitation.html` - Workspace invitation emails
- `report_ready.html` - Report generation ready notifications
- `webhook_failed.html` - Webhook delivery failure notifications
- `digest_email.html` - Daily/weekly digest emails

## 🚀 How to Use Templates

### Method 1: Using Priority-Based Templates

```python
from notifications_system.utils.email_templates import send_priority_email
from notifications_system.enums import NotificationPriority

send_priority_email(
    user=user,
    subject="Welcome!",
    message="Thank you for joining us.",
    priority=NotificationPriority.NORMAL,
    website=website
)
```

### Method 2: Using Custom Templates by Name

```python
from notifications_system.utils.email_renderer import render_notification_email
from notifications_system.utils.email_templates import send_website_mail

# Render the template
html_content = render_notification_email(
    subject="Welcome!",
    message="Thank you for joining us.",
    template_name="notifications/emails/welcome.html",
    context={
        "user": user,
        "website_name": website.name,
        "cta_url": "https://example.com/dashboard",
        "cta_label": "Get Started"
    }
)

# Send the email
send_website_mail(
    subject="Welcome!",
    message="Thank you for joining us.",
    recipient_list=[user.email],
    html_message=html_content,
    website=website
)
```

### Method 3: Using Custom Templates with Context

```python
from django.template.loader import render_to_string
from notifications_system.utils.email_templates import send_website_mail

context = {
    "user": user,
    "subject": "Order Confirmed!",
    "message": "Your order has been confirmed.",
    "order_number": "ORD-12345",
    "order_total": "$99.99",
    "order_items": [
        {"name": "Product 1", "price": "$49.99"},
        {"name": "Product 2", "price": "$49.99"}
    ],
    "cta_url": "https://example.com/orders/12345",
    "cta_label": "View Order",
    "website_name": website.name
}

html_content = render_to_string(
    "notifications/emails/order_confirmation.html",
    context
)

send_website_mail(
    subject="Order Confirmed!",
    message="Your order has been confirmed.",
    recipient_list=[user.email],
    html_message=html_content,
    website=website
)
```

## 📝 Template Variables

### Common Variables Available in All Templates

- `subject` - Email subject line
- `message` - Main message content
- `user` - User object (has `.email`, `.get_full_name()`, etc.)
- `website_name` - Name of the website/platform
- `cta_url` - Call-to-action button URL (optional)
- `cta_label` - Call-to-action button label (optional)

### Template-Specific Variables

#### Welcome Template (`welcome.html`)
- All common variables

#### Order Confirmation Template (`order_confirmation.html`)
- `order_number` - Order number/ID
- `order_total` - Total order amount
- `order_items` - List of order items with `name` and `price`

#### Email Verification Template (`email_verification.html`)
- `verification_url` - Email verification link URL
- `verification_code` - Verification code (optional, for manual entry)
- `expiry_time` - Link expiration time (e.g., "24 hours")

#### Magic Link Login Template (`magic_link_login.html`)
- `magic_link_url` - Magic link URL for passwordless login
- `expiry_time` - Link expiration time (e.g., "15 minutes")
- `login_request_info` - Login request information
- `requested_from` - Where login was requested from
- `device_info` - Device information
- `ip_address` - IP address of request
- `requested_at` - When login was requested

#### Magic Link Verification Template (`magic_link_verification.html`)
- `verification_url` - Verification link URL
- `verification_code` - Verification code (optional)
- `action_description` - Description of action to verify
- `expiry_time` - Link expiration time

#### Account Activation Template (`account_activation.html`)
- `activation_url` - Account activation link URL
- `activation_code` - Activation code (optional)
- `next_steps` - List of next steps after activation
- `expiry_time` - Link expiration time (e.g., "7 days")

#### Password Reset Template (`password_reset.html`)
- `reset_url` - Password reset link URL
- `expiry_time` - Link expiration time (e.g., "1 hour")

#### Password Change Request Template (`password_change_request.html`)
- `change_password_url` - URL to change password
- `requested_from` - Where request came from
- `requested_at` - When request was made
- `expiry_time` - Link expiration time

#### Invoice Template (`invoice.html`)
- `invoice_number` - Invoice number
- `invoice_date` - Invoice date
- `invoice_amount` - Invoice amount
- `invoice_status` - Invoice status (paid, pending, etc.)

#### Payment Received Template (`payment_received.html`)
- `payment_amount` - Payment amount
- `payment_date` - Payment date
- `transaction_id` - Transaction ID

#### Order Status Update Template (`order_status_update.html`)
- `order_number` - Order number
- `order_status` - New order status
- `status_message` - Additional status message

#### Email Verification Template (`email_verification.html`)
- `verification_url` - Email verification link URL
- `verification_code` - Verification code (optional, for manual entry)
- `expiry_time` - Link expiration time (e.g., "24 hours")

#### Order Assigned Template (`order_assigned.html`)
- `order_number` - Order number/ID
- `order_title` - Order title/subject
- `order_type` - Type of order
- `deadline` - Order deadline
- `payment_amount` - Payment amount for the order
- `order_instructions` - Special instructions for the order

#### Order Completed Template (`order_completed.html`)
- `order_number` - Order number
- `order_title` - Order title
- `completed_by` - Name of person who completed the order
- `completed_at` - Completion date/time
- `delivery_notes` - Notes about the delivery

#### Payment Reminder Template (`payment_reminder.html`)
- `invoice_number` - Invoice number
- `amount_due` - Amount that needs to be paid
- `due_date` - Payment due date
- `days_overdue` - Number of days payment is overdue
- `order_details` - Details about the order requiring payment

#### Account Suspended Template (`account_suspended.html`)
- `suspension_reason` - Reason for account suspension
- `suspension_duration` - How long the suspension lasts
- `reactivation_date` - When the account will be reactivated
- `appeal_url` - URL to appeal the suspension
- `support_contact` - Support email address

#### Support Ticket Response Template (`support_ticket_response.html`)
- `ticket_number` - Support ticket number
- `ticket_subject` - Ticket subject
- `ticket_status` - Current ticket status
- `responded_by` - Name of person who responded
- `response_message` - The response message content

#### Two-Factor Authentication Template (`two_factor_code.html`)
- `verification_code` - The 2FA code
- `expiry_time` - Code expiration time (e.g., "10 minutes")
- `login_time` - When the login attempt occurred
- `login_location` - Location of login attempt (optional)
- `device_info` - Device information (optional)

#### Referral Invitation Template (`referral_invitation.html`)
- `referrer_name` - Name of person who referred
- `referral_bonus` - Bonus for the new user
- `referrer_bonus` - Bonus for the referrer
- `referral_url` - Sign-up URL with referral code
- `referral_code` - Referral code (for manual entry)
- `benefits` - List of benefits (optional)

#### Newsletter Template (`newsletter.html`)
- `newsletter_title` - Title of the newsletter
- `newsletter_date` - Publication date
- `featured_articles` - List of articles with `title`, `summary`, `url`
- `announcements` - List of announcements with `title`, `content`
- `unsubscribe_url` - URL to unsubscribe
- `preferences_url` - URL to manage preferences

#### Account Deletion Template (`account_deletion.html`)
- `deletion_date` - When the account will be deleted
- `pending_orders` - Number of pending orders that will be cancelled
- `cancel_url` - URL to cancel the deletion request
- `feedback_url` - URL to provide feedback

#### Writer Application Approved Template (`writer_application_approved.html`)
- `next_steps` - List of next steps for the new writer
- `writer_resources` - Resources and information for writers

#### Writer Application Rejected Template (`writer_application_rejected.html`)
- `rejection_reason` - Reason for rejection
- `can_reapply` - Whether they can reapply
- `reapply_after` - When they can reapply (e.g., "30 days")
- `improvement_tips` - List of tips for improvement

#### Revision Requested Template (`revision_requested.html`)
- `order_number` - Order number
- `order_title` - Order title
- `revision_deadline` - Deadline for revision
- `revision_notes` - Notes about what needs to be revised
- `revision_type` - Type of revision requested

#### Dispute Opened Template (`dispute_opened.html`)
- `order_number` - Order number
- `dispute_id` - Dispute ID
- `opened_by` - Who opened the dispute
- `dispute_reason` - Reason for dispute
- `dispute_description` - Detailed description
- `support_contact` - Support email address

#### Subscription Renewal Template (`subscription_renewal.html`)
- `subscription_plan` - Current plan name
- `renewal_date` - When subscription renews
- `renewal_amount` - Amount to be charged
- `billing_cycle` - Billing cycle (monthly, yearly, etc.)
- `plan_benefits` - List of plan benefits
- `payment_method` - Payment method on file
- `cancel_url` - URL to cancel subscription

#### Subscription Expired Template (`subscription_expired.html`)
- `expired_plan` - Name of expired plan
- `expired_date` - When subscription expired
- `available_plans` - List of available plans

#### Password Changed Template (`password_changed.html`)
- `changed_at` - When password was changed
- `changed_from` - Location/device where change was made
- `device_info` - Device information

#### Email Changed Template (`email_changed.html`)
- `old_email` - Previous email address
- `new_email` - New email address
- `changed_at` - When email was changed
- `verification_required` - Whether verification is needed

#### Email Change Verification Template (`email_change_verification.html`)
- `verification_url` - Verification link URL
- `verification_code` - Verification code (optional)
- `new_email` - New email address
- `old_email` - Previous email address
- `expiry_time` - Link expiration time

#### MFA Setup Template (`mfa_setup.html`)
- `setup_method` - MFA method (TOTP, SMS, etc.)
- `setup_at` - When MFA was enabled
- `backup_codes` - List of backup codes (important!)

#### MFA Disabled Template (`mfa_disabled.html`)
- `disabled_at` - When MFA was disabled
- `disabled_from` - Where it was disabled from

#### Account Locked Template (`account_locked.html`)
- `lock_reason` - Reason for account lock
- `locked_until` - When account will be unlocked
- `unlock_time` - Time remaining until unlock
- `unlock_url` - URL to unlock account immediately
- `unlock_actions` - List of actions to unlock
- `support_contact` - Support email address

#### Account Recovery Template (`account_recovery.html`)
- `recovery_url` - Account recovery link URL
- `recovery_code` - Recovery code (optional)
- `recovery_steps` - List of recovery steps
- `expiry_time` - Link expiration time

#### Login New Device Template (`login_new_device.html`)
- `login_time` - When login occurred
- `device_info` - Device information
- `browser_info` - Browser information
- `location` - Login location
- `ip_address` - IP address
- `this_was_me` - Whether to show "this was me" message

#### Session Expired Template (`session_expired.html`)
- `expired_at` - When session expired
- `session_duration` - How long session lasted
- `expiry_reason` - Reason for expiration
- `login_url` - URL to sign in again

#### Order Cancelled Template (`order_cancelled.html`)
- `order_number` - Order number
- `order_title` - Order title
- `cancelled_at` - When order was cancelled
- `cancelled_by` - Who cancelled the order
- `cancellation_reason` - Reason for cancellation
- `refund_amount` - Refund amount (if applicable)
- `refund_method` - How refund will be processed
- `refund_processing_time` - Expected processing time

#### Refund Processed Template (`refund_processed.html`)
- `refund_amount` - Amount refunded
- `transaction_id` - Transaction ID
- `refund_method` - How refund was processed
- `processed_date` - When refund was processed
- `order_number` - Related order number
- `refund_reason` - Reason for refund
- `expected_arrival` - When refund will arrive

#### Writer Payment Template (`writer_payment.html`)
- `payment_amount` - Payment amount
- `payment_method` - Payment method
- `payment_date` - Payment date
- `transaction_id` - Transaction ID
- `payment_period` - Payment period
- `completed_orders` - List of completed orders with amounts
- `tax_info` - Tax information

#### Deadline Reminder Template (`deadline_reminder.html`)
- `deadline_date` - Deadline date/time
- `time_remaining` - Time remaining until deadline
- `order_number` - Related order number
- `order_title` - Order title
- `is_urgent` - Whether deadline is urgent
- `task_description` - Description of the task

#### System Maintenance Template (`system_maintenance.html`)
- `maintenance_start` - Maintenance start time
- `maintenance_end` - Maintenance end time
- `duration` - Expected duration
- `affected_services` - List of affected services
- `maintenance_details` - Details about the maintenance
- `status_url` - URL to check status

#### Comment Reply Template (`comment_reply.html`)
- `commenter_name` - Name of person who replied
- `reply_content` - The reply content
- `original_comment` - Your original comment
- `context_title` - Title/context of what was commented on

#### Document Shared Template (`document_shared.html`)
- `document_name` - Name of the document
- `shared_by` - Person who shared the document
- `shared_at` - When document was shared
- `access_level` - Access level (view, edit, comment)
- `document_description` - Document description
- `share_message` - Optional message from sharer

#### Team Invitation Template (`team_invitation.html`)
- `team_name` - Name of the team
- `inviter_name` - Person who sent the invitation
- `team_description` - Description of the team
- `role` - Role you'll have on the team
- `invitation_url` - URL to accept invitation
- `expires_at` - When invitation expires

#### Milestone Achieved Template (`milestone_achieved.html`)
- `milestone_name` - Name of the milestone
- `milestone_description` - Description of milestone
- `achievement_stats` - List of achievement statistics
- `reward` - Reward for achieving milestone

#### Rating Request Template (`rating_request.html`)
- `order_number` - Related order number
- `service_name` - Service name
- `completed_date` - When service was completed
- `rating_url` - URL to leave rating
- `quick_ratings` - List of quick rating options with `label` and `url`

#### Trial Ending Template (`trial_ending.html`)
- `trial_end_date` - When trial ends
- `days_remaining` - Days remaining in trial
- `trial_features` - List of features that will be lost
- `subscription_plans` - List of available subscription plans

#### Feature Announcement Template (`feature_announcement.html`)
- `feature_name` - Name of the new feature
- `feature_description` - Description of the feature
- `feature_benefits` - List of feature benefits
- `feature_image_url` - URL to feature image
- `availability_note` - Note about feature availability

#### Security Alert Template (`security_alert.html`)
- `alert_type` - Type of security alert
- `detected_at` - When alert was detected
- `location` - Location of the event
- `device_info` - Device information
- `alert_details` - Detailed alert information
- `recommended_actions` - List of recommended security actions
- `support_contact` - Security support contact

#### Export Ready Template (`export_ready.html`)
- `export_name` - Name of the export
- `export_type` - Export format/type
- `file_size` - Size of the export file
- `created_at` - When export was created
- `export_contents` - List of what's included in export
- `download_url` - URL to download export
- `expires_at` - When download link expires

#### API Key Generated Template (`api_key_generated.html`)
- `api_key_name` - Name of the API key
- `created_at` - When key was created
- `permissions` - Key permissions
- `api_key` - The actual API key (show only once!)
- `documentation_url` - URL to API documentation

#### Bulk Action Completed Template (`bulk_action_completed.html`)
- `action_type` - Type of bulk action
- `total_items` - Total number of items processed
- `successful_count` - Number of successful operations
- `failed_count` - Number of failed operations
- `completed_at` - When action completed
- `errors` - List of error messages (if any)
- `results_summary` - Summary of results

#### Backup Completed Template (`backup_completed.html`)
- `backup_name` - Name of the backup
- `backup_type` - Type of backup
- `file_size` - Size of backup file
- `completed_at` - When backup completed
- `items_backed_up` - Number of items backed up
- `backup_contents` - List of what was backed up
- `download_url` - URL to download backup
- `storage_location` - Where backup is stored
- `retention_period` - How long backup is retained

#### Account Reactivated Template (`account_reactivated.html`)
- `reactivated_at` - When account was reactivated
- `reactivated_by` - Who reactivated the account
- `restored_features` - List of features that are now available

#### Payment Failed Template (`payment_failed.html`)
- `amount` - Payment amount
- `payment_method` - Payment method used
- `failed_at` - When payment failed
- `failure_reason` - Reason for failure
- `retry_attempts` - Number of retry attempts remaining
- `next_retry_date` - When next retry will occur
- `service_interruption` - Whether service will be interrupted

#### Order Delivered Template (`order_delivered.html`)
- `order_number` - Order number
- `order_title` - Order title
- `delivered_at` - When order was delivered
- `delivered_by` - Who delivered the order
- `delivery_notes` - Notes about the delivery
- `download_files` - List of files with `name` and `size`
- `review_period` - Time available to review

#### Contract Signed Template (`contract_signed.html`)
- `contract_name` - Name of the contract
- `contract_id` - Contract ID
- `signed_at` - When contract was signed
- `signed_by` - List of people who signed
- `contract_terms` - List of key contract terms
- `download_url` - URL to download signed contract

#### Contract Pending Template (`contract_pending.html`)
- `contract_name` - Name of the contract
- `contract_id` - Contract ID
- `expires_at` - When contract expires
- `sent_by` - Who sent the contract
- `contract_summary` - Summary of contract
- `sign_url` - URL to sign contract

#### Approval Request Template (`approval_request.html`)
- `request_title` - Title of the request
- `request_description` - Description of what needs approval
- `request_details` - Dictionary of request details
- `requested_by` - Who requested approval
- `requested_at` - When request was made
- `approval_url` - URL to approve/reject
- `expires_at` - When request expires

#### Approval Decision Template (`approval_decision.html`)
- `decision` - Decision made (approved/rejected)
- `request_title` - Title of the request
- `request_description` - Description of the request
- `decided_by` - Who made the decision
- `decided_at` - When decision was made
- `decision_reason` - Reason for decision
- `next_steps` - List of next steps (if approved)
- `appeal_info` - Appeal information (if rejected)

#### Workspace Invitation Template (`workspace_invitation.html`)
- `workspace_name` - Name of the workspace
- `inviter_name` - Person who sent invitation
- `workspace_description` - Description of workspace
- `role` - Role in workspace
- `workspace_features` - List of workspace features
- `invitation_url` - URL to accept invitation
- `expires_at` - When invitation expires

#### Report Ready Template (`report_ready.html`)
- `report_name` - Name of the report
- `report_type` - Type of report
- `file_format` - File format (PDF, CSV, etc.)
- `file_size` - Size of report file
- `generated_at` - When report was generated
- `report_period` - Period covered by report
- `report_summary` - Summary of report contents
- `download_url` - URL to download report
- `expires_at` - When download link expires

#### Webhook Failed Template (`webhook_failed.html`)
- `webhook_url` - Webhook endpoint URL
- `event_type` - Type of event
- `failed_at` - When delivery failed
- `attempt_number` - Current attempt number
- `max_attempts` - Maximum retry attempts
- `error_message` - Error message/details
- `retry_info` - Information about retries

## 🎨 Creating New Templates

### Step 1: Create the Template File

Create a new file in `backend/notifications_system/templates/notifications/emails/`:

```html
{% extends "notifications/emails/base.html" %}
{% block content %}
<div style="text-align: center; padding: 20px 0;">
  <h1 style="color: #2563eb;">{{ subject }}</h1>
</div>

<div style="padding: 20px 0;">
  <p>{{ message|linebreaks }}</p>
  
  {% if cta_url %}
  <div style="text-align: center; margin: 30px 0;">
    <a href="{{ cta_url }}" class="btn">
      {{ cta_label|default:"View Details" }}
    </a>
  </div>
  {% endif %}
</div>
{% endblock %}
```

### Step 2: Use the Template

```python
from django.template.loader import render_to_string
from notifications_system.utils.email_templates import send_website_mail

context = {
    "subject": "Your Custom Email",
    "message": "This is a custom email template.",
    "user": user,
    "website_name": website.name,
    "cta_url": "https://example.com",
    "cta_label": "Click Here"
}

html_content = render_to_string(
    "notifications/emails/your_custom_template.html",
    context
)

send_website_mail(
    subject="Your Custom Email",
    message="This is a custom email template.",
    recipient_list=[user.email],
    html_message=html_content,
    website=website
)
```

## 🔧 Best Practices

1. **Always extend `base.html`** - This ensures consistent styling and structure
2. **Use inline styles** - Email clients don't support external stylesheets well
3. **Test in multiple email clients** - Gmail, Outlook, Apple Mail, etc.
4. **Keep it simple** - Complex layouts may break in some email clients
5. **Use semantic HTML** - Tables for layout, proper heading hierarchy
6. **Include plain text fallback** - Always provide a `message` parameter
7. **Make CTAs clear** - Use prominent buttons with clear labels
8. **Mobile responsive** - Test on mobile devices

## 📧 Template Examples

See the existing templates in `backend/notifications_system/templates/notifications/emails/` for reference:
- `welcome.html` - Welcome email example
- `order_confirmation.html` - Order confirmation example
- `password_reset.html` - Password reset example
- `invoice.html` - Invoice example
- `payment_received.html` - Payment confirmation example
- `order_status_update.html` - Status update example

## 🧪 Testing Templates

### Test in Development

```python
# In Django shell or test
from django.template.loader import render_to_string

context = {
    "subject": "Test Email",
    "message": "This is a test.",
    "user": user,
    "website_name": "Test Platform"
}

html = render_to_string("notifications/emails/welcome.html", context)
print(html)  # View the rendered HTML
```

### Send Test Email

```python
from notifications_system.utils.email_templates import send_website_mail

send_website_mail(
    subject="Test Email",
    message="This is a test email.",
    recipient_list=["your-email@example.com"],
    html_message=html,
    website=website
)
```

## 📚 Additional Resources

- See `EMAIL_TEMPLATES.md` for detailed template system documentation
- See `NOTIFICATION_INTEGRATION_GUIDE.md` for notification system integration
- Django Template Language: https://docs.djangoproject.com/en/stable/topics/templates/

