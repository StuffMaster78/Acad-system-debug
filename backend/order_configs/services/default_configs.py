"""
Service for managing default/common order configurations.
These are the standard configurations that get populated for every website.
Admins can add custom configurations on top of these defaults.

Supports different default sets:
- 'general': General purpose defaults (all subjects, all paper types)
- 'nursing': Nursing-specific defaults (health sciences focus)
- 'technical': Technical defaults (programming, math, engineering focus)
"""
from order_configs.models import (
    PaperType, FormattingandCitationStyle, Subject, AcademicLevel,
    TypeOfWork, EnglishType
)
from websites.models import Website


# ==================== GENERAL DEFAULTS ====================
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

# Comprehensive types of work - import from comprehensive_types_of_work
from .comprehensive_types_of_work import COMPREHENSIVE_TYPES_OF_WORK

# Default types of work (backward compatibility - use comprehensive list)
DEFAULT_TYPES_OF_WORK = COMPREHENSIVE_TYPES_OF_WORK

# English types with codes: (name, code)
DEFAULT_ENGLISH_TYPES = [
    ('US English', 'US'), ('UK English', 'UK'),
    ('Australian English', 'AU'), ('Canadian English', 'CA'),
    ('International English', 'INT'),
]

# ==================== NURSING-SPECIFIC DEFAULTS ====================
NURSING_PAPER_TYPES = [
    'Essay', 'Research Paper', 'Term Paper', 'Dissertation', 'Thesis',
    'Case Study', 'Article Review', 'Literature Review',
    'Annotated Bibliography', 'Coursework', 'Lab Report', 'Presentation',
    'PowerPoint Presentation', 'Reflection Paper', 'Position Paper',
    'Nursing Care Plan', 'Clinical Case Study', 'Evidence-Based Practice Paper',
    'Nursing Research Proposal', 'Capstone Project', 'Discussion Post',
    'Response Paper', 'Summary', 'Outline', 'Q&A', 'Worksheet',
    'Nursing Assessment', 'Patient Care Plan', 'Nursing Diagnosis',
    'Nursing Intervention', 'Quality Improvement Project',
]

NURSING_FORMATTING_STYLES = [
    'APA', 'APA 6th Edition', 'APA 7th Edition', 'MLA', 'Chicago',
    'Turabian', 'Harvard', 'Vancouver', 'AMA', 'NLM',
]

NURSING_ACADEMIC_LEVELS = [
    'High School', 'College', 'Undergraduate', 'Bachelor\'s', 'BSN',
    'Master\'s', 'MSN', 'Graduate', 'DNP', 'PhD', 'Doctorate',
    'Post-Doctorate', 'Professional', 'Certificate Program',
    'Diploma', 'Associate Degree', 'RN to BSN',
]

NURSING_SUBJECTS = [
    # Health Sciences (Nursing Focus)
    ('Nursing', False), ('Nursing Practice', False), ('Nursing Theory', False),
    ('Medical-Surgical Nursing', False), ('Pediatric Nursing', False),
    ('Maternal-Child Nursing', False), ('Psychiatric Nursing', False),
    ('Community Health Nursing', False), ('Public Health', False),
    ('Healthcare', False), ('Health Administration', False),
    ('Health Policy', False), ('Health Promotion', False),
    ('Epidemiology', False), ('Health Education', False),
    
    # Related Health Fields
    ('Medicine', True), ('Pharmacy', True), ('Physical Therapy', False),
    ('Occupational Therapy', False), ('Nutrition', False),
    ('Dietetics', False), ('Kinesiology', False),
    ('Exercise Science', False), ('Sports Medicine', False),
    ('Respiratory Therapy', False), ('Radiology', True),
    ('Medical Laboratory Science', True),
    
    # Supporting Subjects
    ('Biology', True), ('Chemistry', True), ('Psychology', False),
    ('Sociology', False), ('Statistics', True),
]

# ==================== TECHNICAL DEFAULTS ====================
TECHNICAL_PAPER_TYPES = [
    'Essay', 'Research Paper', 'Term Paper', 'Dissertation', 'Thesis',
    'Case Study', 'Article Review', 'Literature Review',
    'Annotated Bibliography', 'Coursework', 'Lab Report', 'Presentation',
    'PowerPoint Presentation', 'Proposal', 'Research Proposal',
    'Capstone Project', 'Discussion Post', 'Response Paper', 'Summary',
    'Outline', 'Q&A', 'Worksheet',
    'Math Problem', 'Statistics Problem', 'Programming Assignment',
    'Code Review', 'Technical Writing', 'Algorithm Design',
    'System Design', 'Database Design', 'Software Architecture',
    'Technical Documentation', 'API Documentation', 'Code Documentation',
    'Project Report', 'Technical Report', 'System Analysis',
]

TECHNICAL_FORMATTING_STYLES = [
    'APA', 'APA 6th Edition', 'APA 7th Edition', 'MLA', 'Chicago',
    'Turabian', 'Harvard', 'IEEE', 'Vancouver', 'CSE', 'ACS',
    'ACM', 'OSCOLA',
]

TECHNICAL_ACADEMIC_LEVELS = [
    'High School', 'College', 'Undergraduate', 'Bachelor\'s', 'Master\'s',
    'Graduate', 'PhD', 'Doctorate', 'Post-Doctorate', 'Professional',
    'Certificate Program', 'Diploma', 'Associate Degree',
    'Bootcamp', 'Professional Certification',
]

TECHNICAL_SUBJECTS = [
    # Computer Science & Programming
    ('Computer Science', True), ('Information Technology', True),
    ('Software Engineering', True), ('Programming', True),
    ('Web Development', True), ('Mobile Development', True),
    ('Game Development', True), ('Database Management', True),
    ('Network Administration', True), ('Cloud Computing', True),
    ('Cybersecurity', True), ('Information Systems', True),
    ('Data Science', True), ('Artificial Intelligence', True),
    ('Machine Learning', True), ('Data Analytics', True),
    ('Big Data', True), ('Blockchain', True), ('DevOps', True),
    
    # Mathematics & Statistics
    ('Mathematics', True), ('Statistics', True), ('Applied Mathematics', True),
    ('Discrete Mathematics', True), ('Linear Algebra', True),
    ('Calculus', True), ('Probability', True), ('Numerical Analysis', True),
    
    # Engineering
    ('Engineering', True), ('Mechanical Engineering', True),
    ('Electrical Engineering', True), ('Civil Engineering', True),
    ('Chemical Engineering', True), ('Biomedical Engineering', True),
    ('Computer Engineering', True), ('Aerospace Engineering', True),
    ('Industrial Engineering', True), ('Environmental Engineering', True),
    
    # Technical Sciences
    ('Physics', True), ('Chemistry', True), ('Biology', True),
    ('Biochemistry', True), ('Organic Chemistry', True),
    ('Inorganic Chemistry', True), ('Physical Chemistry', True),
    ('Quantum Physics', True), ('Astrophysics', True),
    ('Neuroscience', True), ('Genetics', True),
    
    # Technical Business
    ('Information Systems', True), ('Business Analytics', True),
    ('Operations Research', True), ('Supply Chain Management', False),
    ('Project Management', False),
]

# ==================== DEFAULT SET DEFINITIONS ====================
DEFAULT_SETS = {
    'general': {
        'paper_types': DEFAULT_PAPER_TYPES,
        'formatting_styles': DEFAULT_FORMATTING_STYLES,
        'academic_levels': DEFAULT_ACADEMIC_LEVELS,
        'subjects': DEFAULT_SUBJECTS,
        'types_of_work': DEFAULT_TYPES_OF_WORK,
        'english_types': DEFAULT_ENGLISH_TYPES,
        'name': 'General',
        'description': 'Comprehensive defaults for general-purpose websites',
    },
    'nursing': {
        'paper_types': NURSING_PAPER_TYPES,
        'formatting_styles': NURSING_FORMATTING_STYLES,
        'academic_levels': NURSING_ACADEMIC_LEVELS,
        'subjects': NURSING_SUBJECTS,
        'types_of_work': DEFAULT_TYPES_OF_WORK,
        'english_types': DEFAULT_ENGLISH_TYPES,
        'name': 'Nursing',
        'description': 'Defaults optimized for nursing and health sciences websites',
    },
    'technical': {
        'paper_types': TECHNICAL_PAPER_TYPES,
        'formatting_styles': TECHNICAL_FORMATTING_STYLES,
        'academic_levels': TECHNICAL_ACADEMIC_LEVELS,
        'subjects': TECHNICAL_SUBJECTS,
        'types_of_work': DEFAULT_TYPES_OF_WORK,
        'english_types': DEFAULT_ENGLISH_TYPES,
        'name': 'Technical',
        'description': 'Defaults for technical websites (programming, math, engineering)',
    },
}


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


def populate_default_configs_for_website(website: Website, skip_existing: bool = True, default_set: str = 'general'):
    """
    Populate default configurations for a website.
    Uses get_or_create so it won't duplicate existing entries.
    
    Args:
        website: The website to populate configurations for
        skip_existing: If True, skip entries that already exist (default: True)
        default_set: Which default set to use ('general', 'nursing', 'technical')
    
    Returns:
        dict with counts of created items for each config type
    """
    if default_set not in DEFAULT_SETS:
        default_set = 'general'
    
    config_set = DEFAULT_SETS[default_set]
    
    counts = {
        'paper_types': 0,
        'formatting_styles': 0,
        'academic_levels': 0,
        'subjects': 0,
        'types_of_work': 0,
        'english_types': 0,
    }
    
    # Paper Types
    for paper_type_name in config_set['paper_types']:
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
    for style_name in config_set['formatting_styles']:
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
    for level_name in config_set['academic_levels']:
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
    for subject_data in config_set['subjects']:
        if isinstance(subject_data, tuple):
            subject_name, is_technical = subject_data
        else:
            subject_name = subject_data
            is_technical = False
        
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
    for work_type_name in config_set['types_of_work']:
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
    for english_type_data in config_set['english_types']:
        if isinstance(english_type_data, tuple):
            english_type_name, code = english_type_data
        else:
            english_type_name = english_type_data
            code = ''
        
        if skip_existing and EnglishType.objects.filter(website=website, name=english_type_name).exists():
            continue
        # Check for code conflicts across websites
        if code:
            existing = EnglishType.objects.filter(code=code, website=website).first()
            if existing and existing.name != english_type_name:
                # Code already exists for this website with different name, skip
                continue
        
        _, created = EnglishType.objects.get_or_create(
            name=english_type_name,
            website=website,
            defaults={'code': code} if code else {}
        )
        if created:
            counts['english_types'] += 1
    
    return counts


def get_available_default_sets():
    """
    Get list of available default sets with their metadata.
    
    Returns:
        list of dicts with 'id', 'name', 'description' for each default set
    """
    return [
        {
            'id': key,
            'name': value['name'],
            'description': value['description'],
        }
        for key, value in DEFAULT_SETS.items()
    ]

