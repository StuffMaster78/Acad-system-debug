from authentication.models.magic_links import MagicLink


def get_active_magic_link_for_user(
    *,
    user,
    website,
) -> MagicLink | None:
    return MagicLink.objects.filter(
        user=user,
        website=website,
        used_at__isnull=True,
    ).order_by("-created_at").first()


def get_magic_link_by_token_hash(
    *,
    token_hash: str,
    website,
) -> MagicLink | None:
    return MagicLink.objects.filter(
        website=website,
        token_hash=token_hash,
        used_at__isnull=True,
    ).select_related("user", "website").first()


def list_magic_links_for_user(
    *,
    user,
    website,
):
    return MagicLink.objects.filter(
        user=user,
        website=website,
    ).order_by("-created_at")