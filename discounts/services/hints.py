def get_stackable_hint(current_codes, website):
    from discounts.models import Discount

    if len(current_codes) >= 2:
        return None  # Already hit max

    valid_discounts = Discount.objects.filter(code__in=current_codes, website=website)
    if not valid_discounts.exists():
        return None

    # Look at all active stackable discounts
    potential = Discount.objects.filter(
        is_active=True,
        stackable=True,
        website=website
    ).exclude(code__in=current_codes)

    for discount in potential:
        # Can this discount be stacked with the existing ones?
        if all(d.stackable for d in valid_discounts):
            return {
                "hint": f"You can stack this with another code: {discount.code}",
                "suggested_code": discount.code
            }

    return None
