from django.db import models
from core.models.base import WebsiteSpecificBaseModel


class PaperType(WebsiteSpecificBaseModel):
    """
    Represents types of papers (e.g., Essay, Report).
    """
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


class FormattingStyle(WebsiteSpecificBaseModel):
    """
    Represents formatting styles (e.g., APA, MLA).
    """
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


class Subject(WebsiteSpecificBaseModel):
    """
    Represents the subject of the order (e.g., Nursing, Physics).
    """
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


class TypeOfWork(WebsiteSpecificBaseModel):
    """
    Represents types of work (e.g., Writing, Editing).
    """
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


class EnglishType(WebsiteSpecificBaseModel):
    """
    Represents English types (e.g., US English, UK English).
    """
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


class WriterDeadlineConfig(WebsiteSpecificBaseModel):
    """
    Configuration for writer deadlines.
    """
    writer_deadline_percentage = models.PositiveIntegerField(
        default=80,
        help_text="Percentage of the client's deadline given to the writer (e.g., 80%)."
    )

    def __str__(self):
        return f"Writer Deadline: {self.writer_deadline_percentage}%"

    class Meta:
        verbose_name = "Writer Deadline Config"
        verbose_name_plural = "Writer Deadline Configs"