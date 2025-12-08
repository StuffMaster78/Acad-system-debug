from decimal import Decimal
from datetime import timedelta
from uuid import uuid4
import random

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Q

from websites.models import Website
from orders.models import Order
from special_orders.models import SpecialOrder, WriterBonus
from class_management.models import ClassBundle, ClassPurchase
from order_payments_management.models import OrderPayment
from client_wallet.models import ClientWallet, ClientWalletTransaction
from wallet.models import Wallet, WalletTransaction as OldWalletTransaction
from writer_wallet.models import WriterWallet, WalletTransaction as WriterWalletTransaction
from writer_management.models.tipping import Tip
from writer_management.models.profile import WriterProfile

User = get_user_model()


class Command(BaseCommand):
    help = "Seed comprehensive payment logs including orders, special orders, classes, tips, bonuses, wallet top-ups, etc."

    def add_arguments(self, parser):
        parser.add_argument(
            "--transactions",
            type=int,
            default=100,
            help="Number of transactions to create per type",
        )
        parser.add_argument(
            "--days",
            type=int,
            default=90,
            help="Number of days back to generate transactions",
        )

    def handle(self, *args, **options):
        transactions_per_type = max(10, options["transactions"])
        days_back = max(1, options["days"])

        self.stdout.write(f"\n{'='*60}")
        self.stdout.write("Seeding Payment Logs")
        self.stdout.write(f"{'='*60}\n")

        # Get or create websites
        websites = Website.objects.filter(is_active=True)
        if not websites.exists():
            website = Website.objects.create(
                domain="https://demo.writingsystem.test",
                defaults={"name": "Demo Writing System", "contact_email": "support@demo.test", "is_active": True},
            )
            websites = Website.objects.filter(id=website.id)

        total_created = 0

        for website in websites:
            self.stdout.write(f"\nProcessing website: {website.name} (ID: {website.id})")
            self.stdout.write("-" * 60)

            # Get existing users
            clients = User.objects.filter(role="client", website=website)[:10]
            writers = User.objects.filter(role="writer", website=website)[:10]

            if not clients.exists():
                self.stdout.write(self.style.WARNING(f"  No clients found for {website.name}, skipping..."))
                continue
            if not writers.exists():
                self.stdout.write(self.style.WARNING(f"  No writers found for {website.name}, skipping..."))
                continue

            # 1. Create Order Payments (standard orders)
            self.stdout.write(f"  Creating {transactions_per_type} order payments...")
            created = self.create_order_payments(website, clients, transactions_per_type, days_back)
            total_created += created
            self.stdout.write(f"    ✓ Created {created} order payments")

            # 2. Create Special Order Payments
            self.stdout.write(f"  Creating {transactions_per_type} special order payments...")
            created = self.create_special_order_payments(website, clients, transactions_per_type, days_back)
            total_created += created
            self.stdout.write(f"    ✓ Created {created} special order payments")

            # 3. Create Class Payments
            self.stdout.write(f"  Creating {transactions_per_type} class payments...")
            created = self.create_class_payments(website, clients, transactions_per_type, days_back)
            total_created += created
            self.stdout.write(f"    ✓ Created {created} class payments")

            # 4. Create Wallet Top-ups
            self.stdout.write(f"  Creating {transactions_per_type} wallet top-ups...")
            created = self.create_wallet_topups(website, clients, transactions_per_type, days_back)
            total_created += created
            self.stdout.write(f"    ✓ Created {created} wallet top-ups")

            # 5. Create Tips
            self.stdout.write(f"  Creating {transactions_per_type} tips...")
            created = self.create_tips(website, clients, writers, transactions_per_type, days_back)
            total_created += created
            self.stdout.write(f"    ✓ Created {created} tips")

            # 6. Create Writer Bonuses
            self.stdout.write(f"  Creating {transactions_per_type // 2} writer bonuses...")
            created = self.create_bonuses(website, writers, transactions_per_type // 2, days_back)
            total_created += created
            self.stdout.write(f"    ✓ Created {created} writer bonuses")

            # 7. Create Client Wallet Transactions (various types)
            self.stdout.write(f"  Creating {transactions_per_type} client wallet transactions...")
            created = self.create_client_wallet_transactions(website, clients, transactions_per_type, days_back)
            total_created += created
            self.stdout.write(f"    ✓ Created {created} client wallet transactions")

            # 8. Create Writer Wallet Transactions
            self.stdout.write(f"  Creating {transactions_per_type} writer wallet transactions...")
            created = self.create_writer_wallet_transactions(website, writers, transactions_per_type, days_back)
            total_created += created
            self.stdout.write(f"    ✓ Created {created} writer wallet transactions")

        self.stdout.write(self.style.SUCCESS(f"\n{'='*60}"))
        self.stdout.write(self.style.SUCCESS(f"✓ Seeded {total_created} payment log transactions"))
        self.stdout.write(self.style.SUCCESS(f"{'='*60}\n"))

    def create_order_payments(self, website, clients, count, days_back):
        """Create standard order payments"""
        created = 0
        orders = Order.objects.filter(website=website, client__in=clients)[:count * 2]
        
        if not orders.exists():
            return 0

        for i in range(count):
            try:
                order = random.choice(list(orders))
                client = order.client
                days_ago = random.randint(0, days_back)
                created_at = timezone.now() - timedelta(days=days_ago, hours=random.randint(0, 23))

                amount = Decimal(str(random.randint(50, 500)))
                # Use filter().first() to avoid get_or_create issues with multiple matches
                existing = OrderPayment.objects.filter(
                    website=website,
                    client=client,
                    order=order,
                    reference_id=f'ORD-{uuid4().hex[:8]}'
                ).first()
                
                if existing:
                    payment = existing
                else:
                    amount = Decimal(str(random.randint(50, 500)))
                    payment = OrderPayment.objects.create(
                        website=website,
                        client=client,
                        order=order,
                        payment_type='standard',
                        original_amount=amount,
                        amount=amount,
                        discounted_amount=amount,
                        status=random.choice(['succeeded', 'completed', 'pending', 'failed']),
                        payment_method=random.choice(['stripe', 'paypal', 'wallet', 'bank_transfer']),
                        reference_id=f'ORD-{uuid4().hex[:8]}',
                        transaction_id=f'txn_{uuid4().hex[:12]}',
                        created_at=created_at,
                        confirmed_at=created_at if random.random() > 0.3 else None,
                    )
                    created += 1
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"    Warning: Could not create order payment: {e}"))
                continue

        return created

    def create_special_order_payments(self, website, clients, count, days_back):
        """Create special order payments"""
        created = 0
        try:
            special_orders = SpecialOrder.objects.filter(website=website, client__in=clients)[:count * 2]
            
            if not special_orders.exists():
                return 0

            for i in range(count):
                try:
                    special_order = random.choice(list(special_orders))
                    client = special_order.client
                    days_ago = random.randint(0, days_back)
                    created_at = timezone.now() - timedelta(days=days_ago, hours=random.randint(0, 23))
                    payment_type = random.choice(['predefined_special', 'estimated_special'])

                    amount = Decimal(str(random.randint(100, 1000)))
                    ref_id = f'SPO-{uuid4().hex[:8]}'
                    
                    existing = OrderPayment.objects.filter(
                        website=website,
                        client=client,
                        special_order=special_order,
                        reference_id=ref_id
                    ).first()
                    
                    if not existing:
                        payment = OrderPayment.objects.create(
                            website=website,
                            client=client,
                            special_order=special_order,
                            payment_type=payment_type,
                            original_amount=amount,
                            amount=amount,
                            discounted_amount=amount,
                            status=random.choice(['succeeded', 'completed', 'pending']),
                            payment_method=random.choice(['stripe', 'paypal', 'wallet']),
                            reference_id=ref_id,
                            transaction_id=f'txn_{uuid4().hex[:12]}',
                            created_at=created_at,
                            confirmed_at=created_at if random.random() > 0.2 else None,
                        )
                        created += 1
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"    Warning: Could not create special order payment: {e}"))
                    continue
        except Exception:
            pass  # Special orders might not exist

        return created

    def create_class_payments(self, website, clients, count, days_back):
        """Create class bundle payments (deposit, full, installment)"""
        created = 0
        try:
            from class_management.models import ClassBundle, ClassPurchase
            
            # Get or create class bundles
            class_bundles = ClassBundle.objects.filter(website=website, client__in=clients)[:count]
            
            # If no bundles exist, create some
            if not class_bundles.exists():
                for i in range(min(5, count)):
                    try:
                        client = random.choice(list(clients))
                        bundle = ClassBundle.objects.create(
                            website=website,
                            client=client,
                            number_of_classes=random.randint(1, 10),
                            total_price=Decimal(str(random.randint(500, 3000))),
                            price_per_class=Decimal(str(random.randint(100, 300))),
                            level=random.choice(['undergrad', 'grad']),
                            duration=random.choice(['8-10', '12-14', '15-16', '16-18']),
                            status='in_progress',
                        )
                        class_bundles = ClassBundle.objects.filter(id=bundle.id)
                        break
                    except Exception:
                        continue
            
            if not class_bundles.exists():
                return 0

            # Create different types of class payments
            payment_types = ['deposit', 'full', 'installment']
            
            for i in range(count):
                try:
                    bundle = random.choice(list(class_bundles))
                    client = bundle.client
                    days_ago = random.randint(0, days_back)
                    created_at = timezone.now() - timedelta(days=days_ago, hours=random.randint(0, 23))
                    
                    # Determine payment type and amount
                    payment_type_label = random.choice(payment_types)
                    
                    if payment_type_label == 'deposit':
                        # Deposit is typically 20-50% of total
                        amount = bundle.total_price * Decimal(str(random.uniform(0.2, 0.5)))
                    elif payment_type_label == 'full':
                        # Full payment
                        amount = bundle.total_price
                    else:
                        # Installment is typically 10-30% of total
                        amount = bundle.total_price * Decimal(str(random.uniform(0.1, 0.3)))
                    
                    amount = amount.quantize(Decimal('0.01'))
                    ref_id = f'CLS-{payment_type_label[:3].upper()}-{uuid4().hex[:8]}'
                    
                    # Check if payment already exists
                    existing_payment = OrderPayment.objects.filter(
                        website=website,
                        client=client,
                        class_purchase__bundle=bundle,
                        payment_type='class_payment',
                        reference_id=ref_id
                    ).first()
                    
                    if not existing_payment:
                        try:
                            # Create ClassPurchase first (it has UUID primary key, so we create it directly)
                            class_purchase = ClassPurchase(
                                website=website,
                                client=client,
                                bundle=bundle,
                                payment_type=payment_type_label,
                                status='pending',
                                price_locked=amount,
                            )
                            class_purchase.save()
                            
                            # Now create OrderPayment with the class_purchase
                            payment = OrderPayment.objects.create(
                                website=website,
                                client=client,
                                class_purchase=class_purchase,
                                payment_type='class_payment',
                                original_amount=amount,
                                amount=amount,
                                discounted_amount=amount,
                                status=random.choice(['succeeded', 'completed', 'pending']),
                                payment_method=random.choice(['stripe', 'paypal', 'wallet']),
                                reference_id=ref_id,
                                transaction_id=f'txn_{uuid4().hex[:12]}',
                                created_at=created_at,
                                confirmed_at=created_at if random.random() > 0.2 else None,
                            )
                            
                            # Update ClassPurchase with payment info
                            class_purchase.payment_record = payment
                            class_purchase.status = 'paid' if payment.status in ['succeeded', 'completed'] else 'pending'
                            class_purchase.paid_at = payment.confirmed_at
                            class_purchase.save()
                            
                            created += 1
                        except Exception as e:
                            self.stdout.write(self.style.WARNING(f"    Warning: Class payment creation error: {e}"))
                            continue
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"    Warning: Could not create class payment: {e}"))
                    continue
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"    Warning: Class payments error: {e}"))
            pass  # Class purchases might not exist

        return created

    def create_wallet_topups(self, website, clients, count, days_back):
        """Create wallet top-up payments"""
        created = 0

        for i in range(count):
            try:
                client = random.choice(list(clients))
                days_ago = random.randint(0, days_back)
                created_at = timezone.now() - timedelta(days=days_ago, hours=random.randint(0, 23))

                amount = Decimal(str(random.randint(50, 1000)))
                ref_id = f'TOP-{uuid4().hex[:8]}'
                
                existing = OrderPayment.objects.filter(
                    website=website,
                    client=client,
                    payment_type='wallet_loading',
                    reference_id=ref_id
                ).first()
                
                if not existing:
                    payment = OrderPayment.objects.create(
                        website=website,
                        client=client,
                        payment_type='wallet_loading',
                        original_amount=amount,
                        amount=amount,
                        discounted_amount=amount,
                        status=random.choice(['succeeded', 'completed']),
                        payment_method=random.choice(['stripe', 'paypal', 'bank_transfer']),
                        reference_id=ref_id,
                        transaction_id=f'txn_{uuid4().hex[:12]}',
                        created_at=created_at,
                        confirmed_at=created_at,
                    )
                    created += 1
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"    Warning: Could not create wallet top-up: {e}"))
                continue

        return created

    def create_tips(self, website, clients, writers, count, days_back):
        """Create tips"""
        created = 0

        for i in range(count):
            try:
                client = random.choice(list(clients))
                writer = random.choice(list(writers))
                days_ago = random.randint(0, days_back)
                sent_at = timezone.now() - timedelta(days=days_ago, hours=random.randint(0, 23))

                # Get a random order for this client if available
                order = None
                orders = Order.objects.filter(website=website, client=client, assigned_writer=writer)
                if orders.exists():
                    order = random.choice(list(orders))

                tip_type = random.choice(['direct', 'order', 'class'])
                tip_amount = Decimal(str(random.randint(5, 100)))
                writer_percentage = Decimal('85.00')  # Default 85% to writer
                writer_earning = tip_amount * (writer_percentage / 100)
                platform_profit = tip_amount - writer_earning
                
                # Check if tip already exists
                existing = Tip.objects.filter(
                    website=website,
                    client=client,
                    writer=writer,
                    order=order if tip_type == 'order' else None,
                    sent_at__date=sent_at.date()
                ).first()
                
                if not existing:
                    tip = Tip.objects.create(
                        website=website,
                        client=client,
                        writer=writer,
                        order=order if tip_type == 'order' else None,
                        tip_type=tip_type,
                        tip_amount=tip_amount,
                        writer_percentage=writer_percentage,
                        writer_earning=writer_earning,
                        platform_profit=platform_profit,
                        tip_reason=random.choice([
                            'Great work!',
                            'Excellent service',
                            'Fast delivery',
                            'Outstanding quality',
                            'Thank you!',
                            ''
                        ]),
                        sent_at=sent_at,
                    )
                    created += 1
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"    Warning: Could not create tip: {e}"))
                continue

        return created

    def create_bonuses(self, website, writers, count, days_back):
        """Create writer bonuses"""
        created = 0

        for i in range(count):
            try:
                writer = random.choice(list(writers))
                days_ago = random.randint(0, days_back)
                granted_at = timezone.now() - timedelta(days=days_ago, hours=random.randint(0, 23))

                # Get a random special order if available
                special_order = None
                try:
                    special_orders = SpecialOrder.objects.filter(website=website, assigned_writer=writer)
                    if special_orders.exists():
                        special_order = random.choice(list(special_orders))
                except Exception:
                    pass

                # Check if bonus already exists
                existing = WriterBonus.objects.filter(
                    website=website,
                    writer=writer,
                    special_order=special_order,
                    granted_at__date=granted_at.date()
                ).first()
                
                if not existing:
                    bonus = WriterBonus.objects.create(
                        website=website,
                        writer=writer,
                        special_order=special_order,
                        amount=Decimal(str(random.randint(20, 200))),
                        category=random.choice(['performance', 'order_completion', 'client_tip', 'other']),
                        reason=random.choice([
                            'Outstanding performance',
                            'Early completion',
                            'Client appreciation',
                            'Quality work',
                            ''
                        ]),
                        is_paid=random.random() > 0.3,
                        granted_at=granted_at,
                    )
                    created += 1
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"    Warning: Could not create bonus: {e}"))
                continue

        return created

    def create_client_wallet_transactions(self, website, clients, count, days_back):
        """Create client wallet transactions"""
        created = 0

        for i in range(count):
            try:
                client = random.choice(list(clients))
                wallet, _ = ClientWallet.objects.get_or_create(
                    user=client,
                    defaults={'website': website, 'balance': Decimal('0.00')}
                )
                if wallet.website_id != website.id:
                    wallet.website = website
                    wallet.save()

                days_ago = random.randint(0, days_back)
                created_at = timezone.now() - timedelta(days=days_ago, hours=random.randint(0, 23))
                transaction_type = random.choice(['top-up', 'payment', 'refund', 'bonus', 'adjustment'])

                transaction = ClientWalletTransaction.objects.create(
                    wallet=wallet,
                    website=website,
                    amount=Decimal(str(random.randint(10, 500))),
                    transaction_type=transaction_type,
                    description=random.choice(['Wallet top-up', 'Order payment', 'Refund', 'Bonus credit', 'Admin adjustment', '']),
                    created_at=created_at,
                )
                if transaction:
                    created += 1
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"    Warning: Could not create client wallet transaction: {e}"))
                continue

        return created

    def create_writer_wallet_transactions(self, website, writers, count, days_back):
        """Create writer wallet transactions"""
        created = 0

        for i in range(count):
            try:
                writer = random.choice(list(writers))
                writer_wallet = WriterWallet.objects.filter(writer=writer, website=website).first()
                if not writer_wallet:
                    writer_wallet = WriterWallet.objects.create(
                        writer=writer,
                        website=website,
                        balance=Decimal('0.00')
                    )
                if writer_wallet.website_id != website.id:
                    writer_wallet.website = website
                    writer_wallet.save()

                days_ago = random.randint(0, days_back)
                created_at = timezone.now() - timedelta(days=days_ago, hours=random.randint(0, 23), minutes=random.randint(0, 59), seconds=random.randint(0, 59))
                transaction_type = random.choice(['Earning', 'Bonus', 'Reward', 'Adjustment', 'Fine', 'Payout'])

                # Get a random order if available
                order = None
                orders = Order.objects.filter(website=website, assigned_writer=writer)
                if orders.exists() and transaction_type == 'Earning':
                    order = random.choice(list(orders))

                # Generate unique reference code (max 20 chars)
                reference_code = f'TXN-{uuid4().hex[:12]}'
                
                transaction = WriterWalletTransaction.objects.create(
                    writer_wallet=writer_wallet,
                    order=order,
                    website=website,
                    transaction_type=transaction_type,
                    amount=Decimal(str(random.randint(20, 300))),
                    reference_code=reference_code,
                    created_at=created_at,
                )
                if transaction:
                    created += 1
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"    Warning: Could not create writer wallet transaction: {e}"))
                continue

        return created

