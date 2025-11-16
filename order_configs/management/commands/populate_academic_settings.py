"""
Django management command to populate academic settings.
Usage: python manage.py populate_academic_settings [website_domain]
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from websites.models import Website
from order_configs.models import (
    PaperType, FormattingandCitationStyle, Subject, AcademicLevel,
    TypeOfWork, EnglishType
)
from pricing_configs.models import PricingConfiguration, AcademicLevelPricing
from decimal import Decimal


class Command(BaseCommand):
    help = 'Populate academic settings (paper types, formatting styles, subjects, etc.)'

    def add_arguments(self, parser):
        parser.add_argument(
            'website_domain',
            nargs='?',
            type=str,
            help='Website domain to populate settings for (optional, uses first website if not provided)'
        )

    def handle(self, *args, **options):
        website_domain = options.get('website_domain')
        
        # Get or create website
        if website_domain:
            website = Website.objects.filter(domain=website_domain).first()
            if not website:
                self.stdout.write(self.style.ERROR(f'Website with domain "{website_domain}" not found.'))
                self.stdout.write('Available websites:')
                for w in Website.objects.all():
                    self.stdout.write(f'  - {w.domain} ({w.name})')
                return
        else:
            website = Website.objects.first()
            if not website:
                website = Website.objects.create(
                    domain="localhost",
                    name='Academic Writing Service',
                    slug='academic',
                    is_active=True
                )
                self.stdout.write(self.style.SUCCESS(f'Created website: {website.name}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Using existing website: {website.name}'))
        
        # Paper Types
        paper_types = [
            'Essay', 'Research Paper', 'Term Paper', 'Dissertation', 'Thesis',
            'Case Study', 'Article Review', 'Book Report', 'Literature Review',
            'Annotated Bibliography', 'Coursework', 'Lab Report', 'Presentation',
            'PowerPoint Presentation', 'Speech', 'Article', 'Report',
            'Reflection Paper', 'Position Paper', 'Argumentative Essay',
            'Narrative Essay', 'Descriptive Essay', 'Expository Essay',
            'Compare and Contrast Essay', 'Cause and Effect Essay',
            'Admission Essay', 'Scholarship Essay', 'Creative Writing', 'Poem',
            'Proposal', 'Research Proposal', 'Capstone Project', 'Discussion Post',
            'Response Paper', 'Summary', 'Outline', 'Q&A', 'Worksheet',
            'Math Problem', 'Statistics Problem', 'Programming Assignment',
            'Code Review', 'Technical Writing', 'Business Plan', 'Marketing Plan',
            'Financial Analysis',
        ]
        
        self.stdout.write('\n' + '='*70)
        self.stdout.write('POPULATING PAPER TYPES')
        self.stdout.write('='*70)
        for paper_type_name in paper_types:
            paper_type, created = PaperType.objects.get_or_create(
                name=paper_type_name,
                website=website,
                defaults={}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✅ Created paper type: {paper_type_name}'))
        
        # Formatting Styles
        formatting_styles = [
            'APA', 'MLA', 'Chicago', 'Turabian', 'Harvard', 'IEEE', 'Vancouver',
            'CSE', 'ACS', 'AMA', 'ASA', 'OSCOLA', 'Bluebook', 'AGLC', 'Oxford',
            'MHRA', 'Bluebook Legal', 'Chicago/Turabian', 'IEEE', 'CSE/CBE',
            'NLM', 'ACS', 'AIP', 'APS', 'GSA', 'APA 6th Edition',
            'APA 7th Edition', 'MLA 8th Edition', 'MLA 9th Edition',
            'Chicago 16th Edition', 'Chicago 17th Edition',
        ]
        
        self.stdout.write('\n' + '='*70)
        self.stdout.write('POPULATING FORMATTING STYLES')
        self.stdout.write('='*70)
        for style_name in formatting_styles:
            style, created = FormattingandCitationStyle.objects.get_or_create(
                name=style_name,
                website=website,
                defaults={}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✅ Created formatting style: {style_name}'))
        
        # Academic Levels
        academic_levels = [
            'High School', 'College', 'Undergraduate', 'Bachelor\'s', 'Master\'s',
            'Graduate', 'PhD', 'Doctorate', 'Post-Doctorate', 'Professional',
            'Certificate Program', 'Diploma', 'Associate Degree', 'BSN', 'DNP',
            'MBA', 'JD', 'MD', 'DDS', 'DVM', 'EdD', 'PsyD',
        ]
        
        self.stdout.write('\n' + '='*70)
        self.stdout.write('POPULATING ACADEMIC LEVELS')
        self.stdout.write('='*70)
        for level_name in academic_levels:
            level, created = AcademicLevel.objects.get_or_create(
                name=level_name,
                website=website,
                defaults={}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✅ Created academic level: {level_name}'))
        
        # Subjects (with technical flag)
        subjects_data = [
            # Humanities
            ('English', False), ('Literature', False), ('History', False),
            ('Philosophy', False), ('Religion', False), ('Art', False),
            ('Music', False), ('Theater', False), ('Film Studies', False),
            ('Linguistics', False), ('Languages', False), ('Spanish', False),
            ('French', False), ('German', False), ('Chinese', False), ('Japanese', False),
            
            # Social Sciences
            ('Psychology', False), ('Sociology', False), ('Anthropology', False),
            ('Political Science', False), ('Economics', False), ('Geography', False),
            ('Criminal Justice', False), ('Law', False), ('Criminology', False),
            ('Social Work', False), ('Public Administration', False),
            ('International Relations', False), ('Urban Studies', False),
            ('Gender Studies', False), ('Ethnic Studies', False),
            
            # Sciences (Technical)
            ('Biology', True), ('Chemistry', True), ('Physics', True),
            ('Mathematics', True), ('Statistics', True), ('Computer Science', True),
            ('Information Technology', True), ('Engineering', True),
            ('Mechanical Engineering', True), ('Electrical Engineering', True),
            ('Civil Engineering', True), ('Chemical Engineering', True),
            ('Biomedical Engineering', True), ('Environmental Science', True),
            ('Geology', True), ('Astronomy', True), ('Meteorology', True),
            ('Botany', True), ('Zoology', True), ('Microbiology', True),
            ('Genetics', True), ('Neuroscience', True), ('Astrophysics', True),
            ('Biochemistry', True), ('Organic Chemistry', True),
            ('Inorganic Chemistry', True), ('Physical Chemistry', True),
            ('Quantum Physics', True),
            
            # Health Sciences
            ('Nursing', False), ('Medicine', True), ('Public Health', False),
            ('Healthcare', False), ('Health Administration', False),
            ('Pharmacy', True), ('Physical Therapy', False),
            ('Occupational Therapy', False), ('Nutrition', False),
            ('Dietetics', False), ('Kinesiology', False),
            ('Exercise Science', False), ('Sports Medicine', False),
            ('Veterinary Medicine', True), ('Dentistry', True),
            ('Optometry', True), ('Radiology', True),
            ('Medical Laboratory Science', True), ('Respiratory Therapy', False),
            
            # Business
            ('Business', False), ('Management', False), ('Marketing', False),
            ('Finance', False), ('Accounting', False), ('Economics', False),
            ('Entrepreneurship', False), ('Human Resources', False),
            ('Operations Management', False), ('Supply Chain Management', False),
            ('Project Management', False), ('Business Administration', False),
            ('International Business', False), ('Real Estate', False),
            ('Hospitality Management', False), ('Tourism', False),
            
            # Education
            ('Education', False), ('Teaching', False),
            ('Curriculum Development', False), ('Educational Technology', False),
            ('Special Education', False), ('Early Childhood Education', False),
            ('Elementary Education', False), ('Secondary Education', False),
            ('Higher Education', False), ('Educational Leadership', False),
            ('Educational Psychology', False),
            
            # Technology (Technical)
            ('Information Systems', True), ('Cybersecurity', True),
            ('Data Science', True), ('Artificial Intelligence', True),
            ('Machine Learning', True), ('Software Engineering', True),
            ('Web Development', True), ('Database Management', True),
            ('Network Administration', True), ('Cloud Computing', True),
            ('Mobile Development', True), ('Game Development', True),
            
            # Communications
            ('Communications', False), ('Journalism', False),
            ('Public Relations', False), ('Media Studies', False),
            ('Advertising', False), ('Marketing Communications', False),
            ('Digital Media', False), ('Broadcasting', False),
            
            # Other
            ('Environmental Studies', False), ('Sustainability', False),
            ('Agriculture', False), ('Architecture', False),
            ('Urban Planning', False), ('Aviation', False),
            ('Maritime Studies', False), ('Military Science', False),
            ('Security Studies', False),
        ]
        
        self.stdout.write('\n' + '='*70)
        self.stdout.write('POPULATING SUBJECTS')
        self.stdout.write('='*70)
        for subject_name, is_technical in subjects_data:
            subject, created = Subject.objects.get_or_create(
                name=subject_name,
                website=website,
                defaults={'is_technical': is_technical}
            )
            if created:
                tech_label = ' (Technical)' if is_technical else ''
                self.stdout.write(self.style.SUCCESS(f'✅ Created subject: {subject_name}{tech_label}'))
            elif subject.is_technical != is_technical:
                subject.is_technical = is_technical
                subject.save()
                self.stdout.write(self.style.WARNING(f'⚠️  Updated subject: {subject_name} (Technical: {is_technical})'))
        
        # Types of Work
        types_of_work = [
            'Writing', 'Editing', 'Proofreading', 'Rewriting', 'Paraphrasing',
            'Formatting', 'Research', 'Data Analysis', 'Programming', 'Design',
            'Translation',
        ]
        
        self.stdout.write('\n' + '='*70)
        self.stdout.write('POPULATING TYPES OF WORK')
        self.stdout.write('='*70)
        for work_type_name in types_of_work:
            work_type, created = TypeOfWork.objects.get_or_create(
                name=work_type_name,
                website=website,
                defaults={}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✅ Created type of work: {work_type_name}'))
        
        # English Types
        english_types = [
            ('US English', 'US'), ('UK English', 'UK'),
            ('Australian English', 'AU'), ('Canadian English', 'CA'),
            ('International English', 'INT'),
        ]
        
        self.stdout.write('\n' + '='*70)
        self.stdout.write('POPULATING ENGLISH TYPES')
        self.stdout.write('='*70)
        for english_type_name, code in english_types:
            existing = EnglishType.objects.filter(code=code).first()
            if existing and existing.website != website:
                self.stdout.write(self.style.WARNING(f'⚠️  Skipping {english_type_name} - code {code} exists for another website'))
                continue
            
            eng_type, created = EnglishType.objects.get_or_create(
                name=english_type_name,
                website=website,
                defaults={'code': code}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✅ Created English type: {english_type_name} ({code})'))
            elif not eng_type.code:
                eng_type.code = code
                eng_type.save()
                self.stdout.write(self.style.WARNING(f'⚠️  Updated English type: {english_type_name} with code {code}'))
        
        # Pricing Configuration
        self.stdout.write('\n' + '='*70)
        self.stdout.write('CHECKING PRICING CONFIGURATION')
        self.stdout.write('='*70)
        pricing_config = PricingConfiguration.objects.filter(website=website).first()
        if not pricing_config:
            try:
                pricing_config = PricingConfiguration.objects.create(
                    website=website,
                    base_price_per_page=Decimal('10.00'),
                    base_price_per_slide=Decimal('5.00'),
                    technical_multiplier=Decimal('1.5'),
                    non_technical_order_multiplier=Decimal('1.0')
                )
                self.stdout.write(self.style.SUCCESS('✅ Created pricing configuration'))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'⚠️  Note: {e}'))
        
        # Academic Level Pricing
        self.stdout.write('\n' + '='*70)
        self.stdout.write('POPULATING ACADEMIC LEVEL PRICING')
        self.stdout.write('='*70)
        level_multipliers = {
            'High School': Decimal('0.8'),
            'College': Decimal('0.9'),
            'Undergraduate': Decimal('1.0'),
            'Bachelor\'s': Decimal('1.0'),
            'Master\'s': Decimal('1.3'),
            'Graduate': Decimal('1.3'),
            'PhD': Decimal('1.5'),
            'Doctorate': Decimal('1.5'),
            'Post-Doctorate': Decimal('1.6'),
            'Professional': Decimal('1.4'),
        }
        
        for level_name, multiplier in level_multipliers.items():
            level = AcademicLevel.objects.filter(name=level_name, website=website).first()
            if level:
                pricing, created = AcademicLevelPricing.objects.get_or_create(
                    website=website,
                    academic_level=level,
                    defaults={
                        'multiplier': multiplier,
                        'level_name': level_name,
                        'slug': level_name.lower().replace(' ', '-').replace('\'', ''),
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'✅ Created pricing for {level_name}: {multiplier}x'))
        
        # Summary
        self.stdout.write('\n' + '='*70)
        self.stdout.write('SUMMARY')
        self.stdout.write('='*70)
        self.stdout.write(f'✅ Paper Types: {PaperType.objects.filter(website=website).count()}')
        self.stdout.write(f'✅ Formatting Styles: {FormattingandCitationStyle.objects.filter(website=website).count()}')
        self.stdout.write(f'✅ Academic Levels: {AcademicLevel.objects.filter(website=website).count()}')
        self.stdout.write(f'✅ Subjects: {Subject.objects.filter(website=website).count()}')
        self.stdout.write(f'✅ Types of Work: {TypeOfWork.objects.filter(website=website).count()}')
        self.stdout.write(f'✅ English Types: {EnglishType.objects.filter(website=website).count()}')
        self.stdout.write('\n' + self.style.SUCCESS('✅ Academic settings populated successfully!'))
        self.stdout.write('='*70 + '\n')

