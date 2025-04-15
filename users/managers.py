from django.contrib.auth.models import BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and return a user with an email and password.
        """
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True)
        
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and return a superuser with an email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)
    
    def create_writer(self, email, password=None, website=None, **extra_fields):
        """
        Create and return a writer user.
        """
        if not website:
            raise ValueError(_('A website must be assigned to the writer.'))

        extra_fields.setdefault('role', 'writer')
        user = self.create_user(email, password, **extra_fields)
        user.website = website  # Ensure the writer is assigned a website
        user.save(using=self._db)
        return user

    def create_client(self, email, password=None, website=None, **extra_fields):
        """
        Create and return a client user.
        """
        if not website:
            raise ValueError(_('A website must be assigned to the client.'))

        extra_fields.setdefault('role', 'client')
        user = self.create_user(email, password, **extra_fields)
        user.website = website  # Ensure the client is assigned a website
        user.save(using=self._db)
        return user
    
    def active_users(self):
        """Return active users."""
        return self.filter(is_active=True)

# ActiveManager for filtering only active users
class ActiveManager(models.Manager):
    """
    Returns only active users.
    """
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)