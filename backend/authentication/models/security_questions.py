"""
Security Questions Models
Handles security questions for account recovery.
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinLengthValidator
from cryptography.fernet import Fernet
from django.conf import settings
import base64
import os
from websites.models import Website


def get_encryption_key():
    """Get or create encryption key for security question answers."""
    key = getattr(settings, 'SECURITY_QUESTIONS_ENCRYPTION_KEY', None)
    if not key:
        # Generate a key if not set (for development)
        key = Fernet.generate_key().decode()
    elif isinstance(key, str):
        key = key.encode()
    return key


class SecurityQuestion(models.Model):
    """
    Predefined security questions that users can choose from.
    """
    question_text = models.CharField(
        max_length=500,
        unique=True,
        help_text=_("The security question text")
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_("Whether this question is available for selection")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['question_text']
        verbose_name = _("Security Question")
        verbose_name_plural = _("Security Questions")
    
    def __str__(self):
        return self.question_text


class UserSecurityQuestion(models.Model):
    """
    User's security questions and encrypted answers.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='security_questions',
        help_text=_("User who owns this security question")
    )
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='user_security_questions',
        help_text=_("Website context")
    )
    question = models.ForeignKey(
        SecurityQuestion,
        on_delete=models.CASCADE,
        related_name='user_questions',
        help_text=_("The security question")
    )
    custom_question = models.CharField(
        max_length=500,
        blank=True,
        help_text=_("Custom question if user chose to write their own")
    )
    encrypted_answer = models.TextField(
        help_text=_("Encrypted answer to the security question")
    )
    answer_hash = models.CharField(
        max_length=255,
        help_text=_("Hash of answer for quick comparison (not reversible)")
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_("Whether this question is active")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'website', 'question']
        indexes = [
            models.Index(fields=['user', 'website', 'is_active']),
        ]
        verbose_name = _("User Security Question")
        verbose_name_plural = _("User Security Questions")
    
    def set_answer(self, answer: str):
        """Encrypt and store the answer."""
        from django.contrib.auth.hashers import make_password
        key = get_encryption_key()
        fernet = Fernet(key)
        
        # Encrypt answer
        encrypted = fernet.encrypt(answer.encode())
        self.encrypted_answer = encrypted.decode()
        
        # Store hash for quick comparison
        self.answer_hash = make_password(answer)
    
    def verify_answer(self, answer: str) -> bool:
        """Verify the answer."""
        from django.contrib.auth.hashers import check_password
        
        # First check hash for quick comparison
        if not check_password(answer, self.answer_hash):
            return False
        
        # Then verify encryption (double-check)
        try:
            key = get_encryption_key()
            fernet = Fernet(key)
            decrypted = fernet.decrypt(self.encrypted_answer.encode()).decode()
            return decrypted.lower().strip() == answer.lower().strip()
        except Exception:
            return False
    
    def get_question_text(self) -> str:
        """Get the question text (predefined or custom)."""
        return self.custom_question if self.custom_question else self.question.question_text
    
    def __str__(self):
        return f"Security question for {self.user.email}"

