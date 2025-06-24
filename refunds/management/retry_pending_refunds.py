from django.core.management.base import BaseCommand
from refunds.models import Refund
from refunds.tasks import retry_external_refund

class Command(BaseCommand):
    help = "Retries all pending external refunds"

    def handle(self, *args, **kwargs):
        pending_refunds = Refund.objects.filter(
            status=Refund.PENDING,
            refund_method='external',
            external_amount__gt=0
        )

        count = pending_refunds.count()
        for refund in pending_refunds:
            retry_external_refund.delay(refund.id)

        self.stdout.write(
            self.style.SUCCESS(f"Retry triggered for {count} refunds.")
        )