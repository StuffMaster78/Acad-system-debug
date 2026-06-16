"""
Audit signals for configuration changes — always sensitive.
Payment disclosure, pricing, and branding changes are trust-critical.
"""
from __future__ import annotations

import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

log = logging.getLogger("audit")

_SENSITIVE_BRANDING_FIELDS = {
    "payment_processor_name", "payment_statement_descriptor",
    "payment_client_disclosure_text", "primary_color",
}


@receiver(post_save)
def audit_branding_changes(sender, instance, created, **kwargs):
    if sender.__name__ != "WebsiteBranding" or created:
        return
    from audit_logging.factories.audit_event_factory import AuditEventFactory
    try:
        # Capture a snapshot of the current branding for the after state
        after_snap = {
            "payment_processor_name": getattr(instance, "payment_processor_name", ""),
            "payment_statement_descriptor": getattr(instance, "payment_statement_descriptor", ""),
            "brand_name": getattr(instance, "brand_name", ""),
        }
        AuditEventFactory.create(
            action="config.branding_updated",
            website=getattr(instance, "website", None),
            object_type="website_branding",
            object_id=str(instance.pk),
            after=after_snap,
            severity="warning",
            is_sensitive=True,
            sensitivity_level="payment_config",
            service_name="config",
        )
    except Exception:
        log.exception("audit_branding_changes failed")


@receiver(post_save)
def audit_portal_definition_changes(sender, instance, created, **kwargs):
    if sender.__name__ != "PortalDefinition":
        return
    from audit_logging.factories.audit_event_factory import AuditEventFactory
    from websites.models.websites import Website
    from django.db import transaction as _txn
    sid = _txn.savepoint()
    try:
        website = Website.objects.filter(is_active=True, is_deleted=False).first()
        if website is None:
            log.warning(
                "audit_portal_definition_changes skipped: no active website context"
            )
            _txn.savepoint_commit(sid)
            return
        AuditEventFactory.create(
            action="config.portal_definition_changed",
            website=website,
            object_type="portal_definition",
            object_id=str(instance.pk),
            metadata={
                "scope": "platform",
                "code": getattr(instance, "code", ""),
                "domain": getattr(instance, "domain", ""),
                "is_active": getattr(instance, "is_active", None),
                "created": created,
            },
            severity="warning",
            is_sensitive=True,
            sensitivity_level="portal_config",
            service_name="config",
        )
        _txn.savepoint_commit(sid)
    except Exception:
        _txn.savepoint_rollback(sid)
        log.exception("audit_portal_definition_changes failed")


@receiver(post_save)
def audit_writer_level_changes(sender, instance, created, **kwargs):
    """Writer level rate changes affect compensation — sensitive."""
    if sender.__name__ != "WriterLevelRate":
        return
    from audit_logging.factories.audit_event_factory import AuditEventFactory
    try:
        AuditEventFactory.create(
            action="config.writer_level_changed",
            website=getattr(instance, "website", None),
            object_type="writer_level_rate",
            object_id=str(instance.pk),
            metadata={
                "name": getattr(instance, "name", ""),
                "created": created,
            },
            severity="warning",
            is_sensitive=True,
            sensitivity_level="compensation_config",
            service_name="config",
        )
    except Exception:
        log.exception("audit_writer_level_changes failed")
