import os
import redis
from dotenv import load_dotenv

load_dotenv()

r = redis.from_url(
    os.getenv("REDIS_URL"),
    decode_responses=True
)

print("PING:", r.ping())
print("Queue length:", r.llen("recycling_events"))