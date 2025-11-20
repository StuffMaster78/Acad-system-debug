#!/usr/bin/env python3
"""
Populate academic settings (paper types, formatting styles, subjects, etc.)
with realistic academic writing service configurations.
"""
import os
import sys
import django
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'writing_system.settings')
django.setup()

from django.utils import timezone
from websites.models import Website
from order_configs.models import (
    PaperType, FormattingandCitationStyle, Subject, AcademicLevel,
    TypeOfWork, EnglishType
)
from pricing_configs.models import PricingConfiguration, AcademicLevelPricing

def print_success(msg):
    print(f"✅ {msg}")

def print_info(msg):
    print(f"ℹ️  {msg}")

def populate_academic_settings(website=None):
    """
    Populate academic settings for a website.
    If website is None, uses the first available website or creates one.
    """
    # Get or create website
    if not website:
        website = Website.objects.first()
        if not website:
            website = Website.objects.create(
                domain="localhost",
                name='Academic Writing Service',
                slug='academic',
                is_active=True
            )
            print_success(f"Created website: {website.name}")
        else:
            print_info(f"Using existing website: {website.name}")
    
    # Paper Types (common academic paper types)
    paper_types = [
        'Essay',
        'Research Paper',
        'Term Paper',
        'Dissertation',
        'Thesis',
        'Case Study',
        'Article Review',
        'Book Report',
        'Literature Review',
        'Annotated Bibliography',
        'Coursework',
        'Lab Report',
        'Presentation',
        'PowerPoint Presentation',
        'Speech',
        'Article',
        'Report',
        'Reflection Paper',
        'Position Paper',
        'Argumentative Essay',
        'Narrative Essay',
        'Descriptive Essay',
        'Expository Essay',
        'Compare and Contrast Essay',
        'Cause and Effect Essay',
        'Admission Essay',
        'Scholarship Essay',
        'Creative Writing',
        'Poem',
        'Proposal',
        'Research Proposal',
        'Capstone Project',
        'Discussion Post',
        'Response Paper',
        'Summary',
        'Outline',
        'Q&A',
        'Worksheet',
        'Math Problem',
        'Statistics Problem',
        'Programming Assignment',
        'Code Review',
        'Technical Writing',
        'Business Plan',
        'Marketing Plan',
        'Financial Analysis',
    ]
    
    print("\n" + "="*70)
    print("POPULATING PAPER TYPES")
    print("="*70)
    for paper_type_name in paper_types:
        paper_type, created = PaperType.objects.get_or_create(
            name=paper_type_name,
            website=website,
            defaults={}
        )
        if created:
            print_success(f"Created paper type: {paper_type_name}")
        else:
            print_info(f"Paper type already exists: {paper_type_name}")
    
    # Formatting and Citation Styles (common academic styles)
    formatting_styles = [
        'APA',
        'MLA',
        'Chicago',
        'Turabian',
        'Harvard',
        'IEEE',
        'Vancouver',
        'CSE',
        'ACS',
        'AMA',
        'ASA',
        'OSCOLA',
        'Bluebook',
        'AGLC',
        'Oxford',
        'MHRA',
        'Bluebook Legal',
        'Chicago/Turabian',
        'IEEE',
        'CSE/CBE',
        'NLM',
        'ACS',
        'AIP',
        'APS',
        'GSA',
        'APA 6th Edition',
        'APA 7th Edition',
        'MLA 8th Edition',
        'MLA 9th Edition',
        'Chicago 16th Edition',
        'Chicago 17th Edition',
    ]
    
    print("\n" + "="*70)
    print("POPULATING FORMATTING STYLES")
    print("="*70)
    for style_name in formatting_styles:
        style, created = FormattingandCitationStyle.objects.get_or_create(
            name=style_name,
            website=website,
            defaults={}
        )
        if created:
            print_success(f"Created formatting style: {style_name}")
        else:
            print_info(f"Formatting style already exists: {style_name}")
    
    # Academic Levels (common academic levels)
    academic_levels = [
        'High School',
        'College',
        'Undergraduate',
        'Bachelor\'s',
        'Master\'s',
        'Graduate',
        'PhD',
        'Doctorate',
        'Post-Doctorate',
        'Professional',
        'Certificate Program',
        'Diploma',
        'Associate Degree',
        'BSN',
        'DNP',
        'MBA',
        'JD',
        'MD',
        'DDS',
        'DVM',
        'EdD',
        'PsyD',
    ]
    
    print("\n" + "="*70)
    print("POPULATING ACADEMIC LEVELS")
    print("="*70)
    for level_name in academic_levels:
        level, created = AcademicLevel.objects.get_or_create(
            name=level_name,
            website=website,
            defaults={}
        )
        if created:
            print_success(f"Created academic level: {level_name}")
        else:
            print_info(f"Academic level already exists: {level_name}")
    
    # Subjects (common academic subjects)
    subjects = [
        # Humanities
        'English',
        'Literature',
        'History',
        'Philosophy',
        'Religion',
        'Art',
        'Music',
        'Theater',
        'Film Studies',
        'Linguistics',
        'Languages',
        'Spanish',
        'French',
        'German',
        'Chinese',
        'Japanese',
        
        # Social Sciences
        'Psychology',
        'Sociology',
        'Anthropology',
        'Political Science',
        'Economics',
        'Geography',
        'Criminal Justice',
        'Law',
        'Criminology',
        'Social Work',
        'Public Administration',
        'International Relations',
        'Urban Studies',
        'Gender Studies',
        'Ethnic Studies',
        
        # Sciences
        'Biology',
        'Chemistry',
        'Physics',
        'Mathematics',
        'Statistics',
        'Computer Science',
        'Information Technology',
        'Engineering',
        'Mechanical Engineering',
        'Electrical Engineering',
        'Civil Engineering',
        'Chemical Engineering',
        'Biomedical Engineering',
        'Environmental Science',
        'Geology',
        'Astronomy',
        'Meteorology',
        'Botany',
        'Zoology',
        'Microbiology',
        'Genetics',
        'Neuroscience',
        'Astrophysics',
        'Biochemistry',
        'Organic Chemistry',
        'Inorganic Chemistry',
        'Physical Chemistry',
        'Quantum Physics',
        
        # Health Sciences
        'Nursing',
        'Medicine',
        'Public Health',
        'Healthcare',
        'Health Administration',
        'Pharmacy',
        'Physical Therapy',
        'Occupational Therapy',
        'Nutrition',
        'Dietetics',
        'Kinesiology',
        'Exercise Science',
        'Sports Medicine',
        'Veterinary Medicine',
        'Dentistry',
        'Optometry',
        'Radiology',
        'Medical Laboratory Science',
        'Respiratory Therapy',
        
        # Business
        'Business',
        'Management',
        'Marketing',
        'Finance',
        'Accounting',
        'Economics',
        'Entrepreneurship',
        'Human Resources',
        'Operations Management',
        'Supply Chain Management',
        'Project Management',
        'Business Administration',
        'International Business',
        'Real Estate',
        'Hospitality Management',
        'Tourism',
        
        # Education
        'Education',
        'Teaching',
        'Curriculum Development',
        'Educational Technology',
        'Special Education',
        'Early Childhood Education',
        'Elementary Education',
        'Secondary Education',
        'Higher Education',
        'Educational Leadership',
        'Educational Psychology',
        
        # Technology
        'Information Systems',
        'Cybersecurity',
        'Data Science',
        'Artificial Intelligence',
        'Machine Learning',
        'Software Engineering',
        'Web Development',
        'Database Management',
        'Network Administration',
        'Cloud Computing',
        'Mobile Development',
        'Game Development',
        
        # Communications
        'Communications',
        'Journalism',
        'Public Relations',
        'Media Studies',
        'Advertising',
        'Marketing Communications',
        'Digital Media',
        'Broadcasting',
        
        # Other
        'Environmental Studies',
        'Sustainability',
        'Agriculture',
        'Architecture',
        'Urban Planning',
        'Aviation',
        'Maritime Studies',
        'Military Science',
        'Security Studies',
    ]
    
    # Mark technical subjects
    technical_subjects = [
        'Mathematics', 'Statistics', 'Computer Science', 'Engineering',
        'Physics', 'Chemistry', 'Biology', 'Information Technology',
        'Cybersecurity', 'Data Science', 'Artificial Intelligence',
        'Machine Learning', 'Software Engineering', 'Programming',
        'Mechanical Engineering', 'Electrical Engineering', 'Civil Engineering',
        'Chemical Engineering', 'Biomedical Engineering', 'Information Systems',
        'Web Development', 'Database Management', 'Network Administration',
        'Cloud Computing', 'Mobile Development', 'Game Development',
        'Astrophysics', 'Biochemistry', 'Organic Chemistry', 'Quantum Physics',
        'Medical Laboratory Science', 'Biotechnology', 'Bioinformatics',
        'Geology', 'Astronomy', 'Meteorology', 'Environmental Science',
    ]
    
    print("\n" + "="*70)
    print("POPULATING SUBJECTS")
    print("="*70)
    for subject_name in subjects:
        is_technical = subject_name in technical_subjects
        subject, created = Subject.objects.get_or_create(
            name=subject_name,
            website=website,
            defaults={'is_technical': is_technical}
        )
        if created:
            print_success(f"Created subject: {subject_name} {'(Technical)' if is_technical else ''}")
        else:
            # Update if technical status changed
            if subject.is_technical != is_technical:
                subject.is_technical = is_technical
                subject.save()
                print_info(f"Updated subject: {subject_name} (Technical: {is_technical})")
            else:
                print_info(f"Subject already exists: {subject_name}")
    
    # Type of Work
    types_of_work = [
        'Writing',
        'Editing',
        'Proofreading',
        'Rewriting',
        'Paraphrasing',
        'Formatting',
        'Research',
        'Data Analysis',
        'Programming',
        'Design',
        'Translation',
    ]
    
    print("\n" + "="*70)
    print("POPULATING TYPES OF WORK")
    print("="*70)
    for work_type_name in types_of_work:
        work_type, created = TypeOfWork.objects.get_or_create(
            name=work_type_name,
            website=website,
            defaults={}
        )
        if created:
            print_success(f"Created type of work: {work_type_name}")
        else:
            print_info(f"Type of work already exists: {work_type_name}")
    
    # English Types (with codes)
    english_types = [
        ('US English', 'US'),
        ('UK English', 'UK'),
        ('Australian English', 'AU'),
        ('Canadian English', 'CA'),
        ('International English', 'INT'),
    ]
    
    print("\n" + "="*70)
    print("POPULATING ENGLISH TYPES")
    print("="*70)
    for english_type_name, code in english_types:
        # Check if code already exists (might be from another website)
        existing = EnglishType.objects.filter(code=code).first()
        if existing and existing.website != website:
            # Skip if code exists for another website
            print_info(f"Skipping {english_type_name} - code {code} exists for another website")
            continue
        
        eng_type, created = EnglishType.objects.get_or_create(
            name=english_type_name,
            website=website,
            defaults={'code': code}
        )
        if created:
            print_success(f"Created English type: {english_type_name} ({code})")
        else:
            # Update code if missing
            if not eng_type.code:
                eng_type.code = code
                eng_type.save()
                print_info(f"Updated English type: {english_type_name} with code {code}")
            else:
                print_info(f"English type already exists: {english_type_name}")
    
    # Create or update pricing configuration if needed
    print("\n" + "="*70)
    print("CHECKING PRICING CONFIGURATION")
    print("="*70)
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
            print_success("Created pricing configuration")
        except Exception as e:
            print_info(f"Note: {e}")
    else:
        print_info("Pricing configuration already exists")
    
    # Create academic level pricing multipliers
    print("\n" + "="*70)
    print("POPULATING ACADEMIC LEVEL PRICING")
    print("="*70)
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
                print_success(f"Created pricing for {level_name}: {multiplier}x")
            else:
                print_info(f"Pricing already exists for {level_name}")
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"✅ Paper Types: {PaperType.objects.filter(website=website).count()}")
    print(f"✅ Formatting Styles: {FormattingandCitationStyle.objects.filter(website=website).count()}")
    print(f"✅ Academic Levels: {AcademicLevel.objects.filter(website=website).count()}")
    print(f"✅ Subjects: {Subject.objects.filter(website=website).count()}")
    print(f"✅ Types of Work: {TypeOfWork.objects.filter(website=website).count()}")
    print(f"✅ English Types: {EnglishType.objects.filter(website=website).count()}")
    print("\n✅ Academic settings populated successfully!")
    print("="*70 + "\n")

def main():
    """Main function to populate academic settings."""
    import sys
    
    # Check if website domain is provided
    website_domain = None
    if len(sys.argv) > 1:
        website_domain = sys.argv[1]
        website = Website.objects.filter(domain=website_domain).first()
        if not website:
            print(f"❌ Website with domain '{website_domain}' not found.")
            print("Available websites:")
            for w in Website.objects.all():
                print(f"  - {w.domain} ({w.name})")
            return 1
    else:
        website = None
    
    try:
        populate_academic_settings(website)
        return 0
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())

