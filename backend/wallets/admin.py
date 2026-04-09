from django.contrib import admin

from wallets.models import Wallet, WalletEntry, WalletHold


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "owner_user",
        "website",
        "wallet_type",
        "currency",
        "status",
        "available_balance",
        "pending_balance",
        "last_activity_at",
        "created_at",
    )
    list_filter = (
        "wallet_type",
        "status",
        "currency",
        "website",
    )
    search_fields = (
        "id",
        "owner_user__email",
        "owner_user__username",
    )
    readonly_fields = (
        "available_balance",
        "pending_balance",
        "total_credited",
        "total_debited",
        "last_activity_at",
        "created_at",
        "updated_at",
    )


@admin.register(WalletEntry)
class WalletEntryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "wallet",
        "website",
        "entry_type",
        "direction",
        "status",
        "amount",
        "reference_type",
        "reference_id",
        "created_at",
    )
    list_filter = (
        "entry_type",
        "direction",
        "status",
        "website",
    )
    search_fields = (
        "id",
        "wallet__owner_user__email",
        "wallet__owner_user__username",
        "reference",
        "reference_type",
        "reference_id",
    )
    readonly_fields = (
        "wallet",
        "website",
        "entry_type",
        "direction",
        "status",
        "amount",
        "balance_before",
        "balance_after",
        "reference",
        "reference_type",
        "reference_id",
        "description",
        "metadata",
        "created_by",
        "created_at",
        "updated_at",
    )


@admin.register(WalletHold)
class WalletHoldAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "wallet",
        "website",
        "amount",
        "status",
        "reason",
        "reference_type",
        "reference_id",
        "expires_at",
        "created_at",
    )
    list_filter = (
        "status",
        "website",
    )
    search_fields = (
        "id",
        "wallet__owner_user__email",
        "wallet__owner_user__username",
        "reference",
        "reference_type",
        "reference_id",
        "reason",
    )
    readonly_fields = (
        "released_at",
        "captured_at",
        "created_at",
        "updated_at",
    )