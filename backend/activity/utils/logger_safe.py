"""No-op safe logger — activity logging moved to ActivityService."""


def safe_log_activity(*args, **kwargs):
    """No-op: activity logging now uses ActivityService directly."""
    pass
