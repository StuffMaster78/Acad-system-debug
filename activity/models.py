from django.db import models
from django.contrib.auth import get_user_model
from django.apps import apps
from websites.models import Website
from django.utils.translation import gettext_lazy as _
# Use apps.get_model() to access Website model lazily
# def get_website_model():
#     Website = apps.get_model('websites', 'Website')
#     return Website

# Website = get_website_model()
User = get_user_model()


class ActorType(models.TextChoices):
    ADMIN = "admin", _("Admin")
    CLIENT = "client", _("Client")
    SUPPORT = "support", _("Support")
    SUPERADMIN = "superadmin", _("Super Admin")
    EDITOR = "editor", _("Editor")
    WRITER = "writer", _("Writer")
    USER = "user", _("User")
    SYSTEM = "system", _("System")
    SERVICE = "service", _("Background Service") 
class ActivityLog(models.Model):
    """
    Represents a general activity log for actions performed on the website.
    This model is designed to track various actions such as orders, payments, notifications,
    communications, loyalty programs, and user activities.
    It can be used to log actions performed by users, system processes, or background services.
    """
    ACTION_TYPES = [
        ("ORDER", "Order"),
        ("PAYMENT", "Payment"),
        ("NOTIFICATION", "Notification"),
        ("COMMUNICATION", "Communication"),
        ("LOYALTY", "Loyalty"),
        ("USER", "User"),
        ("SYSTEM", "System"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="activity_logs_general"
    )
    triggered_by = models.ForeignKey(
        User, null=True, blank=True,
        related_name="activity_logs_triggered",
        on_delete=models.SET_NULL
    )

    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="activity_logs"
    )
    actor_type = models.CharField(
        max_length=20,
        choices=ActorType.choices,
        default=ActorType.SYSTEM,
        help_text=_("The origin of the action.")
    )
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    action_subtype = models.CharField(max_length=30, blank=True, null=True)
    # action_subtype is optional for more specific categorization of actions
    description = models.TextField()  # Human-readable activity log

    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)

    timestamp = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(blank=True, null=True)  # Extra data for detailed logs (e.g., order_id, amount)
    
    def __str__(self):
        user_str = self.user.username if self.user else "System"
        return f"[{self.action_type}] {user_str}: {self.description[:50]}"


    class Meta:
        indexes = [
            models.Index(fields=["website", "timestamp"]),
            models.Index(fields=["user", "timestamp"]),
            models.Index(fields=["action_type"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "website", "action_type", "timestamp"],
                name="unique_activity_log_per_user_website_action"
            )
        ]
        ordering = ["-timestamp"]  # Newest first   
        verbose_name = "Activity Log"
        verbose_name_plural = "Activity Logs"

    def get_related_object(self):
        """ Retrieve the related object based on metadata.
            Assumes metadata contains 'related_model' and 'related_id'.
        """
        from django.apps import apps
        model_label = self.metadata.get("related_model")
        obj_id = self.metadata.get("related_id")
        if model_label and obj_id:
            model = apps.get_model(model_label)
            return model.objects.filter(pk=obj_id).first()
        return None


    def save(self, *args, **kwargs):
        # Ensure that the user is set if not provided
        if not self.user:
            self.user = self.triggered_by
        super().save(*args, **kwargs)