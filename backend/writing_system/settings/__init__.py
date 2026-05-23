from __future__ import annotations

import os


_ENVIRONMENT_MODULES = {
    "dev": "development",
    "development": "development",
    "local": "development",
    "test": "test",
    "testing": "test",
    "ci": "test",
    "prod": "production",
    "production": "production",
}

_env = os.getenv("DJANGO_ENV", "development").strip().lower()
_module = _ENVIRONMENT_MODULES.get(_env, "development")

if _module == "production":
    from .production import *  # noqa: F401,F403
elif _module == "test":
    from .test import *  # noqa: F401,F403
else:
    from .development import *  # noqa: F401,F403
