"""
Management command to generate referral codes for clients who don't have them.
Usage: python manage.py generate_referral_codes [--website-id ID] [--dry-run]
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from django.conf import settings
from referrals.models import ReferralCode
from referrals.services.referral_service import ReferralService
from websites.models import Website
import logging

logger = logging.getLogger(__name__)
User = settings.AUTH_USER_MODEL


class Command(BaseCommand):
    help = 'Generate referral codes for clients who do not have them'

    def add_arguments(self, parser):
        parser.add_argument(
            '--website-id',
            type=int,
            help='Generate codes only for clients of a specific website',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without actually creating codes',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Regenerate codes even if they already exist (use with caution)',
        )

    def handle(self, *args, **options):
        website_id = options.get('website_id')
        dry_run = options.get('dry_run', False)
        force = options.get('force', False)

        # Get clients without referral codes
        clients_query = User.objects.filter(role='client', is_active=True)
        
        if website_id:
            clients_query = clients_query.filter(website_id=website_id)
        
        # Exclude clients who already have codes
        if not force:
            clients_with_codes = ReferralCode.objects.values_list('user_id', flat=True)
            clients_query = clients_query.exclude(id__in=clients_with_codes)
        
        clients = clients_query.select_related('website')
        
        total_clients = clients.count()
        
        if total_clients == 0:
            self.stdout.write(
                self.style.SUCCESS('No clients found without referral codes.')
            )
            return
        
        self.stdout.write(
            f'Found {total_clients} client(s) without referral codes.'
        )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No codes will be created')
            )
            for client in clients[:10]:  # Show first 10
                website_name = client.website.name if client.website else 'No website'
                self.stdout.write(
                    f'  - {client.username} ({client.email}) - {website_name}'
                )
            if total_clients > 10:
                self.stdout.write(f'  ... and {total_clients - 10} more')
            return
        
        # Generate codes
        created = 0
        failed = 0
        
        for client in clients:
            try:
                if not client.website:
                    self.stdout.write(
                        self.style.WARNING(
                            f'Skipping {client.username}: No website assigned'
                        )
                    )
                    failed += 1
                    continue
                
                # Check if code already exists (if force is False)
                if not force:
                    if ReferralCode.objects.filter(user=client, website=client.website).exists():
                        self.stdout.write(
                            self.style.WARNING(
                                f'Skipping {client.username}: Code already exists'
                            )
                        )
                        continue
                
                # Generate unique code
                with transaction.atomic():
                    code = ReferralService.generate_unique_code(client, client.website)
                    ReferralCode.objects.create(
                        user=client,
                        website=client.website,
                        code=code
                    )
                    created += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Generated code {code} for {client.username}'
                        )
                    )
            except Exception as e:
                failed += 1
                self.stdout.write(
                    self.style.ERROR(
                        f'Failed to generate code for {client.username}: {e}'
                    )
                )
                logger.error(
                    f'Failed to generate referral code for client {client.id}: {e}',
                    exc_info=True
                )
        
        # Summary
        self.stdout.write('')
        self.stdout.write(
            self.style.SUCCESS(
                f'Summary: {created} codes created, {failed} failed'
            )
        )

