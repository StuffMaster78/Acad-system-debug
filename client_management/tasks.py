from core.celery import shared_task
from core.celery import app as celery_app
from django.utils.timezone import now
from users.models import User
from .models import BlacklistedEmail
from django.core.mail import send_mail
from django.db import transaction


@shared_task
def delete_scheduled_accounts():
    """
    Deletes accounts that are frozen and scheduled for deletion.
    Blacklists their email for the associated website and notifies the admin.
    """
    users_to_delete = User.objects.filter(
        is_frozen=True, is_deletion_requested=True, deletion_date__lte=now()
    )

    if not users_to_delete.exists():
        print("No accounts scheduled for deletion at this time.")
        return

    for user in users_to_delete:
        try:
            with transaction.atomic():
                # Blacklist email for the specific website
                BlacklistedEmail.objects.create(email=user.email, website=user.website)

                # Log deletion
                print(f"Deleting user {user.username} (ID: {user.id})")

                # Notify admin
                send_admin_notification(user)

                # Permanently delete the user
                user.delete()

        except Exception as e:
            print(
                f"Error while processing deletion for user {user.username} (ID: {user.id}): {str(e)}"
            )


def send_admin_notification(user):
    """
    Sends an email notification to the admin about the account deletion.
    """
    subject = "Account Deletion Notification"
    message = (
        f"The following account has been deleted:\n\n"
        f"Username: {user.username}\n"
        f"Email: {user.email}\n"
        f"Website: {user.website.name}\n"
        f"Deletion Date: {now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        f"The email address has been blacklisted for this website.\n\n"
        f"Regards,\n"
        f"Your System"
    )
    send_mail(
        subject,
        message,
        "support@yourdomain.com",  # Replace with your support email
        ["admin@yourdomain.com"],  # Replace with your admin email
        fail_silently=False,
    )