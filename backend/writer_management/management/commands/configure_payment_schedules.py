"""
Management command to configure payment schedule preferences for existing writers.
Sets default payment schedules based on website settings or custom rules.
"""
from django.core.management.base import BaseCommand
from writer_management.models.profile import WriterProfile
from websites.models import Website, WebsiteSettings
from django.db.models import Q


class Command(BaseCommand):
    help = "Configure payment schedule preferences for existing writers"

    def add_arguments(self, parser):
        parser.add_argument(
            '--website-id',
            type=int,
            help='Website ID to configure (default: all active websites)',
        )
        parser.add_argument(
            '--schedule',
            type=str,
            choices=['bi-weekly', 'monthly'],
            help='Default payment schedule to set (bi-weekly or monthly)',
        )
        parser.add_argument(
            '--date-preference',
            type=str,
            help='Payment date preference (e.g., "1,15" for bi-weekly, "1" for monthly)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be changed without making changes',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Update writers even if they already have a payment schedule set',
        )

    def handle(self, *args, **options):
        website_id = options.get('website_id')
        schedule = options.get('schedule')
        date_preference = options.get('date_preference')
        dry_run = options.get('dry_run', False)
        force = options.get('force', False)

        # Get websites
        if website_id:
            websites = Website.objects.filter(id=website_id, is_active=True)
        else:
            websites = Website.objects.filter(is_active=True)

        if not websites.exists():
            self.stdout.write(self.style.ERROR('No active websites found'))
            return

        total_updated = 0
        total_skipped = 0

        for website in websites:
            self.stdout.write(f'\n=== Processing Website: {website.name} (ID: {website.id}) ===')

            # Get website settings for default schedule
            website_settings = WebsiteSettings.objects.filter(website=website).first()
            
            # Determine default schedule
            if schedule:
                default_schedule = schedule
            elif website_settings and website_settings.default_payment_schedule:
                default_schedule = website_settings.default_payment_schedule
            else:
                default_schedule = 'bi-weekly'  # Default fallback

            # Determine date preference
            if date_preference:
                default_date_pref = date_preference
            elif default_schedule == 'bi-weekly':
                default_date_pref = '1,15'  # Default: 1st and 15th
            else:
                default_date_pref = '1'  # Default: 1st of month

            self.stdout.write(f'Default Schedule: {default_schedule}')
            self.stdout.write(f'Default Date Preference: {default_date_pref}')

            # Get writers without payment schedule or force update
            if force:
                writers = WriterProfile.objects.filter(
                    website=website,
                    user__is_active=True
                )
            else:
                writers = WriterProfile.objects.filter(
                    Q(payment_schedule__isnull=True) | Q(payment_schedule=''),
                    website=website,
                    user__is_active=True
                )

            writer_count = writers.count()
            self.stdout.write(f'Found {writer_count} writers to process')

            if writer_count == 0:
                self.stdout.write(self.style.WARNING('No writers to update'))
                continue

            updated = 0
            skipped = 0

            for writer in writers:
                # Skip if already has schedule and not forcing
                if not force and writer.payment_schedule:
                    skipped += 1
                    continue

                if dry_run:
                    self.stdout.write(
                        f'  [DRY RUN] Would update {writer.user.username}: '
                        f'schedule={default_schedule}, date_pref={default_date_pref}'
                    )
                else:
                    writer.payment_schedule = default_schedule
                    if not writer.payment_date_preference:
                        writer.payment_date_preference = default_date_pref
                    writer.save()
                    self.stdout.write(
                        f'  ✓ Updated {writer.user.username}: '
                        f'schedule={default_schedule}, date_pref={default_date_pref}'
                    )
                updated += 1

            total_updated += updated
            total_skipped += skipped

            self.stdout.write(f'\nWebsite Summary:')
            self.stdout.write(f'  Updated: {updated}')
            self.stdout.write(f'  Skipped: {skipped}')

        self.stdout.write(self.style.SUCCESS(f'\n=== Summary ==='))
        self.stdout.write(f'Total Updated: {total_updated}')
        self.stdout.write(f'Total Skipped: {total_skipped}')

        if dry_run:
            self.stdout.write(self.style.WARNING('\nThis was a dry run. Use without --dry-run to apply changes.'))

