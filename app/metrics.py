from prometheus_client import Gauge

queue_length = Gauge(
    "recycling_queue_length",
    "Current number of events waiting in the Redis queue",
)
