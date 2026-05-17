from django.contrib.auth import get_user_model
from users_state.services.user_state_service import UserStateService

User = get_user_model()


def handle_user_suspended(event):
    user = User.objects.get(pk=event.user_id)

    UserStateService.suspend_user(
        user=user,
        website=getattr(event, "website", None),
        reason=event.reason,
    )