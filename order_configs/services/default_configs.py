"""
Service for managing default/common order configurations.
These are the standard configurations that get populated for every website.
Admins can add custom configurations on top of these defaults.
"""
from order_configs.models import (
    PaperType, FormattingandCitationStyle, Subject, AcademicLevel,
    TypeOfWork, EnglishType
)
from websites.models import Website


# Default configurations that should be available for all websites
DEFAULT_PAPER_TYPES = [
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

DEFAULT_FORMATTING_STYLES = [
    'APA', 'MLA', 'Chicago', 'Turabian', 'Harvard', 'IEEE', 'Vancouver',
    'CSE', 'ACS', 'AMA', 'ASA', 'OSCOLA', 'Bluebook', 'AGLC', 'Oxford',
    'MHRA', 'Bluebook Legal', 'Chicago/Turabian', 'IEEE', 'CSE/CBE',
    'NLM', 'ACS', 'AIP', 'APS', 'GSA', 'APA 6th Edition',
    'APA 7th Edition', 'MLA 8th Edition', 'MLA 9th Edition',
    'Chicago 16th Edition', 'Chicago 17th Edition',
]

DEFAULT_ACADEMIC_LEVELS = [
    'High School', 'College', 'Undergraduate', 'Bachelor\'s', 'Master\'s',
    'Graduate', 'PhD', 'Doctorate', 'Post-Doctorate', 'Professional',
    'Certificate Program', 'Diploma', 'Associate Degree', 'BSN', 'DNP',
    'MBA', 'JD', 'MD', 'DDS', 'DVM', 'EdD', 'PsyD',
]

# Subjects with technical flag: (name, is_technical)
DEFAULT_SUBJECTS = [
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
    ('Finance', False), ('Accounting', False),
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

DEFAULT_TYPES_OF_WORK = [
    'Writing', 'Editing', 'Proofreading', 'Rewriting', 'Paraphrasing',
    'Formatting', 'Research', 'Data Analysis', 'Programming', 'Design',
    'Translation',
]

# English types with codes: (name, code)
DEFAULT_ENGLISH_TYPES = [
    ('US English', 'US'), ('UK English', 'UK'),
    ('Australian English', 'AU'), ('Canadian English', 'CA'),
    ('International English', 'INT'),
]


def is_default_paper_type(name: str) -> bool:
    """Check if a paper type name is in the default list."""
    return name in DEFAULT_PAPER_TYPES


def is_default_formatting_style(name: str) -> bool:
    """Check if a formatting style name is in the default list."""
    return name in DEFAULT_FORMATTING_STYLES


def is_default_academic_level(name: str) -> bool:
    """Check if an academic level name is in the default list."""
    return name in DEFAULT_ACADEMIC_LEVELS


def is_default_subject(name: str) -> bool:
    """Check if a subject name is in the default list."""
    return any(subj[0] == name for subj in DEFAULT_SUBJECTS)


def is_default_type_of_work(name: str) -> bool:
    """Check if a type of work name is in the default list."""
    return name in DEFAULT_TYPES_OF_WORK


def is_default_english_type(name: str) -> bool:
    """Check if an English type name is in the default list."""
    return any(eng[0] == name for eng in DEFAULT_ENGLISH_TYPES)


def populate_default_configs_for_website(website: Website, skip_existing: bool = True):
    """
    Populate default configurations for a website.
    Uses get_or_create so it won't duplicate existing entries.
    
    Args:
        website: The website to populate configurations for
        skip_existing: If True, skip entries that already exist (default: True)
    
    Returns:
        dict with counts of created items for each config type
    """
    counts = {
        'paper_types': 0,
        'formatting_styles': 0,
        'academic_levels': 0,
        'subjects': 0,
        'types_of_work': 0,
        'english_types': 0,
    }
    
    # Paper Types
    for paper_type_name in DEFAULT_PAPER_TYPES:
        if skip_existing and PaperType.objects.filter(website=website, name=paper_type_name).exists():
            continue
        _, created = PaperType.objects.get_or_create(
            name=paper_type_name,
            website=website,
            defaults={}
        )
        if created:
            counts['paper_types'] += 1
    
    # Formatting Styles
    for style_name in DEFAULT_FORMATTING_STYLES:
        if skip_existing and FormattingandCitationStyle.objects.filter(website=website, name=style_name).exists():
            continue
        _, created = FormattingandCitationStyle.objects.get_or_create(
            name=style_name,
            website=website,
            defaults={}
        )
        if created:
            counts['formatting_styles'] += 1
    
    # Academic Levels
    for level_name in DEFAULT_ACADEMIC_LEVELS:
        if skip_existing and AcademicLevel.objects.filter(website=website, name=level_name).exists():
            continue
        _, created = AcademicLevel.objects.get_or_create(
            name=level_name,
            website=website,
            defaults={}
        )
        if created:
            counts['academic_levels'] += 1
    
    # Subjects
    for subject_name, is_technical in DEFAULT_SUBJECTS:
        if skip_existing and Subject.objects.filter(website=website, name=subject_name).exists():
            continue
        _, created = Subject.objects.get_or_create(
            name=subject_name,
            website=website,
            defaults={'is_technical': is_technical}
        )
        if created:
            counts['subjects'] += 1
    
    # Types of Work
    for work_type_name in DEFAULT_TYPES_OF_WORK:
        if skip_existing and TypeOfWork.objects.filter(website=website, name=work_type_name).exists():
            continue
        _, created = TypeOfWork.objects.get_or_create(
            name=work_type_name,
            website=website,
            defaults={}
        )
        if created:
            counts['types_of_work'] += 1
    
    # English Types
    for english_type_name, code in DEFAULT_ENGLISH_TYPES:
        if skip_existing and EnglishType.objects.filter(website=website, name=english_type_name).exists():
            continue
        # Check for code conflicts across websites
        existing = EnglishType.objects.filter(code=code, website=website).first()
        if existing and existing.name != english_type_name:
            # Code already exists for this website with different name, skip
            continue
        
        _, created = EnglishType.objects.get_or_create(
            name=english_type_name,
            website=website,
            defaults={'code': code}
        )
        if created:
            counts['english_types'] += 1
    
    return counts

