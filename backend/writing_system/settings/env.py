import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")


def get_env(key: str, default=None, required: bool = False):
    value = os.getenv(key, default)

    if required and (value is None or value == ""):
        raise RuntimeError(f"Missing required env var: {key}")

    return value


def get_bool(key: str, default=False):
    val = os.getenv(key, str(default)).lower()
    return val in ["1", "true", "yes", "on"]