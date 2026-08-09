from flask import Blueprint, jsonify

from app import db
from app.services.event_service import get_redis

readiness_bp = Blueprint("readiness", __name__)

@readiness_bp.route("/ready", methods=["GET"])
def ready():
    database_status = "ok"
    redis_status = "ok"

    try:
        db.session.execute(db.text("SELECT 1"))
    except Exception:
        database_status = "unavailable"

    try:
        redis_client = get_redis()
        redis_client.ping()
    except Exception:
        redis_status = "unavailable"

    ready = (
        database_status == "ok"
        and redis_status == "ok"
    )

    response = {
        "status": "ready" if ready else "not_ready",
        "database": database_status,
        "redis": redis_status
    }

    return jsonify(response), 200 if ready else 503