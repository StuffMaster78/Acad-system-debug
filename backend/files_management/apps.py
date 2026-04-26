from django.apps import AppConfig


class FilesManagementConfig(AppConfig):
    """
    Application configuration for the central file management domain.

    The files_management app owns shared file infrastructure for the
    platform. It is responsible for file metadata, attachment records,
    versioning, download logs, external links, deletion workflows, and
    future processing hooks such as scanning, previews, and OCR.

    Business rules that belong to orders, messages, CMS, profiles, or
    payments should remain inside their respective domain apps.
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "files_management"
    verbose_name = "Files Management"

    def ready(self) -> None:
        """
        Register built-in file access policies.
        """

        from files_management.policies import register_default_file_policies

        register_default_file_policies()