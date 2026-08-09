import json

import redis

from flask import current_app

from app import db
from app.models import RecyclingEvent


def get_redis():
    return redis.from_url(
        current_app.config["REDIS_URL"],
        decode_responses=True
    )


def create_event(
    machine_id,
    material_type,
    item_count,
    event_timestamp
):
    event = RecyclingEvent(
        machine_id=machine_id,
        material_type=material_type,
        item_count=item_count,
        event_timestamp=event_timestamp,
        processing_status="received"
    )

    db.session.add(event)
    db.session.commit()

    redis_client = get_redis()

    redis_client.rpush(
        "recycling_events",
        json.dumps({
            "event_id": str(event.id)
        })
    )

    return event