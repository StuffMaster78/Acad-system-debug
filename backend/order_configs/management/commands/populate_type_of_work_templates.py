"""
Management command to populate comprehensive type of work templates.
Run: python manage.py populate_type_of_work_templates
"""
from django.core.management.base import BaseCommand
from order_configs.models import TypeOfWorkTemplate
from order_configs.services.comprehensive_types_of_work import COMPREHENSIVE_TYPES_OF_WORK


class Command(BaseCommand):
    help = 'Populate comprehensive type of work templates from comprehensive types list'

    def add_arguments(self, parser):
        parser.add_argument(
            '--overwrite',
            action='store_true',
            help='Overwrite existing templates',
        )

    def handle(self, *args, **options):
        overwrite = options.get('overwrite', False)
        
        # Organize types of work by category
        all_types = COMPREHENSIVE_TYPES_OF_WORK
        
        # Categorize types
        writing_keywords = ['writing', 'original', 'custom', 'academic writing', 'creative writing', 'technical writing', 'business writing', 'professional writing']
        editing_keywords = ['editing', 'revision', 'revisions', 'copy editing', 'line editing', 'substantive', 'developmental', 'content editing', 'structural', 'style editing']
        proofreading_keywords = ['proofreading', 'grammar', 'spell', 'punctuation', 'language correction', 'error correction', 'formatting check']
        rewriting_keywords = ['rewriting', 'paraphrasing', 'rephrasing', 'ai content', 'ai slop']
        plagiarism_keywords = ['plagiarism', 'duplicate content', 'originality', 'similarity']
        formatting_keywords = ['formatting', 'citation', 'reference', 'apa', 'mla', 'chicago', 'harvard', 'ieee', 'style formatting', 'document formatting']
        research_keywords = ['research', 'literature research', 'academic research', 'primary research', 'secondary research', 'data collection', 'research assistance', 'research support']
        analysis_keywords = ['analysis', 'data analysis', 'statistical', 'qualitative', 'quantitative', 'content analysis', 'text analysis', 'critical analysis', 'case analysis', 'swot']
        review_keywords = ['review', 'critiquing', 'critique', 'critical review', 'critical evaluation', 'critical assessment', 'article review', 'literature review', 'book review', 'peer review']
        grading_keywords = ['marking', 'grading', 'assessment', 'evaluation', 'scoring', 'rubric', 'grade assignment']
        technical_keywords = ['programming', 'coding', 'code', 'algorithm', 'software development', 'code review', 'code debugging']
        
        templates = [
            {
                'name': 'General (All Types)',
                'category': 'general',
                'description': 'Comprehensive list of all types of work (154 types)',
                'types_of_work': all_types
            },
            {
                'name': 'Writing Services',
                'category': 'writing',
                'description': 'All writing services including writing from scratch, original writing, etc.',
                'types_of_work': [t for t in all_types if any(kw in t.lower() for kw in writing_keywords)]
            },
            {
                'name': 'Editing & Revision',
                'category': 'editing',
                'description': 'Editing and revision services',
                'types_of_work': [t for t in all_types if any(kw in t.lower() for kw in editing_keywords)]
            },
            {
                'name': 'Proofreading & Correction',
                'category': 'proofreading',
                'description': 'Proofreading, grammar check, spell check, etc.',
                'types_of_work': [t for t in all_types if any(kw in t.lower() for kw in proofreading_keywords)]
            },
            {
                'name': 'Rewriting & Paraphrasing',
                'category': 'rewriting',
                'description': 'Rewriting AI content, paraphrasing, rephrasing services',
                'types_of_work': [t for t in all_types if any(kw in t.lower() for kw in rewriting_keywords)]
            },
            {
                'name': 'Plagiarism Services',
                'category': 'plagiarism',
                'description': 'Plagiarism removal, check, detection, and elimination',
                'types_of_work': [t for t in all_types if any(kw in t.lower() for kw in plagiarism_keywords)]
            },
            {
                'name': 'Formatting & Styling',
                'category': 'formatting',
                'description': 'Citation formatting, style formatting, document formatting',
                'types_of_work': [t for t in all_types if any(kw in t.lower() for kw in formatting_keywords)]
            },
            {
                'name': 'Research Services',
                'category': 'research',
                'description': 'Research, literature research, data collection',
                'types_of_work': [t for t in all_types if any(kw in t.lower() for kw in research_keywords)]
            },
            {
                'name': 'Analysis Services',
                'category': 'analysis',
                'description': 'Data analysis, statistical analysis, content analysis',
                'types_of_work': [t for t in all_types if any(kw in t.lower() for kw in analysis_keywords)]
            },
            {
                'name': 'Review & Critique',
                'category': 'review',
                'description': 'Review, critiquing, critical evaluation services',
                'types_of_work': [t for t in all_types if any(kw in t.lower() for kw in review_keywords)]
            },
            {
                'name': 'Grading & Marking',
                'category': 'grading',
                'description': 'Marking, grading, assessment, evaluation services',
                'types_of_work': [t for t in all_types if any(kw in t.lower() for kw in grading_keywords)]
            },
            {
                'name': 'Technical Services',
                'category': 'technical',
                'description': 'Programming, coding, software development services',
                'types_of_work': [t for t in all_types if any(kw in t.lower() for kw in technical_keywords)]
            },
        ]
        
        created_count = 0
        updated_count = 0
        skipped_count = 0
        
        for template_data in templates:
            name = template_data['name']
            category = template_data['category']
            
            if overwrite:
                TypeOfWorkTemplate.objects.filter(name=name, category=category).delete()
                template, created = TypeOfWorkTemplate.objects.get_or_create(
                    name=name,
                    category=category,
                    defaults=template_data
                )
                if created:
                    created_count += 1
                    self.stdout.write(self.style.SUCCESS(f'✅ Created template: {name} ({len(template_data["types_of_work"])} types)'))
                else:
                    updated_count += 1
                    self.stdout.write(self.style.SUCCESS(f'🔄 Updated template: {name} ({len(template_data["types_of_work"])} types)'))
            else:
                template, created = TypeOfWorkTemplate.objects.get_or_create(
                    name=name,
                    category=category,
                    defaults=template_data
                )
                if created:
                    created_count += 1
                    self.stdout.write(self.style.SUCCESS(f'✅ Created template: {name} ({len(template_data["types_of_work"])} types)'))
                else:
                    skipped_count += 1
                    self.stdout.write(self.style.WARNING(f'⏭️  Skipped existing template: {name}'))
        
        self.stdout.write(self.style.SUCCESS(
            f'\n📊 Summary: {created_count} created, {updated_count} updated, {skipped_count} skipped'
        ))

