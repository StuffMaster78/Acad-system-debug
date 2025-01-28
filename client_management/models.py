from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from websites.models import Website
from orders.models import Order
from wallet.models import Wallet

User = get_user_model()

class ClientProfile(models.Model):
    """
    Stores client-specific details and integrates order, wallet, and activity data.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="client_profile",
        limit_choices_to={'role': 'client'},
        help_text=_("The user associated with this client profile.")
    )
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="clients",
        help_text=_("Website the client is associated with."),
    )
    country = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text=_("Country of the client.")
    )
    timezone = models.CharField(
        max_length=50,
        default="UTC",
        help_text=_("Client's timezone for accurate date and time displays.")
    )
    ip_address = models.GenericIPAddressField(
        blank=True,
        null=True,
        help_text=_("IP address of the client.")
    )
    location_verified = models.BooleanField(
        default=False,
        help_text=_("Whether the client's location has been verified.")
    )
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        help_text=_("Client's phone number.")
    )
    registration_id = models.CharField(
        max_length=50,
        unique=True,
        help_text=_("Unique client registration ID (e.g., Client #12345).")
    )
    loyalty_points = models.PositiveIntegerField(
        default=0, 
        help_text=_("Total loyalty points accumulated by the client.")
    )
    tier = models.ForeignKey(
        'LoyaltyTier',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="clients_in_tier",
        help_text=_("Loyalty tier of the client.")
    )
    total_spent = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        help_text=_("Total amount spent by the client.")
    )
    preferred_writers = models.ManyToManyField(
        User,
        blank=True,
        limit_choices_to={'role': 'writer'},
        related_name="preferred_by_clients",
        help_text=_("Client's preferred writers.")
    )
    last_online = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("The last time the client was online.")
    )
    date_joined = models.DateTimeField(
        default=now,
        help_text=_("Date when the client registered.")
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_("Indicates whether the client account is active.")
    )
    is_suspended = models.BooleanField(
        default=False,
        help_text=_("Indicates whether the client account is suspended.")
    )
    is_locked = models.BooleanField(
        default=False,
        help_text=_("Indicates if the account is locked due to suspicious activity."),
    )

    def __str__(self):
        return f"Client Profile: {self.user.username} ({self.registration_id})"
    
    @property
    def wallet_balance(self):
        """
        Retrieve the wallet balance from the wallet app.
        """
        wallet = Wallet.objects.filter(user=self.user).first()
        return wallet.balance if wallet else 0.00
    
    def get_wallet_transactions(self):
        """
        Retrieve wallet transactions for the client.
        """
        wallet = Wallet.objects.filter(user=self.user).first()
        return wallet.transactions.all() if wallet else []

    def add_loyalty_points(self, points, reason=None):
        """
        Add loyalty points to the client's balance and update their tier.
        """
        self.loyalty_points += points
        self._update_tier()
        self.save()
        LoyaltyTransaction.objects.create(
            client=self,
            points=points,
            transaction_type="add",
            reason=reason,
        )

    def update_geolocation(self, ip_address):
        """
        Update geolocation data for the client using their IP address.
        """
        from .utils import get_geolocation_from_ip

        geo_data = get_geolocation_from_ip(ip_address)
        if "error" not in geo_data:
            self.country = geo_data.get("country")
            self.timezone = geo_data.get("timezone")
            self.ip_address = ip_address
            self.location_verified = True
            self.save()
        else:
            print(f"Geolocation error: {geo_data['error']}")

    def _update_tier(self):
        """
        Automatically update the client's tier based on loyalty points.
        """
        applicable_tiers = LoyaltyTier.objects.filter(
            website=self.website, threshold__lte=self.loyalty_points
        ).order_by('-threshold')
        self.tier = applicable_tiers.first() if applicable_tiers.exists() else None

    def get_orders(self):
        """
        Retrieve all orders associated with the client.
        """
        return Order.objects.filter(client=self.user).order_by('-created_at')

    def get_activity_log(self):
        """
        Retrieve the client's activity log (to be implemented in activity logging).
        """
        from activity.models import ActivityLog  # Assuming you have an activity log app
        return ActivityLog.objects.filter(user=self.user).order_by('-timestamp')

    def suspend_account(self, admin):
        """
        Suspend the client account and log the action.
        """
        self.is_suspended = True
        self.is_active = False
        self.save()
        # Log the suspension
        from activity.models import ActivityLog
        ActivityLog.objects.create(
            user=admin,
            action=f"Suspended client account: {self.user.username}"
        )

    def deactivate_account(self, admin):
        """
        Deactivate the client account and log the action.
        """
        self.is_active = False
        self.save()
        # Log the deactivation
        from activity.models import ActivityLog
        ActivityLog.objects.create(
            user=admin,
            action=f"Deactivated client account: {self.user.username}"
        )

    def activate_account(self, admin):
        """
        Reactivate the client account and log the action.
        """
        self.is_active = True
        self.is_suspended = False
        self.save()
        # Log the activation
        from activity.models import ActivityLog
        ActivityLog.objects.create(
            user=admin,
            action=f"Reactivated client account: {self.user.username}"
        )

    def set_password_reset_code(self, code, admin):
        """
        Set a password reset code for the client and log the action.
        """
        self.user.password_reset_code = code
        self.user.save()
        # Log the reset code action
        from activity.models import ActivityLog
        ActivityLog.objects.create(
            user=admin,
            action=f"Set password reset code for client: {self.user.username}"
        )

    def set_temporary_password(self, temp_password, admin):
        """
        Set a temporary password for the client and log the action.
        """
        self.user.set_password(temp_password)
        self.user.save()
        # Log the temporary password action
        from activity.models import ActivityLog
        ActivityLog.objects.create(
            user=admin,
            action=f"Set temporary password for client: {self.user.username}"
        )

class SuspiciousLogin(models.Model):
    client = models.ForeignKey(ClientProfile, on_delete=models.CASCADE, related_name="suspicious_logins")
    ip_address = models.GenericIPAddressField()
    detected_country = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Suspicious login for {self.client.user.username} from {self.detected_country}"


class Milestone(models.Model):
    """
    Configurable milestones for clients, defined by admins.
    """
    name = models.CharField(max_length=100, help_text=_("Name of the milestone (e.g., 'First $100 Spent')."))
    description = models.TextField(blank=True, null=True, help_text=_("Details about the milestone."))
    target_type = models.CharField(
        max_length=50,
        choices=(
            ('total_spent', 'Total Spent'),
            ('loyalty_points', 'Loyalty Points'),
            ('orders_placed', 'Orders Placed'),
        ),
        help_text=_("Type of milestone (e.g., total spent, loyalty points).")
    )
    target_value = models.PositiveIntegerField(help_text=_("The value the client must achieve to earn this milestone."))
    reward_points = models.PositiveIntegerField(default=0, help_text=_("Loyalty points rewarded upon achieving this milestone."))
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Milestone: {self.name} (Target: {self.target_value})"
    
class ClientBadge(models.Model):
    """
    Award badges to clients for special achievements.
    """
    client = models.ForeignKey(
        ClientProfile,
        on_delete=models.CASCADE,
        related_name="badges",
    )
    badge_name = models.CharField(max_length=100, help_text=_("Name of the badge (e.g., 'Top Spender')."))
    description = models.TextField(blank=True, null=True, help_text=_("Details about why this badge was awarded."))
    awarded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Badge: {self.badge_name} for {self.client.user.username}"
    
class ClientActivityLog(models.Model):
    """
    Logs all client-related activities for audit purposes.
    """
    client = models.ForeignKey(
        ClientProfile,
        on_delete=models.CASCADE,
        related_name="activity_logs",
    )
    action = models.CharField(max_length=255, help_text=_("Description of the activity."))
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Activity: {self.action} by {self.client.user.username} at {self.timestamp}"

class TemporaryPassword(models.Model):
    """
    Stores temporary passwords or reset codes for clients.
    """
    client = models.OneToOneField(
        ClientProfile,
        on_delete=models.CASCADE,
        related_name="temporary_password",
    )
    code = models.CharField(max_length=50, help_text=_("Temporary password or reset code."))
    expires_at = models.DateTimeField(help_text=_("Expiration date and time for the temporary password."))

    def is_valid(self):
        """
        Check if the temporary password is still valid.
        """
        from django.utils.timezone import now
        return now() < self.expires_at

    def __str__(self):
        return f"Temporary Password for {self.client.user.username} (Expires: {self.expires_at})"

class LoyaltyTier(models.Model):
    """
    Configurable loyalty tiers for clients, defined by admins.
    """
    name = models.CharField(max_length=50, help_text=_("Name of the loyalty tier (e.g., Bronze, Silver, Gold)."))
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="loyalty_tiers",
        help_text=_("Website this tier is associated with."),
    )
    threshold = models.PositiveIntegerField(help_text=_("Minimum points required to qualify for this tier."))
    discount_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.0, help_text=_("Discount percentage for clients in this tier.")
    )
    priority_support = models.BooleanField(default=False, help_text=_("Does this tier include priority support?"))
    dedicated_manager = models.BooleanField(default=False, help_text=_("Does this tier include a dedicated manager?"))
    perks = models.TextField(blank=True, null=True, help_text=_("Additional perks or benefits for this tier."))

    def __str__(self):
        return f"{self.name} (Threshold: {self.threshold})"

class LoyaltyTransaction(models.Model):
    """
    Tracks loyalty points transactions for clients.
    """
    client = models.ForeignKey(
        ClientProfile,
        on_delete=models.CASCADE,
        related_name="loyalty_transactions",
    )
    points = models.IntegerField(help_text=_("Points added or deducted."))
    transaction_type = models.CharField(
        max_length=20,
        choices=(("add", "Add"), ("deduct", "Deduct")),
        default="add",
    )
    reason = models.TextField(blank=True, null=True, help_text=_("Reason for the loyalty transaction."))
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transaction: {self.points} points ({self.transaction_type}) for {self.client.user.username}"