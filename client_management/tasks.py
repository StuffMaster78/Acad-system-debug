from core.celery import shared_task
from django.utils.timezone import now
from users.models import User
from .models import BlacklistedEmail


@shared_task
def delete_scheduled_accounts():
    """
    Deletes accounts that are frozen and scheduled for deletion.
    """
    users_to_delete = User.objects.filter(
        is_frozen=True, is_deletion_requested=True, deletion_date__lte=now()
    )
    for user in users_to_delete:
        # Blacklist email for the specific website
        BlacklistedEmail.objects.create(email=user.email, website=user.website)

        # Log deletion
        print(f"Deleting user {user.username} (ID: {user.id})")

        # Permanently delete the user
        user.delete()