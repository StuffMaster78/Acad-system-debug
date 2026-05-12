from cryptography.fernet import Fernet
from django.conf import settings


class EncryptionService:
    """
    Symmetric encryption using Fernet.
    """

    @staticmethod
    def _get_fernet() -> Fernet:
        return Fernet(settings.FIELD_ENCRYPTION_KEY)

    @classmethod
    def encrypt(cls, value: str) -> str:
        if not value:
            return value
        return cls._get_fernet().encrypt(value.encode()).decode()

    @classmethod
    def decrypt(cls, value: str) -> str:
        if not value:
            return value
        return cls._get_fernet().decrypt(value.encode()).decode()