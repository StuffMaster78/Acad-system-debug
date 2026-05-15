"""
Model for storing writer-specific order priorities.

Allows writers to mark orders as high, medium, or low priority
for better task management and organization.
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class WriterOrderPriority(models.Model):
    """
    Stores priority level assigned by writer to an order.
    
    Each writer can set a priority for each order they're
    assigned to, helping them organize their workload.
    """
    PRIORITY_CHOICES = [
        ('high', 'High Priority'),
        ('medium', 'Medium Priority'),
        ('low', 'Low Priority'),
    ]
    
    writer = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='order_priorities',
        limit_choices_to={'role': 'writer'},
        help_text="The writer who set this priority."
    )
    
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.CASCADE,
        related_name='writer_priorities',
        help_text="The order this priority applies to."
    )
    
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium',
        help_text="Priority level: high, medium, or low."
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the priority was first set."
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the priority was last updated."
    )
    
    notes = models.TextField(
        blank=True,
        null=True,
        max_length=500,
        help_text=(
            "Optional notes about why this priority "
            "was set."
        )
    )
    
    class Meta:
        verbose_name = "Writer Order Priority"
        verbose_name_plural = "Writer Order Priorities"
        unique_together = ['writer', 'order']
        indexes = [
            models.Index(
                fields=['writer', 'priority']
            ),
            models.Index(
                fields=['order', 'priority']
            ),
        ]
        ordering = ['-updated_at']
    
    def __str__(self):
        return (
            f"{self.writer.username} - "
            f"Order #{self.order.id} - "
            f"{self.priority}"
        )
    
    def get_priority_value(self):
        """
        Get numeric value for sorting.
        
        Returns:
            int: 3 for high, 2 for medium, 1 for low
        """
        priority_map = {
            'high': 3,
            'medium': 2,
            'low': 1,
        }
        return priority_map.get(self.priority, 2)
