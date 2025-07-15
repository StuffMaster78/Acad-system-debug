from celery import shared_task
from loyalty_management.models import ClientProfile
from websites.models import Website
from loyalty_management.services.loyalty_conversion_service import LoyaltyConversionService

@shared_task
def auto_convert_loyalty_points(client_id, website_id):
    client = ClientProfile.objects.get(pk=client_id)
    website = Website.objects.get(pk=website_id)
    LoyaltyConversionService.try_auto_convert(client, website)


@shared_task
def sync_loyalty_points_for_all_clients():
    """
    Recalculate and sync loyalty points for all clients based on their transactions.
    """
    count = 0
    for client in ClientProfile.objects.all():
        if LoyaltyConversionService.sync_loyalty_cache(client):
            count += 1
    return f"Loyalty points synced for {count} clients."

@shared_task
def sync_loyalty_points_for_client(client_id):
    from client_management.models import ClientProfile

    client = ClientProfile.objects.get(id=client_id)
    LoyaltyConversionService.sync_loyalty_cache(client)
