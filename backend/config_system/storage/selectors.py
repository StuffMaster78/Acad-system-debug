from config_system.storage.models import ConfigItem


class ConfigSelectors:

    @staticmethod
    def get_active_queryset():
        return ConfigItem.objects.filter(is_active=True)