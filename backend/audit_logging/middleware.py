import logging
import uuid
from django.utils.deprecation import MiddlewareMixin
from django.utils.timezone import now

from .utils import set_current_request, get_current_user
from audit_logging.services.audit_log_service import AuditLogService
from audit_logging.utils import get_client_ip, get_user_agent

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
        request.request_id = str(uuid.uuid4())
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
        ip = get_client_ip(request)
        ua = get_user_agent(request)
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

        AuditLogService.log_auto(
            action="ACCESS",
            actor=user,
            target=None,  # You can’t know model from here — so this may be blank
            metadata={
                "method": request.method,
                "path": request.get_full_path(),
                "status": response.status_code,
                "ip_address": ip,
                "user_agent": ua,
                "request_id": getattr(request, 'request_id', None),
                "notes": "User accessed the resource",
            },
        )
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