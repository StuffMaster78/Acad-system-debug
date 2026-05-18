import os


class Secrets:
    def get(self, key: str, default=None):
        value = os.getenv(key)
        if not value:
            return default
        return value


secrets = Secrets()