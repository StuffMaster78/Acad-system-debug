from django.contrib.auth import get_user_model
from superadmin_management.models import Blacklist
from users_state.services.user_state_service import UserStateService

User = get_user_model()


def handle_user_blacklisted(event):
    user = User.objects.get(pk=event.user_id)

    Blacklist.objects.create(
        user=user,
        website=getattr(event, "website", None),
        reason=event.reason,
        is_active=True,
    )

    UserStateService.blacklist_user(
        user=user,
        website=getattr(event, "website", None),
        reason=event.reason,
    )