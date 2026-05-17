from users_state.models import UserState


def get_user_state(user):
    return UserState.objects.filter(user=user).first()


def is_suspended(user) -> bool:
    state = get_user_state(user)
    return bool(state and state.is_suspended)


def is_blacklisted(user) -> bool:
    state = get_user_state(user)
    return bool(state and state.is_blacklisted)