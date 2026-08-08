import os
#environment variables, docker can override them

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/dropme"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    REDIS_URL = os.getenv(
        "REDIS_URL",
        "redis://localhost:6379/0"
    )