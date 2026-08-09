from flask import Blueprint, render_template

from app.models import RecyclingEvent


ui_bp = Blueprint("ui", __name__)


@ui_bp.get("/")
def dashboard():
    events = RecyclingEvent.query.order_by(
        RecyclingEvent.event_timestamp.desc()
    ).all()

    return render_template(
        "events.html",
        events=events
    )