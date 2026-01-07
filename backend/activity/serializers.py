from rest_framework import serializers
from activity.models import ActivityLog


class ActivityLogSerializer(serializers.ModelSerializer):
    """Serializer for activity logs with expanded context."""
    user_email = serializers.SerializerMethodField()
    user_role = serializers.SerializerMethodField()
    triggered_by_email = serializers.SerializerMethodField()
    website = serializers.SerializerMethodField()
    formatted_timestamp = serializers.SerializerMethodField()
    display_description = serializers.SerializerMethodField()

    class Meta:
        model = ActivityLog
        fields = [
            "id",
            "user_email",
            "user_role",
            "triggered_by_email",
            "website",
            "actor_type",
            "action_type",
            "action_subtype",
            "description",
            "display_description",
            "timestamp",
            "formatted_timestamp",
            "metadata",
        ]
        read_only_fields = ["id", "timestamp", "metadata"]

    def get_user_email(self, obj):
        """Get the email of the user associated with the activity log."""
        if obj.user:
            return obj.user.email
        return None

    def get_user_role(self, obj):
        """Get the role of the user associated with the activity log."""
        try:
            if not obj.user:
                return obj.actor_type if obj.actor_type else None
            # Check if user has a role attribute directly
            if hasattr(obj.user, "role"):
                return obj.user.role
            # Check if user has a profile with role
            if hasattr(obj.user, "profile"):
                return getattr(obj.user.profile, "role", None)
            return getattr(obj.user, "user_type", None)
        except Exception:
            return obj.actor_type if obj.actor_type else None
    
    def get_triggered_by_email(self, obj):
        """Get the email of the user who triggered the activity."""
        if obj.triggered_by:
            return obj.triggered_by.email
        return None
    
    def get_website(self, obj):
        """Get website information."""
        try:
            if obj.website:
                return {
                    "id": obj.website.id,
                    "name": obj.website.name,
                    "domain": obj.website.domain,
                    "slug": obj.website.slug if hasattr(obj.website, "slug") else None,
                }
        except Exception:
            pass
        return None
    
    def get_formatted_timestamp(self, obj):
        """Format timestamp for display (e.g., '05:55 16, Nov 2025')."""
        from django.utils import timezone
        from datetime import datetime
        
        if not obj.timestamp:
            return None
        
        # Format: "HH:MM DD, Mon YYYY"
        return obj.timestamp.strftime("%H:%M %d, %b %Y")
    
    def get_display_description(self, obj):
        """Get formatted description for display.
        
        For user actions (where user or triggered_by matches current user),
        format description with "You" prefix for better UX.
        """
        request = self.context.get('request')
        description = obj.description
        
        # Check if current user performed this action
        if request and request.user:
            current_user = request.user
            user_performed_action = (
                (obj.user and obj.user.id == current_user.id) or
                (obj.triggered_by and obj.triggered_by.id == current_user.id)
            )
            
            # Format description with "You" if user performed the action
            if user_performed_action and not description.lower().startswith('you '):
                # Capitalize first letter and add "You" prefix
                description = description.strip()
                if description:
                    # Remove any existing subject (e.g., "sent a message" -> "You sent a message")
                    description = description[0].lower() + description[1:] if len(description) > 1 else description
                    description = f"You {description}"
        
        # Enhance description based on metadata if available
        if obj.metadata:
            # Add order number if present
            if 'order_id' in obj.metadata:
                order_id = obj.metadata.get('order_id')
                if f"order {order_id}" not in description.lower() and f"#{order_id}" not in description.lower():
                    description = f"{description} (Order #{order_id})"
            
            # Add ticket ID if present
            if 'ticket_id' in obj.metadata:
                ticket_id = obj.metadata.get('ticket_id')
                if ticket_id not in description:
                    description = f"{description} (Ticket ID: {ticket_id})"
        
        return description