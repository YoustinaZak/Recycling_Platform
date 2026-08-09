import json
import os
from datetime import datetime, timezone

import redis
from dotenv import load_dotenv
from prometheus_client import start_http_server

from app import create_app, db
from app.models import RecyclingEvent
from worker.metrics import (
    events_failed,
    events_processed,
    queue_length,
)

load_dotenv()

redis_client = redis.from_url(
    os.getenv("REDIS_URL"),
    decode_responses=True,
    socket_timeout=15,
    socket_connect_timeout=5,
)

QUEUE_NAME = "recycling_events"

MATERIAL_WEIGHTS = {
    "PET": 0.02,
    "CAN": 0.015,
    "GLASS": 0.25,
    "PAPER": 0.01,
}


def process_event(event_id):
    app = create_app()

    with app.app_context():
        event = db.session.get(RecyclingEvent, event_id)

        if event is None:
            print(f"Event {event_id} not found")
            return False

        if event.processing_status == "processed":
            print(f"Event {event_id} is already processed")
            return False

        weight_per_item = MATERIAL_WEIGHTS.get(
            event.material_type.upper(),
            0.02,
        )

        event.estimated_weight_kg = (
            event.item_count * weight_per_item
        )

        event.processing_status = "processed"
        event.processed_at = datetime.now(timezone.utc)

        db.session.commit()

        print(
            f"Processed event {event_id}: "
            f"{event.estimated_weight_kg} kg"
        )

        return True


def run_worker():
    start_http_server(8000)

    print("Worker started...")
    print(f"Listening on queue: {QUEUE_NAME}")

    while True:
        try:
            result = redis_client.blpop(
                QUEUE_NAME,
                timeout=5,
            )

            if result is None:
                queue_length.set(
                    redis_client.llen(QUEUE_NAME)
                )
                continue

            _, message = result

            queue_length.set(
                redis_client.llen(QUEUE_NAME)
            )

            event_data = json.loads(message)
            event_id = event_data["event_id"]

            print(f"Received event: {event_id}")

            try:
                processed = process_event(event_id)

                if processed:
                    events_processed.inc()

                queue_length.set(
                    redis_client.llen(QUEUE_NAME)
                )

            except Exception as exc:  # noqa: BLE001
                events_failed.inc()

                print(
                    f"Failed to process event "
                    f"{event_id}: {exc}"
                )

        except redis.RedisError as exc:
            print(f"Redis connection error: {exc}")


if __name__ == "__main__":
    run_worker()