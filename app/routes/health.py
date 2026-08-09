from flask import Blueprint, jsonify

from app import db
from app.services.event_service import get_redis


health_bp = Blueprint("health", __name__)


@health_bp.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok"
    }), 200