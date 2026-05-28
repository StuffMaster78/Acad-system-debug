"""
Django management command to populate academic settings.
Usage: python manage.py populate_academic_settings [website_domain]
"""
from django.core.management.base import BaseCommand
from websites.models.websites import Website
from order_configs.models import (
    PaperType, FormattingandCitationStyle, Subject, AcademicLevel,
    TypeOfWork, EnglishType
)
from order_configs.services.comprehensive_paper_types import COMPREHENSIVE_PAPER_TYPES
from order_configs.services.comprehensive_subjects import COMPREHENSIVE_SUBJECTS


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
        
        # Paper Types — full list from comprehensive_paper_types service (deduplicated)
        seen_types = set()
        paper_types = []
        for pt in COMPREHENSIVE_PAPER_TYPES:
            if pt not in seen_types:
                seen_types.add(pt)
                paper_types.append(pt)
        
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
        
        # Subjects — full list from comprehensive_subjects service
        # Deduplicate by name while preserving order
        seen_subjects = set()
        subjects_data = []
        for name, is_technical in COMPREHENSIVE_SUBJECTS:
            if name not in seen_subjects:
                seen_subjects.add(name)
                subjects_data.append((name, is_technical))
        
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

