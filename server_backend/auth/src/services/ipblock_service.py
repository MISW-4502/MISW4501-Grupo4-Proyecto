import redis
from src.config.config import Config

BLOCK_THRESHOLD = 5
BLOCK_DURATION_SECONDS = 15 * 60  # 15 minutos

def get_redis_client():
    return redis.Redis(
        host=Config.REDIS_HOST,
        port=Config.REDIS_PORT,
        db=0
    )

def _key(ip):
    return f"ipblock:{ip}"

def is_ip_blocked(ip):
    redis_client = get_redis_client()
    count = redis_client.get(_key(ip))
    return count is not None and int(count) >= BLOCK_THRESHOLD

def register_failed_attempt(ip):
    redis_client = get_redis_client()
    key = _key(ip)
    current = redis_client.get(key)

    if current:
        redis_client.incr(key)
    else:
        redis_client.setex(key, BLOCK_DURATION_SECONDS, 1)

def reset_ip(ip):
    redis_client = get_redis_client()
    redis_client.delete(_key(ip))
