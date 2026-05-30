from celery import shared_task
from django.utils.timezone import now
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta
from referrals.models import ReferralBonusDecay
from wallets.constants import WalletEntryType
from wallets.models import WalletEntry

@shared_task
def expire_referral_bonuses():
    """Legacy no-op kept for backwards compat with any queued messages."""
    count = WalletEntry.objects.filter(
        entry_type=WalletEntryType.REFERRAL_BONUS,
    ).count()
    return f"Referral bonus expiration is policy-managed for {count} wallet entries."


@shared_task
def expire_stale_referral_invitations():
    """Expire pending invitations that have passed their expiry date."""
    from referrals.services.referral_invitation_service import ReferralInvitationService
    expired = ReferralInvitationService.expire_stale()
    return f"Expired {expired} stale referral invitations."


def send_referral_bonus_expired_email(user):
    """Send an email notification to the user when their referral bonus expires."""
    subject = "Referral Bonus Expired"
    message = f"Hello {user.first_name},\n\nYour referral bonus has expired and is no longer available."
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]

    send_mail(subject, message, from_email, recipient_list)


@shared_task
def notify_referral_bonus_expiration():
    """
    This task notifies users 24 hours before their referral bonus expires.
    """
    return "Referral bonus expiration notifications are policy-managed."


def send_referral_bonus_expiration_warning_email(user):
    """Send an email reminder when the referral bonus is close to expiration."""
    subject = "Referral Bonus Expiring Soon"
    message = f"Hello {user.first_name},\n\nYour referral bonus is about to expire in 24 hours. Please make use of it before it expires!"
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]

    send_mail(subject, message, from_email, recipient_list)


@shared_task
def decay_referral_bonuses():
    """
    Periodic task to decay referral bonuses as they approach expiration (if applicable).
    """
    return "Referral bonus decay is policy-managed for canonical wallet entries."

@shared_task
def apply_monthly_referral_bonus_decay():
    decays = ReferralBonusDecay.objects.all().select_related('wallet_transaction')
    for decay in decays:
        decay.apply_decay()

def send_referral_bonus_decay_email(user, new_amount):
    """Send an email notification about the decay of the referral bonus."""
    subject = "Your Referral Bonus Has Decayed"
    message = f"Hello {user.first_name},\n\nYour referral bonus has decreased in value due to the approaching expiration date. " \
              f"The new value of your bonus is {new_amount}."
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]

    send_mail(subject, message, from_email, recipient_list)
