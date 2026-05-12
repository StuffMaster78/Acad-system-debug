class DeduplicationService:

    @staticmethod
    def deduplicate(events):

        seen = set()
        output = []

        for e in events:

            key = (
                e.action,
                e.object_type,
                e.object_id,
                e.span_id,
            )

            if key in seen:
                continue

            seen.add(key)
            output.append(e)

        return output