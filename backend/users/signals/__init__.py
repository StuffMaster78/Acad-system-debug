"""
Signals package for users app.
"""
import importlib.util
from pathlib import Path


def _load_legacy_signal_module() -> None:
    """
    Load the historical users/signals.py module.

    The app now also has a users/signals/ package, which shadows that file
    during normal imports. Loading it explicitly preserves existing profile and
    audit signal registrations while the package layout is cleaned up.
    """
    legacy_path = Path(__file__).resolve().parent.parent / "signals.py"
    spec = importlib.util.spec_from_file_location(
        "users._legacy_signal_module",
        legacy_path,
    )
    if spec and spec.loader:
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
        except ImportError:
            pass


_load_legacy_signal_module()

# Import phone reminder signals.
from . import phone_reminder_signals  # noqa: F401
