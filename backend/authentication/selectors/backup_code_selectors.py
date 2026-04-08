from authentication.models.backup_code import BackupCode


def list_backup_codes(*, user, website):
    """
    Return backup codes for a user and website.
    """
    return BackupCode.objects.filter(
        user=user,
        website=website,
    ).order_by("-created_at")


def list_unused_backup_codes(*, user, website):
    """
    Return unused backup codes for a user and website.
    """
    return BackupCode.objects.filter(
        user=user,
        website=website,
        used=False,
    ).order_by("-created_at")


def count_unused_backup_codes(*, user, website) -> int:
    """
    Return unused backup code count.
    """
    return list_unused_backup_codes(
        user=user,
        website=website,
    ).count()