from django.utils import timezone

from authentication.models.impersonation_token import ImpersonationToken
from authentication.models.impersonation_log import ImpersonationLog


def get_active_impersonation_token(
    *,
    admin_user,
    target_user,
    website,
) -> ImpersonationToken | None:
    return ImpersonationToken.objects.filter(
        admin_user=admin_user,
        target_user=target_user,
        website=website,
        used_at__isnull=True,
        expires_at__gt=timezone.now(),
    ).order_by("-created_at").first()


def list_admin_impersonation_tokens(
    *,
    admin_user,
    website,
):
    return ImpersonationToken.objects.filter(
        admin_user=admin_user,
        website=website,
    ).order_by("-created_at")


def list_target_impersonation_tokens(
    *,
    target_user,
    website,
):
    return ImpersonationToken.objects.filter(
        target_user=target_user,
        website=website,
    ).order_by("-created_at")


def list_impersonation_logs_for_admin(
    *,
    admin_user,
    website,
):
    return ImpersonationLog.objects.filter(
        admin_user=admin_user,
        website=website,
    ).order_by("-created_at")


def list_impersonation_logs_for_target(
    *,
    target_user,
    website,
):
    return ImpersonationLog.objects.filter(
        target_user=target_user,
        website=website,
    ).order_by("-created_at")