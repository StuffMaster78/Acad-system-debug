"""
Management command to seed announcements with example data.
Creates various announcements with different categories, statuses, and features.
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from notifications_system.models.broadcast_notification import BroadcastNotification
from announcements.models import Announcement
from websites.models import Website
from users.models import User
import random


class Command(BaseCommand):
    help = 'Seed announcements with example data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--website-id',
            type=int,
            help='Specific website ID to seed (if not provided, seeds all websites)',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing announcements before seeding',
        )
        parser.add_argument(
            '--count',
            type=int,
            default=10,
            help='Number of announcements to create per website (default: 10)',
        )

    def handle(self, *args, **options):
        website_id = options.get('website_id')
        clear = options.get('clear', False)
        count = options.get('count', 10)

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

        # Get a superadmin user for created_by
        admin_user = User.objects.filter(role='superadmin').first()
        if not admin_user:
            admin_user = User.objects.filter(is_staff=True).first()
        if not admin_user:
            admin_user = User.objects.first()

        with transaction.atomic():
            if clear:
                self.stdout.write('Clearing existing announcements...')
                Announcement.objects.all().delete()
                BroadcastNotification.objects.filter(
                    event_type='broadcast.system_announcement'
                ).delete()
                self.stdout.write(
                    self.style.SUCCESS('Cleared existing announcements')
                )

            # Sample announcement data
            announcements_data = [
                {
                    'title': 'Welcome to Our New Announcements Center! 🎉',
                    'message': '''<p>We're excited to introduce our new Announcements Center! This feature allows you to stay updated with the latest news, system updates, and important information.</p>
                    <p>You can now:</p>
                    <ul>
                        <li>View all system announcements in one place</li>
                        <li>Get notified about important updates</li>
                        <li>Track your engagement with announcements</li>
                    </ul>
                    <p>Make sure to check back regularly for updates!</p>''',
                    'category': 'news',
                    'pinned': True,
                    'target_roles': ['client', 'admin', 'superadmin', 'writer', 'editor', 'support'],
                    'channels': ['in_app', 'email'],
                    'show_to_all': True,  # General announcement for everyone
                },
                {
                    'title': 'System Maintenance Scheduled for This Weekend',
                    'message': '''<p>We will be performing scheduled maintenance on our systems this weekend to improve performance and security.</p>
                    <p><strong>Maintenance Window:</strong> Saturday, 2:00 AM - 6:00 AM EST</p>
                    <p>During this time, you may experience brief interruptions in service. We apologize for any inconvenience and appreciate your patience.</p>
                    <p>All services will be fully operational after the maintenance window.</p>''',
                    'category': 'maintenance',
                    'pinned': True,
                    'target_roles': ['client', 'admin', 'superadmin', 'writer', 'editor', 'support'],
                    'channels': ['in_app', 'email'],
                    'scheduled_for': timezone.now() + timedelta(days=2),
                },
                {
                    'title': 'New Feature: Enhanced Order Tracking',
                    'message': '''<p>We've launched an enhanced order tracking system that provides real-time updates on your orders.</p>
                    <p><strong>New Features:</strong></p>
                    <ul>
                        <li>Real-time status updates</li>
                        <li>Estimated completion times</li>
                        <li>Direct communication with writers</li>
                    </ul>
                    <p>Check out the new tracking features in your dashboard!</p>''',
                    'category': 'update',
                    'pinned': False,
                    'target_roles': ['client'],  # Client-only feature
                    'channels': ['in_app'],
                    'show_to_all': False,
                },
                {
                    'title': 'Special Promotion: 20% Off Your Next Order',
                    'message': '''<p>🎁 Limited Time Offer!</p>
                    <p>Get <strong>20% off</strong> your next order when you use the promo code: <code>SAVE20</code></p>
                    <p>This offer is valid until the end of the month. Don't miss out!</p>
                    <p><a href="/orders">Place your order now</a></p>''',
                    'category': 'promotion',
                    'pinned': False,
                    'target_roles': ['client'],  # Client-only promotion
                    'channels': ['in_app', 'email'],
                    'expires_at': timezone.now() + timedelta(days=30),
                    'show_to_all': False,
                },
                {
                    'title': 'Writer Performance Dashboard Now Available',
                    'message': '''<p>Writers can now access a comprehensive performance dashboard to track their metrics and improve their work.</p>
                    <p>The dashboard includes:</p>
                    <ul>
                        <li>Order completion statistics</li>
                        <li>Average ratings and reviews</li>
                        <li>Earnings overview</li>
                        <li>Performance trends</li>
                    </ul>
                    <p>Visit your dashboard to explore these new features!</p>''',
                    'category': 'update',
                    'pinned': False,
                    'target_roles': ['writer'],  # Writer-only feature
                    'channels': ['in_app'],
                    'show_to_all': False,
                },
                {
                    'title': 'Security Update: Two-Factor Authentication Recommended',
                    'message': '''<p>To enhance the security of your account, we strongly recommend enabling two-factor authentication (2FA).</p>
                    <p>2FA adds an extra layer of security by requiring a second verification step when logging in.</p>
                    <p>You can enable 2FA in your account settings under Security.</p>
                    <p>Stay safe and secure!</p>''',
                    'category': 'update',
                    'pinned': False,
                    'target_roles': ['client', 'admin', 'superadmin', 'writer', 'editor', 'support'],
                    'channels': ['in_app', 'email'],
                    'require_acknowledgement': True,
                },
                {
                    'title': 'Holiday Schedule: Office Hours Adjustment',
                    'message': '''<p>Please note that our support team will have adjusted hours during the upcoming holiday season.</p>
                    <p><strong>Holiday Schedule:</strong></p>
                    <ul>
                        <li>December 24-25: Limited support</li>
                        <li>December 31 - January 1: Limited support</li>
                    </ul>
                    <p>Regular support hours will resume after the holidays. Thank you for your understanding!</p>''',
                    'category': 'general',
                    'pinned': False,
                    'target_roles': ['client', 'admin', 'superadmin', 'writer', 'editor', 'support'],
                    'channels': ['in_app'],
                },
                {
                    'title': 'New Payment Methods Available',
                    'message': '''<p>We've added new payment methods to make transactions easier and more convenient.</p>
                    <p>You can now pay using:</p>
                    <ul>
                        <li>Credit/Debit Cards</li>
                        <li>PayPal</li>
                        <li>Bank Transfer</li>
                        <li>Cryptocurrency (Bitcoin, Ethereum)</li>
                    </ul>
                    <p>Check out the payment options in your account settings!</p>''',
                    'category': 'update',
                    'pinned': False,
                    'target_roles': ['client'],  # Client-only feature
                    'channels': ['in_app', 'email'],
                    'show_to_all': False,
                },
                {
                    'title': 'Editor Training Program Now Open',
                    'message': '''<p>We're launching a comprehensive training program for new and existing editors.</p>
                    <p>The program covers:</p>
                    <ul>
                        <li>Quality assurance best practices</li>
                        <li>Communication guidelines</li>
                        <li>Platform features and tools</li>
                        <li>Performance optimization</li>
                    </ul>
                    <p>Interested editors should contact the admin team to enroll.</p>''',
                    'category': 'news',
                    'pinned': False,
                    'target_roles': ['editor'],
                    'channels': ['in_app'],
                },
                {
                    'title': 'System Performance Improvements',
                    'message': '''<p>We've made significant improvements to our system performance and reliability.</p>
                    <p><strong>Improvements include:</strong></p>
                    <ul>
                        <li>Faster page load times</li>
                        <li>Improved search functionality</li>
                        <li>Enhanced mobile experience</li>
                        <li>Better error handling</li>
                    </ul>
                    <p>You should notice a smoother experience across all features!</p>''',
                    'category': 'update',
                    'pinned': False,
                    'target_roles': ['client', 'admin', 'superadmin', 'writer', 'editor', 'support'],
                    'channels': ['in_app'],
                },
            ]

            total_created = 0

            for website in websites:
                self.stdout.write(f'Seeding announcements for website: {website.name}')

                # Create Happy New Year announcement with discount code
                self.stdout.write('Creating Happy New Year announcement with discount code...')
                try:
                    from discounts.models import Discount
                    from discounts.services.discount_generator import DiscountCodeGenerator
                    
                    # Check if New Year announcement already exists
                    existing_broadcast = BroadcastNotification.objects.filter(
                        website=website,
                        title='🎉 Happy New Year 2026 - Special 25% Discount!',
                        event_type='broadcast.system_announcement'
                    ).first()
                    
                    if existing_broadcast:
                        self.stdout.write(
                            self.style.WARNING(f'  ⚠ New Year announcement already exists, skipping...')
                        )
                    else:
                        # Generate a unique discount code
                        discount_code = DiscountCodeGenerator.generate_unique_code(prefix='NY2026', length=8)
                        
                        # Create discount code valid for 30 days
                        start_date = timezone.now()
                        end_date = start_date + timedelta(days=30)
                        
                        discount, discount_created = Discount.objects.get_or_create(
                            discount_code=discount_code,
                            website=website,
                            defaults={
                                'discount_type': 'percent',
                                'discount_value': 25,  # 25% off
                                'start_date': start_date,
                                'end_date': end_date,
                                'is_active': True,
                                'origin_type': 'promo',
                                'description': 'Happy New Year 2026 - 25% off all orders',
                                'is_general': True,  # Available to all clients
                            }
                        )
                        
                        if discount_created:
                            self.stdout.write(f'  ✓ Created discount code: {discount_code}')
                        else:
                            discount_code = discount.discount_code
                            self.stdout.write(f'  ℹ Using existing discount code: {discount_code}')
                        
                        # Create New Year announcement
                        new_year_message = f'''<div style="text-align: center; padding: 20px;">
                            <h2 style="color: #FF6B35; font-size: 2em; margin-bottom: 20px;">🎉 Happy New Year 2026! 🎉</h2>
                            <p style="font-size: 1.2em; margin-bottom: 20px;">Start the new year with amazing savings!</p>
                            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px; color: white; margin: 20px 0;">
                                <h3 style="font-size: 1.8em; margin-bottom: 15px;">🎁 Special New Year Offer</h3>
                                <p style="font-size: 1.5em; font-weight: bold; margin-bottom: 10px;">25% OFF</p>
                                <p style="font-size: 1.1em; margin-bottom: 20px;">Use code: <code style="background: rgba(255,255,255,0.3); padding: 8px 15px; border-radius: 5px; font-size: 1.3em; font-weight: bold;">{discount_code}</code></p>
                                <p style="font-size: 1em; opacity: 0.9;">Valid for the next 30 days</p>
                            </div>
                            <p style="margin-top: 20px; font-size: 1.1em;">Don't miss out on this limited-time offer! Apply the discount code at checkout.</p>
                            <p style="margin-top: 10px;"><a href="/orders" style="background: #FF6B35; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">Place Your Order Now →</a></p>
                        </div>'''
                        
                        new_year_broadcast, broadcast_created = BroadcastNotification.objects.get_or_create(
                            event_type='broadcast.system_announcement',
                            title='🎉 Happy New Year 2026 - Special 25% Discount!',
                            website=website,
                            defaults={
                                'message': new_year_message,
                                'target_roles': ['client'],  # Client-only promotion (discount codes are for clients)
                                'channels': ['in_app', 'email'],
                                'pinned': True,  # Pin this important announcement
                                'is_active': True,
                                'show_to_all': False,  # Not for all roles
                                'require_acknowledgement': False,
                                'expires_at': end_date,  # Expires when discount expires
                                'created_by': admin_user,
                                'sent_at': timezone.now(),
                            }
                        )
                        
                        if broadcast_created:
                            new_year_announcement, ann_created = Announcement.objects.get_or_create(
                                broadcast=new_year_broadcast,
                                defaults={
                                    'category': 'promotion',
                                    'read_more_url': '/orders',
                                }
                            )
                            
                            if ann_created:
                                total_created += 1
                                self.stdout.write(
                                    self.style.SUCCESS(f'  ✓ Created: {new_year_announcement.broadcast.title} with discount code {discount_code}')
                                )
                            else:
                                total_created += 1
                                self.stdout.write(
                                    self.style.SUCCESS(f'  ✓ Updated: {new_year_announcement.broadcast.title} with discount code {discount_code}')
                                )
                        else:
                            self.stdout.write(
                                self.style.WARNING(f'  ⚠ New Year broadcast already exists')
                            )
                            
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'  ✗ Failed to create New Year announcement: {e}')
                    )
                    import traceback
                    traceback.print_exc()

                # Create other announcements
                for i, ann_data in enumerate(announcements_data[:count]):
                    # Randomize some fields for variety
                    is_pinned = ann_data.get('pinned', False) and i < 2  # Pin first 2
                    is_active = True  # Make all seeded announcements active
                    
                    # Check if broadcast already exists to avoid duplicates
                    broadcast, broadcast_created = BroadcastNotification.objects.get_or_create(
                        event_type='broadcast.system_announcement',
                        title=ann_data['title'],
                        website=website,
                        defaults={
                            'message': ann_data['message'],
                            'target_roles': ann_data.get('target_roles', []),
                            'show_to_all': ann_data.get('show_to_all', False),  # Explicitly set show_to_all
                            'channels': ann_data.get('channels', ['in_app']),
                            'pinned': is_pinned,
                            'is_active': is_active,
                            'require_acknowledgement': ann_data.get('require_acknowledgement', False),
                            'scheduled_for': ann_data.get('scheduled_for'),
                            'expires_at': ann_data.get('expires_at'),
                            'created_by': admin_user,
                            'sent_at': timezone.now() if not ann_data.get('scheduled_for') else None,
                        }
                    )
                    
                    # Update existing broadcasts to ensure show_to_all is set correctly
                    if not broadcast_created:
                        # Only update if show_to_all needs to be set
                        if ann_data.get('show_to_all') is not None and broadcast.show_to_all != ann_data.get('show_to_all'):
                            broadcast.show_to_all = ann_data.get('show_to_all', False)
                            broadcast.save(update_fields=['show_to_all'])
                    
                    if not broadcast_created:
                        # Update existing broadcast to ensure it's active
                        broadcast.is_active = is_active
                        broadcast.pinned = is_pinned
                        broadcast.save(update_fields=['is_active', 'pinned'])

                    # The signal should automatically create the Announcement
                    # But let's ensure it exists
                    announcement, created = Announcement.objects.get_or_create(
                        broadcast=broadcast,
                        defaults={
                            'category': ann_data.get('category', 'general'),
                            'read_more_url': ann_data.get('read_more_url'),
                        }
                    )

                    if created:
                        total_created += 1
                        self.stdout.write(
                            f'  ✓ Created: {announcement.broadcast.title}'
                        )
                    else:
                        # Update if it already exists
                        announcement.category = ann_data.get('category', 'general')
                        announcement.save()
                        total_created += 1
                        self.stdout.write(
                            f'  ✓ Updated: {announcement.broadcast.title}'
                        )

            self.stdout.write(
                self.style.SUCCESS(
                    f'\nSuccessfully seeded {total_created} announcement(s) across {websites.count()} website(s)'
                )
            )

