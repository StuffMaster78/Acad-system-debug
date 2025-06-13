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


class FormattingStyle(models.Model):
    """
    Represents formatting styles (e.g., APA, MLA).
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
        verbose_name = "Formatting Style"
        verbose_name_plural = "Formatting Styles"


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
        verbose_name = "Writer Deadline Config"
        verbose_name_plural = "Writer Deadline Configs"


class RevisionPolicyConfig(models.Model):
    """
    Configuration for revision deadline threshold in days. 
    Days after which revision must be paid.
    """
    website = models.ForeignKey(
        'website.Website',
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