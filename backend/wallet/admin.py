from django.contrib import admin
from .models import Wallet, WalletTransaction

from django.contrib import admin
from .models import Wallet, WalletTransaction, WithdrawalRequest
from wallet.services.wallet_transaction_service import WalletTransactionService


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
                delta = obj.balance - original_obj.balance
                if delta > 0:
                    entry = WalletTransactionService.credit(
                        user=obj.user,
                        website=obj.website,
                        amount=delta,
                        description=f"Admin adjustment by {request.user.username}",
                        source="legacy_wallet_admin",
                        transaction_type="adjustment",
                        created_by=request.user,
                    )
                else:
                    entry = WalletTransactionService.debit(
                        user=obj.user,
                        website=obj.website,
                        amount=abs(delta),
                        description=f"Admin adjustment by {request.user.username}",
                        source="legacy_wallet_admin",
                        transaction_type="adjustment",
                        created_by=request.user,
                    )
                obj.balance = entry.balance_after
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
