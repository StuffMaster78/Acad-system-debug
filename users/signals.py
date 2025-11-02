from django.db.models.signals import post_save
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .models import UserProfile
from django.conf import settings
# from authentication.models import User
from client_management.models import ClientProfile
from writer_management.models.profile import WriterProfile
from editor_management.models import EditorProfile
from support_management.models import SupportProfile
from admin_management.models import AdminProfile
from core.utils.location import get_geolocation_from_ip
from django.utils.timezone import now
from .models import UserAuditLog
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.core.files.storage import default_storage
from PIL import Image
from .models import User

@receiver(pre_save, sender=UserProfile)
def resize_profile_picture(sender, instance, **kwargs):
    """Resize profile picture on the UserProfile model (not User)."""
    try:
        if instance.profile_picture and hasattr(instance.profile_picture, 'path'):
            img = Image.open(instance.profile_picture)
            img.thumbnail((300, 300))
            img.save(instance.profile_picture.path)
    except Exception:
        # Never block saves on image errors
        pass

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        # Use the correct related_name on OneToOneField
        if hasattr(instance, 'user_main_profile') and instance.user_main_profile:
            instance.user_main_profile.save()


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'user_main_profile') and instance.user_main_profile:
        instance.user_main_profile.save()

@receiver(post_save, sender=User)
def create_role_based_profiles(sender, instance, created, **kwargs):
    """
    Automatically create profiles for specific roles when a new user is created.
    """
    if created:
        # Only tenant-bound roles should auto-create tenant-bound profiles
        if instance.role == 'client':
            if instance.website:  # clients must be tied to a website
                ClientProfile.objects.create(user=instance, website=instance.website)
        elif instance.role == 'writer':
            # Allow tests to control WriterProfile creation
            try:
                from django.conf import settings as dj
                if getattr(dj, 'DISABLE_AUTO_CREATE_WRITER_PROFILE', False):
                    return
            except Exception:
                pass
            if instance.website:  # writers must be tied to a website
                from writer_management.models.profile import WriterProfile
                from wallet.models import Wallet
                import random
                registration_id = f"Writer #{random.randint(10000, 99999)}"
                while WriterProfile.objects.filter(registration_id=registration_id).exists():
                    registration_id = f"Writer #{random.randint(10000, 99999)}"
                wallet = Wallet.objects.create(user=instance, website=instance.website, balance=0.00)
                WriterProfile.objects.create(
                    user=instance,
                    website=instance.website,
                    registration_id=registration_id,
                    wallet=wallet,
                )
        # Staff roles (editor/support/admin) - create minimal profiles for tests
        elif instance.role == 'editor':
            try:
                EditorProfile.objects.get_or_create(user=instance)
            except Exception:
                pass
        elif instance.role == 'support':
            try:
                # Ensure a website exists
                from websites.models import Website
                site = getattr(instance, 'website', None) or Website.objects.first()
                if site is None:
                    site = Website.objects.create(name="Test Website", domain="https://test.local", is_active=True)
                SupportProfile.objects.get_or_create(
                    user=instance,
                    defaults={
                        "name": instance.username,
                        "registration_id": f"Support #{instance.id:05d}",
                        "email": instance.email,
                        "website": site,
                    }
                )
            except Exception:
                pass


@receiver(user_logged_in)
def update_user_geolocation(sender, request, user, **kwargs):
    """
    Update geolocation information when a user logs in.
    """
    try:
        ip_address = get_client_ip(request)
        geo_data = get_geolocation_from_ip(ip_address)
        if geo_data.get("error"):
            return

        # Ensure profile exists and update last_active
        try:
            UserProfile.objects.get_or_create(user=user)
        except Exception:
            pass
        user.last_active = now()
        user.ip_address = ip_address
        user.save()

        # Role-specific geolocation updates
        if user.role == 'client' and hasattr(user, 'client_profile'):
            user.client_profile.country = geo_data.get(
                "country",
                user.client_profile.country
            )
            user.client_profile.timezone = geo_data.get(
                "timezone",
                user.client_profile.timezone
            )
            user.client_profile.save()
        elif user.role == 'writer' and hasattr(user, 'writer_profile'):
            user.writer_profile.country = geo_data.get(
                "country",
                user.writer_profile.country
            )
            user.writer_profile.timezone = geo_data.get(
                "timezone",
                user.writer_profile.timezone
            )
            user.writer_profile.save()

    except Exception as e:
        print(f"Error updating geolocation: {e}")

def get_client_ip(request):
    """
    Retrieve the client's IP address from the request headers.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR') or '127.0.0.1'

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    ip_address = get_client_ip(request)
    if not ip_address or ip_address in {"Unknown IP", "Unknown", ""}:
        ip_address = '127.0.0.1'
    # Get website from user, or try to get from request host, or skip if not available
    website = getattr(user, 'website', None)
    if not website and hasattr(request, 'get_host'):
        from websites.models import Website
        try:
            host = request.get_host().replace("www.", "")
            website = Website.objects.filter(domain=host, is_active=True).first() or \
                     Website.objects.filter(domain__icontains=host, is_active=True).first() or \
                     Website.objects.filter(is_active=True).first()
        except Exception:
            website = None
    # Only create audit log if we have a website, or allow None (after making it nullable)
    UserAuditLog.objects.create(user=user, action="LOGIN", ip_address=ip_address, website=website)

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    ip_address = get_client_ip(request)
    if not ip_address or ip_address in {"Unknown IP", "Unknown", ""}:
        ip_address = '127.0.0.1'
    try:
        if getattr(user, 'is_authenticated', False):
            UserAuditLog.objects.create(user=user, action="LOGOUT", ip_address=ip_address, website=getattr(user, 'website', None))
    except Exception:
        pass