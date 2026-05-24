from config_system.cache.redis_cache import ConfigCacheService
from config_system.registry import CONFIG_REGISTRY
from config_system.storage.models import ConfigItem


class ConfigService:

    @classmethod
    def get(
        cls,
        key,
        *,
        website=None,
        user=None,
    ):
        definition = CONFIG_REGISTRY.get(key)

        if not definition:
            raise KeyError(f"Unknown config: {key}")

        cached = ConfigCacheService.get(
            key,
            website_id=website.id if website else None,
            user_id=user.id if user else None,
        )

        if cached is not None:
            return cached

        queryset = ConfigItem.objects.filter(
            key=key,
            is_active=True,
        )

        if user:
            item = queryset.filter(user=user).first()
            if item:
                ConfigCacheService.set(
                    key,
                    item.value,
                    definition.cache_ttl_seconds,
                    website_id=website.id if website else None,
                    user_id=user.id,
                )
                return item.value

        if website:
            item = queryset.filter(website=website).first()
            if item:
                ConfigCacheService.set(
                    key,
                    item.value,
                    definition.cache_ttl_seconds,
                    website_id=website.id if website else None,
                )
                return item.value

        item = queryset.filter(scope="global").first()

        if item:
            return definition.default
