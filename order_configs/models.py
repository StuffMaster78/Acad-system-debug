from django.db import models
from websites.models import Website


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
        max_length=100, unique=True,
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
        max_length=50, unique=True,
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
        max_length=100, unique=True,
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
        max_length=50, unique=True,
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
        max_length=50, unique=True,
        help_text="English type (e.g., US English, UK English)."
    )
    code = models.CharField(
        max_length=10, unique=True,
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
