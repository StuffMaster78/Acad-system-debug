import time
import logging
from django.utils.deprecation import MiddlewareMixin
from activity.utils.logger_safe import safe_log_activity
from audit_logging.utils import get_client_ip  # You already had this

logger = logging.getLogger("activity")


class ActivityAuditMiddleware(MiddlewareMixin):
    """
    Middleware to attach metadata to request and optionally
    log suspicious events or long request durations.
    """

    def process_request(self, request):
        request.start_time = time.time()
        request.ip = get_client_ip(request)
        request.website = getattr(request.user, "website", None)
        request.user_agent = request.META.get("HTTP_USER_AGENT", "Unknown")


    def process_response(self, request, response):
        try:
            if hasattr(request, "start_time"):
                duration = time.time() - request.start_time

                if duration > 2.0:  # Slow request threshold
                    user = getattr(request, "user", None)
                    website = getattr(request, "website", None)

                    safe_log_activity(
                        user=user if user and user.is_authenticated else None,
                        website=website,
                        action_type="SYSTEM",
                        description=f"Slow request to {request.path} "
                                    f"({duration:.2f}s from IP {request.ip})",
                        metadata={
                            "path": request.path,
                            "method": request.method,
                            "duration": duration,
                            "ip": request.ip,
                            "user_agent": request.user_agent,
                        },
                    )
        except Exception as e:
            logger.warning(f"Failed to audit response: {e}")

        return response

    def process_exception(self, request, exception):
        try:
            user = getattr(request, "user", None)
            website = getattr(request, "website", None)

            safe_log_activity(
                user=user if user and user.is_authenticated else None,
                website=website,
                action_type="SYSTEM",
                description=f"Exception during {request.method} {request.path}: {type(exception).__name__}",
                metadata={
                    "error": str(exception),
                    "path": request.path,
                    "method": request.method,
                    "ip": request.ip,
                    "user_agent": request.user_agent,
                },
                triggered_by=user if user and user.is_authenticated else None,
            )
        except Exception as e:
            logger.warning(f"Failed to log exception activity: {e}")