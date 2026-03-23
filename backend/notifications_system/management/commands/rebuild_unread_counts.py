# notifications_system/management/commands/rebuild_unread_counts.py
"""
Rebuild cached unread notification counts from source of truth.

Use when:
    - Unread counts drift out of sync with actual read state
    - After a data migration that touches NotificationsUserStatus
    - After bulk operations that bypassed the normal read/mark pipeline
    - Periodically as a sanity check (optional — run weekly via cron)

Usage:
    python manage.py rebuild_unread_counts
    python manage.py rebuild_unread_counts --website 3
    python manage.py rebuild_unread_counts --user 42
    python manage.py rebuild_unread_counts --dry-run
    python manage.py rebuild_unread_counts --batch-size 500
"""
from __future__ import annotations

import logging
from typing import Optional

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = (
        'Rebuild cached unread notification counts from source of truth. '
        'Safe to run at any time — reads NotificationsUserStatus rows '
        'and updates UserNotificationMeta.unread_count accordingly.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--website',
            type=int,
            default=None,
            metavar='WEBSITE_ID',
            help='Only rebuild counts for a specific website.',
        )
        parser.add_argument(
            '--user',
            type=int,
            default=None,
            metavar='USER_ID',
            help='Only rebuild counts for a specific user.',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help=(
                'Show what would be updated without writing anything. '
                'Prints users whose count is wrong.'
            ),
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=200,
            metavar='N',
            help='Number of UserNotificationMeta rows to process per batch. Default: 200.',
        )
        parser.add_argument(
            '--include-correct',
            action='store_true',
            help='Log users whose count is already correct. Verbose — use for debugging only.',
        )

    def handle(self, *args, **options):
        website_id = options['website']
        user_id = options['user']
        dry_run = options['dry_run']
        batch_size = options['batch_size']
        include_correct = options['include_correct']

        from notifications_system.models.user_notification_meta import (
            UserNotificationMeta,
        )
        from notifications_system.models.notifications_user_status import (
            NotificationsUserStatus,
        )

        self.stdout.write('')
        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN — no changes will be written.\n')
            )

        # --- Build queryset of meta rows to check
        meta_qs = UserNotificationMeta.objects.select_related(
            'user', 'website'
        )

        if website_id:
            meta_qs = meta_qs.filter(website_id=website_id)
            self.stdout.write(f"  Scoped to website_id={website_id}")

        if user_id:
            meta_qs = meta_qs.filter(user_id=user_id)
            self.stdout.write(f"  Scoped to user_id={user_id}")

        total = meta_qs.count()
        self.stdout.write(
            f"  Checking {total} UserNotificationMeta row(s)...\n"
        )

        # --- Process in batches
        checked = 0
        updated = 0
        already_correct = 0
        errors = 0

        offset = 0
        while True:
            batch = list(meta_qs[offset: offset + batch_size])
            if not batch:
                break

            for meta in batch:
                try:
                    # Count actual unread from source of truth
                    actual_count = NotificationsUserStatus.objects.filter(
                        user_id=meta.user_id,
                        website_id=meta.website_id,
                        is_read=False,
                    ).count()

                    checked += 1

                    if meta.unread_count == actual_count:
                        already_correct += 1
                        if include_correct:
                            self.stdout.write(
                                f"  OK      user={meta.user_id} "
                                f"website={meta.website_id} "
                                f"count={actual_count}"
                            )
                        continue

                    # Count is wrong
                    self.stdout.write(
                        self.style.WARNING(
                            f"  DRIFT   user={meta.user_id} "
                            f"website={meta.website_id} "
                            f"cached={meta.unread_count} "
                            f"actual={actual_count}"
                        )
                    )

                    if not dry_run:
                        meta.unread_count = actual_count
                        meta.save(update_fields=['unread_count', 'updated_at'])
                        updated += 1

                except Exception as exc:
                    errors += 1
                    logger.error(
                        "rebuild_unread_counts: error processing "
                        "meta id=%s user=%s website=%s: %s",
                        meta.id,
                        meta.user_id,
                        meta.website_id,
                        exc,
                    )
                    self.stdout.write(
                        self.style.ERROR(
                            f"  ERROR   user={meta.user_id} "
                            f"website={meta.website_id}: {exc}"
                        )
                    )

            offset += batch_size

            # Progress indicator for large datasets
            if total > batch_size:
                self.stdout.write(
                    f"  ... processed {min(offset, total)}/{total}",
                    ending='\r',
                )

        # --- Summary
        self.stdout.write('')
        self.stdout.write('─' * 50)

        if dry_run:
            drift_count = checked - already_correct - errors
            self.stdout.write(
                self.style.WARNING(
                    f"\n[DRY RUN] Summary:\n"
                    f"  Checked:         {checked}\n"
                    f"  Already correct: {already_correct}\n"
                    f"  Would update:    {drift_count}\n"
                    f"  Errors:          {errors}\n"
                )
            )
            if drift_count > 0:
                self.stdout.write(
                    "  Run without --dry-run to fix these counts.\n"
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        "  All counts are correct. No updates needed.\n"
                    )
                )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"\nDone:\n"
                    f"  Checked:         {checked}\n"
                    f"  Already correct: {already_correct}\n"
                    f"  Updated:         {updated}\n"
                    f"  Errors:          {errors}\n"
                )
            )
            if errors:
                self.stdout.write(
                    self.style.WARNING(
                        f"  {errors} error(s) occurred. "
                        f"Check logs for details.\n"
                    )
                )