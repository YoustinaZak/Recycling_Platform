import uuid

from datetime import datetime, timezone

from app import db


class RecyclingEvent(db.Model):
    __tablename__ = "recycling_events"

    id = db.Column(
        db.UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    machine_id = db.Column(
        db.String(100),
        nullable=False
    )

    material_type = db.Column(
        db.String(50),
        nullable=False
    )

    item_count = db.Column(
        db.Integer,
        nullable=False
    )

    event_timestamp = db.Column(
        db.DateTime(timezone=True),
        nullable=False
    )

    processing_status = db.Column(
        db.String(20),
        nullable=False,
        default="received"
    )

    estimated_weight_kg = db.Column(
        db.Float,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    processed_at = db.Column(
        db.DateTime(timezone=True),
        nullable=True
    )
    __table_args__ = (
        db.CheckConstraint(
            "item_count > 0",
            name="check_item_count_positive"
        ),
        db.CheckConstraint(
            "processing_status IN ('received', 'processed', 'failed')",
            name="check_processing_status"
        ),
    )