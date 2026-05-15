"""
Detects and repairs data inconsistencies in writer_management.
Run via management commands after data migrations or bulk imports.
"""
import logging
 
from django.db.models import F
 
logger = logging.getLogger(__name__)
 
 
class WriterReconciliationService:
 
    @staticmethod
    def reconcile_discipline_state(writer) -> dict:
        """
        Rebuild WriterDisciplineState from source records.
        Same as WriterStatusService.recompute() — delegates to it.
        """
        from writer_management.services.writer_status_service import (
            WriterStatusService,
        )
        WriterStatusService.recompute(writer)
        return {"status": "recomputed", "writer": writer.registration_id}
 
    @staticmethod
    def reconcile_active_orders_count(writer) -> dict:
        """
        Recount active orders from the orders app and sync
        WriterCapacity.active_orders_count.
 
        Called after manual order data corrections.
        """
        from writer_management.models.writer_capacity import WriterCapacity
 
        try:
            from orders.models.orders import Order
            active_count = Order.objects.filter(
                assigned_writer=writer,
                status__in=["assigned", "in_progress", "revision"],
            ).count()
        except Exception as exc:
            logger.exception(
                "reconcile_active_orders_count: cannot count orders "
                "for writer=%s: %s",
                writer.registration_id,
                exc,
            )
            return {"status": "error", "writer": writer.registration_id}
 
        updated = WriterCapacity.objects.filter(writer=writer).update(
            active_orders_count=active_count
        )
 
        logger.info(
            "reconcile_active_orders_count: writer=%s count=%d updated=%d",
            writer.registration_id,
            active_count,
            updated,
        )
 
        return {
            "status": "ok",
            "writer": writer.registration_id,
            "active_orders_count": active_count,
        }
 
    @staticmethod
    def reconcile_performance(writer) -> dict:
        """
        Recompute WriterPerformance lifetime totals from order history.
        Called after order data corrections.
        """
        from writer_management.models.writer_performance import WriterPerformance
 
        try:
            from orders.models.orders import Order
            from django.db.models import Count, Sum, Q
 
            stats = Order.objects.filter(
                assigned_writer=writer,
            ).aggregate(
                total=Count("id"),
                completed=Count("id", filter=Q(status="completed")),
                cancelled=Count("id", filter=Q(status="cancelled")),
                disputed=Count("id", filter=Q(is_disputed=True)),
                late=Count("id", filter=Q(is_late=True)),
                on_time=Count("id", filter=Q(
                    status="completed", is_late=False
                )),
                revisions=Sum("revision_count", default=0),
            )
        except Exception as exc:
            logger.exception(
                "reconcile_performance: cannot gather order stats "
                "for writer=%s: %s",
                writer.registration_id,
                exc,
            )
            return {"status": "error", "writer": writer.registration_id}
 
        WriterPerformance.objects.filter(writer=writer).update(
            total_orders=stats["total"] or 0,
            completed_orders=stats["completed"] or 0,
            cancelled_orders=stats["cancelled"] or 0,
            disputed_orders=stats["disputed"] or 0,
            late_deliveries=stats["late"] or 0,
            on_time_deliveries=stats["on_time"] or 0,
            revision_count=stats["revisions"] or 0,
        )
 
        logger.info(
            "reconcile_performance: writer=%s stats=%s",
            writer.registration_id,
            stats,
        )
 
        return {
            "status": "ok",
            "writer": writer.registration_id,
            **{k: v or 0 for k, v in stats.items()},
        }
 
    @staticmethod
    def reconcile_all_for_website(website) -> dict:
        """
        Run all reconciliation checks for every writer on a website.
        Use sparingly — expensive. Intended for post-migration runs.
        """
        from writer_management.models.writer_profile import WriterProfile
 
        writers = WriterProfile.objects.filter(
            writer_level__website=website,
            is_deleted=False,
        )
 
        results = {
            "total": 0,
            "discipline_recomputed": 0,
            "orders_reconciled": 0,
            "performance_reconciled": 0,
            "errors": 0,
        }
 
        for writer in writers.iterator(chunk_size=50):
            results["total"] += 1
            try:
                WriterReconciliationService.reconcile_discipline_state(writer)
                results["discipline_recomputed"] += 1
            except Exception:
                results["errors"] += 1
 
            try:
                WriterReconciliationService.reconcile_active_orders_count(writer)
                results["orders_reconciled"] += 1
            except Exception:
                results["errors"] += 1
 
            try:
                WriterReconciliationService.reconcile_performance(writer)
                results["performance_reconciled"] += 1
            except Exception:
                results["errors"] += 1
 
        logger.info(
            "reconcile_all_for_website: website=%s results=%s",
            website.pk,
            results,
        )
 
        return results