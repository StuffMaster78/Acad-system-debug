# from celery import shared_task
# from notifications_system.models import Notification

# @shared_task
# def send_scheduled_notification(notification_id):
#     """
#     Task to send scheduled notifications.
#     """
#     notification = Notification.objects.get(id=notification_id)
#     notification.send()