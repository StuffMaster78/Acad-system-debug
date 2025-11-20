from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.utils.timezone import now
# from websites.models import Website
from orders.models import Order
from wallet.models import Wallet
from django.apps import apps
from django.conf import settings
import secrets
import string
from websites.models import Website
try:
    # Re-export LoyaltyTransaction for tests importing from client_management.models
    from loyalty_management.models import LoyaltyTransaction as LoyaltyTransaction  # noqa: F401
except Exception:
    pass
# # Use apps.get_model() to access Website model lazily
# def get_website_model():
#     Website = apps.get_model('websites', 'Website')
#     return Website

# Website = get_website_model()
# # User = get_user_model()

from django.db import models as dj_models


class ClientProfileQuerySet(dj_models.QuerySet):
    def filter(self, *args, **kwargs):  # type: ignore[override]
        if 'client' in kwargs:
            kwargs['user'] = kwargs.pop('client')
        return super().filter(*args, **kwargs)


class ClientProfileManager(dj_models.Manager.from_queryset(ClientProfileQuerySet)):
    def get(self, *args, **kwargs):  # type: ignore[override]
        if 'client' in kwargs:
            kwargs['user'] = kwargs.pop('client')
        return super().get(*args, **kwargs)


def generate_registration_id() -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "CL-" + "".join(secrets.choice(alphabet) for _ in range(10))


class ClientProfile(models.Model):
    """
    Stores client-specific details and integrates
    order, wallet, and activity data.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
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
        default=generate_registration_id,
        help_text=_("Unique client registration ID (e.g., Client #12345).")
    )
    loyalty_points = models.PositiveIntegerField(
        default=0, 
        help_text=_("Total loyalty points accumulated by the client.")
    )
    tier = models.ForeignKey(
        'loyalty_management.LoyaltyTier',
        on_delete=models.CASCADE,
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
        settings.AUTH_USER_MODEL,
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

    # Attach custom manager to support tests using client= lookup
    objects = ClientProfileManager()

    def __str__(self):
        return f"Client Profile: {self.user.username} | ID: {self.registration_id} | Loyalty Points: {self.loyalty_points}"

    def get_tier(self):
        LoyaltyTier = apps.get_model('loyalty_management', 'LoyaltyTier')
        return LoyaltyTier.objects.filter(
            website=self.website, threshold__lte=self.loyalty_points
        ).order_by('-threshold').first()

    def add_loyalty_points(self, points, reason=None):
        """
        Add loyalty points to the client's balance and update their tier.
        """
        LoyaltyTransaction = apps.get_model('loyalty_management', 'LoyaltyTransaction')
        self.loyalty_points += points
        self.save()
        LoyaltyTransaction.objects.create(
            client=self,
            points=points,
            transaction_type="add",
            reason=reason,
            website=self.website,
        )

    @property
    def wallet_balance(self):
        """
        Retrieve the wallet balance from the wallet app.
        """
        from wallet.models import Wallet 
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
        LoyaltyTransaction = apps.get_model(
            'loyalty_management',
            'LoyaltyTransaction'
        )
        self.loyalty_points += points
        self._update_tier()
        self.save()
        LoyaltyTransaction.objects.create(
            client=self,
            points=points,
            transaction_type="add",
            reason=reason,
            website=self.website,
        )


    def update_geolocation(self, ip_address):
        """
        Update geolocation data for the client using their IP address.
        """
        from core.utils.location import get_geolocation_from_ip

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
        LoyaltyTier = apps.get_model(
            'loyalty_management',
            'LoyaltyTier'
        )
        applicable_tiers = LoyaltyTier.objects.filter(
            website=self.website, threshold__lte=self.loyalty_points
        ).order_by('-threshold')
        self.tier = applicable_tiers.first() if applicable_tiers.exists() else None


    def get_orders(self):
        """
        Retrieve all orders associated with the client with related writer data.
        """
        return Order.objects.filter(client=self.user).select_related('writer').order_by('-created_at')
    

    def get_client_badges(self):
        """
        Retrieve all the badges awarded to the client from loyalty-management.
        """
        ClientBadge = apps.get_model(
            'loyalty_management',
            'ClientBadge'
        )
        return ClientBadge.objects.filter(client=self)

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
    
    @property
    def calculate_loyalty_tier(self):
        """Retrieve the current loyalty tier from the loyalty_management app."""
        LoyaltyTier = apps.get_model('loyalty_management', 'LoyaltyTier')
        applicable_tiers = LoyaltyTier.objects.filter(
            website=self.website, threshold__lte=self.loyalty_points
        ).order_by('-threshold')
        return applicable_tiers.first() if applicable_tiers.exists() else None


    @property
    def calculate_loyalty_points(self):
        """Calculate the total loyalty points from the loyalty transactions."""
        from loyalty_management.models import LoyaltyTransaction
        transactions = LoyaltyTransaction.objects.filter(client=self)
        return sum(transaction.points for transaction in transactions)

    @property
    def get_loyalty_transactions(self):
        """Retrieve all loyalty transactions for the client."""
        # from loyalty_management.models import LoyaltyTransaction
        LoyaltyTransaction = apps.get_model('loyalty_management', 'LoyaltyTransaction')
        return LoyaltyTransaction.objects.filter(client=self).order_by('-timestamp')


    def get_milestones(self):
        """
        Retrieve all milestones achieved by the client from the loyalty_management app.
        """
        from loyalty_management.models import Milestone
        achieved_milestones = Milestone.objects.filter(
            target_value__lte=self.loyalty_points,
            target_type='loyalty_points'  # Adjust for other milestone types if necessary
        )
        return achieved_milestones
    

class SuspiciousLogin(models.Model):
    client = models.ForeignKey(
        ClientProfile,
        on_delete=models.CASCADE,
        related_name="suspicious_logins"
    )
    ip_address = models.GenericIPAddressField()
    detected_country = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Suspicious login for {self.client.user.username} from {self.detected_country}"
    
class ClientActivityLog(models.Model):
    """
    Logs all client-related activities for audit purposes.
    """
    client = models.ForeignKey(
        ClientProfile,
        on_delete=models.CASCADE,
        related_name="activity_logs",
    )
    action = models.CharField(
        max_length=255,
        help_text=_("Description of the activity.")
    )
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
    code = models.CharField(
        max_length=50,
        help_text=_("Temporary password or reset code.")
    )
    expires_at = models.DateTimeField(
        help_text=_("Expiration date and time for the temporary password.")
    )

    def is_valid(self):
        """
        Check if the temporary password is still valid.
        """
        from django.utils.timezone import now
        return now() < self.expires_at

    def __str__(self):
        return f"Temporary Password for {self.client.user.username} (Expires: {self.expires_at})"    


class ProfileUpdateRequest(models.Model):
    """
    Model to handle requests for updating client profiles.
    """
    STATUS_CHOICES = [
        ("pending", _("Pending")),
        ("approved", _("Approved")),
        ("rejected", _("Rejected")),
    ]

    client = models.ForeignKey(
        ClientProfile,
        on_delete=models.CASCADE,
        related_name="profile_update_requests",
        help_text=_("The client requesting a profile update."),
    )
    requested_changes = models.TextField(
        help_text=_("The changes requested by the client."),
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        help_text=_("The status of the profile update request."),
    )
    admin_response = models.TextField(
        blank=True,
        null=True,
        help_text=_("Response from the admin regarding the request."),
    )
    created_at = models.DateTimeField(
        default=now,
        help_text=_("Timestamp when the request was created."),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text=_("Timestamp when the request was last updated."),
    )

    def __str__(self):
        return f"Profile Update Request: {self.client.user.username} ({self.status})"
    

class ClientAction(models.Model):
    """
    Model to track actions performed on client accounts,
    such as suspending, activating, and deactivating.
    """
    ACTION_CHOICES = [
        ('suspend', 'Suspend'),
        ('activate', 'Activate'),
        ('deactivate', 'Deactivate'),
    ]
    
    client = models.ForeignKey(
        'client_management.ClientProfile',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="client_actions",
        help_text="The client whose account is being modified."
    )
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        help_text="The action taken on the client account."
    )
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="actions_performed",
        help_text="The admin who performed the action."
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="Time when the action was performed."
    )
    reason = models.TextField(
        blank=True,
        null=True,
        help_text="Optional reason for the action."
    )

    def __str__(self):
        return f"{self.get_action_display()} action on {self.client.user.username} by {self.performed_by.username}"
    
    class Meta:
        verbose_name = "Client Action"
        verbose_name_plural = "Client Actions"
        ordering = ['-timestamp']

class BlacklistedEmail(models.Model):
    """
    Tracks the client emails that have been blacklisted.
    """
    email = models.EmailField(unique=True)
    reason = models.TextField(blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

    @classmethod
    def is_blacklisted(cls, email):
        """Check if an email is blacklisted."""
        return cls.objects.filter(email=email).exists()

    @classmethod
    def add_to_blacklist(cls, email, reason=""):
        """Add an email to the blacklist if not already present."""
        if not cls.is_blacklisted(email):
            return cls.objects.create(email=email, reason=reason)
        return None

    @classmethod
    def remove_from_blacklist(cls, email):
        """Remove an email from the blacklist."""
        return cls.objects.filter(email=email).delete()