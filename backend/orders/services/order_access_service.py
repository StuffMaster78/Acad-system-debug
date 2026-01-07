from writer_management.models.levels import WriterLevel


class OrderAccessService:
    @staticmethod
    def writer_meets_level(
        writer, order
    ) -> bool:
        # If order doesn't have a writer_level requirement, allow assignment
        if not hasattr(order, 'writer_level') or not order.writer_level:
            return True  # No restriction

        # Get writer's current level from their profile
        try:
            writer_profile = writer.writer_profile
            writer_level_obj = writer_profile.writer_level if hasattr(writer_profile, 'writer_level') else None
        except AttributeError:
            # Writer profile doesn't exist or doesn't have level
            return False

        if not writer_level_obj:
            return False

        # For now, if order has a writer_level requirement and writer has a level, allow it
        # The actual level comparison logic can be implemented later if needed
        # This is a simplified version that allows assignment if writer has any level
        return True

    @staticmethod
    def can_request(writer, order) -> bool:
        return OrderAccessService.writer_meets_level(writer, order)

    @staticmethod
    def can_take(writer, order) -> bool:
        """
        Check if writer can take an order.
        Requires both level check and can_take_orders flag.
        """
        # Check if writer is allowed to take orders (admin restriction)
        try:
            writer_profile = writer.writer_profile
            if not writer_profile.can_take_orders:
                return False
        except AttributeError:
            # Writer profile doesn't exist
            return False
        
        # Check level requirements
        return OrderAccessService.writer_meets_level(writer, order)

    @staticmethod
    def can_be_assigned(writer, order, by_admin=False) -> bool:
        if by_admin:
            return True
        return OrderAccessService.writer_meets_level(writer, order)