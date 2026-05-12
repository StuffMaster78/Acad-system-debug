class EventGrouper:

    @staticmethod
    def group_by_correlation(events):

        grouped = {}

        for e in events:
            grouped.setdefault(e.correlation_id, []).append(e)

        return grouped

    @staticmethod
    def group_by_span(events):

        grouped = {}

        for e in events:
            key = e.span_id or "no-span"
            grouped.setdefault(key, []).append(e)

        return grouped

    @staticmethod
    def group_by_object(events):

        grouped = {}

        for e in events:
            key = f"{e.object_type}:{e.object_id}"
            grouped.setdefault(key, []).append(e)

        return grouped