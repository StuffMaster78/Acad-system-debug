class WriterPerformanceAggregator:
    @staticmethod
    def aggregate(writer) -> dict:
        """
        Returns a dict of writer performance stats used in badge logic.
        This should be cached or precomputed where possible.
        """
        return {
            "weeks_in_top_10": 3,
            "total_earned": 1025,
            "orders_with_zero_revisions": 12,
            "dispute_free_orders": 25,
            "daily_activity_streak": 8,
            "preferred_by_clients": 6,
        }