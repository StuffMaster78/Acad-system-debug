from writer_management.models.levels import WriterLevel


class OrderAccessService:
    @staticmethod
    def writer_meets_level(
        writer, order
    ) -> bool:
        if not order.min_writer_level:
            return True  # No restriction

        writer_level = (
            WriterLevel.objects
            .filter(writer=writer)
            .values_list("level", flat=True)
            .first()
        )

        if not writer_level:
            return False

        levels = ["Novice", "Skilled", "Pro", "Elite"]

        try:
            writer_idx = levels.index(writer_level)
            required_idx = levels.index(order.min_writer_level)
        except ValueError:
            return False

        return writer_idx >= required_idx

    @staticmethod
    def can_request(writer, order) -> bool:
        return OrderAccessService.writer_meets_level(writer, order)

    @staticmethod
    def can_take(writer, order) -> bool:
        return OrderAccessService.writer_meets_level(writer, order)

    @staticmethod
    def can_be_assigned(writer, order, by_admin=False) -> bool:
        if by_admin or order.admin_override:
            return True
        return OrderAccessService.writer_meets_level(writer, order)