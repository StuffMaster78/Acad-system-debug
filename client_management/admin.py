from django.contrib import admin
from .models import ClientProfile, LoyaltyTransaction
from client_management.models import LoyaltyPoint, LoyaltyPointHistory

@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    list_display = ('client', 'loyalty_points', 'total_spent')
    search_fields = ('client__username', 'client__email')
    list_filter = ('loyalty_points',)


@admin.register(LoyaltyTransaction)
class LoyaltyTransactionAdmin(admin.ModelAdmin):
    list_display = ('client', 'points', 'transaction_type', 'timestamp')
    search_fields = ('client__client__username',)
    list_filter = ('transaction_type',)


@admin.register(LoyaltyPoint)
class LoyaltyPointAdmin(admin.ModelAdmin):
    list_display = ('client', 'points', 'last_updated')
    search_fields = ('client__username', 'client__email')
    ordering = ('-points',)


@admin.register(LoyaltyPointHistory)
class LoyaltyPointHistoryAdmin(admin.ModelAdmin):
    list_display = ('client', 'points_change', 'reason', 'timestamp')
    search_fields = ('client__username', 'client__email')
    ordering = ('-timestamp',)