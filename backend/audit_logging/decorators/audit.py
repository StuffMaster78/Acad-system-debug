from functools import wraps
from audit_logging.factories.audit_event_factory import AuditEventFactory


def audit_action(action: str, *, object_type=None):

    def wrapper(func):

        @wraps(func)
        def inner(*args, **kwargs):

            result = func(*args, **kwargs)

            request = kwargs.get("request")

            AuditEventFactory.create(
                website=getattr(request, "website", None),
                actor_id=getattr(getattr(request, "user", None), "id", None),
                action=action,
                object_type=object_type,
                metadata={
                    "args": str(args),
                    "kwargs": str(kwargs),
                },
            )

            return result

        return inner

    return wrapper