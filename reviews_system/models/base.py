from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

class ReviewBase(models.Model):
    """Base model for all reviews in the system."""
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="%(class)s_reviews_given"
    )
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True)
    origin = models.CharField(
        max_length=20,
        choices=[("client", "Client"), ("admin", "Admin")],
        default="client"
    )

    is_approved = models.BooleanField(default=False)
    is_shadowed = models.BooleanField(default=False)
    is_flagged = models.BooleanField(default=False)
    flag_reason = models.TextField(blank=True)

    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.reviewer.username} - {self.rating} stars"