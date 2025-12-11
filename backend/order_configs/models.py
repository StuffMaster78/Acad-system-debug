from django.db import models
from websites.models import Website
import json


class CriticalDeadlineSetting(models.Model):
    """
    Stores the threshold (in hours) before the deadline when an order
    is considered CRITICAL (urgent).
    """
    critical_deadline_threshold_hours = models.PositiveIntegerField(
        default=8,
        help_text="Hours before deadline when order becomes critical"
    )

    class Meta:
        verbose_name = "Critical Deadline Setting"
        verbose_name_plural = "Critical Deadline Settings"

    def __str__(self):
        return f"CriticalDeadlineSetting: {self.threshold_hours} hours"


class EditingRequirementConfig(models.Model):
    """
    Configuration for when orders should undergo editing.
    Admin can configure editing requirements per website.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='editing_requirements',
        help_text="Website this configuration applies to"
    )
    
    # Global settings
    enable_editing_by_default = models.BooleanField(
        default=True,
        help_text="Enable editing for orders by default (unless urgent or explicitly disabled)"
    )
    
    skip_editing_for_urgent = models.BooleanField(
        default=True,
        help_text="Skip editing for urgent orders (deadline < 24 hours or is_urgent=True)"
    )
    
    allow_editing_for_early_submissions = models.BooleanField(
        default=True,
        help_text="Allow editing for orders submitted before deadline"
    )
    
    early_submission_hours_threshold = models.PositiveIntegerField(
        default=24,
        help_text="Hours before deadline to consider submission 'early' (for editing eligibility)"
    )
    
    # Order type specific settings
    editing_required_for_first_orders = models.BooleanField(
        default=True,
        help_text="Require editing for client's first order"
    )
    
    editing_required_for_high_value = models.BooleanField(
        default=True,
        help_text="Require editing for high-value orders"
    )
    
    high_value_threshold = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=300.00,
        help_text="Order value threshold (USD) to consider 'high value'"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_editing_configs',
        help_text="Admin who created this configuration"
    )
    
    class Meta:
        verbose_name = "Editing Requirement Config"
        verbose_name_plural = "Editing Requirement Configs"
        unique_together = ('website',)
    
    def __str__(self):
        return f"Editing Config for {self.website.domain}"


class AcademicLevel(models.Model):
    """
    Represents types of Academic Levels, tied to specific Websites.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='academic_levels'
    )
    name = models.CharField(
        max_length=100,
        help_text="Academic Level (e.g., University, College, Masters, BSN, etc)."
    )

    class Meta:
        unique_together = ('website', 'name')
        verbose_name = 'Academic Level'
        verbose_name_plural = 'Academic Levels'

    def __str__(self):
        return f"{self.name} ({self.website.domain})"


class PaperType(models.Model):
    """
    Represents types of papers (e.g., Essay, Report).
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='paper_type'
    )
    name = models.CharField(
        max_length=100,
        help_text="Type of paper (e.g., Essay, Report)."
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = "Paper Type"
        verbose_name_plural = "Paper Types"
        unique_together = ('website', 'name')


class FormattingandCitationStyle(models.Model):
    """
    Represents formatting and citation styles (e.g., APA, MLA).
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='formatting'
    )
    name = models.CharField(
        max_length=50,
        help_text="Formatting style (e.g., APA, MLA)."
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        unique_together = ('website', 'name')
        verbose_name = "Formatting and Citation Style"
        verbose_name_plural = "Formatting and Citation Styles"


class Subject(models.Model):
    """
    Represents the subject of the order (e.g., Nursing, Physics).
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='subject'
    )
    name = models.CharField(
        max_length=100,
        help_text="Subject (e.g., Nursing, Physics)."
    )
    is_technical = models.BooleanField(
        default=False, 
        help_text="Is this subject technical?"
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = "Subject"
        verbose_name_plural = "Subjects"
        unique_together = ('website', 'name')


class TypeOfWork(models.Model):
    """
    Represents types of work (e.g., Writing, Editing).
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='type_of_work'
    )
    name = models.CharField(
        max_length=50,
        help_text="Type of work (e.g., Writing, Editing)."
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = "Type of Work"
        verbose_name_plural = "Types of Work"
        unique_together = ('website', 'name')


class EnglishType(models.Model):
    """
    Represents English types (e.g., US English, UK English).
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='english_type'
    )
    name = models.CharField(
        max_length=50,
        help_text="English type (e.g., US English, UK English)."
    )
    code = models.CharField(
        max_length=10,
        help_text="Short code (e.g., US, UK)."
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = "English Type"
        verbose_name_plural = "English Types"
        unique_together = ('website', 'name', 'code')


class WriterDeadlineConfig(models.Model):
    """
    Configuration for writer deadlines.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='writer_deadline_threshold'
    )
    writer_deadline_percentage = models.PositiveIntegerField(
        default=80,
        help_text="Percentage of the client's deadline given to the writer (e.g., 80%)."
    )

    def __str__(self):
        return f"Writer Deadline: {self.writer_deadline_percentage}%"

    class Meta:
        unique_together = ('website', 'writer_deadline_percentage')
        ordering = ['writer_deadline_percentage']
        verbose_name = "Writer Deadline Config"
        verbose_name_plural = "Writer Deadline Configs"


class RevisionPolicyConfig(models.Model):
    """
    Configuration for revision deadline threshold in days. 
    Days after which revision must be paid.
    """
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name='revision_policies'
    )
    name = models.CharField(max_length=255)
    free_revision_days = models.PositiveIntegerField(default=14)
    active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('website', 'active')
        verbose_name = "Revision Policy Config"
        verbose_name_plural = "Revision Policy Configs"


class SubjectTemplate(models.Model):
    """
    Global subject templates that can be cloned to websites.
    Templates are categorized by field (Nursing, Computing, General, etc.)
    """
    CATEGORY_CHOICES = [
        ('general', 'General'),
        ('humanities', 'Humanities'),
        ('sciences', 'Sciences'),
        ('health_sciences', 'Health Sciences'),
        ('nursing', 'Nursing & Healthcare'),
        ('computing', 'Computing & Computer Science'),
        ('engineering', 'Engineering'),
        ('business', 'Business'),
        ('education', 'Education'),
        ('social_sciences', 'Social Sciences'),
    ]
    
    name = models.CharField(
        max_length=200,
        help_text="Template name (e.g., 'Nursing & Healthcare', 'Computer Science')"
    )
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default='general',
        help_text="Category of this template"
    )
    description = models.TextField(
        blank=True,
        help_text="Description of what this template includes"
    )
    subjects = models.JSONField(
        default=list,
        help_text="List of subjects as [{'name': 'Subject Name', 'is_technical': bool}, ...]"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this template is active and available for cloning"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_subject_templates',
        help_text="User who created this template"
    )
    
    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"
    
    def clone_to_website(self, website, skip_existing=True):
        """
        Clone this template's subjects to a website.
        
        Args:
            website: Website instance to clone to
            skip_existing: If True, skip subjects that already exist
            
        Returns:
            dict with counts of created/updated/skipped subjects
        """
        from .models import Subject
        
        counts = {
            'created': 0,
            'updated': 0,
            'skipped': 0,
            'errors': []
        }
        
        for subject_data in self.subjects:
            if isinstance(subject_data, dict):
                subject_name = subject_data.get('name', '')
                is_technical = subject_data.get('is_technical', False)
            elif isinstance(subject_data, (list, tuple)) and len(subject_data) == 2:
                subject_name, is_technical = subject_data
            else:
                subject_name = str(subject_data)
                is_technical = False
            
            if not subject_name:
                continue
            
            try:
                if skip_existing and Subject.objects.filter(website=website, name=subject_name).exists():
                    counts['skipped'] += 1
                    continue
                
                subject, created = Subject.objects.get_or_create(
                    website=website,
                    name=subject_name,
                    defaults={'is_technical': is_technical}
                )
                
                if created:
                    counts['created'] += 1
                else:
                    # Update if technical status changed
                    if subject.is_technical != is_technical:
                        subject.is_technical = is_technical
                        subject.save()
                        counts['updated'] += 1
                    else:
                        counts['skipped'] += 1
            except Exception as e:
                counts['errors'].append(f"Error creating {subject_name}: {str(e)}")
        
        return counts
    
    class Meta:
        ordering = ['category', 'name']
        verbose_name = "Subject Template"
        verbose_name_plural = "Subject Templates"
        unique_together = ('name', 'category')


class PaperTypeTemplate(models.Model):
    """
    Global paper type templates that can be cloned to websites.
    Templates are categorized by academic level and assignment type.
    """
    CATEGORY_CHOICES = [
        ('general', 'General'),
        ('high_school', 'High School'),
        ('undergraduate', 'Undergraduate'),
        ('graduate', 'Graduate'),
        ('professional', 'Professional'),
        ('nursing', 'Nursing & Healthcare'),
        ('technical', 'Technical & Engineering'),
        ('business', 'Business'),
        ('law', 'Law & Legal'),
    ]
    
    name = models.CharField(
        max_length=200,
        help_text="Template name (e.g., 'High School Assignments', 'Graduate Research Papers')"
    )
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default='general',
        help_text="Category of this template"
    )
    description = models.TextField(
        blank=True,
        help_text="Description of what this template includes"
    )
    paper_types = models.JSONField(
        default=list,
        help_text="List of paper types as ['Paper Type Name', ...]"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this template is active and available for cloning"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_paper_type_templates',
        help_text="User who created this template"
    )
    
    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"
    
    def clone_to_website(self, website, skip_existing=True):
        """
        Clone this template's paper types to a website.
        
        Args:
            website: Website instance to clone to
            skip_existing: If True, skip paper types that already exist
            
        Returns:
            dict with counts of created/updated/skipped paper types
        """
        from .models import PaperType
        
        counts = {
            'created': 0,
            'updated': 0,
            'skipped': 0,
            'errors': []
        }
        
        for paper_type_name in self.paper_types:
            if not paper_type_name or not isinstance(paper_type_name, str):
                continue
            
            try:
                if skip_existing and PaperType.objects.filter(website=website, name=paper_type_name).exists():
                    counts['skipped'] += 1
                    continue
                
                paper_type, created = PaperType.objects.get_or_create(
                    website=website,
                    name=paper_type_name,
                    defaults={}
                )
                
                if created:
                    counts['created'] += 1
                else:
                    counts['skipped'] += 1
            except Exception as e:
                counts['errors'].append(f"Error creating {paper_type_name}: {str(e)}")
        
        return counts
    
    class Meta:
        ordering = ['category', 'name']
        verbose_name = "Paper Type Template"
        verbose_name_plural = "Paper Type Templates"
        unique_together = ('name', 'category')


class TypeOfWorkTemplate(models.Model):
    """
    Global type of work templates that can be cloned to websites.
    Templates are categorized by service type.
    """
    CATEGORY_CHOICES = [
        ('general', 'General'),
        ('writing', 'Writing Services'),
        ('editing', 'Editing & Revision'),
        ('proofreading', 'Proofreading & Correction'),
        ('rewriting', 'Rewriting & Paraphrasing'),
        ('plagiarism', 'Plagiarism Services'),
        ('formatting', 'Formatting & Styling'),
        ('research', 'Research Services'),
        ('analysis', 'Analysis Services'),
        ('review', 'Review & Critique'),
        ('grading', 'Grading & Marking'),
        ('technical', 'Technical Services'),
    ]
    
    name = models.CharField(
        max_length=200,
        help_text="Template name (e.g., 'Complete Writing Services', 'Editing & Proofreading')"
    )
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default='general',
        help_text="Category of this template"
    )
    description = models.TextField(
        blank=True,
        help_text="Description of what this template includes"
    )
    types_of_work = models.JSONField(
        default=list,
        help_text="List of types of work as ['Type Name', ...]"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this template is active and available for cloning"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_type_of_work_templates',
        help_text="User who created this template"
    )
    
    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"
    
    def clone_to_website(self, website, skip_existing=True):
        """
        Clone this template's types of work to a website.
        
        Args:
            website: Website instance to clone to
            skip_existing: If True, skip types that already exist
            
        Returns:
            dict with counts of created/updated/skipped types
        """
        from .models import TypeOfWork
        
        counts = {
            'created': 0,
            'updated': 0,
            'skipped': 0,
            'errors': []
        }
        
        for work_type_name in self.types_of_work:
            if not work_type_name or not isinstance(work_type_name, str):
                continue
            
            try:
                if skip_existing and TypeOfWork.objects.filter(website=website, name=work_type_name).exists():
                    counts['skipped'] += 1
                    continue
                
                work_type, created = TypeOfWork.objects.get_or_create(
                    website=website,
                    name=work_type_name,
                    defaults={}
                )
                
                if created:
                    counts['created'] += 1
                else:
                    counts['skipped'] += 1
            except Exception as e:
                counts['errors'].append(f"Error creating {work_type_name}: {str(e)}")
        
        return counts
    
    class Meta:
        ordering = ['category', 'name']
        verbose_name = "Type of Work Template"
        verbose_name_plural = "Type of Work Templates"
        unique_together = ('name', 'category')
