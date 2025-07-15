from django.db import transaction
from celery import shared_task
from refunds.models import Refund

from refunds.services.refunds_processor import RefundProcessorService
@shared_task
def retry_external_refund(refund_id):
    refund = Refund.objects.get(id=refund_id)
    if refund.status == Refund.PENDING and refund.external_amount > 0:
        RefundProcessorService.process_external_refund(
            refund, admin_user=None
        )
