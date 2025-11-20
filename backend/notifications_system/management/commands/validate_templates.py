"""
Django management command to validate notification templates.
"""
from django.core.management.base import BaseCommand, CommandError
from notifications_system.templates.validator import validate_all_templates, test_all_templates
from notifications_system.registry.template_registry import autoload_all_templates


class Command(BaseCommand):
    help = 'Validate and test notification templates'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--test',
            action='store_true',
            help='Run template tests in addition to validation',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed output',
        )
    
    def handle(self, *args, **options):
        """Handle the command execution."""
        self.stdout.write("Loading notification templates...")
        
        # Load all templates
        autoload_all_templates()
        
        # Validate templates
        self.stdout.write("Validating templates...")
        is_valid, errors, warnings = validate_all_templates()
        
        # Show validation results
        if errors:
            self.stdout.write(self.style.ERROR(f"Validation failed with {len(errors)} errors:"))
            for error in errors:
                self.stdout.write(self.style.ERROR(f"  ❌ {error}"))
        else:
            self.stdout.write(self.style.SUCCESS("✅ All templates passed validation"))
        
        if warnings:
            self.stdout.write(self.style.WARNING(f"Found {len(warnings)} warnings:"))
            for warning in warnings:
                self.stdout.write(self.style.WARNING(f"  ⚠️  {warning}"))
        
        # Run tests if requested
        if options['test']:
            self.stdout.write("\nRunning template tests...")
            test_results = test_all_templates()
            
            for event_key, results in test_results.items():
                self.stdout.write(f"\nTesting {event_key}:")
                for result in results:
                    test_name = result['test']
                    status = result['status']
                    
                    if status == 'passed':
                        self.stdout.write(self.style.SUCCESS(f"  ✅ {test_name}"))
                    elif status == 'warning':
                        self.stdout.write(self.style.WARNING(f"  ⚠️  {test_name}"))
                    else:
                        self.stdout.write(self.style.ERROR(f"  ❌ {test_name}"))
                        if 'error' in result:
                            self.stdout.write(self.style.ERROR(f"      Error: {result['error']}"))
                    
                    if options['verbose'] and 'message' in result:
                        self.stdout.write(f"      {result['message']}")
        
        # Summary
        if not is_valid:
            raise CommandError("Template validation failed")
        
        self.stdout.write(self.style.SUCCESS("\n🎉 All templates are valid and working correctly!"))
