from special_orders.models import WriterBonus


class WriterBonusService:
    """
    Service class to manage operations related to WriterBonus.
    """
    
    def get_user_bonuses(user):
        """Return writer bonuses for the user."""
        if user.is_staff:
            return WriterBonus.objects.all()
        return WriterBonus.objects.filter(writer=user)


    def create_writer_bonus(serializer):
        """Create a writer bonus."""
        return serializer.save()
        
    @staticmethod
    def grant_bonus(writer, special_order, amount, category, reason=''):
        """
        Grants a bonus to a writer for a special order.

        Args:
            writer (User): The writer receiving the bonus.
            special_order (SpecialOrder): The special order related to the bonus.
            amount (float): The bonus amount.
            category (str): The category of the bonus.
            reason (str, optional): The reason for granting the bonus.

        Returns:
            WriterBonus: The created writer bonus object.
        """
        return WriterBonus.objects.create(
            writer=writer,
            special_order=special_order,
            amount=amount,
            category=category,
            reason=reason
        )

    @staticmethod
    def mark_bonus_as_paid(bonus):
        """
        Marks a writer bonus as paid.

        Args:
            bonus (WriterBonus): The bonus to mark as paid.

        Returns:
            WriterBonus: The updated writer bonus object.
        """
        bonus.is_paid = True
        bonus.save()
        return bonus