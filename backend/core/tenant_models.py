# core/tenant_models.py
from django.db import models
from core.tenant_context import get_current_website

class TenantQuerySet(models.QuerySet):
    def for_current(self):
        site = get_current_website()
        return self.filter(website=site) if site else self.none()

class TenantManager(models.Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        site = get_current_website()
        return qs.filter(website=site) if site else qs.none()

class BaseTenantModel(models.Model):
    website = models.ForeignKey("websites.Website",
                                on_delete=models.CASCADE, db_index=True)
    objects = TenantManager.from_queryset(TenantQuerySet)()
    all_objects = models.Manager()  # escape hatch

    class Meta:
        abstract = True