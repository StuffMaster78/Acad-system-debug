from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
from django.contrib.auth import get_user_model
from .models import ClientProfile
from core.utils.location import get_geolocation_from_ip, get_client_ip

User = get_user_model()

# Signal to create a ClientProfile when a new client user is created
@receiver(post_save, sender=User)
def create_client_profile(sender, instance, created, **kwargs):
    """
    Automatically create a ClientProfile for a user with the 'client' role.
    """
    if created and instance.role == "client":
        ClientProfile.objects.create(user=instance)


# Signal to fetch and update geolocation data on client login
@receiver(user_logged_in)
def update_client_geolocation(sender, request, user, **kwargs):
    """
    Fetch and update geolocation data for the client on login.
    """
    if user.role == "client":
        try:
            client_profile = user.client_profile
            ip_address = get_client_ip(request)  # Fetch client IP address
            geo_data = get_geolocation_from_ip(ip_address)  # Fetch geolocation data

            if "error" not in geo_data:
                detected_country = geo_data.get("country")
                previous_country = client_profile.country

                # Check for country mismatch and log it
                if previous_country and detected_country != previous_country:
                    print(
                        f"Country mismatch detected for {user.username}: "
                        f"{previous_country} (previous) vs {detected_country} (current)"
                    )
                    # Optional: Add logic to send location alert
                    send_location_alert(user, previous_country, detected_country, ip_address)

                # Update the client profile with new geolocation data
                client_profile.country = detected_country
                client_profile.timezone = geo_data.get("timezone")
                client_profile.ip_address = ip_address
                client_profile.location_verified = True
                client_profile.save()
        except ClientProfile.DoesNotExist:
            print(f"No ClientProfile found for user {user.username}")


def send_location_alert(user, previous_country, current_country, ip_address):
    """
    Send an email notification to the client about a login from a new location.
    """
    from django.core.mail import send_mail

    subject = "Account Login from a New Location"
    message = (
        f"Hi {user.username},\n\n"
        f"We noticed a login to your account from a new location:\n"
        f"- Previous Location: {previous_country}\n"
        f"- Current Location: {current_country}\n"
        f"- IP Address: {ip_address}\n\n"
        f"If this was not you, please secure your account immediately by changing your password.\n\n"
        f"Thank you,\n"
        f"Your Support Team"
    )
    send_mail(
        subject,
        message,
        "support@yourdomain.com",  # Replace with your support email
        [user.email],
    )