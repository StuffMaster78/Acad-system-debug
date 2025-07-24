import json
from django.core.management.base import BaseCommand
from notifications_system.registry.event_config_loader import (
    get_event_config, CONFIG_CACHE_KEY
)
from django.core.cache import cache

class Command(BaseCommand):
    help = "Reloads and prints the merged notification event config (JSON + DB overrides)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear-cache",
            action="store_true",
            help="Clear the event config cache before reload",
        )

    def handle(self, *args, **options):
        if options["clear_cache"]:
            cache.delete(CONFIG_CACHE_KEY)
            self.stdout.write(self.style.WARNING("Cache cleared."))

        config = get_event_config(force_reload=True)
        self.stdout.write(self.style.SUCCESS("Notification event config reloaded:\n"))
        self.stdout.write(json.dumps(config, indent=2))