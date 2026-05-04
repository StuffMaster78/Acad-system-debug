from __future__ import annotations

from django.core.exceptions import ValidationError


class ClassFileGuardService:
    """
    Guardrails for class files.
    """

    ALLOWED_CATEGORIES = {
        "client_upload",
        "writer_upload",
        "portal_download",
        "portal_upload",
        "final_deliverable",
        "supporting_material",
        "access_related",
        "admin_internal",
    }

    ALLOWED_VISIBILITIES = {
        "client_visible",
        "writer_visible",
        "staff_only",
        "internal_only",
    }

    @classmethod
    def validate_file_context(
        cls,
        *,
        category: str,
        visibility: str,
        uploaded_by,
    ) -> None:
        """
        Validate category, visibility, and uploader permissions.
        """
        if category not in cls.ALLOWED_CATEGORIES:
            raise ValidationError("Invalid class file category.")

        if visibility not in cls.ALLOWED_VISIBILITIES:
            raise ValidationError("Invalid class file visibility.")

        if visibility in {"staff_only", "internal_only"}:
            is_staff = getattr(uploaded_by, "is_staff", False)
            is_superuser = getattr(uploaded_by, "is_superuser", False)

            if not is_staff and not is_superuser:
                raise ValidationError(
                    "Only staff can upload internal class files."
                )