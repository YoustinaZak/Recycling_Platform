from prometheus_client import Counter, Gauge

events_processed = Counter(
    "recycling_events_processed_total",
    "Number of recycling events successfully processed",
)

events_failed = Counter(
    "recycling_events_failed_total",
    "Number of recycling events that failed",
)

queue_length = Gauge(
    "recycling_queue_length",
    "Current number of events waiting in the Redis queue",
)