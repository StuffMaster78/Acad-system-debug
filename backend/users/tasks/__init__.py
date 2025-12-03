# Import tasks from submodules to ensure they're registered with Celery
from .deletion import cleanup_soft_deleted_models  # noqa: F401

