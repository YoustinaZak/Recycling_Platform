from prometheus_client import Counter

events_processed = Counter(
    "recycling_events_processed_total",
    "Number of recycling events successfully processed",
)

events_failed = Counter(
    "recycling_events_failed_total",
    "Number of recycling events that failed",
)