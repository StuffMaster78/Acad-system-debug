from django.core.mail import send_mail
from django.conf import settings

def send_registration_email(user, registration_token, website):
    """
    Sends a registration confirmation email to the user.
    
    Args:
        user (User): The user the email is for.
        registration_token (RegistrationToken): The token object.
        website (Website): The website/tenant instance.
    """
    subject = "Complete Your Registration"
    registration_link = f"{website.domain}/register/confirm/{registration_token.token}"
    message = (
        f"Hi {user.first_name},\n\n"
        f"You're almost done setting up your account. "
        f"Click the link below to complete your registration:\n\n"
        f"{registration_link}\n\n"
        f"This link expires in 24 hours.\n\n"
        f"Cheers,\n{website.name} Team"
    )
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False
    )