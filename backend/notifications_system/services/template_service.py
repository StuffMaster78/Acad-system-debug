# notifications_system/services/template_service.py
"""
Template resolution and rendering.
Absorbed render.py — all template logic lives here.
"""
from __future__ import annotations

import logging
from typing import Dict, Optional

from django.core.cache import cache
from django.db.models import Case, IntegerField, Q, Value, When
from django.template import Context, Template

logger = logging.getLogger(__name__)

TEMPLATE_CACHE_TTL = 300  # 5 minutes


class TemplateService:
    """
    Resolves and renders notification templates.

    Resolution order:
        1. Website-specific template (matching locale + latest version)
        2. Global template (matching locale + latest version)
        3. Global template (default locale 'en')
    """

    @staticmethod
    def resolve(
        event_key: str,
        channel: str,
        website,
        locale: str = 'en',
        use_cache: bool = True,
    ):
        """
        Resolve the best template for an event + channel + website + locale.

        Args:
            event_key:  Event key e.g. 'order.completed'
            channel:    Channel e.g. 'email', 'in_app'
            website:    Website instance or None for global
            locale:     BCP-47 locale e.g. 'sw-KE', 'en'
            use_cache:  Cache resolved template PK for TEMPLATE_CACHE_TTL

        Returns:
            NotificationTemplate or None
        """
        from notifications_system.models.notifications_template import NotificationTemplate
        from notifications_system.models.notification_event import NotificationEvent

        website_id = getattr(website, 'id', None)
        locales = TemplateService._locale_chain(locale)

        # Cache check
        cache_key = (
            f"notif:tmpl:{event_key}:{channel}"
            f":{website_id or 'global'}:{'/'.join(locales)}"
        )
        if use_cache:
            cached_pk = cache.get(cache_key)
            if cached_pk:
                template = NotificationTemplate.objects.filter(
                    pk=cached_pk, is_active=True
                ).first()
                if template:
                    return template

        # Resolve event
        event = NotificationEvent.objects.filter(
            event_key=event_key,
            is_active=True,
        ).first()
        if not event:
            logger.warning(
                "TemplateService.resolve() no active event: event_key=%s.",
                event_key,
            )
            return None

        # Query — website-specific and global, all locale candidates
        qs = NotificationTemplate.objects.filter(
            event=event,
            channel=channel,
            locale__in=locales,
            is_active=True,
        ).filter(
            Q(website_id=website_id) | Q(website_id__isnull=True)
        )

        # Score: website match and locale precision
        website_score = Case(
            When(website_id=website_id, then=Value(1)),
            default=Value(0),
            output_field=IntegerField(),
        )

        # Higher weight = more preferred locale
        weights = {
            loc: idx + 1
            for idx, loc in enumerate(reversed(locales))
        }
        locale_score = Case(
            *[
                When(locale=loc, then=Value(weight))
                for loc, weight in weights.items()
            ],
            default=Value(0),
            output_field=IntegerField(),
        )

        template = (
            qs
            .annotate(_wscore=website_score, _lscore=locale_score)
            .order_by('-_wscore', '-_lscore', '-version', '-id')
            .first()
        )

        if template and use_cache:
            cache.set(cache_key, template.pk, timeout=TEMPLATE_CACHE_TTL)

        if not template:
            logger.warning(
                "TemplateService.resolve() no template found: "
                "event=%s channel=%s website=%s locale=%s.",
                event_key,
                channel,
                website_id,
                locale,
            )

        return template

    @staticmethod
    def render(template, context: dict) -> Dict[str, str]:
        """
        Render a template with context variables.
        Uses Django's template engine for {{variable}} substitution.

        Args:
            template: NotificationTemplate instance
            context:  Dict of variables to inject

        Returns:
            Dict with rendered fields relevant to the channel.
            Email: subject, body_html, body_text
            In-app: title, message
        """
        ctx = Context(context or {})

        def render_field(text: str) -> str:
            if not text:
                return ''
            try:
                return Template(text).render(ctx)
            except Exception as exc:
                logger.warning(
                    "TemplateService.render() field rendering failed: %s", exc
                )
                return text  # return unrendered rather than crashing

        rendered = {}

        # Email fields
        if template.subject:
            rendered['subject'] = render_field(template.subject)
        if template.body_html:
            rendered['body_html'] = render_field(template.body_html)
        if template.body_text:
            rendered['body_text'] = render_field(template.body_text)

        # In-app fields
        if template.title:
            rendered['title'] = render_field(template.title)
        if template.message:
            rendered['message'] = render_field(template.message)

        return rendered

    @staticmethod
    def invalidate_cache(event_key: str, channel: str, website) -> None:
        """
        Invalidate cached template resolution for an event + channel + website.
        Call this when a template is created, updated, or deactivated.
        """
        from notifications_system.models.notification_event import NotificationEvent

        website_id = getattr(website, 'id', None)
        event = NotificationEvent.objects.filter(event_key=event_key).first()
        if not event:
            return

        # Invalidate for common locales — extend if you support more
        for locale in ['en', 'sw', 'fr', 'sw-KE', 'en-US']:
            locales = TemplateService._locale_chain(locale)
            key = (
                f"notif:tmpl:{event_key}:{channel}"
                f":{website_id or 'global'}:{'/'.join(locales)}"
            )
            cache.delete(key)

    @staticmethod
    def _locale_chain(locale: str) -> list:
        """
        Build fallback locale chain from most to least specific.
        'sw-KE' → ['sw-KE', 'sw', 'en']
        'en-US' → ['en-US', 'en']
        'en'    → ['en']
        """
        if not locale:
            return ['en']

        loc = locale.replace('_', '-')
        parts = loc.split('-')
        chain = [loc]

        if len(parts) > 1:
            chain.append(parts[0])

        if 'en' not in chain:
            chain.append('en')

        return chain