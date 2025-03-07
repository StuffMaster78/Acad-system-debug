from django.contrib import admin
from .models import (
    WriterWallet, WalletTransaction, WriterPaymentBatch, PaymentSchedule, 
    ScheduledWriterPayment, PaymentOrderRecord, WriterPayment, AdminPaymentAdjustment, PaymentConfirmation
)

admin.site.register(WriterWallet)
admin.site.register(WalletTransaction)
admin.site.register(WriterPaymentBatch)
admin.site.register(PaymentSchedule)
admin.site.register(ScheduledWriterPayment)
admin.site.register(PaymentOrderRecord)
admin.site.register(WriterPayment)
admin.site.register(AdminPaymentAdjustment)
admin.site.register(PaymentConfirmation)
