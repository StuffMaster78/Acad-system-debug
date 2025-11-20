from functools import wraps
from activity.services.logger import ActivityLogger

def auto_log_activity(
    action_type,
    get_user=lambda args, kwargs, result: None,
    get_website=lambda args, kwargs, result: None,
    get_description=lambda args, kwargs, result: "",
    get_metadata=lambda args, kwargs, result: {},
    get_triggered_by=lambda args, kwargs, result: None,
):
    """
    Auto-log activity when this function runs successfully.

    Args:
        action_type (str): e.g. "ORDER", "USER", "PAYMENT"
        get_user (callable): Returns user from args/kwargs/result
        get_website (callable): Returns website instance
        get_description (callable): Builds log description
        get_metadata (callable): Builds log metadata
        get_triggered_by (callable): Optional actor

    Usage:
        @auto_log_activity(
            action_type="ORDER",
            get_user=lambda args, kwargs, res: kwargs["user"],
            get_website=lambda a, k, r: r.website,
            get_description=lambda a, k, r: f"Order #{r.id} placed.",
            get_metadata=lambda a, k, r: {"order_id": r.id}
        )
        def create_order(...): ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            try:
                ActivityLogger.log_activity(
                    user=get_user(args, kwargs, result),
                    website=get_website(args, kwargs, result),
                    action_type=action_type,
                    description=get_description(args, kwargs, result),
                    metadata=get_metadata(args, kwargs, result),
                    triggered_by=get_triggered_by(args, kwargs, result),
                )
            except Exception as e:
                # Optional: Log the error, don't block core flow
                import logging
                logging.getLogger("activity").warning(
                    f"Auto-log failed for {func.__name__}: {e}"
                )

            return result
        return wrapper
    return decorator