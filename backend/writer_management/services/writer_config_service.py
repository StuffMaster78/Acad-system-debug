"""
writer_management/services/writer_config_service.py

Owns all mutations to WriterConfig and WriterWarningEscalationConfig.

No view or signal writes to these models directly.
All changes go through this service so the audit history
is always complete.

OPERATIONS
----------
get_config(website) — fetch or create with defaults
update_config(website, fields, by) — update WriterConfig fields
get_escalation_config(website) — fetch or create with defaults
update_escalation_config(website, ...) — update escalation thresholds

AUDIT
-----
Every update to WriterConfig creates a WriterConfigHistory row
with a JSON snapshot of the previous values.

This means you can reconstruct the config at any point in time
by replaying the history forward from the creation record.
"""

import logging

from django.db import transaction
from django.utils.timezone import now

from writer_management.models.configs import (
    WriterConfig,
    WriterConfigHistory,
    WriterWarningEscalationConfig,
)

logger = logging.getLogger(__name__)

# Fields on WriterConfig that can be updated via update_config()
UPDATABLE_CONFIG_FIELDS = {
    "takes_enabled",
    "max_requests_per_writer",
    "max_takes_per_writer",
    "auto_assign_enabled",
    "preferred_assignment_window_hours",
}

# Fields on WriterWarningEscalationConfig that can be updated
UPDATABLE_ESCALATION_FIELDS = {
    "admin_alert_threshold",
    "auto_probation_threshold",
    "auto_suspension_threshold",
    "default_warning_duration_days",
    "auto_suspend_days",
}


class WriterConfigService:

    # ----------------------------------------------------------------
    # WRITER CONFIG
    # ----------------------------------------------------------------

    @staticmethod
    def get_config(website) -> WriterConfig:
        """
        Fetch WriterConfig for a website.
        Creates with defaults if it does not exist.

        Args:
            website: Website instance.

        Returns:
            WriterConfig instance.
        """
        config, created = WriterConfig.objects.get_or_create(
            website=website,
            defaults={
                "takes_enabled": True,
                "max_requests_per_writer": 5,
                "max_takes_per_writer": 10,
                "auto_assign_enabled": False,
                "preferred_assignment_window_hours": 24,
            },
        )
        if created:
            logger.info(
                "WriterConfig created with defaults for website=%s",
                website.pk,
            )
            WriterConfigHistory.objects.create(
                config=config,
                change_type=WriterConfigHistory.ChangeType.CREATED,
                previous_values={},
                notes="Auto-created with defaults.",
            )
        return config

    @staticmethod
    @transaction.atomic
    def update_config(
        website,
        updated_by=None,
        notes: str = "",
        **fields,
    ) -> WriterConfig:
        """
        Update WriterConfig fields for a website.

        Only fields in UPDATABLE_CONFIG_FIELDS are accepted.
        Unknown fields raise ValueError immediately — no silent ignoring.

        Creates an audit history record with a snapshot of
        the previous values.

        Args:
            website: Website instance.
            updated_by: Admin User making the change. None = system.
            notes: Optional reason for the change.
            **fields: Config fields to update with their new values.

        Returns:
            Updated WriterConfig instance.

        Raises:
            ValueError: If any unknown fields are passed.
        """
        unknown = set(fields) - UPDATABLE_CONFIG_FIELDS
        if unknown:
            raise ValueError(
                f"Unknown WriterConfig fields: {unknown}. "
                f"Allowed fields: {UPDATABLE_CONFIG_FIELDS}"
            )

        if not fields:
            raise ValueError(
                "No fields provided to update_config. "
                "Pass at least one field to update."
            )

        config = WriterConfigService.get_config(website)

        # Snapshot previous values before mutation
        previous_values = {
            field: getattr(config, field)
            for field in UPDATABLE_CONFIG_FIELDS
        }

        # Apply updates
        changed_fields = []
        for field, value in fields.items():
            if getattr(config, field) != value:
                setattr(config, field, value)
                changed_fields.append(field)

        if not changed_fields:
            logger.info(
                "update_config called for website=%s but no values changed.",
                website.pk,
            )
            return config

        changed_fields.append("updated_at")
        changed_fields.append("updated_by")
        config.updated_by = updated_by
        config.save(update_fields=changed_fields)

        # Write audit record
        WriterConfigHistory.objects.create(
            config=config,
            changed_by=updated_by,
            change_type=WriterConfigHistory.ChangeType.UPDATED,
            previous_values=previous_values,
            notes=notes,
        )

        logger.info(
            "WriterConfig updated: website=%s fields=%s by=%s",
            website.pk,
            changed_fields,
            getattr(updated_by, "pk", "system"),
        )

        return config


    @staticmethod
    def get_config_history(website):
        """
        Return the full change history for a website's WriterConfig.
        """
        config = WriterConfigService.get_config(website)
        return (
            WriterConfigHistory.objects
            .filter(config=config)
            .select_related("changed_by")
            .order_by("-changed_at")
        )

    # ----------------------------------------------------------------
    # WRITER WARNING ESCALATION CONFIG
    # ----------------------------------------------------------------

    @staticmethod
    def get_escalation_config(website) -> WriterWarningEscalationConfig:
        """
        Fetch WriterWarningEscalationConfig for a website.
        Creates with defaults if it does not exist.

        Args:
            website: Website instance.

        Returns:
            WriterWarningEscalationConfig instance.
        """
        config, created = WriterWarningEscalationConfig.objects.get_or_create(
            website=website,
            defaults={
                "admin_alert_threshold": 3,
                "auto_probation_threshold": 5,
                "auto_suspension_threshold": 7,
                "default_warning_duration_days": 30,
                "auto_suspend_days": 7,
            },
        )
        if created:
            logger.info(
                "WriterWarningEscalationConfig created with defaults "
                "for website=%s",
                website.pk,
            )
        return config

    @staticmethod
    @transaction.atomic
    def update_escalation_config(
        website,
        updated_by=None,
        **fields,
    ) -> WriterWarningEscalationConfig:
        """
        Update WriterWarningEscalationConfig thresholds.

        Validates threshold ordering before saving:
            admin_alert <= auto_probation <= auto_suspension

        Args:
            website: Website instance.
            updated_by: Admin User making the change.
            **fields: Escalation config fields to update.

        Returns:
            Updated WriterWarningEscalationConfig instance.

        Raises:
            ValueError: On unknown fields or invalid threshold ordering.
        """
        unknown = set(fields) - UPDATABLE_ESCALATION_FIELDS
        if unknown:
            raise ValueError(
                f"Unknown WriterWarningEscalationConfig fields: {unknown}."
            )

        config = WriterConfigService.get_escalation_config(website)

        # Merge new values with existing for validation
        resolved = {
            field: fields.get(field, getattr(config, field))
            for field in UPDATABLE_ESCALATION_FIELDS
        }

        # Validate threshold ordering
        alert = resolved["admin_alert_threshold"]
        probation = resolved["auto_probation_threshold"]
        suspension = resolved["auto_suspension_threshold"]

        if probation > 0 and alert > probation:
            raise ValueError(
                f"admin_alert_threshold ({alert}) cannot exceed "
                f"auto_probation_threshold ({probation})."
            )
        if suspension > 0 and probation > suspension:
            raise ValueError(
                f"auto_probation_threshold ({probation}) cannot exceed "
                f"auto_suspension_threshold ({suspension})."
            )

        # Apply updates
        update_fields = []
        for field, value in fields.items():
            if getattr(config, field) != value:
                setattr(config, field, value)
                update_fields.append(field)

        if not update_fields:
            return config

        update_fields.append("updated_at")
        config.save(update_fields=update_fields)

        logger.info(
            "WriterWarningEscalationConfig updated: website=%s "
            "fields=%s by=%s",
            website.pk,
            update_fields,
            getattr(updated_by, "pk", "system"),
        )

        return config

    # ----------------------------------------------------------------
    # CONVENIENCE — for services that need both configs
    # ----------------------------------------------------------------

    @staticmethod
    def get_all_configs(website) -> dict:
        """
        Return both configs for a website in one call.

        Returns:
            {
                "writer_config": WriterConfig,
                "escalation_config": WriterWarningEscalationConfig,
            }
        """
        return {
            "writer_config": WriterConfigService.get_config(website),
            "escalation_config": WriterConfigService.get_escalation_config(
                website
            ),
        }