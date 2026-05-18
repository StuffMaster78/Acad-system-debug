from config_system.storage.models import ConfigItem
from backend.config_system.registry import CONFIG_REGISTRY


class ConfigStore:

    def get(self, key, context=None):
        context = context or {}

        user = context.get("user")
        website = context.get("website")

        queryset = ConfigItem.objects.filter(
            key=key,
            is_active=True,
        )

        # 1. User override
        if user:
            item = queryset.filter(user=user).first()
            if item:
                return item.value

        # 2. Website override
        if website:
            item = queryset.filter(
                website=website,
                scope="website",
            ).first()

            if item:
                return item.value

        # 3. Global override
        item = queryset.filter(
            scope="global",
        ).first()

        if item:
            return item.value

        # 4. Registry default
        definition = CONFIG_REGISTRY.get(key)

        if definition:
            return definition.default

        return None