from celery import shared_task

from refunds.models import Refund
from refunds.services.refunds_processor import RefundProcessorService


@shared_task
def retry_external_refund(refund_id):
    refund = Refund.objects.get(id=refund_id)
    if refund.status == Refund.PENDING:
        RefundProcessorService.process_refund(
            refund=refund,
            processed_by=None,
            reason="Automated refund retry",
        )
