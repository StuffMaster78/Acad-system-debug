# communications/throttles.py

from rest_framework.throttling import UserRateThrottle


class SuperAdminAuditThrottle(UserRateThrottle):
    scope = "superadmin_audit"

class AuditLogThrottle(UserRateThrottle):
    scope = "audit_log" 
    rate = "10/minute"  # Adjust as needed
class CommunicationMessageThrottle(UserRateThrottle):
    scope = "communication_message"
    rate = "60/minute"  # Increased from 20/minute for better UX
class CommunicationThreadThrottle(UserRateThrottle):
    scope = "communication_thread"
    rate = "60/minute"  # Increased from 15/minute for better UX

class CommunicationNotificationThrottle(UserRateThrottle):
    scope = "communication_notification"
    rate = "30/minute"  # Adjust as needed

class FlaggedMessageThrottle(UserRateThrottle):
    scope = "flagged_message"
    rate = "5/minute"  # Adjust as needed

class DisputeMessageThrottle(UserRateThrottle):
    scope = "dispute_message"
    rate = "10/minute"  # Adjust as needed

class ScreenedWordThrottle(UserRateThrottle):
    scope = "screened_word"
    rate = "10/minute"  # Adjust as needed

class OrderMessageThreadThrottle(UserRateThrottle):
    scope = "order_message_thread"
    rate = "15/minute"  # Adjust as needed

class OrderMessageNotificationThrottle(UserRateThrottle):
    scope = "order_message_notification"
    rate = "30/minute"  # Adjust as needed

class OrderMessageThrottle(UserRateThrottle):
    scope = "order_message"
    rate = "60/minute"  # Increased from 20/minute for better UX

class OrderMessageReadReceiptThrottle(UserRateThrottle):
    scope = "order_message_read_receipt"
    rate = "10/minute"  # Adjust as needed

class OrderMessageFlagThrottle(UserRateThrottle):
    scope = "order_message_flag"
    rate = "5/minute"  # Adjust as needed

class OrderMessageUnblockThrottle(UserRateThrottle):
    scope = "order_message_unblock"
    rate = "5/minute"  # Adjust as needed   

class OrderMessageSearchThrottle(UserRateThrottle):
    scope = "order_message_search"
    rate = "10/minute"  # Adjust as needed

class OrderMessageCreateThrottle(UserRateThrottle):
    scope = "order_message_create"
    rate = "5/minute"  # Adjust as needed

class OrderMessageUpdateThrottle(UserRateThrottle):
    scope = "order_message_update"
    rate = "5/minute"  # Adjust as needed

class OrderMessageDeleteThrottle(UserRateThrottle):
    scope = "order_message_delete"
    rate = "5/minute"  # Adjust as needed

class OrderMessageBulkCreateThrottle(UserRateThrottle):
    scope = "order_message_bulk_create"
    rate = "3/minute"  # Adjust as needed

class OrderMessageBulkUpdateThrottle(UserRateThrottle):
    scope = "order_message_bulk_update"
    rate = "3/minute"  # Adjust as needed

class OrderMessageBulkDeleteThrottle(UserRateThrottle):
    scope = "order_message_bulk_delete"
    rate = "3/minute"  # Adjust as needed

class OrderMessageNotificationCreateThrottle(UserRateThrottle):
    scope = "order_message_notification_create"
    rate = "10/minute"  # Adjust as needed  

class OrderMessageNotificationUpdateThrottle(UserRateThrottle):
    scope = "order_message_notification_update"
    rate = "10/minute"  # Adjust as needed

class OrderMessageNotificationDeleteThrottle(UserRateThrottle):
    scope = "order_message_notification_delete"
    rate = "10/minute"  # Adjust as needed

class OrderMessageNotificationBulkCreateThrottle(UserRateThrottle):
    scope = "order_message_notification_bulk_create"
    rate = "5/minute"  # Adjust as needed

class OrderMessageNotificationBulkUpdateThrottle(UserRateThrottle):
    scope = "order_message_notification_bulk_update"
    rate = "5/minute"  # Adjust as needed

class OrderMessageNotificationBulkDeleteThrottle(UserRateThrottle):
    scope = "order_message_notification_bulk_delete"
    rate = "5/minute"  # Adjust as needed

class OrderMessageThreadCreateThrottle(UserRateThrottle):
    scope = "order_message_thread_create"
    rate = "10/minute"  # Adjust as needed  

class OrderMessageThreadUpdateThrottle(UserRateThrottle):
    scope = "order_message_thread_update"
    rate = "10/minute"  # Adjust as needed  

class OrderMessageThreadDeleteThrottle(UserRateThrottle):
    scope = "order_message_thread_delete"
    rate = "10/minute"  # Adjust as needed