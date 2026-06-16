"""
Management command to seed promotional campaigns and discount codes with sample data.
Creates campaigns with various statuses and discount codes linked to them.
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from decimal import Decimal
from websites.models.websites import Website
from discounts.models.promotional_campaign import PromotionalCampaign
from discounts.models.discount import Discount
from discounts.services.discount_code_generator import DiscountCodeGenerator
from users.models import User
from django.utils import timezone
from datetime import timedelta
import random
import string


class Command(BaseCommand):
    help = 'Seed promotional campaigns and discount codes with sample data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--website-id',
            type=int,
            help='Specific website ID to seed (if not provided, seeds all websites)',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing campaigns and discounts before seeding',
        )
        parser.add_argument(
            '--campaigns',
            type=int,
            default=8,
            help='Number of campaigns to create per website (default: 8)',
        )
        parser.add_argument(
            '--discounts-per-campaign',
            type=int,
            default=3,
            help='Number of discount codes per campaign (default: 3)',
        )
        parser.add_argument(
            '--standalone-discounts',
            type=int,
            default=10,
            help='Number of standalone discount codes to create per website (default: 10)',
        )

    def handle(self, *args, **options):
        website_id = options.get('website_id')
        clear = options.get('clear', False)
        campaigns_count = options.get('campaigns', 8)
        discounts_per_campaign = options.get('discounts_per_campaign', 3)
        standalone_discounts = options.get('standalone_discounts', 10)

        # Get websites to process
        if website_id:
            websites = Website.objects.filter(id=website_id)
            if not websites.exists():
                self.stdout.write(
                    self.style.ERROR(f'Website with ID {website_id} not found')
                )
                return
        else:
            websites = Website.objects.filter(is_active=True)

        if not websites.exists():
            self.stdout.write(
                self.style.WARNING('No active websites found')
            )
            return

        if clear:
            self.stdout.write('Clearing existing campaigns and discounts...')
            Discount.objects.all().delete()
            PromotionalCampaign.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Cleared existing data'))

        # Get admins for created_by fields
        admins = list(User.objects.filter(role__in=['admin', 'superadmin'], is_active=True)[:5])

        # Campaign names and types
        campaign_names = [
            "Black Friday Sale",
            "Cyber Monday",
            "Summer Special",
            "Back to School",
            "Holiday Season",
            "New Year Promotion",
            "Spring Sale",
            "Flash Sale",
            "Student Discount",
            "Loyalty Rewards",
            "Referral Bonus",
            "First Order Special",
        ]

        campaign_types = [
            'flash-sale',
            'seasonal',
            'email-blast',
            'referral',
            'loyalty',
            'student',
            None, # Some campaigns don't have a type
        ]

        campaign_descriptions = [
            "Special promotional campaign with exclusive discounts for our customers.",
            "Limited time offer with amazing savings on all services.",
            "Celebrate with us and enjoy great discounts on your orders.",
            "Seasonal promotion with special pricing for a limited time.",
            "Exclusive campaign for our valued customers.",
        ]

        # Status distribution: 40% active, 20% draft, 15% completed, 10% paused, 10% pending, 5% archived
        campaign_status_distribution = [
            ('active', 0.40),
            ('draft', 0.20),
            ('completed', 0.15),
            ('paused', 0.10),
            ('pending', 0.10),
            ('archived', 0.05),
        ]

        total_campaigns = 0
        total_discounts = 0

        for website in websites:
            self.stdout.write(f'\nProcessing website: {website.name} (ID: {website.id})')

            # Create Promotional Campaigns
            self.stdout.write(' Creating promotional campaigns...')
            created_campaigns = []

            for i in range(campaigns_count):
                try:
                    # Select campaign details
                    campaign_name = random.choice(campaign_names)
                    # Make name unique by appending website ID if needed
                    if PromotionalCampaign.objects.filter(name=campaign_name, website=website).exists():
                        campaign_name = f"{campaign_name} {website.id}-{i+1}"

                    description = random.choice(campaign_descriptions)
                    campaign_type = random.choice(campaign_types)

                    # Determine dates and status
                    rand = random.random()
                    cumulative = 0
                    status = 'draft'
                    for stat, prob in campaign_status_distribution:
                        cumulative += prob
                        if rand <= cumulative:
                            status = stat
                            break

                    # Set dates based on status
                    now = timezone.now()
                    if status == 'active':
                        # Active campaigns: started in the past, ends in the future
                        start_date = now - timedelta(days=random.randint(1, 30))
                        end_date = now + timedelta(days=random.randint(1, 60))
                        is_active = True
                    elif status == 'completed':
                        # Completed campaigns: ended in the past
                        start_date = now - timedelta(days=random.randint(60, 120))
                        end_date = now - timedelta(days=random.randint(1, 30))
                        is_active = False
                    elif status == 'pending':
                        # Pending campaigns: starts in the future
                        start_date = now + timedelta(days=random.randint(1, 30))
                        end_date = now + timedelta(days=random.randint(31, 90))
                        is_active = False
                    elif status == 'paused':
                        # Paused campaigns: started but paused
                        start_date = now - timedelta(days=random.randint(1, 30))
                        end_date = now + timedelta(days=random.randint(1, 60))
                        is_active = False
                    else: # draft, archived
                        # Draft/archived: future dates or past dates
                        start_date = now + timedelta(days=random.randint(1, 60))
                        end_date = now + timedelta(days=random.randint(61, 120))
                        is_active = False

                    created_by = random.choice(admins) if admins else None

                    from django.utils.text import slugify as _slugify
                    campaign = PromotionalCampaign.objects.create(
                        website=website,
                        name=campaign_name,
                        slug=_slugify(f"{campaign_name}-{website.id}-{i}"),
                        description=description,
                        starts_at=start_date,
                        ends_at=end_date,
                        is_active=is_active,
                        is_archived=(status == 'archived'),
                        created_by=created_by,
                    )

                    created_campaigns.append(campaign)
                    total_campaigns += 1

                    self.stdout.write(
                        f' Created campaign: {campaign.name} | '
                        f'{status} | {start_date.date()} - {end_date.date()}'
                    )

                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(
                            f' Failed to create campaign: {str(e)}'
                        )
                    )
                    continue

            # Create Discount Codes for Campaigns
            self.stdout.write(' Creating discount codes for campaigns...')
            for campaign in created_campaigns:
                for j in range(discounts_per_campaign):
                    try:
                        # Generate unique discount code
                        prefix = campaign.name.replace(' ', '').upper()[:8]
                        discount_code = DiscountCodeGenerator.generate_unique(website=website, prefix=prefix)

                        discount_type = random.choice(['percentage', 'percentage', 'percentage', 'fixed_amount'])
                        discount_value = (
                            Decimal(str(random.choice([5, 10, 15, 20, 25, 30, 40, 50])))
                            if discount_type == 'percentage'
                            else Decimal(str(random.choice([5, 10, 15, 20, 25, 50, 75, 100])))
                        )
                        usage_limit = random.choice([None, None, 50, 100, 200, 500])
                        per_client_usage_limit = random.choice([None, 1, 1, 2, 3])
                        min_payable_amount = (
                            Decimal(str(random.choice([50, 100, 150, 200, 250])))
                            if random.random() < 0.50 else Decimal('0.00')
                        )
                        max_discount_amount = (
                            Decimal(str(random.choice([25, 50, 75, 100])))
                            if discount_type == 'percentage' and random.random() < 0.30 else None
                        )

                        discount = Discount.objects.create(
                            website=website,
                            campaign=campaign,
                            discount_code=discount_code,
                            description=f"Discount code for {campaign.name}",
                            discount_type=discount_type,
                            origin='campaign',
                            discount_value=discount_value,
                            usage_limit=usage_limit,
                            per_client_usage_limit=per_client_usage_limit,
                            min_payable_amount=min_payable_amount,
                            max_discount_amount=max_discount_amount,
                            starts_at=campaign.starts_at,
                            ends_at=campaign.ends_at,
                            is_active=campaign.is_active,
                            is_campaign_managed=True,
                        )

                        total_discounts += 1

                        self.stdout.write(
                            f' Created discount: {discount_code} | '
                            f'{discount_type} | {discount_value}{"%" if discount_type == "percent" else "$"} | '
                            f'Campaign: {campaign.name}'
                        )

                    except Exception as e:
                        self.stdout.write(
                            self.style.WARNING(
                                f' Failed to create discount: {str(e)}'
                            )
                        )
                        continue

            # Create Standalone Discount Codes
            self.stdout.write(' Creating standalone discount codes...')
            for i in range(standalone_discounts):
                try:
                    # Generate unique discount code
                    prefixes = ['SAVE', 'DEAL', 'SPECIAL', 'OFFER', 'PROMO', 'DISCOUNT', 'BONUS']
                    prefix = random.choice(prefixes)
                    discount_code = DiscountCodeGenerator.generate_unique(website=website, prefix=prefix)

                    discount_type = random.choice(['percentage', 'percentage', 'percentage', 'fixed_amount'])
                    discount_value = (
                        Decimal(str(random.choice([5, 10, 15, 20, 25, 30])))
                        if discount_type == 'percentage'
                        else Decimal(str(random.choice([10, 15, 20, 25, 50])))
                    )
                    origin = random.choice(['manual', 'manual', 'holiday', 'loyalty'])
                    usage_limit = random.choice([None, None, 100, 200, 500])
                    per_client_usage_limit = random.choice([None, 1, 1, 2])
                    min_payable_amount = (
                        Decimal(str(random.choice([50, 100, 150, 200])))
                        if random.random() < 0.40 else Decimal('0.00')
                    )
                    max_discount_amount = (
                        Decimal(str(random.choice([25, 50, 75])))
                        if discount_type == 'percentage' and random.random() < 0.20 else None
                    )

                    now = timezone.now()
                    rand = random.random()
                    if rand < 0.60:
                        starts_at = now - timedelta(days=random.randint(1, 30))
                        ends_at = now + timedelta(days=random.randint(1, 90))
                        is_active = True
                    elif rand < 0.80:
                        starts_at = now + timedelta(days=random.randint(1, 30))
                        ends_at = now + timedelta(days=random.randint(31, 120))
                        is_active = False
                    else:
                        starts_at = now - timedelta(days=random.randint(60, 120))
                        ends_at = now - timedelta(days=random.randint(1, 30))
                        is_active = False

                    discount = Discount.objects.create(
                        website=website,
                        discount_code=discount_code,
                        description=f"Standalone discount code - {origin}",
                        discount_type=discount_type,
                        origin=origin,
                        discount_value=discount_value,
                        usage_limit=usage_limit,
                        per_client_usage_limit=per_client_usage_limit,
                        min_payable_amount=min_payable_amount,
                        max_discount_amount=max_discount_amount,
                        starts_at=starts_at,
                        ends_at=ends_at,
                        is_active=is_active,
                    )

                    total_discounts += 1

                    status = "Active" if is_active else ("Expired" if rand >= 0.80 else "Future")
                    self.stdout.write(
                        f' Created discount: {discount_code} | '
                        f'{discount_type} | {discount_value}{"%" if discount_type == "percentage" else "$"} | '
                        f'{status} | Origin: {origin}'
                    )

                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(
                            f' Failed to create discount: {str(e)}'
                        )
                    )
                    continue

        self.stdout.write(
            self.style.SUCCESS(
                f'\n Successfully created:\n'
                f' - {total_campaigns} promotional campaigns\n'
                f' - {total_discounts} discount codes'
            )
        )

