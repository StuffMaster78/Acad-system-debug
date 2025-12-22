"""
Management command to seed message threads with sample data.
Creates threads between various user roles (admin-client, admin-writer, client-writer, etc.)
with realistic messages and timestamps.
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import timedelta
import random

from websites.models import Website
from orders.models import Order
from communications.models import CommunicationThread, CommunicationMessage
from communications.services.thread_service import ThreadService
from communications.services.messages import MessageService

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed message threads with sample data (various role combinations with messages)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--website-id',
            type=int,
            help='Specific website ID to seed (if not provided, seeds all websites)',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing threads before seeding',
        )
        parser.add_argument(
            '--threads',
            type=int,
            default=20,
            help='Number of threads to create per website (default: 20)',
        )
        parser.add_argument(
            '--messages-per-thread',
            type=int,
            default=5,
            help='Number of messages per thread (default: 5)',
        )

    def get_sample_messages(self, sender_role, recipient_role):
        """Return sample messages based on role combination."""
        messages = {
            ('admin', 'client'): [
                "Hello! I wanted to check in on your order. How is everything going?",
                "We've reviewed your requirements and everything looks good. The writer will start working on it soon.",
                "Is there anything specific you'd like us to focus on?",
                "Great! I'm glad to hear that. Let me know if you need any adjustments.",
                "Your order is progressing well. We'll keep you updated.",
            ],
            ('client', 'admin'): [
                "Hi, I have a question about my order.",
                "Could you please clarify the deadline?",
                "Thank you for the update!",
                "I'd like to request a revision on the last draft.",
                "Everything looks perfect, thank you!",
            ],
            ('admin', 'writer'): [
                "Hi! We have a new order that matches your expertise. Would you like to take it?",
                "Please make sure to follow the client's instructions carefully.",
                "Great work on the last order! The client was very satisfied.",
                "Can you provide an update on the current order?",
                "Thank you for your hard work!",
            ],
            ('writer', 'admin'): [
                "I've completed the first draft. Please review it.",
                "I have a question about the requirements.",
                "I need an extension on the deadline. Is that possible?",
                "The order is ready for submission.",
                "Thank you for the feedback. I'll make the revisions.",
            ],
            ('client', 'writer'): [
                "Hello! I wanted to discuss the paper topic.",
                "Could you please clarify this section?",
                "This looks great! Just a few minor changes needed.",
                "Thank you for your excellent work!",
                "I appreciate your attention to detail.",
            ],
            ('writer', 'client'): [
                "Hi! I've started working on your order.",
                "I have a question about the requirements. Could you clarify?",
                "I've completed the first draft. Please review it.",
                "I've made the requested changes. Let me know if you need anything else.",
                "Thank you for choosing our service!",
            ],
            ('support', 'client'): [
                "Hello! I'm here to help with any questions you might have.",
                "I've reviewed your concern and will get back to you shortly.",
                "Is there anything else I can help you with?",
                "I've escalated your issue to the appropriate team.",
                "Thank you for your patience!",
            ],
            ('editor', 'writer'): [
                "I've reviewed your submission. Here are my suggestions.",
                "The quality looks good overall. Just a few minor edits needed.",
                "Please revise the introduction section.",
                "Excellent work! This meets all the requirements.",
                "I've completed the final review. Everything looks great.",
            ],
        }
        
        # Try to get role-specific messages
        key = (sender_role, recipient_role)
        if key in messages:
            return messages[key]
        
        # Fallback to generic messages
        return [
            f"Hello from {sender_role}!",
            "How can I help you today?",
            "I've reviewed your request.",
            "Thank you for your message.",
            "Is there anything else you need?",
        ]

    @transaction.atomic
    def handle(self, *args, **options):
        website_id = options.get('website_id')
        clear_existing = options.get('clear', False)
        threads_count = options.get('threads', 20)
        messages_per_thread = options.get('messages_per_thread', 5)

        # Get websites
        if website_id:
            websites = Website.objects.filter(id=website_id)
        else:
            websites = Website.objects.all()

        if not websites.exists():
            self.stdout.write(self.style.WARNING('No websites found. Please create a website first.'))
            return

        # Clear existing threads if requested
        if clear_existing:
            deleted_count = CommunicationThread.objects.filter(thread_type='order').count()
            CommunicationThread.objects.filter(thread_type='order').delete()
            self.stdout.write(self.style.SUCCESS(f'Cleared {deleted_count} existing threads.'))

        total_threads = 0
        total_messages = 0

        for website in websites:
            self.stdout.write(f'\nSeeding threads for website: {website.name} (ID: {website.id})')

            # Get users by role
            admins = User.objects.filter(website=website, role__in=['admin', 'superadmin'], is_active=True)
            clients = User.objects.filter(website=website, role='client', is_active=True)
            writers = User.objects.filter(website=website, role='writer', is_active=True)
            support_users = User.objects.filter(website=website, role='support', is_active=True)
            editors = User.objects.filter(website=website, role='editor', is_active=True)

            if not admins.exists():
                self.stdout.write(self.style.WARNING(f'  No admin users found for website {website.name}. Skipping.'))
                continue

            # Get orders for this website
            orders = Order.objects.filter(website=website, status__in=['in_progress', 'assigned', 'submitted', 'completed'])

            if not orders.exists():
                self.stdout.write(self.style.WARNING(f'  No orders found for website {website.name}. Skipping.'))
                continue

            # Create threads with various role combinations
            role_combinations = [
                ('admin', 'client'),
                ('client', 'admin'),
                ('admin', 'writer'),
                ('writer', 'admin'),
                ('client', 'writer'),
                ('writer', 'client'),
                ('support', 'client'),
                ('editor', 'writer'),
            ]

            threads_created = 0
            messages_created = 0

            for i in range(threads_count):
                # Select a random order
                order = random.choice(list(orders))

                # Select a role combination
                sender_role, recipient_role = random.choice(role_combinations)

                # Get users for these roles
                if sender_role in ['admin', 'superadmin']:
                    sender = random.choice(list(admins)) if admins.exists() else None
                elif sender_role == 'client':
                    sender = order.client if order.client else (random.choice(list(clients)) if clients.exists() else None)
                elif sender_role == 'writer':
                    sender = order.assigned_writer if order.assigned_writer else (random.choice(list(writers)) if writers.exists() else None)
                elif sender_role == 'support':
                    sender = random.choice(list(support_users)) if support_users.exists() else None
                elif sender_role == 'editor':
                    sender = random.choice(list(editors)) if editors.exists() else None
                else:
                    sender = None

                if not sender:
                    continue

                # Get recipient
                if recipient_role in ['admin', 'superadmin']:
                    recipient = random.choice(list(admins)) if admins.exists() else None
                elif recipient_role == 'client':
                    recipient = order.client if order.client else (random.choice(list(clients)) if clients.exists() else None)
                elif recipient_role == 'writer':
                    recipient = order.assigned_writer if order.assigned_writer else (random.choice(list(writers)) if writers.exists() else None)
                elif recipient_role == 'support':
                    recipient = random.choice(list(support_users)) if support_users.exists() else None
                elif recipient_role == 'editor':
                    recipient = random.choice(list(editors)) if editors.exists() else None
                else:
                    recipient = None

                if not recipient or recipient == sender:
                    continue

                # Check if thread already exists for this order with these exact participants
                existing_threads = CommunicationThread.objects.filter(order=order)
                thread = None
                for t in existing_threads:
                    participants = set(t.participants.all())
                    if participants == {sender, recipient}:
                        thread = t
                        break

                if not thread:
                    # Create thread
                    try:
                        thread = ThreadService.create_thread(
                            order=order,
                            created_by=sender,
                            participants=[sender, recipient],
                            thread_type="order",
                            website=website
                        )
                        threads_created += 1
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f'  Failed to create thread: {str(e)}'))
                        continue

                # Add messages to the thread
                sample_messages = self.get_sample_messages(sender_role, recipient_role)
                base_time = timezone.now() - timedelta(days=random.randint(1, 30))

                for msg_idx in range(messages_per_thread):
                    # Alternate between sender and recipient
                    if msg_idx % 2 == 0:
                        msg_sender = sender
                        msg_recipient = recipient
                        msg_sender_role = sender_role
                    else:
                        msg_sender = recipient
                        msg_recipient = sender
                        msg_sender_role = recipient_role

                    # Get message text
                    message_text = random.choice(sample_messages)

                    # Calculate timestamp (spread messages over time)
                    message_time = base_time + timedelta(
                        hours=random.randint(0, 24 * (msg_idx + 1)),
                        minutes=random.randint(0, 59)
                    )

                    # Create message
                    try:
                        message = MessageService.create_message(
                            thread=thread,
                            sender=msg_sender,
                            recipient=msg_recipient,
                            sender_role=msg_sender_role,
                            message=message_text,
                            message_type="text"
                        )
                        
                        # Update sent_at timestamp manually (bypass auto_now_add)
                        # Use direct database update to set custom timestamp
                        from django.db import connection
                        with connection.cursor() as cursor:
                            cursor.execute(
                                "UPDATE communications_communicationmessage SET sent_at = %s WHERE id = %s",
                                [message_time, message.id]
                            )
                        
                        messages_created += 1
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f'  Failed to create message: {str(e)}'))
                        continue

            total_threads += threads_created
            total_messages += messages_created

            self.stdout.write(
                self.style.SUCCESS(
                    f'  Created {threads_created} threads and {messages_created} messages for {website.name}'
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Successfully seeded {total_threads} threads with {total_messages} messages total!'
            )
        )

