"""
Management command to ensure universal file categories exist and are available to all websites.
"""
from django.core.management.base import BaseCommand
from order_files.models import OrderFileCategory
from websites.models import Website


class Command(BaseCommand):
    help = 'Ensure universal file categories exist and are available to all websites'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without actually creating categories',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Expected universal categories
        expected_categories = [
            # Writer categories
            {
                'name': 'Final Draft',
                'allowed_extensions': ['pdf', 'docx', 'doc'],
                'is_final_draft': True,
                'is_extra_service': False,
            },
            {
                'name': 'First Draft',
                'allowed_extensions': ['pdf', 'docx', 'doc'],
                'is_final_draft': False,
                'is_extra_service': False,
            },
            {
                'name': 'DRAFT',
                'allowed_extensions': ['pdf', 'docx', 'doc'],
                'is_final_draft': False,
                'is_extra_service': False,
            },
            {
                'name': 'Outline',
                'allowed_extensions': ['pdf', 'docx', 'doc', 'txt'],
                'is_final_draft': False,
                'is_extra_service': False,
            },
            {
                'name': 'Resource',
                'allowed_extensions': ['pdf', 'docx', 'doc', 'txt', 'jpg', 'jpeg', 'png'],
                'is_final_draft': False,
                'is_extra_service': False,
            },
            {
                'name': 'Plagiarism Report',
                'allowed_extensions': ['pdf'],
                'is_final_draft': False,
                'is_extra_service': True,
            },
            {
                'name': 'AI Similarity Report',
                'allowed_extensions': ['pdf'],
                'is_final_draft': False,
                'is_extra_service': True,
            },
            # Client categories
            {
                'name': 'Materials',
                'allowed_extensions': ['pdf', 'docx', 'doc', 'txt', 'jpg', 'jpeg', 'png', 'zip', 'rar'],
                'is_final_draft': False,
                'is_extra_service': False,
            },
            {
                'name': 'Sample',
                'allowed_extensions': ['pdf', 'docx', 'doc', 'txt'],
                'is_final_draft': False,
                'is_extra_service': False,
            },
            {
                'name': 'My Previous Papers',
                'allowed_extensions': ['pdf', 'docx', 'doc'],
                'is_final_draft': False,
                'is_extra_service': False,
            },
            {
                'name': 'Friends Paper',
                'allowed_extensions': ['pdf', 'docx', 'doc'],
                'is_final_draft': False,
                'is_extra_service': False,
            },
            {
                'name': 'Reading Materials',
                'allowed_extensions': ['pdf', 'docx', 'doc', 'txt'],
                'is_final_draft': False,
                'is_extra_service': False,
            },
            {
                'name': 'Syllabus',
                'allowed_extensions': ['pdf', 'docx', 'doc'],
                'is_final_draft': False,
                'is_extra_service': False,
            },
            {
                'name': 'Rubric',
                'allowed_extensions': ['pdf', 'docx', 'doc'],
                'is_final_draft': False,
                'is_extra_service': False,
            },
            {
                'name': 'Guidelines',
                'allowed_extensions': ['pdf', 'docx', 'doc', 'txt'],
                'is_final_draft': False,
                'is_extra_service': False,
            },
            {
                'name': 'Order Instructions',
                'allowed_extensions': ['pdf', 'docx', 'doc', 'txt'],
                'is_final_draft': False,
                'is_extra_service': False,
            },
        ]
        
        created_count = 0
        existing_count = 0
        
        self.stdout.write(self.style.SUCCESS('\n=== Ensuring Universal File Categories ===\n'))
        
        for category_data in expected_categories:
            name = category_data['name']
            
            # Check if universal category exists (website=None)
            existing = OrderFileCategory.objects.filter(
                name=name,
                website__isnull=True
            ).first()
            
            if existing:
                existing_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ {name} (already exists)')
                )
            else:
                if dry_run:
                    self.stdout.write(
                        self.style.WARNING(f'→ {name} (would be created)')
                    )
                else:
                    OrderFileCategory.objects.create(
                        website=None,  # Universal category
                        **category_data
                    )
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ {name} (created)')
                    )
        
        # Summary
        self.stdout.write(self.style.SUCCESS(f'\n=== Summary ==='))
        self.stdout.write(f'Existing categories: {existing_count}')
        if not dry_run:
            self.stdout.write(f'Created categories: {created_count}')
        else:
            self.stdout.write(f'Would create: {created_count}')
        
        # Show website availability
        websites = Website.objects.filter(is_active=True)
        self.stdout.write(f'\n=== Availability ===')
        self.stdout.write(f'Universal categories are available to ALL {websites.count()} active website(s):')
        for website in websites:
            self.stdout.write(f'  - {website.name} ({website.domain})')
        
        if not dry_run and created_count > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✓ Successfully ensured {len(expected_categories)} universal categories are available to all websites!'
                )
            )
        elif existing_count == len(expected_categories):
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✓ All {len(expected_categories)} universal categories already exist and are available to all websites!'
                )
            )

