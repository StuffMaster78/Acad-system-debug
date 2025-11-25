"""
Management command to seed express classes with sample data.
Creates express classes with various statuses, disciplines, and workloads.
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from decimal import Decimal
from websites.models import Website
from class_management.models import ExpressClass
from users.models import User
from django.utils import timezone
from datetime import timedelta
import random


class Command(BaseCommand):
    help = 'Seed express classes with sample data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--website-id',
            type=int,
            help='Specific website ID to seed (if not provided, seeds all websites)',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing express classes before seeding',
        )
        parser.add_argument(
            '--count',
            type=int,
            default=15,
            help='Number of express classes to create per website (default: 15)',
        )

    def handle(self, *args, **options):
        website_id = options.get('website_id')
        clear = options.get('clear', False)
        count = options.get('count', 15)

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
                self.stdout.write('Clearing existing express classes...')
                ExpressClass.objects.all().delete()
                self.stdout.write(
                    self.style.SUCCESS('Cleared existing data')
                )

            # Get clients and writers
            clients = list(User.objects.filter(role='client', is_active=True)[:10])
            writers = list(User.objects.filter(role='writer', is_active=True)[:5])
            admins = list(User.objects.filter(role__in=['admin', 'superadmin'], is_active=True)[:3])

            if not clients:
                self.stdout.write(
                    self.style.WARNING('No active clients found. Skipping express class creation.')
                )
                return

            # Sample data configurations
            disciplines = [
                'Nursing', 'Mathematics', 'Business Administration', 'Psychology',
                'Computer Science', 'Engineering', 'Biology', 'Chemistry',
                'English Literature', 'History', 'Economics', 'Sociology'
            ]

            institutions = [
                'University of California', 'Harvard University', 'Stanford University',
                'MIT', 'Yale University', 'Princeton University', 'Columbia University',
                'University of Texas', 'State University', 'Community College'
            ]

            courses = [
                'Introduction to Nursing', 'Calculus I', 'Business Ethics',
                'Introduction to Psychology', 'Data Structures', 'Thermodynamics',
                'Cell Biology', 'Organic Chemistry', 'Shakespeare Studies',
                'World History', 'Microeconomics', 'Social Theory'
            ]

            academic_levels = ['Undergraduate', 'Graduate', 'Doctoral']

            status_distribution = [
                (ExpressClass.INQUIRY, 0.20),  # 20% in inquiry
                (ExpressClass.SCOPE_REVIEW, 0.15),  # 15% in scope review
                (ExpressClass.PRICED, 0.15),  # 15% priced
                (ExpressClass.ASSIGNED, 0.20),  # 20% assigned
                (ExpressClass.IN_PROGRESS, 0.25),  # 25% in progress
                (ExpressClass.COMPLETED, 0.05),  # 5% completed
            ]

            total_created = 0

            for website in websites:
                self.stdout.write(f'\nProcessing website: {website.name} (ID: {website.id})')

                for i in range(count):
                    # Select random client
                    client = random.choice(clients) if clients else None
                    if not client:
                        break

                    # Select status based on distribution
                    rand = random.random()
                    cumulative = 0
                    status = ExpressClass.INQUIRY
                    for stat, prob in status_distribution:
                        cumulative += prob
                        if rand <= cumulative:
                            status = stat
                            break

                    # Determine if writer should be assigned
                    writer = None
                    if status in [ExpressClass.ASSIGNED, ExpressClass.IN_PROGRESS, ExpressClass.COMPLETED]:
                        writer = random.choice(writers) if writers else None

                    # Determine if admin should have reviewed
                    reviewed_by = None
                    reviewed_at = None
                    if status in [ExpressClass.SCOPE_REVIEW, ExpressClass.PRICED, ExpressClass.ASSIGNED, ExpressClass.IN_PROGRESS, ExpressClass.COMPLETED]:
                        reviewed_by = random.choice(admins) if admins else None
                        reviewed_at = timezone.now() - timedelta(days=random.randint(1, 30))

                    # Calculate dates
                    start_date = timezone.now().date() + timedelta(days=random.randint(-30, 60))
                    end_date = start_date + timedelta(days=random.randint(30, 120))

                    # Select random discipline and related data
                    discipline = random.choice(disciplines)
                    institution = random.choice(institutions)
                    course = random.choice(courses)
                    academic_level = random.choice(academic_levels)

                    # Generate workload
                    workload_configs = [
                        {'discussions': 5, 'replies': 10, 'assignments': 3, 'exams': 2, 'quizzes': 5, 'projects': 1, 'presentations': 1, 'papers': 2, 'pages': '25-30'},
                        {'discussions': 8, 'replies': 15, 'assignments': 5, 'exams': 3, 'quizzes': 8, 'projects': 2, 'presentations': 2, 'papers': 3, 'pages': '40-50'},
                        {'discussions': 10, 'replies': 20, 'assignments': 6, 'exams': 4, 'quizzes': 10, 'projects': 3, 'presentations': 3, 'papers': 4, 'pages': '60-75'},
                        {'discussions': 12, 'replies': 25, 'assignments': 8, 'exams': 5, 'quizzes': 12, 'projects': 4, 'presentations': 4, 'papers': 5, 'pages': '80-100'},
                    ]
                    workload = random.choice(workload_configs)

                    # Calculate price based on workload and academic level
                    base_price = Decimal('500.00')
                    if academic_level == 'Graduate':
                        base_price = Decimal('750.00')
                    elif academic_level == 'Doctoral':
                        base_price = Decimal('1000.00')
                    
                    # Adjust price based on workload
                    total_items = (
                        workload['discussions'] + workload['assignments'] + 
                        workload['exams'] + workload['quizzes'] + 
                        workload['projects'] + workload['papers']
                    )
                    price = base_price + (Decimal(str(total_items)) * Decimal('50.00'))
                    
                    # Round to nearest 10
                    price = Decimal(str(round(float(price) / 10) * 10))

                    # Determine if price is approved
                    price_approved = status in [ExpressClass.PRICED, ExpressClass.ASSIGNED, ExpressClass.IN_PROGRESS, ExpressClass.COMPLETED]

                    # Determine if completed
                    is_complete = status == ExpressClass.COMPLETED

                    express_class = ExpressClass.objects.create(
                        client=client,
                        website=website,
                        assigned_writer=writer,
                        status=status,
                        start_date=start_date,
                        end_date=end_date,
                        discipline=discipline,
                        institution=institution,
                        course=course,
                        academic_level=academic_level,
                        number_of_discussion_posts=workload['discussions'],
                        number_of_discussion_posts_replies=workload['replies'],
                        number_of_assignments=workload['assignments'],
                        number_of_exams=workload['exams'],
                        number_of_quizzes=workload['quizzes'],
                        number_of_projects=workload['projects'],
                        number_of_presentations=workload['presentations'],
                        number_of_papers=workload['papers'],
                        total_workload_in_pages=workload['pages'],
                        price=price if price_approved else None,
                        price_approved=price_approved,
                        installments_needed=random.choice([0, 0, 0, 2, 3]),  # Mostly full payment, some installments
                        instructions=f'Sample express class for {discipline} course. Please follow all course guidelines and maintain high quality standards.',
                        scope_review_notes=f'Scope reviewed: {workload["pages"]} pages of work expected.' if reviewed_by else '',
                        admin_notes=f'Admin notes for {discipline} express class.' if reviewed_by else '',
                        reviewed_by=reviewed_by,
                        reviewed_at=reviewed_at,
                        is_complete=is_complete,
                    )

                    total_created += 1
                    status_display = dict(ExpressClass.STATUS_CHOICES).get(status, status)
                    self.stdout.write(
                        f'  ✓ Created express class #{express_class.id} | '
                        f'{client.email} | {discipline} | {status_display} | ${price if price_approved else "TBD"}'
                    )

            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✓ Successfully created {total_created} express classes'
                )
            )

