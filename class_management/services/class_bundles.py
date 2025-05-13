# services/class_bundles.py

from class_management.models import ClassBundle

def list_bundles_for_website(website):
    return ClassBundle.objects.filter(website=website)

def create_bundle(data, website):
    return ClassBundle.objects.create(**data, website=website)

def use_slot(bundle, tutor):
    if bundle.remaining_slots <= 0:
        raise ValueError("No available slots.")
    bundle.remaining_slots -= 1
    bundle.save()
    # log slot usage or notify tutor if needed
    return bundle