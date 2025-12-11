"""
Management command to populate comprehensive types of work.
Run: python manage.py populate_types_of_work [--website-id=ID] [--all]
"""
from django.core.management.base import BaseCommand
from order_configs.models import TypeOfWork
from order_configs.services.comprehensive_types_of_work import COMPREHENSIVE_TYPES_OF_WORK
from websites.models import Website


class Command(BaseCommand):
    help = 'Populate comprehensive types of work for websites'

    def add_arguments(self, parser):
        parser.add_argument(
            '--website-id',
            type=int,
            help='Populate types of work for a specific website ID',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Populate types of work for all websites',
        )
        parser.add_argument(
            '--skip-existing',
            action='store_true',
            default=True,
            help='Skip types of work that already exist (default: True)',
        )

    def handle(self, *args, **options):
        website_id = options.get('website_id')
        all_websites = options.get('all', False)
        skip_existing = options.get('skip_existing', True)
        
        # Determine which websites to process
        if website_id:
            try:
                websites = [Website.objects.get(id=website_id)]
            except Website.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Website with ID {website_id} not found'))
                return
        elif all_websites:
            websites = Website.objects.filter(is_active=True)
            if not websites.exists():
                self.stdout.write(self.style.WARNING('No active websites found'))
                return
        else:
            self.stdout.write(self.style.ERROR(
                'Please specify --website-id=ID or --all to populate types of work'
            ))
            return
        
        total_created = 0
        total_skipped = 0
        
        for website in websites:
            self.stdout.write(f'\n📋 Processing website: {website.name} (ID: {website.id})')
            created = 0
            skipped = 0
            
            for work_type in COMPREHENSIVE_TYPES_OF_WORK:
                if skip_existing and TypeOfWork.objects.filter(website=website, name=work_type).exists():
                    skipped += 1
                    continue
                
                try:
                    TypeOfWork.objects.create(website=website, name=work_type)
                    created += 1
                except Exception as e:
                    self.stdout.write(self.style.WARNING(
                        f'  ⚠️  Failed to create "{work_type}": {str(e)}'
                    ))
            
            total_created += created
            total_skipped += skipped
            
            self.stdout.write(self.style.SUCCESS(
                f'  ✅ Created: {created}, Skipped: {skipped}'
            ))
        
        self.stdout.write(self.style.SUCCESS(
            f'\n📊 Total Summary: {total_created} created, {total_skipped} skipped across {len(websites)} website(s)'
        ))

