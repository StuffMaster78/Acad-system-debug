from django.contrib import admin
from .models import ClientProfile
from loyalty_management.models import LoyaltyTier, LoyaltyTransaction
from client_management.models import BlacklistedEmail

@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user", 
        "registration_id", 
        "website", 
        "country", 
        "timezone", 
        "ip_address", 
        "loyalty_points", 
        "tier", 
        "is_active", 
        "is_suspended", 
        "location_verified",
        "get_milestones_display",  # Display milestones for the client
        "get_loyalty_transactions_display",  # Display loyalty transactions for the client
        "display_client_badges"
    )
    list_filter = (
        "location_verified", 
        "is_active", 
        "is_suspended", 
        "country", 
        "website"
    )
    search_fields = (
        "user__username", 
        "registration_id", 
        "ip_address", 
        "country", 
        "website__name"
    )

    # Custom method to display milestones in the admin
    def get_milestones_display(self, obj):
        """
        Display the milestones achieved by the client in the admin panel.
        """
        milestones = obj.get_milestones()
        if not milestones.exists():
            return "No milestones achieved"
        return "\n".join([f"{milestone.name}: {milestone.description}" for milestone in milestones])
    
    get_milestones_display.short_description = "Achieved Milestones"

    # Custom method to display loyalty transactions in the admin
    def get_loyalty_transactions_display(self, obj):
        """
        Display the loyalty transactions for the client in the admin panel.
        """
        # get_loyalty_transactions is a @property, so access it without parentheses
        transactions = obj.get_loyalty_transactions
        if not transactions.exists():
            return "No transactions"
        return "\n".join([f"Transaction {transaction.id}: {transaction.points} points ({transaction.transaction_type})" for transaction in transactions])
    
    get_loyalty_transactions_display.short_description = "Loyalty Transactions"
    
    # A Custom method to fetch and display client badges in the admin
    def display_client_badges(self, obj):
        return ", ".join([badge.badge_name for badge in obj.get_client_badges()])
    display_client_badges.short_description = "Badges"

@admin.register(BlacklistedEmail)
class BlacklistedEmailAdmin(admin.ModelAdmin):
    list_display = ("email", "reason", "date_added")
    search_fields = ("email",)
    list_filter = ("date_added",)