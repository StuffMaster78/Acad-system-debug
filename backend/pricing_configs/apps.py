from django.apps import AppConfig


class PricingConfigsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pricing_configs'

    def ready(self):
        import pricing_configs.signals 
