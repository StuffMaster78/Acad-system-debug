"""
Backward-compatible test settings module.

Pytest and older scripts still point at ``writing_system.settings_test``.
The canonical test settings now live in ``writing_system.settings.test``.
"""

from writing_system.settings.test import *  # noqa: F401,F403
