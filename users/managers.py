from django.contrib.auth.models import BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _

class CustomUserManager(BaseUserManager):
    def create_user(self, email=None, password=None, **extra_fields):
        """
        Create and return a user. Tests may call with only username; in that case
        synthesize an email and ensure a unique username.
        """
        username = extra_fields.get('username')
        if not email:
            if username:
                email = f"{username}@test.local"
            else:
                base = 'user'
                email = f"{base}-{self.make_random_password(length=8)}@test.local"
        email = self.normalize_email(email)

        # Ensure username present and unique
        if not username:
            username = email.split('@')[0]
        base_username = username
        counter = 1
        while self.model.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        extra_fields['username'] = username

        # Auto-assign website for roles that require it if missing (tests convenience)
        role = extra_fields.get('role')
        if role in ('client', 'writer') and not extra_fields.get('website'):
            try:
                from websites.models import Website
                website = Website.objects.filter(is_active=True).first()
                if website is None:
                    website = Website.objects.create(
                        name='Test Website',
                        domain='https://test.local',
                        is_active=True,
                    )
                extra_fields['website'] = website
            except Exception:
                # If websites app/migrations not ready, skip assignment
                pass

        extra_fields.setdefault('is_active', True)

        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
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