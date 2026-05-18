import os


class RemoteConfig:
    def __init__(self):
        self.enabled = os.getenv("REMOTE_CONFIG", "false") == "true"
        self.store = {}

    def fetch(self):
        if not self.enabled:
            return

        # placeholder: plug Redis / API / DB config service here
        self.store = {}

    def get(self, key: str, default=None):
        return self.store.get(key, default)


remote_config = RemoteConfig()