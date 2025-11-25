"""
Management command to seed invoices with sample data.
Creates invoices with various statuses, purposes, and optional references.
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from decimal import Decimal
from websites.models import Website
from order_payments_management.models import Invoice
from order_payments_management.services.invoice_service import InvoiceService
from orders.models import Order
from special_orders.models import SpecialOrder
from users.models import User
from django.utils import timezone
from datetime import timedelta
import random


class Command(BaseCommand):
    help = 'Seed invoices with sample data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--website-id',
            type=int,
            help='Specific website ID to seed (if not provided, seeds all websites)',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing invoices before seeding',
        )
        parser.add_argument(
            '--count',
            type=int,
            default=20,
            help='Number of invoices to create per website (default: 20)',
        )

    def handle(self, *args, **options):
        website_id = options.get('website_id')
        clear = options.get('clear', False)
        count = options.get('count', 20)

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

        with transaction.atomic():
            if clear:
                self.stdout.write('Clearing existing invoices...')
                Invoice.objects.all().delete()
                self.stdout.write(
                    self.style.SUCCESS('Cleared existing data')
                )

            # Get clients and admins
            clients = list(User.objects.filter(role='client', is_active=True)[:30])
            admins = list(User.objects.filter(role__in=['admin', 'superadmin'], is_active=True)[:5])

            if not clients:
                self.stdout.write(
                    self.style.WARNING('No active clients found. Skipping invoice creation.')
                )
                return

            if not admins:
                self.stdout.write(
                    self.style.WARNING('No admins found. Creating invoices without issuer.')
                )

            # Sample invoice titles and purposes
            invoice_titles = [
                "Order Payment Invoice",
                "Class Bundle Payment",
                "Special Order Payment",
                "Outstanding Balance",
                "Service Payment",
                "Additional Services",
                "Revision Payment",
                "Express Service Fee",
                "Premium Service Charge",
                "Account Balance",
            ]

            invoice_purposes = [
                "Order Payment",
                "Class Purchase",
                "Special Order",
                "Service Fee",
                "Additional Services",
                "Revision",
                "Express Service",
                "Premium Service",
                "Account Balance",
                "Miscellaneous",
            ]

            invoice_descriptions = [
                "Payment for completed order. Please review and pay by the due date.",
                "Invoice for class bundle purchase. Thank you for your business.",
                "Payment request for special order services.",
                "Outstanding balance on your account. Please settle at your earliest convenience.",
                "Service fee for additional services rendered.",
                "Payment for order revisions and modifications.",
                "Express service fee for expedited processing.",
                "Premium service charge for enhanced features.",
                "Account balance payment request.",
                "Miscellaneous charges and fees.",
            ]

            # Invoice amount ranges
            amount_ranges = [
                (Decimal('50.00'), Decimal('200.00')),   # Small invoices
                (Decimal('200.00'), Decimal('500.00')), # Medium invoices
                (Decimal('500.00'), Decimal('1000.00')), # Large invoices
                (Decimal('1000.00'), Decimal('2500.00')), # Very large invoices
            ]

            total_created = 0
            total_paid = 0
            total_unpaid = 0
            total_overdue = 0

            for website in websites:
                self.stdout.write(f'\nProcessing website: {website.name} (ID: {website.id})')

                # Get website-specific data
                website_clients = [c for c in clients if c.website_id == website.id]
                if not website_clients:
                    self.stdout.write(
                        f'  ⚠ No clients found for {website.name}. Skipping.'
                    )
                    continue

                # Get orders for this website
                orders = Order.objects.filter(
                    website=website,
                    is_paid=False
                )[:count]

                # Get special orders for this website
                special_orders = SpecialOrder.objects.filter(
                    website=website,
                    status__in=['inquiry', 'scope_review', 'priced', 'assigned', 'in_progress']
                )[:count]

                # Get an admin for this website (or use first available)
                issuer = None
                if admins:
                    issuer = random.choice(admins)

                for i in range(count):
                    try:
                        # Select random client
                        client = random.choice(website_clients)

                        # Select invoice details
                        title = random.choice(invoice_titles)
                        purpose = random.choice(invoice_purposes)
                        description = random.choice(invoice_descriptions)

                        # Select amount
                        amount_range = random.choice(amount_ranges)
                        amount = Decimal(str(random.uniform(float(amount_range[0]), float(amount_range[1]))))
                        amount = amount.quantize(Decimal('0.01'))

                        # Determine due date and payment status
                        # 60% paid, 30% unpaid, 10% overdue
                        rand = random.random()
                        if rand < 0.60:  # Paid
                            is_paid = True
                            due_date = timezone.now().date() - timedelta(days=random.randint(1, 30))
                            paid_at = due_date + timedelta(days=random.randint(0, 5))
                        elif rand < 0.90:  # Unpaid (not yet due)
                            is_paid = False
                            due_date = timezone.now().date() + timedelta(days=random.randint(1, 30))
                            paid_at = None
                        else:  # Overdue
                            is_paid = False
                            due_date = timezone.now().date() - timedelta(days=random.randint(1, 30))
                            paid_at = None

                        # Determine if invoice should reference an order or special order
                        order = None
                        special_order = None
                        order_number = ""

                        if random.random() < 0.40 and orders.exists():  # 40% linked to orders
                            order = random.choice(orders)
                            order_number = f"ORD-{order.id}"
                            purpose = "Order Payment"
                            description = f"Payment for Order #{order.id}. Please review and pay by the due date."
                        elif random.random() < 0.20 and special_orders.exists():  # 20% linked to special orders
                            special_order = random.choice(special_orders)
                            order_number = f"SO-{special_order.id}"
                            purpose = "Special Order Payment"
                            description = f"Payment for Special Order #{special_order.id}. Please review and pay by the due date."

                        # Create invoice using InvoiceService
                        invoice = InvoiceService.create_invoice(
                            recipient_email=client.email,
                            website=website,
                            amount=amount,
                            title=title,
                            due_date=due_date,
                            issued_by=issuer,
                            recipient_name=client.get_full_name() or client.username,
                            purpose=purpose,
                            description=description,
                            order_number=order_number,
                            client=client,
                            order=order,
                            special_order=special_order,
                            send_email=False,  # Don't send emails during seeding
                            token_expires_in_days=30
                        )

                        # Set payment status
                        if is_paid:
                            invoice.is_paid = True
                            invoice.paid_at = timezone.make_aware(
                                timezone.datetime.combine(paid_at, timezone.datetime.min.time())
                            )
                            invoice.email_sent = True
                            invoice.email_sent_at = invoice.created_at
                            invoice.email_sent_count = 1
                        else:
                            invoice.is_paid = False
                            invoice.email_sent = random.choice([True, True, False])  # 66% sent
                            if invoice.email_sent:
                                invoice.email_sent_at = invoice.created_at - timedelta(days=random.randint(1, 5))
                                invoice.email_sent_count = random.randint(1, 3)

                        invoice.save()

                        total_created += 1
                        if is_paid:
                            total_paid += 1
                        elif due_date < timezone.now().date():
                            total_overdue += 1
                        else:
                            total_unpaid += 1

                        status = "Paid" if is_paid else ("Overdue" if due_date < timezone.now().date() else "Unpaid")
                        entity_info = ""
                        if order:
                            entity_info = f" | Order #{order.id}"
                        elif special_order:
                            entity_info = f" | Special Order #{special_order.id}"

                        self.stdout.write(
                            f'  ✓ Created invoice #{invoice.reference_id} | '
                            f'{client.email} | ${amount} | {status} | Due: {due_date}{entity_info}'
                        )

                    except Exception as e:
                        self.stdout.write(
                            self.style.WARNING(
                                f'  ⚠ Failed to create invoice: {str(e)}'
                            )
                        )
                        continue

            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✓ Successfully created:\n'
                    f'  - {total_created} total invoices\n'
                    f'  - {total_paid} paid invoices\n'
                    f'  - {total_unpaid} unpaid invoices\n'
                    f'  - {total_overdue} overdue invoices'
                )
            )

