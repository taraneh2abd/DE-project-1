import os
import redis

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

# هر key کش‌شده بعد از ۱۰ دقیقه expire می‌شود
CACHE_TTL_SECONDS = 600
