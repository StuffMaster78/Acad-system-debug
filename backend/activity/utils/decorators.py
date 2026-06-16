"""No-op decorators — activity logging moved to ActivityService."""


def auto_log_activity(*args, **kwargs):
    """No-op decorator: activity logging now uses ActivityService directly."""
    def decorator(func):
        return func
    if len(args) == 1 and callable(args[0]):
        return args[0]
    return decorator
