from django.db.models.signals import post_save
from django.dispatch import receiver
from decimal import Decimal
from orders.models import Order
from client_management.models import ClientProfile
from .models import Milestone, ClientBadge, LoyaltyTransaction, LoyaltyTier


@receiver(post_save, sender=Order)
def add_loyalty_points_on_order(sender, instance, created, **kwargs):
    """
    Adds loyalty points to a client's balance when an order is marked as 'completed'.
    """
    if created or instance.status != 'completed':
        return

    # Get the client's profile
    client_profile = ClientProfile.objects.filter(user=instance.client).first()
    if not client_profile:
        return

    # Calculate points (e.g., 1 point for every $10 spent)
    # Order model uses total_price, but some code may reference total_cost
    total_cost = getattr(instance, 'total_cost', None) or getattr(instance, 'total_price', Decimal('0.00'))
    points = int(total_cost // 10)

    # Update the client's loyalty points and create a transaction
    client_profile.loyalty_points += points
    client_profile.save()

    LoyaltyTransaction.objects.create(
        client=client_profile,
        points=points,
        transaction_type='add',
        reason=f"Loyalty points for order #{instance.id}",
    )


@receiver(post_save, sender=LoyaltyTransaction)
def update_loyalty_tier(sender, instance, created, **kwargs):
    """
    Updates the client's loyalty tier based on their total points.
    """
    if not created:
        return

    client_profile = instance.client
    total_points = client_profile.loyalty_points

    # Get the highest tier the client qualifies for
    applicable_tiers = LoyaltyTier.objects.filter(
        website=client_profile.website,
        threshold__lte=total_points
    ).order_by('-threshold')

    if applicable_tiers.exists():
        client_profile.tier = applicable_tiers.first()
        client_profile.save()


@receiver(post_save, sender=LoyaltyTransaction)
def award_milestone_on_points(sender, instance, created, **kwargs):
    """
    Awards milestones to clients based on their achievements.
    """
    if not created:
        return

    client_profile = instance.client

    # Check if any milestones have been achieved
    milestones = Milestone.objects.filter(
        target_type='loyalty_points',
        target_value__lte=client_profile.loyalty_points
    ).exclude(
        id__in=client_profile.badges.values_list('id', flat=True)  # Avoid re-awarding badges
    )

    for milestone in milestones:
        # Award points for the milestone
        client_profile.loyalty_points += milestone.reward_points
        client_profile.save()

        # Log the milestone as a badge
        ClientBadge.objects.create(
            client=client_profile,
            badge_name=f"Milestone: {milestone.name}",
            description=milestone.description
        )

        # Create a transaction for the milestone reward
        LoyaltyTransaction.objects.create(
            client=client_profile,
            points=milestone.reward_points,
            transaction_type='add',
            reason=f"Milestone achieved: {milestone.name}"
        )


@receiver(post_save, sender=LoyaltyTransaction)
def handle_redeemed_points(sender, instance, created, **kwargs):
    """
    Deducts loyalty points from the client's balance when redeemed.
    """
    if not created or instance.transaction_type != 'redeem':
        return

    client_profile = instance.client

    # Deduct the points
    if client_profile.loyalty_points >= abs(instance.points):
        client_profile.loyalty_points -= abs(instance.points)
        client_profile.save()
    else:
        raise ValueError("Insufficient points for redemption.")