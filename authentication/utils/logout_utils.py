from django.contrib.auth import logout
from authentication.services.logout_event_service import LogoutEventService
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import logout as django_logout

def logout_user(request, reason="user_initiated"):
    """
    Logs out a user and records the logout event.

    Args:
        request (HttpRequest): The request initiating logout.
        reason (str): Optional reason for the logout.
    """
    user = request.user
    website = getattr(request, "website", None)
    ip_address = get_client_ip(request)
    user_agent = request.META.get("HTTP_USER_AGENT", "")
    session_key = request.session.session_key

    if request.session.get("is_impersonating"):
        reason = "impersonation_ended"
        request.session.pop("is_impersonating")


    if user.is_authenticated:
        LogoutEventService.log_event(
            user=user,
            website=website,
            ip_address=ip_address,
            user_agent=user_agent,
            session_key=session_key,
            reason=reason
        )
        logout(request)  # Django session logout (works for DRF too)

     # If using JWT and refresh token exists
    refresh_token = request.data.get("refresh")
    if refresh_token:
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            pass  # Optionally log this error

    # For session-auth
    django_logout(request)


def get_client_ip(request):
    """
    Gets the real IP from request headers.

    Args:
        request (HttpRequest): The current request.

    Returns:
        str: The client's IP address.
    """
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0].strip()
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip