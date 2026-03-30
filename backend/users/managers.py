from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _

if TYPE_CHECKING:
    from users.models.user import User


class CustomUserManager(BaseUserManager["User"]):
    """Manager for the custom user model."""

    use_in_migrations = True

    def _generate_unique_username(self, base_username: str) -> str:
        """
        Generate a unique username from a base value.
        """
        username = base_username
        counter = 1

        while self.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        return username

    def _create_user(
        self,
        email: str,
        password: str | None = None,
        **extra_fields: Any,
    ) -> User:
        """
        Create and save a user with the given email and password.
        """
        if not email:
            raise ValueError(_("The email field must be set."))

        email = self.normalize_email(email)

        username = extra_fields.get("username")
        if not username:
            base_username = email.split("@")[0]
            username = self._generate_unique_username(base_username)

        extra_fields["username"] = username
        extra_fields.setdefault("is_active", True)

        user = self.model(email=email, **extra_fields)

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)
        return user

    def create_user(
        self,
        email: str,
        password: str | None = None,
        **extra_fields: Any,
    ) -> User:
        """
        Create and return a regular user.
        """
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(
            email=email,
            password=password,
            **extra_fields,
        )

    def create_superuser(
        self,
        email: str,
        password: str | None = None,
        **extra_fields: Any,
    ) -> User:
        """
        Create and return a superuser.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("role", "superadmin")

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))

        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))

        return self._create_user(
            email=email,
            password=password,
            **extra_fields,
        )

    def create_writer(
        self,
        email: str,
        password: str | None = None,
        website=None,
        **extra_fields: Any,
    ) -> User:
        """
        Create and return a writer user.
        """
        if website is None:
            raise ValueError(_("A website must be assigned to the writer."))

        extra_fields.setdefault("role", "writer")
        extra_fields["website"] = website

        return self._create_user(
            email=email,
            password=password,
            **extra_fields,
        )

    def create_client(
        self,
        email: str,
        password: str | None = None,
        website=None,
        **extra_fields: Any,
    ) -> User:
        """
        Create and return a client user.
        """
        if website is None:
            raise ValueError(_("A website must be assigned to the client."))

        extra_fields.setdefault("role", "client")
        extra_fields["website"] = website

        return self._create_user(
            email=email,
            password=password,
            **extra_fields,
        )


class ActiveManager(models.Manager["User"]):
    """Return only active users."""

    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)