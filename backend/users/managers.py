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

    def create_user(
        self,
        username: str | None = None,
        email: str | None = None,
        password: str | None = None,
        **extra_fields: Any,
    ):
        """Create and return a user."""
        if not email:
            if username:
                email = f"{username}@test.local"
            else:
                base = "user"
                email = (
                    f"{base}-{self.make_random_password(length=8)}@test.local"
                )

        email = self.normalize_email(email)

        if not username:
            username = extra_fields.get("username")

        if not username:
            username = email.split("@")[0]

        base_username = username
        counter = 1

        while self.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        extra_fields["username"] = username

        role = extra_fields.get("role")
        if role in ("client", "writer") and not extra_fields.get("website"):
            try:
                from websites.models.websites import Website

                website = Website.objects.filter(is_active=True).first()
                if website is None:
                    website = Website.objects.create(
                        name="Test Website",
                        domain="https://test.local",
                        is_active=True,
                    )
                extra_fields["website"] = website
            except Exception:
                pass

        extra_fields.setdefault("is_active", True)

        model_cls = self.model
        if model_cls is None:
            raise ValueError("CustomUserManager is not bound to a model.")

        user = model_cls(email=email, **extra_fields)

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)
        return user

    def create_superuser(
        self,
        username: str | None = None,
        email: str | None = None,
        password: str | None = None,
        **extra_fields: Any,
    ):
        """Create and return a superuser."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))

        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))

        return self.create_user(
            username=username,
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
    ):
        """Create and return a writer user."""
        if not website:
            raise ValueError(_("A website must be assigned to the writer."))

        extra_fields.setdefault("role", "writer")
        extra_fields["website"] = website

        return self.create_user(
            username=extra_fields.get("username"),
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
    ):
        """Create and return a client user."""
        if not website:
            raise ValueError(_("A website must be assigned to the client."))

        extra_fields.setdefault("role", "client")
        extra_fields["website"] = website

        return self.create_user(
            username=extra_fields.get("username"),
            email=email,
            password=password,
            **extra_fields,
        )


class ActiveManager(models.Manager):
    """Return only active users."""

    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)