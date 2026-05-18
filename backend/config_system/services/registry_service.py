from backend.config_system.registry import CONFIG_REGISTRY


class RegistryService:

    @staticmethod
    def get(key: str):
        return CONFIG_REGISTRY.get(key)

    @staticmethod
    def all():
        return CONFIG_REGISTRY.values()