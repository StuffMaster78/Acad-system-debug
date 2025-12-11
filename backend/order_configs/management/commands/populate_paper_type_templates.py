"""
Management command to populate comprehensive paper type templates.
Run: python manage.py populate_paper_type_templates
"""
from django.core.management.base import BaseCommand
from order_configs.models import PaperTypeTemplate
from order_configs.services.comprehensive_paper_types import COMPREHENSIVE_PAPER_TYPES


class Command(BaseCommand):
    help = 'Populate comprehensive paper type templates from comprehensive paper types list'

    def add_arguments(self, parser):
        parser.add_argument(
            '--overwrite',
            action='store_true',
            help='Overwrite existing templates',
        )

    def handle(self, *args, **options):
        overwrite = options.get('overwrite', False)
        
        # Organize paper types by category
        all_paper_types = COMPREHENSIVE_PAPER_TYPES
        
        # Categorize paper types
        high_school_keywords = ['book report', 'book review', 'book summary', 'reading response', 'journal entry', 'diary entry', 'letter writing', 'five paragraph essay', 'short answer', 'fill in the blank', 'multiple choice', 'true/false', 'worksheet', 'homework', 'classwork']
        undergraduate_keywords = ['essay', 'research paper', 'term paper', 'case study', 'lab report', 'presentation', 'coursework', 'assignment', 'report', 'article review', 'literature review', 'annotated bibliography', 'summary', 'outline', 'discussion post', 'response paper']
        graduate_keywords = ['thesis', 'dissertation', 'master\'s', 'phd', 'doctoral', 'prospectus', 'defense', 'comprehensive exam', 'qualifying exam', 'preliminary exam', 'grant application', 'fellowship', 'postdoctoral', 'systematic review', 'meta-analysis', 'journal article', 'conference paper', 'scholarly paper']
        professional_keywords = ['business plan', 'marketing plan', 'strategic plan', 'proposal', 'grant proposal', 'business case', 'executive summary', 'swot analysis', 'market analysis', 'financial analysis', 'memo', 'business letter', 'press release', 'newsletter']
        nursing_keywords = ['nursing', 'care plan', 'patient care', 'clinical', 'soap note', 'progress note', 'discharge summary', 'evidence-based practice', 'quality improvement']
        technical_keywords = ['technical', 'engineering', 'programming', 'coding', 'code', 'algorithm', 'system design', 'database design', 'software design', 'api documentation', 'code documentation', 'technical specification', 'user manual', 'technical manual', 'test plan', 'test report']
        business_keywords = ['business', 'marketing', 'finance', 'accounting', 'management', 'strategic', 'operations', 'project management', 'supply chain', 'human resources', 'leadership', 'organizational behavior']
        law_keywords = ['legal', 'brief', 'case brief', 'legal memorandum', 'legal opinion', 'contract', 'court', 'motion', 'legal argument', 'legal research']
        
        templates = [
            {
                'name': 'General (All Paper Types)',
                'category': 'general',
                'description': 'Comprehensive list of all paper types from high school to post-graduate level',
                'paper_types': all_paper_types
            },
            {
                'name': 'High School Assignments',
                'category': 'high_school',
                'description': 'Paper types commonly assigned in high school',
                'paper_types': [pt for pt in all_paper_types if any(kw in pt.lower() for kw in high_school_keywords)]
            },
            {
                'name': 'Undergraduate Papers',
                'category': 'undergraduate',
                'description': 'Common undergraduate assignment types',
                'paper_types': [pt for pt in all_paper_types if any(kw in pt.lower() for kw in undergraduate_keywords) and not any(kw in pt.lower() for kw in graduate_keywords)]
            },
            {
                'name': 'Graduate & Post-Graduate',
                'category': 'graduate',
                'description': 'Thesis, dissertation, and advanced research papers',
                'paper_types': [pt for pt in all_paper_types if any(kw in pt.lower() for kw in graduate_keywords)]
            },
            {
                'name': 'Professional & Business',
                'category': 'professional',
                'description': 'Business plans, proposals, reports, and professional documents',
                'paper_types': [pt for pt in all_paper_types if any(kw in pt.lower() for kw in professional_keywords) or any(kw in pt.lower() for kw in business_keywords)]
            },
            {
                'name': 'Nursing & Healthcare',
                'category': 'nursing',
                'description': 'Nursing care plans, clinical case studies, and healthcare papers',
                'paper_types': [pt for pt in all_paper_types if any(kw in pt.lower() for kw in nursing_keywords)]
            },
            {
                'name': 'Technical & Engineering',
                'category': 'technical',
                'description': 'Technical reports, engineering papers, programming assignments',
                'paper_types': [pt for pt in all_paper_types if any(kw in pt.lower() for kw in technical_keywords)]
            },
            {
                'name': 'Law & Legal',
                'category': 'law',
                'description': 'Legal briefs, case studies, and legal research papers',
                'paper_types': [pt for pt in all_paper_types if any(kw in pt.lower() for kw in law_keywords)]
            },
        ]
        
        created_count = 0
        updated_count = 0
        skipped_count = 0
        
        for template_data in templates:
            name = template_data['name']
            category = template_data['category']
            
            if overwrite:
                PaperTypeTemplate.objects.filter(name=name, category=category).delete()
                template, created = PaperTypeTemplate.objects.get_or_create(
                    name=name,
                    category=category,
                    defaults=template_data
                )
                if created:
                    created_count += 1
                    self.stdout.write(self.style.SUCCESS(f'✅ Created template: {name} ({len(template_data["paper_types"])} paper types)'))
                else:
                    updated_count += 1
                    self.stdout.write(self.style.SUCCESS(f'🔄 Updated template: {name} ({len(template_data["paper_types"])} paper types)'))
            else:
                template, created = PaperTypeTemplate.objects.get_or_create(
                    name=name,
                    category=category,
                    defaults=template_data
                )
                if created:
                    created_count += 1
                    self.stdout.write(self.style.SUCCESS(f'✅ Created template: {name} ({len(template_data["paper_types"])} paper types)'))
                else:
                    skipped_count += 1
                    self.stdout.write(self.style.WARNING(f'⏭️  Skipped existing template: {name}'))
        
        self.stdout.write(self.style.SUCCESS(
            f'\n📊 Summary: {created_count} created, {updated_count} updated, {skipped_count} skipped'
        ))

