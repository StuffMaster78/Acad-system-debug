"""
Writer Portfolio Model
Opt-in, privacy-aware portfolio for writers that clients can view when assigning.
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
from websites.models import Website


class WriterPortfolio(models.Model):
    """
    Writer portfolio with sample work and achievements.
    Opt-in and privacy-aware.
    """
    VISIBILITY_CHOICES = [
        ('private', 'Private'),
        ('clients_only', 'Clients Only'),
        ('public', 'Public'),
    ]
    
    writer = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='portfolio',
        limit_choices_to={'role': 'writer'}
    )
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='writer_portfolios'
    )
    
    # Portfolio settings
    is_enabled = models.BooleanField(
        default=False,
        help_text="Whether portfolio is enabled (opt-in)"
    )
    visibility = models.CharField(
        max_length=20,
        choices=VISIBILITY_CHOICES,
        default='clients_only',
        help_text="Who can view this portfolio"
    )
    
    # Portfolio content
    bio = models.TextField(
        blank=True,
        help_text="Writer bio/introduction"
    )
    specialties = models.ManyToManyField(
        'order_configs.Subject',
        blank=True,
        related_name='portfolio_specialists',
        help_text="Subjects this writer specializes in"
    )
    years_of_experience = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Years of writing experience"
    )
    education = models.TextField(
        blank=True,
        help_text="Educational background"
    )
    certifications = models.JSONField(
        default=list,
        blank=True,
        help_text="List of certifications: [{'name': '...', 'issuer': '...', 'year': 2020}]"
    )
    
    # Sample work
    sample_works = models.ManyToManyField(
        'writer_management.PortfolioSample',
        blank=True,
        related_name='portfolios',
        help_text="Sample work pieces"
    )
    
    # Statistics (auto-calculated)
    total_orders_completed = models.PositiveIntegerField(
        default=0,
        help_text="Total orders completed"
    )
    average_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.00,
        help_text="Average rating from feedback"
    )
    on_time_delivery_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        help_text="Percentage of orders delivered on time"
    )
    
    # Privacy settings
    show_contact_info = models.BooleanField(
        default=False,
        help_text="Whether to show contact information"
    )
    show_order_history = models.BooleanField(
        default=False,
        help_text="Whether to show order history"
    )
    show_earnings = models.BooleanField(
        default=False,
        help_text="Whether to show earnings information"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('writer', 'website')
        indexes = [
            models.Index(fields=['writer', 'website', 'is_enabled']),
            models.Index(fields=['is_enabled', 'visibility']),
        ]
        verbose_name = "Writer Portfolio"
        verbose_name_plural = "Writer Portfolios"
    
    def __str__(self):
        return f"Portfolio for {self.writer.email}"
    
    def can_view(self, user):
        """Check if a user can view this portfolio."""
        if not self.is_enabled:
            return False
        
        if self.visibility == 'private':
            return user == self.writer
        
        if self.visibility == 'clients_only':
            return user.role == 'client' or user == self.writer
        
        return True  # public
    
    def update_statistics(self):
        """Update portfolio statistics from orders and feedback."""
        from orders.models import Order
        from writer_management.models.feedback import FeedbackHistory
        
        # Total orders completed
        self.total_orders_completed = Order.objects.filter(
            writer=self.writer,
            website=self.website,
            status='completed'
        ).count()
        
        # Average rating
        try:
            history = FeedbackHistory.objects.get(user=self.writer, website=self.website)
            self.average_rating = history.average_rating or 0
        except FeedbackHistory.DoesNotExist:
            self.average_rating = 0
        
        # On-time delivery rate
        from django.db.models import F
        completed_orders = Order.objects.filter(
            writer=self.writer,
            website=self.website,
            status='completed',
            submitted_at__isnull=False
        )
        
        if completed_orders.exists():
            from django.db.models.functions import Coalesce
            # Use writer_deadline if available, otherwise fall back to client_deadline
            on_time = completed_orders.filter(
                submitted_at__lte=Coalesce('writer_deadline', 'client_deadline')
            ).count()
            self.on_time_delivery_rate = (on_time / completed_orders.count()) * 100
        else:
            self.on_time_delivery_rate = 0
        
        self.save(update_fields=[
            'total_orders_completed',
            'average_rating',
            'on_time_delivery_rate'
        ])


class PortfolioSample(models.Model):
    """
    Sample work piece for writer portfolio.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='portfolio_samples'
    )
    writer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='portfolio_samples',
        limit_choices_to={'role': 'writer'}
    )
    
    # Sample information
    title = models.CharField(
        max_length=255,
        help_text="Title of the sample work"
    )
    description = models.TextField(
        blank=True,
        help_text="Description of the sample"
    )
    
    # Source order (if from actual order)
    source_order = models.ForeignKey(
        'orders.Order',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='portfolio_samples',
        help_text="The order this sample came from (if applicable)"
    )
    
    # File/content
    file = models.FileField(
        upload_to='portfolio_samples/',
        null=True,
        blank=True,
        help_text="Sample file (anonymized if from order)"
    )
    content_preview = models.TextField(
        blank=True,
        help_text="Text preview of the sample"
    )
    
    # Metadata
    subject = models.ForeignKey(
        'order_configs.Subject',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    type_of_work = models.ForeignKey(
        'order_configs.TypeOfWork',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    # Privacy
    is_anonymized = models.BooleanField(
        default=True,
        help_text="Whether client information has been removed"
    )
    is_featured = models.BooleanField(
        default=False,
        help_text="Whether this is a featured sample"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_featured', '-created_at']
        indexes = [
            models.Index(fields=['writer', 'website']),
            models.Index(fields=['is_featured']),
        ]
        verbose_name = "Portfolio Sample"
        verbose_name_plural = "Portfolio Samples"
    
    def __str__(self):
        return f"Sample: {self.title} - {self.writer.email}"

