from __future__ import annotations

from typing import cast

from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models

from users.managers import ActiveManager, CustomUserManager


class UserRole(models.TextChoices):
    """Temporary role choices for the user model."""

    SUPERADMIN = "superadmin", "Super Admin"
    ADMIN = "admin", "Admin"
    EDITOR = "editor", "Editor"
    SUPPORT = "support", "Support"
    WRITER = "writer", "Writer"
    CLIENT = "client", "Client"


class User(AbstractUser):
    """
    Core identity model.

    Keep this model small and boring.
    Do not store auth security state, privacy state, or subscription state
    here.
    """

    email = models.EmailField(
        unique=True,
        db_index=True,
    )
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.CLIENT,
        db_index=True,
    )
    website = models.ForeignKey(
        "websites.Website",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="users",
    )
    phone_number = models.CharField(
        max_length=32,
        blank=True,
    )
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = cast(UserManager["User"], CustomUserManager())
    active_objects = ActiveManager()

    class Meta:
        ordering = ["id"]
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self) -> str:
        return self.email or self.username

    @property
    def full_name(self) -> str:
        """Return full name or fall back to username."""
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name or self.username