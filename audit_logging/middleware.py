import logging

from django.utils.deprecation import MiddlewareMixin
from django.utils.timezone import now

from .utils import set_current_request, get_current_user

logger = logging.getLogger("audit")


class AuditUserMiddleware(MiddlewareMixin):
    """
    Middleware that sets the current request and user in contextvars
    for global access. Also logs authenticated user activity per request.
    """

    def process_request(self, request):
        """
        Store the current request in a context variable.

        Args:
            request (HttpRequest): The incoming HTTP request.
        """
        set_current_request(request)

    def process_response(self, request, response):
        """
        Logs the user action if authenticated and returns the response.

        Args:
            request (HttpRequest): The original HTTP request.
            response (HttpResponse): The HTTP response to be returned.

        Returns:
            HttpResponse: The original or modified response object.
        """
        user = get_current_user()
        if user and user.is_authenticated:
            try:
                logger.info(
                    "[AUDIT] User %s (%s) accessed %s %s at %s",
                    user.id,
                    user.username,
                    request.method,
                    request.get_full_path(),
                    now().isoformat()
                )
            except Exception as e:
                logger.warning("[AUDIT] Logging failed: %s", str(e))
        return response

    def process_exception(self, request, exception):
        """
        Logs unhandled exceptions during request processing.

        Args:
            request (HttpRequest): The HTTP request during which
                the exception occurred.
            exception (Exception): The exception raised.

        Returns:
            None
        """
        logger.exception(
            "[AUDIT] Exception during request: %s | %s",
            request.path,
            str(exception)
        )
        return None