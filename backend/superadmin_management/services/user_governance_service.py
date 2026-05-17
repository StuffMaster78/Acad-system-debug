from django.contrib.auth import get_user_model
from django.db import transaction

from users.domain.user_roles import UserRole
from notifications_system.services.notification_service import NotificationService

User = get_user_model()


class UserGovernanceService:

    @staticmethod
    @transaction.atomic
    def create_user(*, superadmin, username, email, role: UserRole, phone_number="", website=None):

        temp_password = UserGovernanceService._generate_temp_password()

        user = User(
            username=username,
            email=email,
            role=role.value,
            phone_number=phone_number,
        )
        user.set_password(temp_password)
        user.save()

        NotificationService.notify(
            event_key="superadmin.user.created",
            recipient=user,
            website=website,
            context={
                "username": username,
                "role": role.value,
                "temp_password": temp_password,
            },
        )

        return user


    @staticmethod
    @transaction.atomic
    def change_role(*, superadmin, user, new_role: UserRole, website=None):

        old_role = user.role
        user.role = new_role.value
        user.save(update_fields=["role"])

        NotificationService.notify(
            event_key="superadmin.user.role_changed",
            recipient=user,
            website=website,
            context={
                "old_role": old_role,
                "new_role": new_role.value,
            },
        )

        return user


    @staticmethod
    def _generate_temp_password(length=12):
        import secrets
        import string

        alphabet = string.ascii_letters + string.digits
        return "".join(secrets.choice(alphabet) for _ in range(length))