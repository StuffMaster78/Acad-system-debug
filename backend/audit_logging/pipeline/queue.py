from collections import deque
import threading


class AuditQueue:
    """
    Lightweight buffer for future async scaling.
    """

    def __init__(self):
        self.queue = deque()
        self.lock = threading.Lock()

    def push(self, event):
        with self.lock:
            self.queue.append(event)

    def drain(self, limit=100):
        events = []

        with self.lock:
            while self.queue and len(events) < limit:
                events.append(self.queue.popleft())

        return events