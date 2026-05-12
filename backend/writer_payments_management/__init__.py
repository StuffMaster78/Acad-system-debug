"""
Compatibility package for the renamed writer_compensation app.

New code should import from writer_compensation. This shim keeps older imports
working while the rest of the codebase migrates.
"""
from importlib import import_module

_renamed_app = import_module("writer_compensation")
__path__ = _renamed_app.__path__
