from django.contrib.auth.models import BaseUserManager

class ActiveManager(BaseUserManager):
    def create_user(self, username, email=None, password=None, **extra_fields):
        """
        Create and return a regular user.
        """
        if not username:
            raise ValueError("The Username field must be set")
        email = self.normalize_email(email)
        extra_fields.setdefault("is_active", True)
        
        # Default role to client if not provided
        if "role" not in extra_fields:
            extra_fields["role"] = "client"

        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        """
        Create and return a superuser.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "superadmin")  # Ensure superuser is assigned the correct role

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        if extra_fields.get("role") != "superadmin":
            raise ValueError("Superuser must have role='superadmin'.")

        return self.create_user(username, email, password, **extra_fields)