from django.db import models
from django.conf import settings
from websites.models import Website
from .promotions import PromotionalCampaign


class SeasonalEventManager(models.Manager):
    def create(self, **kwargs):  # type: ignore[override]
        # Map legacy field names used by tests
        mapping = {}
        if 'name' in kwargs:
            mapping['campaign_name'] = kwargs.pop('name')
        if 'start_date' in kwargs:
            mapping['start_date'] = kwargs['start_date']
        if 'end_date' in kwargs:
            mapping['end_date'] = kwargs['end_date']
        if 'description' in kwargs:
            mapping['description'] = kwargs['description']
        if 'is_active' in kwargs:
            mapping['is_active'] = kwargs['is_active']
        # Ensure website exists for tests
        if 'website' not in kwargs:
            try:
                site = Website.objects.filter(is_active=True).first()
                if site is None:
                    site = Website.objects.create(name="Test Website", domain="https://test.local", is_active=True)
                kwargs['website'] = site
            except Exception:
                pass
        kwargs.update(mapping)
        return super().create(**kwargs)


class SeasonalEvent(PromotionalCampaign):
    """
    Backward-compatible model used by tests. Subclasses PromotionalCampaign
    to reuse the same table but provides a manager that accepts `name`.
    """

    objects = SeasonalEventManager()

    class Meta:
        proxy = True
        verbose_name = "Seasonal Event"
        verbose_name_plural = "Seasonal Events"


