from celery import shared_task
from django.utils.timezone import now
from users.models import User
from datetime import timedelta
from users.models import UserSession, SecureToken

@shared_task
def archive_expired_accounts():
    """
    Archives all accounts that have been frozen for over 3 months.
    """
    expired_users = User.objects.filter(
        is_frozen=True,
        deletion_date__lte=now()
    )

    for user in expired_users:
        user.archive_account()

    return f"Archived {expired_users.count()} accounts."


@shared_task
def soft_delete_expired_accounts():
    """Deletes accounts that have been frozen for over 3 months."""
    three_months_ago = now() - timedelta(days=90)
    users_to_delete = User.objects.filter(
        is_frozen=True,
        deletion_date__lte=three_months_ago
    )

    for user in users_to_delete:
        user.is_active = False
        user.is_archived = True  # Mark as archived instead of deleting
        user.save()

    return f"{users_to_delete.count()} accounts archived."


@shared_task
def expire_old_sessions():
    """Deletes inactive sessions older than 24 hours."""
    UserSession.objects.filter(last_active__lt=now() - timedelta(hours=24)).delete()

@shared_task
def expire_old_sessions():
    """Terminate all expired sessions."""
    expired_sessions = UserSession.objects.filter(expires_at__lt=now(), is_active=True)
    for session in expired_sessions:
        session.terminate()
    return f"Expired {expired_sessions.count()} sessions."


@shared_task
def expire_old_tokens():
    """Terminate all expired tokens."""
    expired_tokens = SecureToken.objects.filter(
        expires_at__lt=now(),
        is_active=True
    )
    for token in expired_tokens:
        token.revoke()
    return f"Expired {expired_tokens.count()} tokens."



# To ensure that if a session is inactive for 30 days
# it should be automatically logged out.
@shared_task
def expire_old_sessions():
    """Removes sessions inactive for over 30 days."""
    expired_sessions = UserSession.objects.filter(last_active__lt=now() - timedelta(days=30))
    expired_sessions.delete()