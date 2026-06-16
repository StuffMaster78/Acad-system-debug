"""
Seed class bundle configurations.

Delegates to seed_class_service_configs which handles the current schema.
ClassDurationOption / ClassBundleConfig were removed; duration data is now
stored as JSON on ClassServiceConfig (duration_options field).
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = "Seed class service configs (delegates to seed_class_service_configs)."

    def add_arguments(self, parser):
        parser.add_argument("--website-id", type=int)
        parser.add_argument("--clear", action="store_true")

    def handle(self, *args, **options):
        self.stdout.write("Note: seed_class_configs delegates to seed_class_service_configs (current schema).")
        call_command("seed_class_service_configs")
