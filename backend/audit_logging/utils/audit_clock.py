import time


def now_seconds() -> float:
    return time.time()


def now_ms() -> int:
    return int(time.time() * 1000)