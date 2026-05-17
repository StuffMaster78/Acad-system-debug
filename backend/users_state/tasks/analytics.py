# from celery import shared_task


# @shared_task
# def handle_analytics_event(event_payload: dict):
#     """
#     Emits analytics events for dashboards and reporting.
#     """

#     event_type = event_payload.get("type")

#     # Replace later with:
#     # - Kafka
#     # - ClickHouse
#     # - Segment
#     # - BigQuery

#     _track_event(event_type, event_payload)


# def _track_event(event_type: str, payload: dict):
#     print(f"[ANALYTICS] {event_type} -> {payload}")