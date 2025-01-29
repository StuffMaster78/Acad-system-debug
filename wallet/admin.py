from django.contrib import admin
from .models import Wallet, WalletTransaction

from django.contrib import admin
from .models import Wallet, WalletTransaction, WithdrawalRequest


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance', 'last_updated', 'website')
    search_fields = ('user__username', 'user__email', 'website__name')
    list_filter = ('website',)
    ordering = ['-last_updated']


    def save_model(self, request, obj, form, change):
        """
        Log admin adjustments when the balance is changed manually.
        """
        if change:  # Editing an existing wallet
            original_obj = Wallet.objects.get(pk=obj.pk)
            if original_obj.balance != obj.balance:
                WalletTransaction.objects.create(
                    wallet=obj,
                    transaction_type='adjustment',
                    amount=obj.balance - original_obj.balance,
                    description=f"Admin adjustment by {request.user.username}",
                    website=obj.website,
                )
        super().save_model(request, obj, form, change)

@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = ('wallet', 'transaction_type', 'amount', 'description', 'created_at', 'website')
    search_fields = ('wallet__user__username', 'wallet__user__email', 'description')
    list_filter = ('transaction_type', 'website')
    ordering = ['-created_at']


@admin.register(WithdrawalRequest)
class WithdrawalRequestAdmin(admin.ModelAdmin):
    list_display = ('wallet', 'amount', 'status', 'created_at', 'processed_at', 'website')
    search_fields = ('wallet__user__username', 'wallet__user__email', 'website__name')
    list_filter = ('status', 'website')
    ordering = ['-created_at']