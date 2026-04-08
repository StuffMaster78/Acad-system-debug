from typing import Any


def get_impersonation_context(request) -> dict[str, Any]:
    """
    Return normalized impersonation context from request.
    """
    return getattr(
        request,
        "_impersonation_context",
        {
            "is_impersonating": False,
            "impersonated_by": None,
            "original_user_id": None,
            "target_user_id": None,
            "started_at": None,
        },
    )


def is_impersonating(request) -> bool:
    """
    Return whether the current request is impersonated.
    """
    return bool(
        get_impersonation_context(request).get(
            "is_impersonating",
            False,
        )
    )


def get_impersonator_user_id(request) -> int | None:
    """
    Return the original impersonator user ID if present.
    """
    return get_impersonation_context(request).get(
        "original_user_id",
    )


def get_impersonated_target_user_id(request) -> int | None:
    """
    Return the impersonated target user ID if present.
    """
    return get_impersonation_context(request).get(
        "target_user_id",
    )

def get_impersonation_banner_payload(request) -> dict[str, Any]:
    """
    Return UI-friendly impersonation metadata.
    """
    context = get_impersonation_context(request)

    if not context.get("is_impersonating", False):
        return {
            "show_banner": False,
        }

    return {
        "show_banner": True,
        "impersonated_by": context.get("impersonated_by"),
        "started_at": context.get("started_at"),
    }