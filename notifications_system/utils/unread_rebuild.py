# notifications_system/utils/unread_rebuild.py
from notifications_system.models.notifications_user_status import NotificationsUserStatus
from .unread_counter import set_

def rebuild_unread(user, website=None):
    qs = NotificationsUserStatus.objects.filter(user=user, is_read=False)
    if website:
        qs = qs.filter(notification__website=website)
    count = qs.count()
    set_(user.id, count, getattr(website, "id", None))
    return count