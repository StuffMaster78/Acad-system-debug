from django.contrib.auth.models import AbstractUser
from .managers import ActiveManager
from core.models.base import WebsiteSpecificBaseModel
from django.core.exceptions import ValidationError
from django.db import models

class User(WebsiteSpecificBaseModel, AbstractUser):
    """
    Custom user model with roles for admin, editors, support, writers, and clients.
    """
    objects = ActiveManager()
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('editor', 'Editor'),
        ('support', 'Support'),
        ('writer', 'Writer'),
        ('client', 'Client'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='client')
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    bio = models.TextField(null=True, blank=True)  # Optional bio field for writers/editors
    phone_number = models.CharField(max_length=15, null=True, blank=True)  # Contact number

    # Fields for writers
    verification_documents = models.JSONField(null=True, blank=True)  # Store uploaded documents
    rating = models.FloatField(default=0.0)  # Average rating for writers

    # Fields for clients
    company_name = models.CharField(max_length=255, null=True, blank=True)  # For clients with businesses

    def clean(self):
        """
        Add custom validation to enforce website assignment only for clients.
        """
        if self.role != 'client' and self.website is not None:
            raise ValidationError("Only clients can be associated with a website.")
        super().clean()

    def __str__(self):
        return f"{self.username} ({self.role})"