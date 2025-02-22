from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
from django.contrib.auth import get_user_model
from .models import ClientProfile, SuspiciousLogin
from core.utils.location import get_geolocation_from_ip, get_client_ip
from django.core.mail import send_mail

User = get_user_model()


@receiver(post_save, sender=User)
def create_client_profile(sender, instance, created, **kwargs):
    """
    Automatically create a ClientProfile for a user with the 'client' role.
    """
    if created and instance.role == "client":
        ClientProfile.objects.create(user=instance)
        print(f"ClientProfile created for user: {instance.username}")


@receiver(user_logged_in)
def update_client_geolocation(sender, request, user, **kwargs):
    """
    Fetch and update geolocation data for the client on login.
    Detect suspicious logins if the location changes.
    """
    if user.role == "client":
        try:
            client_profile = user.client_profile
            ip_address = get_client_ip(request)  # Fetch client IP address
            geo_data = get_geolocation_from_ip(ip_address)  # Fetch geolocation data

            if "error" not in geo_data:
                detected_country = geo_data.get("country")
                detected_timezone = geo_data.get("timezone")
                previous_country = client_profile.country
                previous_ip = client_profile.ip_address

                # Check for location mismatch
                if previous_country and detected_country != previous_country:
                    print(
                        f"Location mismatch detected for user {user.username}: "
                        f"{previous_country} (previous) vs {detected_country} (current)."
                    )
                    # Log the suspicious login
                    SuspiciousLogin.objects.create(
                        client=client_profile,
                        ip_address=ip_address,
                        detected_country=detected_country,
                    )
                    # Send a location alert email to the client
                    send_location_alert(user, previous_country, detected_country, ip_address)

                # Update the client profile with new geolocation data
                client_profile.country = detected_country
                client_profile.timezone = detected_timezone
                client_profile.ip_address = ip_address
                client_profile.location_verified = True
                client_profile.save()
                print(f"Geolocation updated for user {user.username}: {detected_country}.")

            else:
                print(f"Geolocation error for user {user.username}: {geo_data['error']}")

        except ClientProfile.DoesNotExist:
            print(f"No ClientProfile found for user {user.username}")


def send_location_alert(user, previous_country, current_country, ip_address):
    """
    Send an email notification to the client about a login from a new location.
    """
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
        fail_silently=False,
    )