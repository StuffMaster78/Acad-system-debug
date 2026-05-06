import threading
from audit_logging.storage.writer import AuditWriter


class AuditDispatcher:
    def __init__(self, async_mode: bool = False):
        self.async_mode = async_mode
        self.writer = AuditWriter()

    def dispatch(self, event):
        if self.async_mode:
            threading.Thread(
                target=self.writer.write,
                args=(event,),
                daemon=True
            ).start()
        else:
            self.writer.write(event)