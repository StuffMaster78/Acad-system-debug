from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from decimal import Decimal
import random
from datetime import timedelta

from writer_wallet.models import WriterPaymentRequest, WriterWallet, ScheduledWriterPayment
from users.models import User


class Command(BaseCommand):
    help = "Seed writer payment requests with various statuses for testing"

    def add_arguments(self, parser):
        parser.add_argument(
            '--website-id',
            type=int,
            help='Website ID to seed payment requests for (optional)',
        )
        parser.add_argument(
            '--count',
            type=int,
            default=30,
            help='Number of payment requests to create per website (default: 30)',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        website_id = options.get('website_id')
        count_per_website = options.get('count', 30)
        
        # Get all writer wallets
        if website_id:
            writer_wallets = WriterWallet.objects.filter(website_id=website_id).select_related('writer', 'website')
        else:
            writer_wallets = WriterWallet.objects.all().select_related('writer', 'website')
        
        if not writer_wallets.exists():
            self.stdout.write(self.style.WARNING('No writer wallets found. Please seed writer wallets first.'))
            return
        
        # Get admin users for reviewing requests
        admin_users = User.objects.filter(role__in=['admin', 'superadmin'])
        if not admin_users.exists():
            self.stdout.write(self.style.WARNING('No admin users found. Payment requests will be created without reviewers.'))
        
        # Status distribution: 40% pending, 30% approved, 20% rejected, 10% processed
        status_weights = {
            'pending': 0.4,
            'approved': 0.3,
            'rejected': 0.2,
            'processed': 0.1,
        }
        
        # Reasons for payment requests
        reasons = [
            "Need funds for urgent expenses",
            "Requesting payment for completed work",
            "Monthly payment request",
            "Emergency financial need",
            "Accumulated earnings payment",
            "Requesting partial payment",
            "Need funds for upcoming expenses",
            "Standard payment request",
            "Requesting payment for multiple completed orders",
            "Early payment request",
        ]
        
        # Review notes templates
        review_notes = {
            'approved': [
                "Payment approved. Processing scheduled payment.",
                "Approved. Amount verified and within balance limits.",
                "Payment request approved. Will be processed in next batch.",
                "Approved. Writer has sufficient balance.",
                "Payment approved and scheduled.",
            ],
            'rejected': [
                "Request rejected: Insufficient balance at time of review.",
                "Rejected: Requested amount exceeds available balance.",
                "Rejected: Multiple pending requests detected.",
                "Rejected: Account verification required.",
                "Rejected: Payment schedule conflict.",
            ],
        }
        
        total_created = 0
        total_skipped = 0
        
        # Group wallets by website
        wallets_by_website = {}
        for wallet in writer_wallets:
            if wallet.website_id not in wallets_by_website:
                wallets_by_website[wallet.website_id] = []
            wallets_by_website[wallet.website_id].append(wallet)
        
        for website_id, wallets in wallets_by_website.items():
            self.stdout.write(f"\n{'='*60}")
            self.stdout.write(f"Seeding payment requests for website ID: {website_id}")
            self.stdout.write(f"Found {len(wallets)} writer wallets")
            self.stdout.write(f"{'='*60}\n")
            
            # Delete existing payment requests for this website to start fresh
            deleted_count = WriterPaymentRequest.objects.filter(website_id=website_id).delete()[0]
            if deleted_count > 0:
                self.stdout.write(f"  Deleted {deleted_count} existing payment requests")
            
            created_count = 0
            skipped_count = 0
            
            # Create payment requests
            for i in range(count_per_website):
                if not wallets:
                    break
                
                # Select a random wallet
                wallet = random.choice(wallets)
                
                # Ensure wallet has a balance
                if wallet.balance <= 0:
                    # Set a random balance for testing
                    wallet.balance = Decimal(str(random.uniform(100, 5000)))
                    wallet.save(update_fields=['balance'])
                
                # Determine status based on weights
                rand = random.random()
                cumulative = 0
                status = 'pending'
                for stat, weight in status_weights.items():
                    cumulative += weight
                    if rand <= cumulative:
                        status = stat
                        break
                
                # Calculate requested amount (between 10% and 90% of balance)
                balance_ratio = random.uniform(0.1, 0.9)
                requested_amount = Decimal(str(wallet.balance * Decimal(str(balance_ratio)))).quantize(Decimal('0.01'))
                
                # Ensure requested amount is at least $10
                if requested_amount < 10:
                    requested_amount = Decimal('10.00')
                
                # Set dates
                now = timezone.now()
                days_ago = random.randint(0, 90)  # Requests from last 90 days
                created_at = now - timedelta(days=days_ago)
                
                reviewed_at = None
                processed_at = None
                reviewed_by = None
                review_notes_text = None
                scheduled_payment = None
                
                if status in ['approved', 'rejected']:
                    # Reviewed within 1-7 days of creation
                    review_delay = random.randint(1, 7)
                    reviewed_at = created_at + timedelta(days=review_delay)
                    reviewed_by = random.choice(admin_users) if admin_users.exists() else None
                    review_notes_text = random.choice(review_notes.get(status, ['Reviewed.']))
                
                if status == 'processed':
                    # Processed within 1-14 days of approval
                    review_delay = random.randint(1, 7)
                    reviewed_at = created_at + timedelta(days=review_delay)
                    reviewed_by = random.choice(admin_users) if admin_users.exists() else None
                    review_notes_text = random.choice(review_notes.get('approved', ['Approved.']))
                    
                    # Try to link to a scheduled payment if available
                    scheduled_payments = ScheduledWriterPayment.objects.filter(
                        writer_wallet=wallet,
                        status='paid'
                    ).order_by('-payment_date')
                    
                    if scheduled_payments.exists():
                        scheduled_payment = random.choice(scheduled_payments[:5])  # Pick from recent 5
                        processed_at = scheduled_payment.payment_date
                    else:
                        processed_at = reviewed_at + timedelta(days=random.randint(1, 14))
                
                # Create payment request
                try:
                    payment_request = WriterPaymentRequest.objects.create(
                        website=wallet.website,
                        writer_wallet=wallet,
                        requested_amount=requested_amount,
                        available_balance=wallet.balance,
                        status=status,
                        reason=random.choice(reasons),
                        requested_by=wallet.writer,
                        reviewed_by=reviewed_by,
                        reviewed_at=reviewed_at,
                        review_notes=review_notes_text,
                        processed_at=processed_at,
                        scheduled_payment=scheduled_payment,
                        created_at=created_at,
                    )
                    
                    created_count += 1
                    total_created += 1
                    
                    if created_count % 10 == 0:
                        self.stdout.write(f"  Created {created_count} payment requests...")
                    
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f"  Could not create payment request for {wallet.writer.email}: {e}")
                    )
                    skipped_count += 1
                    total_skipped += 1
                    continue
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"\n  ✓ Created {created_count} payment requests for website {website_id}"
                )
            )
            if skipped_count > 0:
                self.stdout.write(
                    self.style.WARNING(f"  ⚠ Skipped {skipped_count} payment requests")
                )
        
        # Summary
        self.stdout.write(f"\n{'='*60}")
        self.stdout.write(self.style.SUCCESS(f"Total payment requests created: {total_created}"))
        if total_skipped > 0:
            self.stdout.write(self.style.WARNING(f"Total skipped: {total_skipped}"))
        
        # Status breakdown
        status_counts = {}
        for status in ['pending', 'approved', 'rejected', 'processed']:
            count = WriterPaymentRequest.objects.filter(status=status).count()
            status_counts[status] = count
            self.stdout.write(f"  {status.capitalize()}: {count}")
        
        self.stdout.write(f"{'='*60}\n")

