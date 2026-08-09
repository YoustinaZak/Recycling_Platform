from flask import Blueprint, Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    generate_latest,
)

from app.metrics import queue_length

metrics_bp = Blueprint("metrics", __name__)

events_created = Counter(
    "events_created_total",
    "Total number of recycling events created",
)

events_processed = Counter(
    "events_processed_total",
    "Total number of recycling events processed",
)

events_failed = Counter(
    "events_failed_total",
    "Total number of recycling events that failed",
)


@metrics_bp.route("/metrics")
def metrics():
    return Response(
        generate_latest(),
        mimetype=CONTENT_TYPE_LATEST,
    )