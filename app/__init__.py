from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from app.config import Config

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    from app.routes.events import events_bp
    from app.routes.health import health_bp
    from app.routes.readiness import readiness_bp

    app.register_blueprint(events_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(readiness_bp)

    return app