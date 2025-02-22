from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class ActivityLog(models.Model):
    ACTION_TYPES = [
        ("ORDER", "Order"),
        ("PAYMENT", "Payment"),
        ("NOTIFICATION", "Notification"),
        ("COMMUNICATION", "Communication"),
        ("LOYALTY", "Loyalty"),
        ("USER", "User"),
        ("SYSTEM", "System"),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="activity_logs_general")
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    description = models.TextField()  # Human-readable activity log
    timestamp = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(blank=True, null=True)  # Extra data for detailed logs (e.g., order_id, amount)
    
    def __str__(self):
        return f"{self.user} - {self.action_type} - {self.description[:50]}"
