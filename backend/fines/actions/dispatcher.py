from importlib import import_module
from actions.base import BaseAction, PermissionDenied
from audit_logging.services.audit_log_service import AuditLogService

ACTION_REGISTRY = {}


def register_action(name):
    """Decorator to register an action class by name.

    Args:
        name (str): Unique name to identify the action.

    Returns:
        Callable: Decorator to register the action class.
    """
    def decorator(cls):
        if not issubclass(cls, BaseAction):
            raise TypeError(
                f"Action '{name}' must inherit from BaseAction"
            )
        ACTION_REGISTRY[name] = cls
        return cls
    return decorator


def dispatch_action(name, actor, **kwargs):
    """Resolve and execute the named action with permission check and audit log."""

    action_cls = ACTION_REGISTRY.get(name)
    if not action_cls:
        raise ValueError(f"Unknown action: {name}")

    action = action_cls(actor, **kwargs)

    try:
        action.validate()
        result = action.perform(**kwargs)

        # Log success audit event
        AuditLogService.log_auto(
            actor=actor,
            action=name,
            target=result if hasattr(result, 'pk') else None,
            changes={'status': 'success'},
            context=kwargs
        )

        return result

    except PermissionDenied as e:
        # Log permission denied event
        AuditLogService.log_auto(
            actor=actor,
            action=f"{name}_permission_denied",
            target=None,
            changes={'error': str(e)},
            context=kwargs
        )
        raise

    except Exception:
        # Could add more nuanced logging here for failures
        raise