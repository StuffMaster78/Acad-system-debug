"""
Management command to test the payment batching service.
Creates test batches and verifies the batch generation logic.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal
from writer_wallet.services.payment_batching_service import PaymentBatchingService
from writer_wallet.models import PaymentSchedule, ScheduledWriterPayment, PaymentOrderRecord
from writer_management.models.profile import WriterProfile
from writer_wallet.models import WriterWallet
from websites.models import Website
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Test the payment batching service with sample data"

    def add_arguments(self, parser):
        parser.add_argument(
            '--website-id',
            type=int,
            help='Website ID to use for testing (default: first active website)',
        )
        parser.add_argument(
            '--create-test-data',
            action='store_true',
            help='Create test writers and wallets if they don\'t exist',
        )

    def handle(self, *args, **options):
        website_id = options.get('website_id')
        create_test_data = options.get('create_test_data', False)

        # Get or create website
        if website_id:
            try:
                website = Website.objects.get(id=website_id, is_active=True)
            except Website.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Website with ID {website_id} not found'))
                return
        else:
            website = Website.objects.filter(is_active=True).first()
            if not website:
                self.stdout.write(self.style.ERROR('No active website found'))
                return

        self.stdout.write(self.style.SUCCESS(f'Using website: {website.name} (ID: {website.id})'))

        # Get writers with payment schedules
        writers = WriterProfile.objects.filter(
            website=website,
            user__is_active=True
        ).select_related('user')

        if not writers.exists():
            self.stdout.write(self.style.WARNING('No writers found for this website'))
            if create_test_data:
                self.stdout.write('Creating test writers...')
                self._create_test_writers(website)
                writers = WriterProfile.objects.filter(website=website, user__is_active=True)
            else:
                self.stdout.write(self.style.ERROR('Use --create-test-data to create test writers'))
                return

        self.stdout.write(f'\nFound {writers.count()} writers')

        # Test bi-weekly batch generation
        self.stdout.write(self.style.SUCCESS('\n=== Testing Bi-Weekly Batch Generation ==='))
        today = timezone.now().date()
        
        # Calculate next bi-weekly date (15th or 1st)
        if today.day < 15:
            biweekly_date = today.replace(day=15)
        else:
            next_month = today.replace(day=1) + timedelta(days=32)
            biweekly_date = next_month.replace(day=1)

        self.stdout.write(f'Generating bi-weekly batch for date: {biweekly_date}')
        
        try:
            schedule = PaymentBatchingService.generate_payment_batch(
                website=website,
                schedule_type='Bi-Weekly',
                scheduled_date=biweekly_date,
                processed_by=None
            )
            
            self.stdout.write(self.style.SUCCESS(f'✓ Created batch: {schedule.reference_code}'))
            self.stdout.write(f'  Schedule Type: {schedule.schedule_type}')
            self.stdout.write(f'  Scheduled Date: {schedule.scheduled_date}')
            self.stdout.write(f'  Completed: {schedule.completed}')
            
            # Get breakdown
            breakdown = PaymentBatchingService.get_batch_breakdown(schedule)
            self.stdout.write(f'\n  Batch Breakdown:')
            self.stdout.write(f'    Total Writers: {breakdown["total_writers"]}')
            self.stdout.write(f'    Total Amount: ${breakdown["total_amount"]:,.2f}')
            
            if breakdown['writers']:
                self.stdout.write(f'\n  Writers in batch:')
                for writer in breakdown['writers'][:5]:  # Show first 5
                    self.stdout.write(f'    - {writer["writer_name"]}: ${writer["total_amount"]:,.2f} ({writer["orders_count"]} orders)')
                if len(breakdown['writers']) > 5:
                    self.stdout.write(f'    ... and {len(breakdown["writers"]) - 5} more')
            else:
                self.stdout.write(self.style.WARNING('    No writers with earnings in this period'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Error generating bi-weekly batch: {str(e)}'))
            import traceback
            traceback.print_exc()

        # Test monthly batch generation
        self.stdout.write(self.style.SUCCESS('\n=== Testing Monthly Batch Generation ==='))
        
        # Calculate next monthly date (1st of next month)
        if today.day == 1:
            monthly_date = today
        else:
            next_month = today.replace(day=1) + timedelta(days=32)
            monthly_date = next_month.replace(day=1)

        self.stdout.write(f'Generating monthly batch for date: {monthly_date}')
        
        try:
            schedule = PaymentBatchingService.generate_payment_batch(
                website=website,
                schedule_type='Monthly',
                scheduled_date=monthly_date,
                processed_by=None
            )
            
            self.stdout.write(self.style.SUCCESS(f'✓ Created batch: {schedule.reference_code}'))
            self.stdout.write(f'  Schedule Type: {schedule.schedule_type}')
            self.stdout.write(f'  Scheduled Date: {schedule.scheduled_date}')
            self.stdout.write(f'  Completed: {schedule.completed}')
            
            # Get breakdown
            breakdown = PaymentBatchingService.get_batch_breakdown(schedule)
            self.stdout.write(f'\n  Batch Breakdown:')
            self.stdout.write(f'    Total Writers: {breakdown["total_writers"]}')
            self.stdout.write(f'    Total Amount: ${breakdown["total_amount"]:,.2f}')
            
            if breakdown['writers']:
                self.stdout.write(f'\n  Writers in batch:')
                for writer in breakdown['writers'][:5]:  # Show first 5
                    self.stdout.write(f'    - {writer["writer_name"]}: ${writer["total_amount"]:,.2f} ({writer["orders_count"]} orders)')
                if len(breakdown['writers']) > 5:
                    self.stdout.write(f'    ... and {len(breakdown["writers"]) - 5} more')
            else:
                self.stdout.write(self.style.WARNING('    No writers with earnings in this period'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Error generating monthly batch: {str(e)}'))
            import traceback
            traceback.print_exc()

        # Test payment date calculation
        self.stdout.write(self.style.SUCCESS('\n=== Testing Payment Date Calculation ==='))
        
        test_writers = writers[:3]  # Test with first 3 writers
        for writer_profile in test_writers:
            if not writer_profile.payment_schedule:
                continue
                
            # Test bi-weekly
            if writer_profile.payment_schedule == 'bi-weekly':
                next_date = PaymentBatchingService.calculate_payment_date(
                    writer_profile,
                    'bi-weekly',
                    today
                )
                self.stdout.write(f'  {writer_profile.user.username} (bi-weekly, pref: {writer_profile.payment_date_preference or "default"}): {next_date}')
            
            # Test monthly
            elif writer_profile.payment_schedule == 'monthly':
                next_date = PaymentBatchingService.calculate_payment_date(
                    writer_profile,
                    'monthly',
                    today
                )
                self.stdout.write(f'  {writer_profile.user.username} (monthly, pref: {writer_profile.payment_date_preference or "default"}): {next_date}')

        self.stdout.write(self.style.SUCCESS('\n=== Test Complete ==='))

    def _create_test_writers(self, website):
        """Create test writers with different payment schedule preferences."""
        from writer_management.models.profile import WriterProfile
        from writer_wallet.models import WriterWallet
        
        test_writers = [
            {
                'username': 'test_writer_biweekly_1',
                'email': 'test_biweekly1@example.com',
                'payment_schedule': 'bi-weekly',
                'payment_date_preference': '1,15',
            },
            {
                'username': 'test_writer_biweekly_2',
                'email': 'test_biweekly2@example.com',
                'payment_schedule': 'bi-weekly',
                'payment_date_preference': '5,20',
            },
            {
                'username': 'test_writer_monthly_1',
                'email': 'test_monthly1@example.com',
                'payment_schedule': 'monthly',
                'payment_date_preference': '1',
            },
            {
                'username': 'test_writer_monthly_2',
                'email': 'test_monthly2@example.com',
                'payment_schedule': 'monthly',
                'payment_date_preference': '15',
            },
        ]

        for writer_data in test_writers:
            user, created = User.objects.get_or_create(
                username=writer_data['username'],
                defaults={
                    'email': writer_data['email'],
                    'role': 'writer',
                    'website': website,
                }
            )
            
            if created:
                user.set_password('testpass123')
                user.save()

            profile, _ = WriterProfile.objects.get_or_create(
                user=user,
                website=website,
                defaults={
                    'payment_schedule': writer_data['payment_schedule'],
                    'payment_date_preference': writer_data['payment_date_preference'],
                    'registration_id': f"Writer #{user.id}",
                }
            )
            
            # Update if exists
            if not created:
                profile.payment_schedule = writer_data['payment_schedule']
                profile.payment_date_preference = writer_data['payment_date_preference']
                profile.save()

            # Create wallet
            WriterWallet.objects.get_or_create(
                writer=user,
                website=website,
                defaults={'balance': Decimal('1000.00')}
            )

        self.stdout.write(self.style.SUCCESS(f'Created {len(test_writers)} test writers'))

