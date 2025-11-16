"""
Custom runserver command that ignores __pycache__ files to reduce unnecessary reloads.
"""
from django.core.management.commands.runserver import Command as BaseCommand
from django.utils.autoreload import StatReloader


class Command(BaseCommand):
    help = 'Starts a lightweight Web server for development with optimized file watching.'

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            '--noreload',
            action='store_true',
            help='Tells Django to NOT use the auto-reloader.',
        )

    def run(self, *args, **options):
        """Override run to configure StatReloader to ignore __pycache__ files."""
        # Configure StatReloader to ignore common patterns that cause unnecessary reloads
        if not options.get('noreload'):
            # Monkey-patch StatReloader to ignore __pycache__ directories
            original_watch_dir = StatReloader.watch_dir

            def watch_dir_with_ignore(self, path, glob):
                # Skip __pycache__ directories
                if '__pycache__' in path or path.endswith('.pyc'):
                    return
                return original_watch_dir(self, path, glob)

            StatReloader.watch_dir = watch_dir_with_ignore

        super().run(*args, **options)

