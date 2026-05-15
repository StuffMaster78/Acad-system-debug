from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from writer_management.models.requests import (
    WriterOrderRequest, WriterOrderTake,
    WriterReassignmentRequest
)
User = get_user_model()


class BaseHistory(models.Model):
    """"
    Abstract base class for tracking changes to models.
    Contains fields for tracking who made the change, when it was made,
    the type of change, and any notes.
    """
    changed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        related_name="%(class)s_changes"
    )
    change_date = models.DateTimeField(auto_now_add=True)
    change_type = models.CharField(
        max_length=50,
        choices=[("Created", "Created"), ("Updated", "Updated"), ("Deleted", "Deleted")]
    )
    notes = models.TextField(blank=True, null=True)

    class Meta:
        abstract = True
        ordering = ['-change_date']


class WriterOrderRequestHistory(BaseHistory):
    """
    Tracks changes to writer order requests.
    Useful for auditing and tracking request history.
    """
    request = models.ForeignKey(
        WriterOrderRequest, on_delete=models.CASCADE,
        related_name="history"
    )


    def __str__(self):
        return f"History: {self.request.writer.user.username} for Order {self.request.order.id} ({self.change_type})"
    
    class Meta:
        verbose_name = "Writer Order Request History"
        verbose_name_plural = "Writer Order Request Histories"
        ordering = ['-change_date']


class WriterOrderTakeHistory(BaseHistory):
    """
    Tracks changes to writer order takes.
    Useful for auditing and tracking take history.
    """
    take = models.ForeignKey(
        WriterOrderTake, on_delete=models.CASCADE,
        related_name="history"
    )
    
    def __str__(self):
        return f"History: {self.take.writer.user.username} - Order {self.take.order.id} ({self.change_type})"
    
    class Meta:
        verbose_name = "Writer Order Take History"
        verbose_name_plural = "Writer Order Take Histories"
        ordering = ['-change_date']


class WriterReassignmentHistory(BaseHistory):
    """
    Tracks reassignment requests made by writers.
    Useful for auditing and tracking reassignment history.
    """
    request = models.ForeignKey(
        WriterReassignmentRequest, on_delete=models.CASCADE,
        related_name="reassignment_history"
    )

    def __str__(self):
        return f"Reassignment History: {self.request.writer.user.username} for Order {self.request.order.id} ({self.change_type})"
    
    class Meta:
        verbose_name = "Writer Reassignment History"
        verbose_name_plural = "Writer Reassignment Histories"
        ordering = ['-change_date']