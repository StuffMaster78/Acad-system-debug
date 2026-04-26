from __future__ import annotations

from django.core.files.storage import default_storage


class FileStorageBackend:
    """
    Thin wrapper around Django's configured storage backend.

    This keeps file services decoupled from a concrete storage provider.
    Local storage, S3, and DigitalOcean Spaces can all sit behind the
    same service boundary.
    """

    @staticmethod
    def save(
        *,
        storage_key: str,
        content,
    ) -> str:
        """
        Save content to storage and return the final storage name.
        """

        return default_storage.save(storage_key, content)

    @staticmethod
    def exists(*, storage_name: str) -> bool:
        """
        Return whether a file exists in storage.
        """

        return default_storage.exists(storage_name)

    @staticmethod
    def delete(*, storage_name: str) -> None:
        """
        Delete a file from storage.

        Callers should only use this after retention and business rules
        have allowed physical deletion.
        """

        default_storage.delete(storage_name)

    @staticmethod
    def size(*, storage_name: str) -> int:
        """
        Return the size of a stored file in bytes.
        """

        return default_storage.size(storage_name)

    @staticmethod
    def open(*, storage_name: str, mode: str = "rb"):
        """
        Open a stored file using Django storage.
        """

        return default_storage.open(storage_name, mode)