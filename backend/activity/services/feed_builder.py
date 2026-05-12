from activity.services.deduplication_service import DeduplicationService
from activity.domain.scoring_rules import ActivityScoringRules
from activity.selectors.activity_selectors import AuditTraceSelectors


class FeedBuilder:

    def build_user_feed(self, actor_id, limit=100):

        events = AuditTraceSelectors.full_trace_by_actor(actor_id)

        # 1. deduplicate noise
        events = DeduplicationService.deduplicate(events)

        # 2. attach scores
        enriched = [
            {
                "event": e,
                "score": ActivityScoringRules.score(e),
            }
            for e in events
        ]

        # 3. rank by score + recency
        enriched.sort(
            key=lambda x: (
                x["score"],
                x["event"].timestamp
            ),
            reverse=True
        )

        # 4. return structured feed
        return [
            {
                "action": item["event"].action,
                "actor": item["event"].actor_id,
                "object": item["event"].object_id,
                "correlation_id": item["event"].correlation_id,
                "span": item["event"].span_name,
                "score": item["score"],
                "timestamp": item["event"].timestamp,
            }
            for item in enriched[:limit]
        ]