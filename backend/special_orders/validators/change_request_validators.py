class ChangeRequestValidator:
    """
    Prevents silent scope creep.
    """

    @staticmethod
    def validate_requires_quote(pricing_impact):
        if pricing_impact == "additional_charge":
            return True
        return False