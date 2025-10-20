"""
Multi-language template support system.
"""
from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional, Tuple
from django.db import models
from django.utils import timezone
from django.core.cache import cache
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


class TemplateTranslation(models.Model):
    """Store template translations for different languages."""
    
    event_key = models.CharField(max_length=100, db_index=True)
    template_type = models.CharField(max_length=20, choices=[
        ('class_based', 'Class Based'),
        ('database', 'Database'),
        ('generic', 'Generic'),
        ('emergency', 'Emergency')
    ])
    language_code = models.CharField(max_length=10, db_index=True)
    website_id = models.IntegerField(null=True, blank=True, db_index=True)
    
    # Translated content
    title = models.CharField(max_length=200, blank=True)
    text_content = models.TextField(blank=True)
    html_content = models.TextField(blank=True)
    
    # Metadata
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'users.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    
    class Meta:
        unique_together = [
            'event_key', 'template_type', 'language_code', 'website_id'
        ]
        indexes = [
            models.Index(fields=['event_key', 'language_code']),
            models.Index(fields=['template_type', 'language_code']),
            models.Index(fields=['website_id', 'language_code']),
        ]
    
    def __str__(self):
        return f"{self.event_key} ({self.language_code})"


class LanguagePreference(models.Model):
    """Store user language preferences."""
    
    user = models.OneToOneField(
        'users.User',
        on_delete=models.CASCADE,
        related_name='language_preference'
    )
    primary_language = models.CharField(max_length=10, default='en')
    fallback_languages = models.JSONField(default=list, blank=True)
    auto_detect = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.primary_language}"
    
    @property
    def language_chain(self) -> List[str]:
        """Get ordered list of languages to try."""
        languages = [self.primary_language]
        languages.extend(self.fallback_languages)
        
        # Add English as final fallback if not already present
        if 'en' not in languages:
            languages.append('en')
        
        return languages


class WebsiteLanguageConfig(models.Model):
    """Configure supported languages per website."""
    
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name='language_configs'
    )
    language_code = models.CharField(max_length=10)
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    display_name = models.CharField(max_length=100)
    native_name = models.CharField(max_length=100)
    
    class Meta:
        unique_together = ['website', 'language_code']
        indexes = [
            models.Index(fields=['website', 'is_default']),
            models.Index(fields=['website', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.website.name} - {self.language_code}"


class TemplateI18nManager:
    """Manager for internationalized template operations."""
    
    def __init__(self):
        self.cache_timeout = 3600  # 1 hour
        self.supported_languages = ['en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'zh', 'ja', 'ko']
    
    def get_translated_template(
        self,
        event_key: str,
        language_code: str,
        template_type: str = "class_based",
        website_id: Optional[int] = None,
        user_id: Optional[int] = None
    ) -> Optional[Tuple[str, str, str]]:
        """Get translated template content."""
        # Try to get user's language preferences
        if user_id:
            language_chain = self._get_user_language_chain(user_id)
        else:
            language_chain = [language_code, 'en']
        
        # Try each language in the chain
        for lang in language_chain:
            cache_key = f"template_i18n:{event_key}:{lang}:{template_type}:{website_id}"
            cached_content = cache.get(cache_key)
            
            if cached_content:
                return cached_content
            
            # Try to get from database
            translation = self._get_translation(
                event_key, lang, template_type, website_id
            )
            
            if translation:
                content = (
                    translation.title,
                    translation.text_content,
                    translation.html_content
                )
                
                # Cache the result
                cache.set(cache_key, content, self.cache_timeout)
                return content
        
        return None
    
    def _get_user_language_chain(self, user_id: int) -> List[str]:
        """Get user's language preference chain."""
        try:
            preference = LanguagePreference.objects.get(user_id=user_id)
            return preference.language_chain
        except LanguagePreference.DoesNotExist:
            return ['en']
    
    def _get_translation(
        self,
        event_key: str,
        language_code: str,
        template_type: str,
        website_id: Optional[int]
    ) -> Optional[TemplateTranslation]:
        """Get translation from database."""
        query = TemplateTranslation.objects.filter(
            event_key=event_key,
            template_type=template_type,
            language_code=language_code,
            is_active=True
        )
        
        if website_id:
            query = query.filter(website_id=website_id)
        else:
            query = query.filter(website_id__isnull=True)
        
        return query.first()
    
    def create_translation(
        self,
        event_key: str,
        language_code: str,
        template_type: str,
        title: str,
        text_content: str,
        html_content: str,
        website_id: Optional[int] = None,
        created_by_id: Optional[int] = None
    ) -> TemplateTranslation:
        """Create a new template translation."""
        translation = TemplateTranslation.objects.create(
            event_key=event_key,
            template_type=template_type,
            language_code=language_code,
            website_id=website_id,
            title=title,
            text_content=text_content,
            html_content=html_content,
            created_by_id=created_by_id
        )
        
        # Invalidate cache
        self._invalidate_cache(event_key, language_code, template_type, website_id)
        
        return translation
    
    def update_translation(
        self,
        translation_id: int,
        title: Optional[str] = None,
        text_content: Optional[str] = None,
        html_content: Optional[str] = None
    ) -> TemplateTranslation:
        """Update existing translation."""
        translation = TemplateTranslation.objects.get(id=translation_id)
        
        if title is not None:
            translation.title = title
        if text_content is not None:
            translation.text_content = text_content
        if html_content is not None:
            translation.html_content = html_content
        
        translation.save()
        
        # Invalidate cache
        self._invalidate_cache(
            translation.event_key,
            translation.language_code,
            translation.template_type,
            translation.website_id
        )
        
        return translation
    
    def _invalidate_cache(
        self,
        event_key: str,
        language_code: str,
        template_type: str,
        website_id: Optional[int]
    ):
        """Invalidate cached translation."""
        cache_key = f"template_i18n:{event_key}:{language_code}:{template_type}:{website_id}"
        cache.delete(cache_key)
    
    def get_supported_languages(self, website_id: Optional[int] = None) -> List[Dict[str, str]]:
        """Get supported languages for website."""
        if website_id:
            configs = WebsiteLanguageConfig.objects.filter(
                website_id=website_id,
                is_active=True
            ).order_by('-is_default', 'language_code')
            
            return [
                {
                    'code': config.language_code,
                    'display_name': config.display_name,
                    'native_name': config.native_name,
                    'is_default': config.is_default
                }
                for config in configs
            ]
        else:
            # Return default languages
            return [
                {'code': 'en', 'display_name': 'English', 'native_name': 'English', 'is_default': True},
                {'code': 'es', 'display_name': 'Spanish', 'native_name': 'Español', 'is_default': False},
                {'code': 'fr', 'display_name': 'French', 'native_name': 'Français', 'is_default': False},
                {'code': 'de', 'display_name': 'German', 'native_name': 'Deutsch', 'is_default': False},
            ]
    
    def get_translation_coverage(
        self,
        event_key: str,
        website_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get translation coverage for an event."""
        query = TemplateTranslation.objects.filter(
            event_key=event_key,
            is_active=True
        )
        
        if website_id:
            query = query.filter(website_id=website_id)
        else:
            query = query.filter(website_id__isnull=True)
        
        translations = query.values_list('language_code', flat=True)
        supported_languages = self.get_supported_languages(website_id)
        
        coverage = {
            'total_languages': len(supported_languages),
            'translated_languages': len(translations),
            'coverage_percentage': (len(translations) / len(supported_languages) * 100) if supported_languages else 0,
            'missing_languages': [
                lang['code'] for lang in supported_languages 
                if lang['code'] not in translations
            ],
            'available_languages': list(translations)
        }
        
        return coverage
    
    def auto_translate_template(
        self,
        event_key: str,
        source_language: str,
        target_language: str,
        template_type: str = "class_based",
        website_id: Optional[int] = None
    ) -> Optional[TemplateTranslation]:
        """Auto-translate template using external service."""
        # This would integrate with translation services like Google Translate, DeepL, etc.
        # For now, we'll return None to indicate manual translation is needed
        
        logger.info(f"Auto-translation requested for {event_key} from {source_language} to {target_language}")
        
        # In a real implementation, this would:
        # 1. Get the source translation
        # 2. Call translation API
        # 3. Create new translation record
        # 4. Return the translation
        
        return None


class TemplateI18nMiddleware:
    """Middleware for handling template internationalization."""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.i18n_manager = TemplateI18nManager()
    
    def __call__(self, request):
        # Set user's language preference in request
        if hasattr(request, 'user') and request.user.is_authenticated:
            try:
                preference = LanguagePreference.objects.get(user=request.user)
                request.user_language = preference.primary_language
                request.user_language_chain = preference.language_chain
            except LanguagePreference.DoesNotExist:
                request.user_language = 'en'
                request.user_language_chain = ['en']
        else:
            request.user_language = 'en'
            request.user_language_chain = ['en']
        
        response = self.get_response(request)
        return response


# Global i18n manager
_i18n_manager = TemplateI18nManager()

def get_i18n_manager() -> TemplateI18nManager:
    """Get the global template i18n manager."""
    return _i18n_manager


def get_translated_template(
    event_key: str,
    language_code: str,
    template_type: str = "class_based",
    website_id: Optional[int] = None,
    user_id: Optional[int] = None
) -> Optional[Tuple[str, str, str]]:
    """Get translated template content."""
    manager = get_i18n_manager()
    return manager.get_translated_template(
        event_key, language_code, template_type, website_id, user_id
    )


def create_template_translation(
    event_key: str,
    language_code: str,
    template_type: str,
    title: str,
    text_content: str,
    html_content: str,
    website_id: Optional[int] = None,
    created_by_id: Optional[int] = None
) -> TemplateTranslation:
    """Create a new template translation."""
    manager = get_i18n_manager()
    return manager.create_translation(
        event_key, language_code, template_type, title, 
        text_content, html_content, website_id, created_by_id
    )
