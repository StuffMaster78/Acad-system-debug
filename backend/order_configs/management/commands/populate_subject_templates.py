"""
Management command to populate comprehensive subject templates.
Run: python manage.py populate_subject_templates
"""
from django.core.management.base import BaseCommand
from order_configs.models import SubjectTemplate
from order_configs.services.comprehensive_subjects import COMPREHENSIVE_SUBJECTS


class Command(BaseCommand):
    help = 'Populate comprehensive subject templates from comprehensive subjects list'

    def add_arguments(self, parser):
        parser.add_argument(
            '--overwrite',
            action='store_true',
            help='Overwrite existing templates',
        )

    def handle(self, *args, **options):
        overwrite = options.get('overwrite', False)
        
        # Organize subjects by category
        all_subjects = [{'name': name, 'is_technical': is_tech} for name, is_tech in COMPREHENSIVE_SUBJECTS]
        
        # Categorize subjects
        humanities_keywords = ['english', 'literature', 'history', 'philosophy', 'religion', 'art', 'music', 'theater', 'film', 'linguistics', 'language', 'spanish', 'french', 'german', 'italian', 'portuguese', 'russian', 'chinese', 'japanese', 'korean', 'arabic', 'latin', 'greek', 'classical', 'poetry', 'drama', 'shakespeare', 'creative writing']
        social_sciences_keywords = ['psychology', 'sociology', 'anthropology', 'political', 'economics', 'geography', 'criminal', 'law', 'criminology', 'social work', 'public administration', 'international relations', 'urban studies', 'gender', 'ethnic', 'african american', 'asian american', 'latin american', 'middle eastern']
        sciences_keywords = ['biology', 'chemistry', 'physics', 'mathematics', 'statistics', 'geology', 'astronomy', 'meteorology', 'botany', 'zoology', 'microbiology', 'genetics', 'neuroscience', 'astrophysics', 'biochemistry', 'ecology', 'environmental science', 'earth science', 'oceanography', 'atmospheric']
        computing_keywords = ['computer', 'programming', 'software', 'it', 'information systems', 'information technology', 'data', 'cyber', 'network', 'cloud', 'web', 'mobile', 'game', 'database', 'ai', 'machine learning', 'blockchain', 'devops', 'algorithm', 'code', 'sql', 'security']
        engineering_keywords = ['engineering', 'mechanical', 'electrical', 'civil', 'chemical', 'biomedical', 'aerospace', 'aeronautical', 'automotive', 'industrial', 'environmental', 'structural', 'materials', 'nuclear', 'petroleum', 'systems', 'telecommunications', 'marine', 'agricultural']
        health_keywords = ['nursing', 'medicine', 'health', 'pharmacy', 'therapy', 'nutrition', 'dietetics', 'kinesiology', 'exercise', 'sports medicine', 'veterinary', 'dentistry', 'optometry', 'audiology', 'medical laboratory', 'biomedical science', 'health informatics', 'epidemiology', 'public health']
        business_keywords = ['business', 'management', 'marketing', 'finance', 'accounting', 'entrepreneurship', 'human resources', 'operations', 'supply chain', 'project management', 'real estate', 'hospitality', 'tourism', 'event', 'retail', 'leadership', 'organizational behavior']
        education_keywords = ['education', 'teaching', 'curriculum', 'instructional', 'educational', 'special education', 'early childhood', 'elementary', 'secondary', 'higher education', 'adult education', 'learning']
        communications_keywords = ['communications', 'journalism', 'public relations', 'media', 'broadcasting', 'radio', 'television', 'film production', 'video production', 'social media', 'digital media']
        aviation_keywords = ['aviation', 'aeronautics', 'aerospace', 'air traffic', 'pilot', 'aircraft', 'maritime', 'marine', 'transportation', 'logistics']
        architecture_keywords = ['architecture', 'urban planning', 'landscape', 'interior design', 'graphic design', 'web design', 'industrial design', 'fashion design']
        agriculture_keywords = ['agriculture', 'agricultural', 'agronomy', 'animal science', 'plant science', 'forestry', 'environmental', 'sustainability', 'renewable energy', 'climate', 'conservation']
        military_keywords = ['military', 'security', 'homeland', 'intelligence', 'forensics', 'criminal investigation']
        
        templates = [
            {
                'name': 'General (All Subjects)',
                'category': 'general',
                'description': 'Comprehensive list of all subjects from high school to post-graduate level, covering all disciplines',
                'subjects': all_subjects
            },
            {
                'name': 'Humanities',
                'category': 'humanities',
                'description': 'Humanities subjects: English, Literature, History, Philosophy, Art, Music, Languages, etc.',
                'subjects': [s for s in all_subjects if any(kw in s['name'].lower() for kw in humanities_keywords)]
            },
            {
                'name': 'Social Sciences',
                'category': 'social_sciences',
                'description': 'Social sciences: Psychology, Sociology, Political Science, Economics, Law, etc.',
                'subjects': [s for s in all_subjects if any(kw in s['name'].lower() for kw in social_sciences_keywords)]
            },
            {
                'name': 'Natural Sciences',
                'category': 'sciences',
                'description': 'Natural and physical sciences: Biology, Chemistry, Physics, Mathematics, Statistics, etc.',
                'subjects': [s for s in all_subjects if any(kw in s['name'].lower() for kw in sciences_keywords)]
            },
            {
                'name': 'Computing & Computer Science',
                'category': 'computing',
                'description': 'Computer science, IT, programming, data science, AI, cybersecurity, etc.',
                'subjects': [s for s in all_subjects if any(kw in s['name'].lower() for kw in computing_keywords)]
            },
            {
                'name': 'Engineering',
                'category': 'engineering',
                'description': 'All engineering disciplines: Mechanical, Electrical, Civil, Chemical, Aerospace, etc.',
                'subjects': [s for s in all_subjects if any(kw in s['name'].lower() for kw in engineering_keywords)]
            },
            {
                'name': 'Health Sciences',
                'category': 'health_sciences',
                'description': 'Health sciences: Medicine, Public Health, Health Administration, etc.',
                'subjects': [s for s in all_subjects if any(kw in s['name'].lower() for kw in health_keywords)]
            },
            {
                'name': 'Nursing & Healthcare',
                'category': 'nursing',
                'description': 'Nursing and healthcare subjects: Nursing, Medical-Surgical, Pediatric, Community Health, etc.',
                'subjects': [s for s in all_subjects if any(kw in s['name'].lower() for kw in health_keywords) and ('nursing' in s['name'].lower() or 'healthcare' in s['name'].lower() or 'public health' in s['name'].lower())]
            },
            {
                'name': 'Business',
                'category': 'business',
                'description': 'Business subjects: Management, Marketing, Finance, Accounting, Entrepreneurship, etc.',
                'subjects': [s for s in all_subjects if any(kw in s['name'].lower() for kw in business_keywords)]
            },
            {
                'name': 'Education',
                'category': 'education',
                'description': 'Education subjects: Teaching, Curriculum Development, Educational Technology, etc.',
                'subjects': [s for s in all_subjects if any(kw in s['name'].lower() for kw in education_keywords)]
            },
            {
                'name': 'Communications',
                'category': 'general',
                'description': 'Communications and media: Journalism, Public Relations, Broadcasting, etc.',
                'subjects': [s for s in all_subjects if any(kw in s['name'].lower() for kw in communications_keywords)]
            },
            {
                'name': 'Aviation & Transportation',
                'category': 'general',
                'description': 'Aviation, maritime, and transportation subjects',
                'subjects': [s for s in all_subjects if any(kw in s['name'].lower() for kw in aviation_keywords)]
            },
            {
                'name': 'Architecture & Design',
                'category': 'general',
                'description': 'Architecture, urban planning, and design subjects',
                'subjects': [s for s in all_subjects if any(kw in s['name'].lower() for kw in architecture_keywords)]
            },
            {
                'name': 'Agriculture & Environment',
                'category': 'general',
                'description': 'Agriculture, environmental science, and sustainability',
                'subjects': [s for s in all_subjects if any(kw in s['name'].lower() for kw in agriculture_keywords)]
            },
            {
                'name': 'Military & Security',
                'category': 'general',
                'description': 'Military science, security studies, and forensics',
                'subjects': [s for s in all_subjects if any(kw in s['name'].lower() for kw in military_keywords)]
            },
        ]
        
        created_count = 0
        updated_count = 0
        skipped_count = 0
        
        for template_data in templates:
            name = template_data['name']
            category = template_data['category']
            
            if overwrite:
                SubjectTemplate.objects.filter(name=name, category=category).delete()
                template, created = SubjectTemplate.objects.get_or_create(
                    name=name,
                    category=category,
                    defaults=template_data
                )
                if created:
                    created_count += 1
                    self.stdout.write(self.style.SUCCESS(f'✅ Created template: {name} ({len(template_data["subjects"])} subjects)'))
                else:
                    updated_count += 1
                    self.stdout.write(self.style.SUCCESS(f'🔄 Updated template: {name} ({len(template_data["subjects"])} subjects)'))
            else:
                template, created = SubjectTemplate.objects.get_or_create(
                    name=name,
                    category=category,
                    defaults=template_data
                )
                if created:
                    created_count += 1
                    self.stdout.write(self.style.SUCCESS(f'✅ Created template: {name} ({len(template_data["subjects"])} subjects)'))
                else:
                    skipped_count += 1
                    self.stdout.write(self.style.WARNING(f'⏭️  Skipped existing template: {name}'))
        
        self.stdout.write(self.style.SUCCESS(
            f'\n📊 Summary: {created_count} created, {updated_count} updated, {skipped_count} skipped'
        ))
