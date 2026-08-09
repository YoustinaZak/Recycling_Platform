from datetime import datetime

from flask import Blueprint, jsonify, request

from app.models import RecyclingEvent
from app import db
from app.services.event_service import create_event


events_bp = Blueprint("events", __name__)


@events_bp.route("/events", methods=["POST"])
def create_event_route():
    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body must be JSON"
        }), 400

    required_fields = [
        "machine_id",
        "material_type",
        "item_count",
        "event_timestamp"
    ]

    missing_fields = [
        field for field in required_fields
        if field not in data
    ]

    if missing_fields:
        return jsonify({
            "error": "Missing required fields",
            "fields": missing_fields
        }), 400

    if not isinstance(data["machine_id"], str) or not data["machine_id"].strip():
        return jsonify({
            "error": "machine_id must be a non-empty string"
        }), 400

    if not isinstance(data["material_type"], str) or not data["material_type"].strip():
        return jsonify({
            "error": "material_type must be a non-empty string"
        }), 400

    if not isinstance(data["item_count"], int) or data["item_count"] <= 0:
        return jsonify({
            "error": "item_count must be a positive integer"
        }), 400

    try:
        event_timestamp = datetime.fromisoformat(
            data["event_timestamp"].replace("Z", "+00:00")
        )
    except (ValueError, TypeError):
        return jsonify({
            "error": "event_timestamp must be a valid ISO-8601 timestamp"
        }), 400

    event = create_event(
        machine_id=data["machine_id"],
        material_type=data["material_type"],
        item_count=data["item_count"],
        event_timestamp=event_timestamp
    )

    return jsonify(event_to_dict(event)), 202

@events_bp.route("/events", methods=["GET"])
def list_events():
    events = RecyclingEvent.query.order_by(
        RecyclingEvent.event_timestamp.desc()
    ).all()

    return jsonify([
        event_to_dict(event)
        for event in events
    ]), 200

def event_to_dict(event):
    return {
        "id": str(event.id),
        "machine_id": event.machine_id,
        "material_type": event.material_type,
        "item_count": event.item_count,
        "event_timestamp": event.event_timestamp.isoformat(),
        "processing_status": event.processing_status,
        "estimated_weight_kg": event.estimated_weight_kg,
        "created_at": event.created_at.isoformat(),
        "processed_at": (
            event.processed_at.isoformat()
            if event.processed_at
            else None
        )
    }

@events_bp.get("/events/<uuid:event_id>")
def get_event(event_id):
    event = db.session.get(RecyclingEvent, event_id)

    if event is None:
        return {"error": "Event not found"}, 404

    return {
        "id": str(event.id),
        "machine_id": event.machine_id,
        "material_type": event.material_type,
        "item_count": event.item_count,
        "event_timestamp": event.event_timestamp.isoformat(),
        "processing_status": event.processing_status,
        "estimated_weight_kg": event.estimated_weight_kg,
        "created_at": event.created_at.isoformat(),
        "processed_at": (
            event.processed_at.isoformat()
            if event.processed_at
            else None
        )
    }, 200