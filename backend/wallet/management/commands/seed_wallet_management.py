from decimal import Decimal
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model
import random

from websites.models import Website
from wallet.models import Wallet, WalletTransaction, WithdrawalRequest
from client_wallet.models import ClientWallet, ClientWalletTransaction
from writer_wallet.models import (
    WriterWallet, WalletTransaction as WriterWalletTransaction,
    WriterPaymentBatch, PaymentSchedule, ScheduledWriterPayment,
    PaymentOrderRecord, WriterPayment, AdminPaymentAdjustment
)
from orders.models import Order
from order_payments_management.models import WalletTransaction as OrderPaymentWalletTransaction

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed wallet management data including wallets, transactions, and withdrawal requests'

    def add_arguments(self, parser):
        parser.add_argument(
            '--website-id',
            type=int,
            help='Specific website ID to seed (if not provided, seeds all websites)'
        )
        parser.add_argument(
            '--transactions-per-wallet',
            type=int,
            default=10,
            help='Number of transactions to create per wallet (default: 10)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing wallet data before seeding'
        )

    @transaction.atomic
    def handle(self, *args, **options):
        website_id = options['website_id']
        transactions_per_wallet = options['transactions_per_wallet']
        clear_data = options['clear']

        if website_id:
            websites = Website.objects.filter(id=website_id)
        else:
            websites = Website.objects.all()

        if not websites.exists():
            self.stdout.write(self.style.ERROR("No websites found to seed."))
            return

        if clear_data:
            self.stdout.write(self.style.WARNING("Clearing existing wallet data..."))
            WithdrawalRequest.objects.all().delete()
            WalletTransaction.objects.all().delete()
            ClientWalletTransaction.objects.all().delete()
            WriterWalletTransaction.objects.all().delete()
            OrderPaymentWalletTransaction.objects.all().delete()
            ScheduledWriterPayment.objects.all().delete()
            PaymentSchedule.objects.all().delete()
            WriterPaymentBatch.objects.all().delete()
            WriterPayment.objects.all().delete()
            AdminPaymentAdjustment.objects.all().delete()
            PaymentOrderRecord.objects.all().delete()
            Wallet.objects.all().delete()
            ClientWallet.objects.all().delete()
            WriterWallet.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("Cleared existing wallet data."))

        created_wallets_count = 0
        created_transactions_count = 0
        created_withdrawal_requests_count = 0
        created_payment_schedules_count = 0

        transaction_types = [
            'top-up', 'withdrawal', 'refund', 'payment', 'bonus',
            'adjustment', 'referral_bonus', 'credit', 'debit', 'loyalty_point'
        ]

        client_transaction_types = [
            'top-up', 'payment', 'refund', 'bonus', 'adjustment',
            'referral_bonus', 'loyalty_conversion'
        ]

        writer_transaction_types = [
            'Earning', 'Bonus', 'Reward', 'Adjustment', 'Fine',
            'Refund Deduction', 'Payout', 'Order Payment', 'Other'
        ]

        status_choices = [
            'pending', 'succeeded', 'completed', 'failed', 'cancelled'
        ]

        for website in websites:
            self.stdout.write(self.style.SUCCESS(f"\nProcessing website: {website.name} (ID: {website.id})"))

            # Get users for this website
            clients = User.objects.filter(role='client', website=website)
            writers = User.objects.filter(role='writer', website=website)
            admins = User.objects.filter(role__in=['admin', 'superadmin'], website=website)

            if not clients.exists() and not writers.exists():
                self.stdout.write(self.style.WARNING(f"  No clients or writers found for {website.name}. Skipping."))
                continue

            # Create general wallets for clients
            for client in clients[:20]:  # Limit to 20 clients per website
                wallet, created = Wallet.objects.get_or_create(
                    user=client,
                    website=website,
                    defaults={'balance': Decimal('0.00')}
                )
                if created:
                    created_wallets_count += 1
                    self.stdout.write(f"  ✓ Created general wallet for client: {client.email}")

                # Create client wallet
                client_wallet, created = ClientWallet.objects.get_or_create(
                    user=client,
                    website=website,
                    defaults={
                        'balance': Decimal(str(random.uniform(0, 500))),
                        'loyalty_points': random.randint(0, 1000)
                    }
                )
                if created:
                    created_wallets_count += 1
                    self.stdout.write(f"  ✓ Created client wallet for: {client.email}")

                # Create wallet transactions
                for i in range(transactions_per_wallet):
                    transaction_type = random.choice(transaction_types)
                    amount = Decimal(str(random.uniform(10, 200)))
                    status = random.choice(status_choices)
                    
                    # Determine if credit or debit
                    is_credit = transaction_type in ['top-up', 'refund', 'bonus', 'referral_bonus', 'credit', 'loyalty_point']
                    transaction_amount = amount if is_credit else -amount
                    
                    # Update wallet balance (only for successful transactions)
                    if status in ['succeeded', 'completed']:
                        wallet.balance = max(Decimal('0.00'), wallet.balance + transaction_amount)
                        wallet.save()

                    try:
                        WalletTransaction.objects.create(
                            website=website,
                            wallet=wallet,
                            transaction_type=transaction_type,
                            amount=abs(amount),
                            description=f"{transaction_type.replace('_', ' ').title()} transaction",
                            source='order' if transaction_type == 'payment' else 'manual',
                            created_at=timezone.now() - timedelta(days=random.randint(0, 30))
                        )
                        created_transactions_count += 1
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f"  Warning: Failed to create wallet transaction: {e}"))
                        continue

                # Create client wallet transactions
                for i in range(transactions_per_wallet):
                    transaction_type = random.choice(client_transaction_types)
                    amount = Decimal(str(random.uniform(10, 200)))
                    status = random.choice(status_choices)
                    
                    is_credit = transaction_type in ['top-up', 'refund', 'bonus', 'referral_bonus', 'loyalty_conversion']
                    transaction_amount = amount if is_credit else -amount
                    
                    if status in ['succeeded', 'completed']:
                        client_wallet.balance = max(Decimal('0.00'), client_wallet.balance + transaction_amount)
                        client_wallet.save()

                    try:
                        ClientWalletTransaction.objects.create(
                            website=website,
                            wallet=client_wallet,
                            transaction_type=transaction_type,
                            amount=abs(amount),
                            description=f"{transaction_type.replace('_', ' ').title()} for client",
                            created_at=timezone.now() - timedelta(days=random.randint(0, 30))
                        )
                        created_transactions_count += 1
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f"  Warning: Failed to create client wallet transaction: {e}"))
                        continue

                # Create withdrawal requests for some clients
                if random.random() < 0.3:  # 30% chance
                    withdrawal_amount = Decimal(str(random.uniform(50, 200)))
                    if client_wallet.balance >= withdrawal_amount:
                        withdrawal_status = random.choice(['pending', 'approved', 'rejected'])
                        withdrawal = WithdrawalRequest.objects.create(
                            website=website,
                            wallet=wallet,
                            amount=withdrawal_amount,
                            status=withdrawal_status,
                            description=f"Withdrawal request for {client.email}",
                            created_at=timezone.now() - timedelta(days=random.randint(0, 7))
                        )
                        if withdrawal_status == 'approved':
                            withdrawal.processed_at = timezone.now() - timedelta(days=random.randint(0, 3))
                            withdrawal.save()
                        created_withdrawal_requests_count += 1

            # Create writer wallets
            for writer in writers[:15]:  # Limit to 15 writers per website
                wallet, created = Wallet.objects.get_or_create(
                    user=writer,
                    website=website,
                    defaults={'balance': Decimal('0.00')}
                )
                if created:
                    created_wallets_count += 1
                    self.stdout.write(f"  ✓ Created general wallet for writer: {writer.email}")

                # Create writer wallet
                writer_wallet, created = WriterWallet.objects.get_or_create(
                    writer=writer,
                    website=website,
                    defaults={
                        'balance': Decimal(str(random.uniform(0, 1000))),
                        'total_earnings': Decimal(str(random.uniform(500, 5000))),
                        'total_fines': Decimal(str(random.uniform(0, 100))),
                        'total_adjustments': Decimal(str(random.uniform(0, 200))),
                        'is_locked': random.random() < 0.1  # 10% chance of being locked
                    }
                )
                if created:
                    created_wallets_count += 1
                    self.stdout.write(f"  ✓ Created writer wallet for: {writer.email}")

                # Create writer wallet transactions
                for i in range(transactions_per_wallet):
                    transaction_type = random.choice(writer_transaction_types)
                    amount = Decimal(str(random.uniform(20, 300)))
                    
                    # Determine if positive or negative
                    is_positive = transaction_type in ['Earning', 'Bonus', 'Reward', 'Order Payment']
                    transaction_amount = amount if is_positive else -amount
                    
                    # Get a random order if available
                    orders = Order.objects.filter(website=website, assigned_writer=writer)
                    order = random.choice(orders) if orders.exists() else None

                    try:
                        WriterWalletTransaction.objects.create(
                            website=website,
                            writer_wallet=writer_wallet,
                            transaction_type=transaction_type,
                            order=order,
                            amount=abs(amount),
                            reference_code=f"TXN{random.randint(100000, 999999)}",
                            created_at=timezone.now() - timedelta(days=random.randint(0, 30))
                        )
                        created_transactions_count += 1
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f"  Warning: Failed to create writer wallet transaction: {e}"))
                        continue

                    # Update writer wallet totals
                    if transaction_type == 'Earning' or transaction_type == 'Order Payment':
                        writer_wallet.total_earnings += abs(amount)
                    elif transaction_type == 'Fine':
                        writer_wallet.total_fines += abs(amount)
                    elif transaction_type == 'Adjustment':
                        writer_wallet.total_adjustments += abs(amount)
                    
                    if is_positive:
                        writer_wallet.balance += abs(amount)
                    else:
                        writer_wallet.balance = max(Decimal('0.00'), writer_wallet.balance - abs(amount))
                    
                    writer_wallet.save()

                # Create admin payment adjustments
                if random.random() < 0.4 and admins.exists():  # 40% chance
                    adjustment_type = random.choice(['Bonus', 'Fine', 'Correction', 'Other'])
                    action = random.choice(['Topup', 'Deduct'])
                    amount = Decimal(str(random.uniform(10, 150)))
                    admin = random.choice(admins)

                    adjustment = AdminPaymentAdjustment.objects.create(
                        website=website,
                        writer_wallet=writer_wallet,
                        adjustment_type=adjustment_type,
                        action=action,
                        amount=amount,
                        reason=f"{adjustment_type} adjustment: {action}",
                        adjusted_by=admin,
                        created_at=timezone.now() - timedelta(days=random.randint(0, 14))
                    )
                    created_transactions_count += 1

                    # Update wallet balance
                    if action == 'Topup':
                        writer_wallet.balance += amount
                        writer_wallet.total_adjustments += amount
                    else:
                        writer_wallet.balance = max(Decimal('0.00'), writer_wallet.balance - amount)
                        writer_wallet.total_adjustments += amount
                    writer_wallet.save()

            # Create payment schedules and batches
            if writers.exists() and admins.exists():
                admin = random.choice(admins)
                
                # Create bi-weekly payment schedules
                for i in range(2):
                    schedule_date = timezone.now().date() - timedelta(days=14 * i)
                    schedule = PaymentSchedule.objects.create(
                        website=website,
                        schedule_type='Bi-Weekly',
                        scheduled_date=schedule_date,
                        processed_by=admin,
                        completed=(i == 0),
                        reference_code=f"PB{random.randint(100000, 999999)}",
                        created_at=timezone.now() - timedelta(days=14 * i)
                    )
                    created_payment_schedules_count += 1

                    # Create scheduled payments for writers
                    for writer in writers[:5]:
                        writer_wallet = WriterWallet.objects.filter(writer=writer, website=website).first()
                        if writer_wallet:
                            amount = Decimal(str(random.uniform(200, 800)))
                            payment = ScheduledWriterPayment.objects.create(
                                website=website,
                                batch=schedule,
                                writer_wallet=writer_wallet,
                                amount=amount,
                                status='Paid' if schedule.completed else 'Pending',
                                payment_date=timezone.now() - timedelta(days=14 * i - 1) if schedule.completed else None,
                                reference_code=f"PAY{random.randint(100000, 999999)}"
                            )
                            created_transactions_count += 1

                            # Link orders to payment
                            orders = Order.objects.filter(
                                website=website,
                                assigned_writer=writer,
                                status='COMPLETED'
                            )[:3]
                            for order in orders:
                                PaymentOrderRecord.objects.create(
                                    website=website,
                                    payment=payment,
                                    order=order,
                                    amount_paid=order.writer_compensation or Decimal('100.00')
                                )

                # Create monthly payment schedules
                for i in range(2):
                    month_start = (timezone.now().date().replace(day=1) - timedelta(days=30 * i))
                    schedule = PaymentSchedule.objects.create(
                        website=website,
                        schedule_type='Monthly',
                        scheduled_date=month_start,
                        processed_by=admin,
                        completed=(i == 0),
                        reference_code=f"PB{random.randint(100000, 999999)}",
                        created_at=timezone.now() - timedelta(days=30 * i)
                    )
                    created_payment_schedules_count += 1

                    # Create scheduled payments for writers
                    for writer in writers[:5]:
                        writer_wallet = WriterWallet.objects.filter(writer=writer, website=website).first()
                        if writer_wallet:
                            amount = Decimal(str(random.uniform(500, 1500)))
                            payment = ScheduledWriterPayment.objects.create(
                                website=website,
                                batch=schedule,
                                writer_wallet=writer_wallet,
                                amount=amount,
                                status='Paid' if schedule.completed else 'Pending',
                                payment_date=timezone.now() - timedelta(days=30 * i - 1) if schedule.completed else None,
                                reference_code=f"PAY{random.randint(100000, 999999)}"
                            )
                            created_transactions_count += 1

                # Create payment batches
                for i in range(2):
                    batch = WriterPaymentBatch.objects.create(
                        website=website,
                        processed_by=admin,
                        completed=(i == 0),
                        reference_code=f"BATCH{random.randint(100000, 999999)}",
                        created_at=timezone.now() - timedelta(days=7 * i)
                    )

                    # Create writer payments in batch
                    for writer in writers[:5]:
                        writer_wallet = WriterWallet.objects.filter(writer=writer, website=website).first()
                        if writer_wallet:
                            amount = Decimal(str(random.uniform(300, 1000)))
                            WriterPayment.objects.create(
                                website=website,
                                batch=batch,
                                writer_wallet=writer_wallet,
                                amount=amount,
                                status='Paid' if batch.completed else 'Pending',
                                payment_date=timezone.now() - timedelta(days=7 * i - 1) if batch.completed else None,
                                reference_code=f"PAY{random.randint(100000, 999999)}"
                            )
                            created_transactions_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"\n✓ Successfully seeded wallet management data:\n"
            f"  - {created_wallets_count} wallets created\n"
            f"  - {created_transactions_count} transactions created\n"
            f"  - {created_withdrawal_requests_count} withdrawal requests created\n"
            f"  - {created_payment_schedules_count} payment schedules created"
        ))

